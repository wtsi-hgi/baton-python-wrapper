import json
import logging
import os
import subprocess
from abc import ABCMeta
from datetime import timedelta
from enum import Enum
from typing import List, Union, Any

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, File

from baton._baton_constants import BATON_ERROR_MESSAGE_KEY, BATON_FILE_DOES_NOT_EXIST_ERROR_CODE
from baton._baton_constants import BATON_ERROR_PROPERTY, BATON_ERROR_CODE_KEY
from baton._json_to_model import baton_json_to_irods_file
from baton._model_to_json import file_to_baton_json, search_criteria_to_baton_json
from baton.mappers import IrodsMapper, IrodsFileMapper
from baton.models import IrodsFile


class BatonBinary(Enum):
    """
    Names of baton binaries.
    """
    BATON = "baton"
    BATON_METAQUERY = "baton-metaquery"
    BATON_LIST = "baton-list"


class BatonIrodsMapper(IrodsMapper, metaclass=ABCMeta):
    """
    Superclass for all baton mappers.
    """
    def __init__(self, baton_binaries_directory: str, irods_query_zone: str,
                 skip_baton_binaries_validation: bool=False, timeout_queries_after: timedelta=None):
        """
        Constructor.
        :param baton_binaries_directory: the location of baton's binaries
        :param irods_query_zone: the iRODS zone to query
        :param skip_baton_binaries_validation: skips validation of baton binaries (intending for testing only)
        """
        if not skip_baton_binaries_validation:
            if not BatonIrodsMapper.validate_baton_binaries_location(baton_binaries_directory):
                raise ValueError(
                    "Given baton binary direcory (%s) did not contain all of the required binaries with executable "
                    "permissions (%s)"
                    % (baton_binaries_directory, [name.value for name in BatonBinary]))

        self._baton_binaries_directory = baton_binaries_directory
        self._irods_query_zone = irods_query_zone
        self.timeout_queries_after = timeout_queries_after

    def run_baton_query(self, baton_binary: BatonBinary, program_arguments: List[str]=None, input_data: Any=None) \
            -> List[dict]:
        """
        Runs a baton query.
        :param baton_binary: the baton binary to use
        :param program_arguments: arguments to give to the baton binary
        :param input_data: input data to the baton binary
        :return: parsed json returned by baton
        """
        if program_arguments is None:
            program_arguments = []

        baton_binary_location = os.path.join(self._baton_binaries_directory, baton_binary.value)
        program_arguments = [baton_binary_location] + program_arguments

        logging.debug("Running baton command: '%s' with data '%s'" % (program_arguments, input_data))
        baton_out = self._run_command(program_arguments, input_data=input_data)
        logging.debug("baton output: %s" % baton_out)

        if baton_out[0] != '[':
            # If information about multiple files is returned, baton does not return valid JSON - it returns a line
            # separated list of JSON, where each line corresponds to a different file
            baton_out = "[%s]" % baton_out.replace('\n', ',')

        baton_out_as_json = json.loads(baton_out)
        BatonIrodsMapper._raise_any_errors_given_in_baton_out(baton_out_as_json)

        return baton_out_as_json

    def _run_command(self, arguments: List[str], input_data: Any=None, output_encoding: str="utf-8") -> str:
        """
        Run a command as a subprocess.

        Ignores errors given over stderr if there is output on stdout (this is the case where baton has been run
        correctly and has expressed the error in it's JSON out, which can be handled more appropriately upstream to this
        method.)
        :param arguments: the arguments to run
        :param input_data: the input data to pass to the subprocess
        :param output_encoding: optional specification of the output encoding to expect
        :return: the process' standard out
        """
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        if isinstance(input_data, list):
            for to_write in input_data:
                to_write_as_json = json.dumps(to_write)
                process.stdin.write(str.encode(to_write_as_json))
            input_data = None
        else:
            input_data = str.encode(json.dumps(input_data))

        out, error = process.communicate(input=input_data, timeout=self.timeout_queries_after)

        if out == "" and error != "":
            IOError(error)

        return out.decode(output_encoding).rstrip()

    @staticmethod
    def validate_baton_binaries_location(baton_binaries_directory: str) -> bool:
        """
        Validates that the given directory contains the baton binaries required to use the metadata_mapper.
        :param baton_binaries_directory: the directory to check
        :return: whether the directory has the required binaries
        """
        for baton_binary in BatonBinary:
            binary_location = os.path.join(baton_binaries_directory, baton_binary.value)
            if not (os.path.isfile(binary_location) and os.access(binary_location, os.X_OK)):
                return False
        return True

    @staticmethod
    def _raise_any_errors_given_in_baton_out(baton_out_as_json: List[dict]):
        """
        Raises any errors that baton has expressed in its output.
        :param baton_out_as_json: the output baton gave as parsed json
        """
        if not isinstance(baton_out_as_json, list):
            baton_out_as_json = [baton_out_as_json]

        for baton_item_as_json in baton_out_as_json:
            if BATON_ERROR_PROPERTY in baton_item_as_json:
                error = baton_item_as_json[BATON_ERROR_PROPERTY]
                error_message = error[BATON_ERROR_MESSAGE_KEY]
                error_code = error[BATON_ERROR_CODE_KEY]

                if error_code == BATON_FILE_DOES_NOT_EXIST_ERROR_CODE:
                    raise FileNotFoundError(error_message)
                else:
                    raise RuntimeError(error_message)


class BatonIrodsFileMapper(BatonIrodsMapper, IrodsFileMapper):
    """
    Mapper for iRODS files.
    """
    def get_by_metadata(self, search_criteria: Union[SearchCriterion, SearchCriteria],
                        load_metadata: bool=True) -> List[IrodsFile]:
        if isinstance(search_criteria, SearchCriterion):
            search_criteria = SearchCriteria([search_criteria])

        baton_json = search_criteria_to_baton_json(search_criteria)
        arguments = self._create_baton_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return BatonIrodsFileMapper._baton_json_to_irods_files(baton_out_as_json)

    def get_by_path(self, files: Union[File, List[File]], load_metadata: bool=True) -> List[IrodsFile]:
        if not isinstance(files, list):
            files = [files]
        if len(files) == 0:
            return []

        baton_json = []
        for file in files:
            baton_json.append(file_to_baton_json(file))
        arguments = self._create_baton_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)

        return BatonIrodsFileMapper._baton_json_to_irods_files(baton_out_as_json)

    def _create_baton_arguments(self, load_metadata: bool=True) -> List[str]:
        """
        Create arguments to use with baton.
        :param load_metadata: whether baton should load metadata
        :return: the arguments to use with baton
        """
        arguments = ["--obj", "--acl", "--checksum", "--replicate", "--zone", self._irods_query_zone]
        if load_metadata:
            arguments.append("--avu")
        return arguments

    @staticmethod
    def _baton_json_to_irods_files(files_as_baton_json: List[dict]) -> List[IrodsFile]:
        """
        Converts the baton representation of multiple iRODS files to a list of `IrodsFile` models.
        :param files_as_baton_json: the baton json representation of the files
        :return: the equivalent models of the json represented files
        """
        assert(isinstance(files_as_baton_json, list))

        files = []
        for file_as_baton_json in files_as_baton_json:
            files.append(baton_json_to_irods_file(file_as_baton_json))

        return files
