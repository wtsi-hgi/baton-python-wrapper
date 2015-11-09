import json
import os
import subprocess

from typing import List


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

    def query_by_metadata_and_get_results_as_json(self, avu_tuple_list, operator='='):
        """
        This method is querying iRODS using BATON in order to get the metadata for the files (data objects) that match the search criteria.
        The information is returned as a dict of collection, data_object and avus. It can be filtered afterwards for leaving in only the info of interest.
        :param avu_tuple_list: key = attribute name, value = attribute_value
        :param zone:
        :param operator:
        :return: a tempfile
        WARNING:
            1. This assumes that the operator is always =
            2. This assumes that there is exactly 1 entry for each type of attribute - there can't be a query for 2 samples for exp.
        """
        irods_avus = self._from_dict_to_irods_avus(avu_tuple_list)
        irods_avus_json = json.dumps(irods_avus)
        return self._get_baton_metaquery_result(irods_avus_json)

    def get_file_metadata(self, file_path):
        """
        :param file_path:
        :return:
        """
        fpath_as_dict = self._split_path_in_data_obj_and_coll(file_path)
        irods_fpath_dict_as_json = json.dumps(fpath_as_dict)
        return self._get_baton_list_metadata_result(irods_fpath_dict_as_json)

    def get_all_files_metadata(self, file_paths: List[str]):
        """
        TODO
        :param file_paths:
        :return:
        """
        # TODO: This probably has commonality with `get_file_metadata` yet it doesn't use it
        list_of_fpaths_as_json = []
        for file_path in file_paths:
            fpath_as_dict = self._split_path_in_data_obj_and_coll(file_path)
            irods_fpath_dict_as_json = json.dumps(fpath_as_dict)
            list_of_fpaths_as_json.append(irods_fpath_dict_as_json)
        return self._get_baton_list_metadata_for_list_of_files_result(list_of_fpaths_as_json)

    def _from_dict_to_irods_avus(self, avus_tuple_list):
        """
        TODO
        :param avus_tuple_list:
        :return:
        """
        irods_avu_list = []
        for attribute, value in avus_tuple_list:
            irods_avu_list.append({ "attribute": attribute, "value" : value, "o" : "="})
        return {'avus' : irods_avu_list}

    def _split_path_in_data_obj_and_coll(self, fpath_irods):
        """
        TODO
        :param fpath_irods:
        :return:
        """
        dir, fname = os.path.split(fpath_irods)
        return {'data_object' : fname, 'collection' : dir}

    def _get_baton_metaquery_result(self, query_as_json):
        """
        This method queries by metadata iRODS using BATON and returns the result as json writen to a temp file.
        :param query_as_json:
        :return: the path to a temp file where the results are
        """
        # Open/create a tempfile:
        #temp = tempfile.NamedTemporaryFile(mode='w')
        p = subprocess.Popen([self._baton_location, '--zone', self._irods_query_zone, '--obj', '--checksum', '--avu', '--acl'],   # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE) # ,stdout=temp, stderr=subprocess.STDERR
        out, err = p.communicate(input=query_as_json)
        if err:
            #print "ERROR REPORT: " + str(err)
            raise IOError("Some irods error : " + str(err))
        # if err:
        #     print "ERROR VIA stderr " + str(err)
        #     #raise IOError
        return out
        #return temp

    def _get_baton_list_metadata_result(self, data_obj_as_json):
        """
        TODO
        :param data_obj_as_json:
        :return:
        """
        #jq -n '[{data_object: "10080_8#64.bam", collection: "/seq/10080/"}]' | /software/gapi/pkg/baton/0.15.0/bin/baton-list -avu --acl
        p = subprocess.Popen([self._baton_location, '--avu', '--acl', '--checksum'],     # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate(input=data_obj_as_json)
        #print "OUT: " + str(out) + "ERR " + str(err)
        if err:
            raise IOError("Some irods error : " + str(err))
        return out

    def _get_baton_list_metadata_for_list_of_files_result(self, list_of_data_obj_as_json):
        """
        TODO
        :param list_of_data_obj_as_json:
        :return:
        """
        p = subprocess.Popen([self._baton_location, '--avu', '--acl', '--checksum'],     # not necessary to add also '--checksum' if --replicate is there
                             stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        for f in list_of_data_obj_as_json:
            p.stdin.write(f)
        out, err = p.communicate()
        #print "OUT: " + str(out) + "ERR " + str(err)
        if err:
            raise IOError("Some irods error : " + str(err))
        return out
