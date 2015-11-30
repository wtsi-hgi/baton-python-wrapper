import json
import logging
import os
import subprocess
from abc import ABCMeta
from enum import Enum
from typing import List, Union

from datetime import timedelta
from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, Model, File

from baton._json_converters import object_to_baton_json, baton_json_to_object
from baton.mappers import IrodsMapper, IrodsMetadataMapper, IrodsFileMapper
from baton.models import IrodsFile, IrodsMetadata

_BATON_ERROR = "error"
_BATON_AVUS = "avus"
_BATON_ERROR_MESSAGE_KEY = "message"
_BATON_ERROR_CODE_KEY = "code"
_BATON_FILE_DOES_NOT_EXIST_ERROR_CODE = -310000


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

    def run_baton_query(
            self, baton_binary: BatonBinary, program_arguments: List[str]=None, input_data_as_json: dict=None) -> dict:
        """
        Runs a baton query.
        :param baton_binary: the baton binary to use
        :param program_arguments: arguments to give to the baton binary
        :param input_data_as_json: input data to the baton binary
        :return: parsed json returned by baton
        """
        if program_arguments is None:
            program_arguments = []

        baton_binary_location = os.path.join(self._baton_binaries_directory, baton_binary.value)
        program_arguments = [baton_binary_location] + program_arguments

        logging.debug("Running baton command: '%s' with data '%s'" % (program_arguments, input_data_as_json))
        baton_out = self._run_command(program_arguments, input_data=input_data_as_json)
        logging.debug("baton output: %s" % baton_out)

        baton_out_as_json = json.loads(baton_out)
        BatonIrodsMapper._raise_any_errors_given_in_baton_out(baton_out_as_json)

        return baton_out_as_json

    def _run_command(self, arguments: List[str], input_data: dict=None, output_encoding: str="utf-8") -> str:
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
    def _raise_any_errors_given_in_baton_out(baton_out_as_json: dict):
        """
        Raises any errors that baton has expressed in its output.
        :param baton_out_as_json: the output baton gave as parsed json
        """
        if _BATON_ERROR in baton_out_as_json:
            error = baton_out_as_json[_BATON_ERROR]
            error_message = error[_BATON_ERROR_MESSAGE_KEY]
            error_code = error[_BATON_ERROR_CODE_KEY]

            if error_code == _BATON_FILE_DOES_NOT_EXIST_ERROR_CODE:
                raise FileNotFoundError(error_message)
            else:
                raise RuntimeError(error_message)

    # TODO: Move to JSON converts
    @staticmethod
    def _baton_out_as_json_to_model(
            baton_output_as_json: dict, expect_type: type, expect_list: bool) -> Union[Model, List[Model]]:
        """
        Converts baton output to a model or collection of models.
        :param baton_output_as_json:
        :param expect_type:
        :param expect_list:
        :return:
        """
        if expect_list:
            models = []
            for array_element in baton_output_as_json:
                model = baton_json_to_object(array_element, expect_type)
                models.append(model)
            return models
        else:
            return baton_json_to_object(baton_output_as_json, expect_type)


class BatonIrodsMetadataMapper(BatonIrodsMapper, IrodsMetadataMapper):
    """
    Mapper for iRODS metadata.
    """
    def get_for_file(self, files: Union[File, List[File]]) -> IrodsMetadata:
        if not isinstance(files, list):
            files = [files]
        if len(files) == 0:
            return []

        baton_json = []
        for file in files:
            baton_json.append(object_to_baton_json(file))

        return self._run_file_metadata_query(baton_json)

    def _run_file_metadata_query(self, baton_json: Union[dict, List[dict]]) -> IrodsMetadata:
        """
        Run a baton attribute value query defined by the given JSON.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_out_as_json = self.run_baton_query(
            BatonBinary.BATON_LIST, ["--avu", "--acl", "--checksum"], input_data_as_json=baton_json)
        return BatonIrodsMapper._baton_out_as_json_to_model(baton_out_as_json, IrodsMetadata, False)


class BatonIrodsFileMapper(BatonIrodsMapper, IrodsFileMapper):
    """
    Mapper for iRODS files.
    """
    def get_by_metadata_attribute(self, search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[IrodsFile]:
        if isinstance(search_criteria, SearchCriterion):
            search_criteria = SearchCriteria([search_criteria])

        baton_json = object_to_baton_json(search_criteria)
        return self._run_baton_irods_file_query(baton_json)

    def _run_baton_irods_file_query(self, baton_json: Union[dict, List[dict]]) -> List[IrodsFile]:
        """
        Runs a baton meta query.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_out_as_json = self.run_baton_query(
            BatonBinary.BATON_METAQUERY,
            ["--obj", "--checksum", "--replicate" "--zone", self._irods_query_zone], input_data_as_json=baton_json)
        return BatonIrodsMapper._baton_out_as_json_to_model(baton_out_as_json, IrodsFile, True)
