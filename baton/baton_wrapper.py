import os
import subprocess
from typing import List, Tuple, Union
import json¶

from baton.json_converters import object_to_baton_json
from baton.models import IrodsFileLocation, SearchCriteria


class Baton:
    """
    Setup to run queries using baton.
    """
    def __init__(self, baton_location: str, irods_query_zone: str):
        """
        Constructor.
        :param baton_location: the location of baton's binaries
        :param irods_query_zone: the iRODS zone to query
        """
        self._baton_location = baton_location
        self._irods_query_zone = irods_query_zone

    def get_metadata_by_file_path(self, file_paths: Union[str, List[str]]) -> List[Tuple(str, str)]:
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
            irods_file_location = IrodsFileLocation(directory, file_name)
            baton_json.append(object_to_baton_json(irods_file_location))

        return self._run_baton_attribute_query(baton_json)

    def get_metadata_by_attribute(self, search_criteria: SearchCriteria) -> List[Tuple(str, str)]:
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
        arguments = [self._baton_location, "--avu", "--acl", "--checksum"]

        if isinstance(baton_json, list):
            return Baton._parse_baton_output(Baton._run_command(arguments, write_to_standard_in=baton_json))
        else:
            return Baton._parse_baton_output(Baton._run_command(arguments, input_data=baton_json))

    # TODO: What is the difference between input_data and write to standard in?
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
