import json
import os
import subprocess

from typing import List, Tuple, Mapping


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

    def query_by_metadata_and_get_results_as_json(self, avu_tuple_list, operator="="):
        """
        This method is querying iRODS using BATON in order to get the metadata for the files (data objects) that match the search criteria.
        The information is returned as a dict of collection, data_object and avus. It can be filtered afterwards for leaving in only the info of interest.
        :param avu_tuple_list: key = attribute name, value = attribute_value
        :param zone:
        :param operator:
        :return: a tempfile
        WARNING:
            1. This assumes that the operator is always =
            2. This assumes that there is exactly 1 entry for each type of attribute - there can"t be a query for 2 samples for exp.
        """
        irods_avus = self._convert_to_baton_avus(avu_tuple_list)
        irods_avus_json = json.dumps(irods_avus)
        return self._get_baton_metaquery_result(irods_avus_json)

    def get_file_metadata(self, file_path):
        """
        :param file_path:
        :return:
        """
        fpath_as_dict = Baton._extract_data_object_and_collection(file_path)
        irods_fpath_dict_as_json = json.dumps(fpath_as_dict)
        return self._get_baton_list_metadata_result(irods_fpath_dict_as_json)

    def get_all_files_metadata(self, file_paths: List[str]):
        """
        TODO
        :param file_paths:
        :return:
        """
        list_of_fpaths_as_json = []
        for file_path in file_paths:
            irods_fpath_dict_as_json = self.get_file_metadata(file_path)
            list_of_fpaths_as_json.append(irods_fpath_dict_as_json)
        return self._get_baton_list_metadata_for_list_of_files_result(list_of_fpaths_as_json)

    def _get_baton_metaquery_result(self, query_as_json):
        """
        This method queries by metadata iRODS using BATON and returns the result as json writen to a temp file.
        :param query_as_json:
        :return: the path to a temp file where the results are
        """
        # Note: it is not necessary to add also "--checksum" if --replicate is there
        return self.run_query(
            [self._baton_location, "--zone", self._irods_query_zone, "--obj", "--checksum", "--avu", "--acl"])

    def _get_baton_list_metadata_result(self, data_obj_as_json):
        """
        TODO
        :param data_obj_as_json:
        :return:
        """
        # Note: it is not necessary to add also "--checksum" if --replicate is there
        return Baton.run_query([self._baton_location, "--avu", "--acl", "--checksum"], input_data=data_obj_as_json)
        #jq -n "[{data_object: "10080_8#64.bam", collection: "/seq/10080/"}]" | /software/gapi/pkg/baton/0.15.0/bin/baton-list -avu --acl

    def _get_baton_list_metadata_for_list_of_files_result(self, list_of_data_obj_as_json):
        """
        TODO
        :param list_of_data_obj_as_json:
        :return:
        """
        return Baton.run_query(
            [self._baton_location, "--avu", "--acl", "--checksum"], write_to_standard_in=list_of_data_obj_as_json)

    @staticmethod
    # TODO: What is the difference between input_data and write to standard in?
    def run_query(arguments: List[str], input_data: dict=None, write_to_standard_in: List[str]=()):
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

    @staticmethod
    def _extract_data_object_and_collection(irods_file_path: str) -> Mapping[str, str]:
        """
        TODO
        :param irods_file_path:
        :return:
        """
        directory, file_name = os.path.split(irods_file_path)
        return {"data_object" : file_name, "collection" : directory}

    @staticmethod
    def _convert_to_baton_avus(list_of_avu_tuples: List[Tuple[str, str]]) -> Mapping[str, List[Mapping[str, str]]]:
        """
        TODO
        :param list_of_avu_tuples:
        :return:
        """
        irods_avu_list = []
        for attribute, value in list_of_avu_tuples:
            irods_avu_list.append({ "attribute": attribute, "value": value, "o": "="})
        return {"avus" : irods_avu_list}
