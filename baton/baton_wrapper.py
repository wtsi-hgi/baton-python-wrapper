import os
import subprocess
from enum import Enum
from typing import List, Tuple, Union
import json

from baton.json_converters import object_to_baton_json
from baton.models import IrodsFile, SearchCriteria, SearchCriterion


class _BinaryNames(Enum):
    """
    TODO
    """
    BATON = "baton",
    METAQUERY = "baton-metaquery"


class BatonMapper:
    """
    TODO
    """
    def __init__(self, baton_binaries_directory: str, irods_query_zone: str):
        """
        Constructor.
        :param baton_binaries_directory: the location of baton's binaries
        :param irods_query_zone: the iRODS zone to query
        """
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
        TODO. "duck-checking"
        :param baton_binaries_directory:
        :return:
        """
        for binary_name in _BinaryNames:
            binary_location = os.path.join(baton_binaries_directory, binary_name)
            if not (os.path.isfile(binary_location) and os.access(binary_location, os.X_OK)):
                return False
        return True

    # TODO: This can probably be tidied up
    @staticmethod
    def _run_command(arguments: List[str], input_data: dict=None, write_to_standard_in: List[str]=()) -> str:
        """
        Run a command as a subprocess.
        :param arguments: the arguments to run
        :param input_data: the input data to communicate to the subprocess
        :param write_to_standard_in: the data to write into the subprocess through the process' standard in
        :return: the process' standard out
        """
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        if write_to_standard_in is not None:
            for to_write in write_to_standard_in:
                process.stdin.write(to_write)

        out, error = process.communicate(input=input_data)  # TODO: timeout=
        if error:
            raise IOError(error)

        return out

    @staticmethod
    def _parse_baton_output(out: str) -> dict:
        """
        Parses baton's JSON output, converting it from a string to a dict.
        :param out: the output as a string
        :return: the output as a dict
        """
        returned_json = json.loads(out)
        if isinstance(returned_json, dict):
            raise ValueError("baton did not return a JSON object:\n%s" % returned_json)
        return returned_json


class BatonMetadataMapper(BatonMapper):
    """
    TODO
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

    # TODO: Allow use with just SearchCriterion
    def get_by_attribute(self, search_criteria: SearchCriteria) -> List[Tuple[str, str]]:
        """
        Gets metadata in iRODS that matches one or more of the given attribute search criteria.
        :param search_criteria: the search criteria to get metadata by
        :return: metadata that matches the given search critera
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

        # TODO: Look at a better way of doing this
        if isinstance(baton_json, list):
            return BatonMapper._parse_baton_output(BatonMapper._run_command(arguments, write_to_standard_in=baton_json))
        else:
            return BatonMapper._parse_baton_output(BatonMapper._run_command(arguments, input_data=baton_json))


class BatonFileMapper(BatonMapper):
    """
    TODO
    """
    def get_by_metadata_attribute(
            self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[IrodsFile]:
        """
        TODO
        :param metadata_search_criteria:
        :return:
        """
        baton_json = object_to_baton_json(metadata_search_criteria)
        return self._run_baton_meta_query(baton_json)

    def _run_baton_meta_query(self, baton_json: Union[dict, List[dict]]) -> dict:
        """
        TODO.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        baton_meta_query_binary_location = os.path.join(self._baton_binaries_directory, _BinaryNames.METAQUERY)
        arguments = [baton_meta_query_binary_location, "--obj", "--zone", self._irods_query_zone]

        # TODO: Look at a better way of doing this
        if isinstance(baton_json, list):
            return BatonMapper._parse_baton_output(BatonMapper._run_command(arguments, write_to_standard_in=baton_json))
        else:
            return BatonMapper._parse_baton_output(BatonMapper._run_command(arguments, input_data=baton_json))
