import os
import subprocess
from typing import List, Tuple, Union

from baton.json_converters import object_to_baton_json
from baton.models import IrodsFileLocation, SearchCriteria


class Baton:
    """
    TODO
    """
    def __init__(self, baton_location: str, irods_query_zone: str):
        """
        TODO
        :param baton_location:
        :param irods_query_zone:
        """
        self._baton_location = baton_location
        self._irods_query_zone = irods_query_zone

    def get_metadata_by_file_path(self, file_paths: Union[str, List[str]]) -> List[Tuple(str, str)]:
        """
        Gets the metadata in iRODS for the file with at the given path.
        :param file_path: the path of the file in iRODS
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

        return self._run_baton_query(baton_json)

    def get_metadata_by_attribute(self, search_criteria: SearchCriteria) -> List[Tuple(str, str)]:
        """
        Gets metadata in iRODS that matches one or more of the given attribute search criteria.
        :param search_criteria_to_match: the search criteria to get metadata by
        :return: metadata that matches the given search critera
        """
        baton_json = object_to_baton_json(search_criteria)
        return self._run_baton_query(baton_json)

    def _run_baton_query(self, baton_json):
        """
        TODO
        :param baton_json:
        :return:
        """
        arguments = [self._baton_location, "--avu", "--acl", "--checksum"]

        if isinstance(baton_json, list):
            return Baton._run(arguments, write_to_standard_in=baton_json)
        else:
            return Baton._run(arguments, input_data=baton_json)

    @staticmethod
    # TODO: What is the difference between input_data and write to standard in?
    def _run(arguments: List[str], input_data: dict=None, write_to_standard_in: List[str]=()):
        """
        TODO
        :param arguments:
        :param input_data:
        :param write_to_standard_in:
        :return:
        """
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        if write_to_standard_in is not None:
            for to_write in write_to_standard_in:
                process.stdin.write(to_write)

        out, error = process.communicate(input=input_data)  # TODO: timeout=

        if error:
            raise IOError("iRODs error : " + str(error))
        return out
