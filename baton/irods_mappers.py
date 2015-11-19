import json
import os
import subprocess
from abc import ABCMeta
from enum import Enum
from typing import List, Tuple, Union

from baton._json_converters import object_to_baton_json, baton_json_to_object
from baton.models import IrodsFile, SearchCriteria, SearchCriterion


class _BinaryNames(Enum):
    """
    Names of the baton binaries that are required.
    """
    BATON = "baton"
    META_QUERY = "baton-metaquery"


class BatonMapper(metaclass=ABCMeta):
    """
    A data mapper as defined by Martin Fowler (see: http://martinfowler.com/eaaCatalog/dataMapper.html) that moves data
    between objects and iRODS, while keeping them independent of each other and the mapper itself. Uses baton.
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
            if not BatonMapper.validate_baton_binaries_location(baton_binaries_directory):
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
            # print(binary_location)
            # print(os.path.isfile(binary_location))
            # print(os.access(binary_location, os.X_OK))
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

        if isinstance(input_data, list):
            for to_write in input_data:
                process.stdin.write(to_write)
            # input_data = None

        # out, error = process.communicate(input=input_data)  # TODO: timeout=
        out, error = process.communicate()  # TODO: timeout=
        if error:
            raise IOError(error)

        processed_out = out.decode(output_encoding).rstrip()
        return processed_out

    @staticmethod
    def _parse_json_output(out: str) -> dict:
        """
        Parses JSON output, converting it from a string to a dict.
        :param out: the output as a string
        :return: the output as a dict
        """
        returned_json = json.loads(out)
        if isinstance(returned_json, dict):
            raise ValueError("Not JSON:\n%s" % returned_json)
        return returned_json


class BatonMetadataMapper(BatonMapper):
    """
    Mapper for iRODS metadata.
    """
    def get_for_file(self, file_paths: Union[str, List[str]]) -> List[Tuple[str, str]]:
        """
        Gets the metadata in iRODS for the file with at the given path.
        :param file_paths: the path of the file in iRODS
        :return: the metadata associated with the file
        """
        if not isinstance(file_paths, list):
            file_paths = [file_paths]
        if len(file_paths) == 0:
            return []

        baton_json = []
        for file_path in file_paths:
            directory, file_name = os.path.split(file_path)
            irods_file = IrodsFile(directory, file_name)
            baton_json.append(object_to_baton_json(irods_file))

        return self._run_baton_attribute_query(baton_json)

    def get_by_attribute(self, search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[Tuple[str, str]]:
        """
        Gets metadata in iRODS that matches one or more of the given attribute search criteria.
        :param search_criteria: the search criteria to get metadata by
        :return: metadata that matches the given search criteria
        """
        baton_json = object_to_baton_json(search_criteria)
        return self._run_baton_attribute_query(baton_json)

    def _run_baton_attribute_query(self, baton_json: Union[dict, List[dict]]) -> dict:
        """
        Run a baton attribute value query defined by the given JSON.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_binary_location = os.path.join(self._baton_binaries_directory, _BinaryNames.BATON)
        arguments = [baton_binary_location, "--avu", "--acl", "--checksum", "--zone", self._irods_query_zone]

        baton_out = BatonMapper._run_command(arguments, input_data=baton_json)
        return BatonMapper._parse_json_output(baton_out)


class BatonFileMapper(BatonMapper):
    """
    Mapper for iRODS files.
    """
    def get_by_metadata_attribute(
            self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[IrodsFile]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :return: the matched files in iRODS
        """
        baton_json = object_to_baton_json(metadata_search_criteria)
        return self._run_baton_meta_query(baton_json)

    def _run_baton_meta_query(self, baton_json: Union[dict, List[dict]]) -> List[IrodsFile]:
        """
        Runs a baton meta query.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_meta_query_binary_location = os.path.join(self._baton_binaries_directory, _BinaryNames.META_QUERY)
        arguments = [baton_meta_query_binary_location, "--obj", "--zone", self._irods_query_zone]

        baton_out = BatonMapper._run_command(arguments, input_data=baton_json)
        parsed_out = BatonMapper._parse_json_output(baton_out)

        irods_files = []
        for irods_file_as_baton_json in parsed_out:
            irods_file = baton_json_to_object(irods_file_as_baton_json, IrodsFile)
            irods_files.append(irods_file)

        return irods_files
