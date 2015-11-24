import json
import os
import subprocess
from abc import ABCMeta
from enum import Enum
from typing import List, Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, Metadata, Model, File

from baton._json_converters import object_to_baton_json, baton_json_to_object
from baton.mappers import IrodsMapper, IrodsMetadataMapper, IrodsFileMapper


class _BinaryNames(Enum):
    """
    Names of the baton binaries that are required.
    """
    BATON = "baton"
    BATON_METAQUERY = "baton-metaquery"
    BATON_LIST = "baton-list"


class BatonIrodsMapper(IrodsMapper, metaclass=ABCMeta):
    """
    Superclass for all baton mappers.
    """
    def __init__(self, baton_binaries_directory: str, irods_query_zone: str,
                 skip_baton_binaries_validation: bool=False):
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
                    % (baton_binaries_directory, [name.value for name in _BinaryNames]))

        self._baton_binaries_directory = baton_binaries_directory
        self._irods_query_zone = irods_query_zone

    @staticmethod
    def validate_baton_binaries_location(baton_binaries_directory: str) -> bool:
        """
        Validates that the given directory contains the baton binaries required to use the mapper.
        :param baton_binaries_directory: the directory to check
        :return: whether the directory has the required binaries
        """
        for binary_name in _BinaryNames:
            binary_location = os.path.join(baton_binaries_directory, binary_name.value)
            if not (os.path.isfile(binary_location) and os.access(binary_location, os.X_OK)):
                return False
        return True

    @staticmethod
    def _run_command(arguments: List[str], input_data: dict=None, output_encoding: str="utf-8") -> str:
        """
        Run a command as a subprocess.
        :param arguments: the arguments to run
        :param input_data: the input data to pass to the subprocess
        :param output_encoding: optional specification of the output encoding to expect
        :return: the process' standard out
        """
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        # print(input_data)
        # input_data = str.encode('{"collection": "/iplant/home/testuser", "avus": []}')

        # FIXME: Other types?
        if isinstance(input_data, list):
            for to_write in input_data:
                to_write_as_json = json.dumps(to_write)
                process.stdin.write(str.encode(to_write_as_json))
            # input_data = None

        # out, error = process.communicate(input=input_data)  # TODO: timeout=
        out, error = process.communicate()  # TODO: timeout=
        if error:
            raise IOError(error)

        return out.decode(output_encoding).rstrip()

    @staticmethod
    def _parse_baton_output(baton_output_as_str: str, expect_type: type, expect_list: bool) -> Union[Model, List[Model]]:
        """
        TODO
        :param baton_output_as_str:
        :param expect_type:
        :param expect_list:
        :return:
        """
        print(baton_output_as_str)
        baton_output_as_json = json.loads(baton_output_as_str)

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
    def get_for_file(self, files: Union[File, List[File]]) -> List[Metadata]:
        if not isinstance(files, list):
            files = [files]
        if len(files) == 0:
            return []

        baton_json = []
        for file in files:
            baton_json.append(object_to_baton_json(file))

        return self._run_file_metadata_query(baton_json)

    def get_by_attribute(self, search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[Metadata]:
        baton_json = object_to_baton_json(search_criteria)
        return self._run_file_metadata_query(baton_json)

    def _run_file_metadata_query(self, baton_json: Union[dict, List[dict]]) -> Metadata:
        """
        Run a baton attribute value query defined by the given JSON.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_binary_location = os.path.join(self._baton_binaries_directory, _BinaryNames.BATON_LIST.value)
        arguments = [baton_binary_location, "--avu", "--acl", "--checksum"]

        baton_out = BatonIrodsMapper._run_command(arguments, input_data=baton_json)
        return BatonIrodsMapper._parse_baton_output(baton_out, File, True)


class BatonIrodsFileMapper(BatonIrodsMapper, IrodsFileMapper):
    """
    Mapper for iRODS files.
    """
    def get_by_metadata_attribute(
            self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[File]:
        baton_json = object_to_baton_json(metadata_search_criteria)
        return self._run_baton_irods_file_query(baton_json)

    def _run_baton_irods_file_query(self, baton_json: Union[dict, List[dict]]) -> List[File]:
        """
        Runs a baton meta query.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_meta_query_binary_location = os.path.join(self._baton_binaries_directory, _BinaryNames.BATON_METAQUERY.value)
        arguments = [baton_meta_query_binary_location, "--obj", "--zone", self._irods_query_zone]

        baton_out = BatonIrodsMapper._run_command(arguments, input_data=baton_json)
        return BatonIrodsMapper._parse_baton_output(baton_out, File, True)
