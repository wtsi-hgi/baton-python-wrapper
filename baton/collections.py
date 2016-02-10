from copy import copy
from typing import Dict, Sequence, Union, Optional, Sized, Iterable, Any, Set

from baton.models import DataObjectReplica
from hgicommon.collections import Metadata
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion


class IrodsMetadata(Metadata):
    """
    iRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are sets.

    Units are no currently considered.
    """
    def __init__(self, seq: Dict=None):
        super().__init__()
        if seq is not None:
            for key, value in seq.items():
                self[key] = value

    def get(self, key: str, default=None) -> Set[str]:
        value = super().get(key, default)
        assert isinstance(value, set)
        return value

    def add(self, key: str, value: str):
        """
        Adds the given value to the set of data stored under the given key.
        :param key: the set's key
        :param value: the value to add in the set associated to the given key
        """
        if key in self:
            # Use super to get mutable set
            super().__getitem__(key).add(value)
        else:
            self[key] = {value}

    def __getitem__(self, key: str) -> Set[str]:
        value = super().__getitem__(key)
        assert isinstance(value, set)
        # Return copy to keep underlying data immutable
        return copy(value)

    def __setitem__(self, key: str, value: Set[str]):
        assert isinstance(value, set)
        super().__setitem__(key, value)

    @staticmethod
    def from_metadata(metadata: Metadata) -> Any:
        """
        Static factory method to create an equivalent instance of this type from the given `Metadata` instance.
        :param metadata: the `Metadata` instance to create an instance of this class from
        :return: the created instance of this class
        """
        irods_metadata = IrodsMetadata()
        for key, value in metadata.items():
            irods_metadata[key] = {value}
        return irods_metadata


class DataObjectReplicaCollection(Sized, Iterable):
    """
    Collection of data object replicas.
    """
    def __init__(self, data_object_replicas: Iterable[DataObjectReplica]=()):
        """
        Constructor.
        :param data_object_replicas: (optional) replica to go into this collection initially
        """
        self._data = dict()     # type: Dict[int, DataObjectReplica]
        for data_object_replica in data_object_replicas:
            self.add(data_object_replica)

    def get_all(self) -> Sequence[DataObjectReplica]:
        """
        Gets all of the replica in this collection.
        :return: the replica in this collection
        """
        return list(self._data.values())

    def get_by_number(self, number: int) -> Optional[DataObjectReplica]:
        """
        Gets the data object replica in this collection with the given number. Will return `None` if such replica does
        not exist.
        :param number: the number of the data object replica to get
        :return: the data object replica in this collection with the given number
        """
        return self._data[number]

    def get_out_of_date(self) -> Sequence[DataObjectReplica]:
        """
        Gets any data object replica that are marked as out of date/not in date.
        :return: the out of data object replica
        """
        out_of_date = []
        for number, data_object_replica in self._data.items():
            if not data_object_replica.up_to_date:
                out_of_date.append(data_object_replica)
        return out_of_date

    def add(self, data_object_replica: DataObjectReplica):
        """
        Adds the given data object replica to this collection. Will raise a `ValueError` if a data object replica with
        the same number already exists.
        :param data_object_replica: the data object replica to add
        """
        if data_object_replica.number in self._data:
            raise ValueError(
                    "Data object replica with number %d already exists in this collection" % data_object_replica.number)
        self._data[data_object_replica.number] = data_object_replica

    def remove(self, identifier: Union[DataObjectReplica, int]):
        """
        Removes a data object from this collection that has the given unique identifier. A `ValueError` will be raised
        if a data object with the given identifier does not exist.
        :param identifier: the identifier of the data object
        """
        if isinstance(identifier, int):
            self._remove_by_number(identifier)
        elif isinstance(identifier, DataObjectReplica):
            self._remove_by_object(identifier)
        else:
            raise TypeError("Can only remove by number or by object reference: `%s` given" % type(identifier))

    def _remove_by_number(self, number: int):
        """
        Removes the data object from this collection with the given number. A `ValueError` will be raised if a data
        object with the given number does not exist.
        :param number: the number of the data object to remove
        """
        if number not in self._data:
            raise ValueError("Data object replica number %d is not in this collection" % number)
        del self._data[number]
        assert number not in self._data

    def _remove_by_object(self, data_object_replica: DataObjectReplica):
        """
        Removes the given data object from this collection. A `ValueError` will be raised if the given data object does
        not exist within this collection.
        :param data_object_replica: the data object replica to remove
        """
        self.remove(data_object_replica.number)

    def __eq__(self, other: Any) -> bool:
        if type(other) != DataObjectReplicaCollection:
            return False
        return other._data == self._data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterable[DataObjectReplica]:
        return self._data.values().__iter__()



# class SearchCriteria(Sequence):
#     """
#     A collection of `SearchCriterion`.
#     """
#     _DUPLICATE_ERROR_MESSAGE = "Search criterion based on the attribute `%s` already added"
#     _SENTINEL = SearchCriterion("", "", ComparisonOperator.EQUALS)
#
#     def __init__(self, search_criterions: Iterable[SearchCriterion]=()):
#         self._data = []
#         for search_criterion in search_criterions:
#             self.append(search_criterion)
#
#     def append(self, search_criterion: SearchCriterion):
#         """
#         Appends a search criterion to this collection.
#         :param search_criterion: the search criterion to add
#         """
#         if self.find_by_attribute(search_criterion.attribute) is not None:
#             raise ValueError(SearchCriteria._DUPLICATE_ERROR_MESSAGE)
#         self._data.append(search_criterion)
#
#     def extend(self, search_criteria: Iterable[SearchCriterion]):
#         """
#         Extend this collection by appending search criterion from another search criteria.
#         :param search_criteria: the search criteria to merge
#         """
#         for search_criteria in search_criteria:
#             self.append(search_criteria)
#
#     def pop(self, index: int) -> SearchCriterion:
#         """
#         Removes the search criterion from this collection at the given index.
#         :param index: index of the search criteria to remove
#         """
#         return self._data.pop(index)
#
#     def find_by_attribute(self, attribute: str) -> Optional[SearchCriterion]:
#         """
#         Find search criteria in this collection based on the attribute it searches on.
#         :param attribute: the search criterion attribute to search on
#         :return: the matched search criterion
#         """
#         for existing_search_criterion in self:
#             if existing_search_criterion.attribute == attribute:
#                 return existing_search_criterion
#         return None
#
#     def remove_by_attribute(self, attribute: str):
#         """
#         Remove search criteria that uses the given attribute from this collection.
#         :param attribute: the search criteria attribute to search on
#         """
#         if self.find_by_attribute(attribute) is None:
#             raise ValueError("Search criteria with the given attribute was not found")
#         deleted = False
#         index = 0
#         while not deleted:
#             if self[index].attribute == attribute:
#                 del self[index]
#                 deleted = True
#             index += 1
#
#     def __delitem__(self, index: int):
#         del self._data[index]
#
#     def __eq__(self, other: Any) -> bool:
#         if type(other) != type(self):
#             return False
#         return other._data == self._data
#
#     def __iter__(self) -> Iterable[SearchCriterion]:
#         return self._data.__iter__()
#
#     def __len__(self) -> int:
#         return len(self._data)
#
#     def __getitem__(self, index: int) -> Any:
#         return self._data[index]
#
#     def __setitem__(self, index: int, search_criterion: SearchCriterion):
#         if len(self._data) <= index:
#             raise IndexError("Index out of range")
#
#         # Temp replace current so checking for search criteria with same attribute ignores the value at the replace
#         # index
#         current_value = self._data[index]
#         self._data[index] = SearchCriteria._SENTINEL
#
#         if self.find_by_attribute(search_criterion.attribute):
#             self._data[index] = current_value
#             raise ValueError(SearchCriteria._DUPLICATE_ERROR_MESSAGE)
#
#         self._data[index] = search_criterion
#
#     def __contains__(self, value: SearchCriterion) -> bool:
#         return value in self._data
#
#     def __str__(self):
#         return str(self._data)
#
#     def __repr__(self) -> str:
#         return "<%s object at %s: %s>" % (type(self), id(self), str(self))
