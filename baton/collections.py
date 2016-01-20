from typing import Sequence, Union, Optional, Sized, Iterable, Any

from baton.models import DataObjectReplica


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
        return self._data.values()

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

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterable[DataObjectReplica]:
        return self._data.values().__iter__()
