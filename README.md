[![Build Status](https://travis-ci.org/wtsi-hgi/python-common.svg)](https://travis-ci.org/wtsi-hgi/python-baton-wrapper)
[![codecov.io](https://codecov.io/github/wtsi-hgi/python-baton-wrapper/coverage.svg?branch=develop)](https://codecov.io/github/wtsi-hgi/python-baton-wrapper?branch=develop)
# baton Python Wrapper


## Introduction
Python 3 Wrapper for [baton](https://github.com/wtsi-npg/baton), superseding a 
[previous implementation in meta-datacheck]
(https://github.com/wtsi-hgi/metadata-check/blob/9cd5c41b0f2e254fc1d6249a14752bd428587bb7/irods_baton/baton_wrapper.py).

The wrapper provides access to most, but not all, of baton's functionality.


## How to use in your project
### Including required libraries
In ``/requirements.txt`` or in your ``/setup.py`` script:
```
git+https://github.com/wtsi-hgi/baton-python-wrapper.git@master#egg=baton
```
*See more about using libraries for git repositories in the 
[pip documentation](https://pip.readthedocs.org/en/1.1/requirements.html#git).*


### API
#### Setup
To use the iRODS API, you must first define a "connection" to an iRODS server:
```python
from baton.api import connect_to_irods_with_baton, Connection

# Setup connection to iRODS using baton
irods = connect_to_irods_with_baton("/where/baton/binaries/are/installed/", skip_baton_binaries_validation=False) # type: Connection
```

#### Data Objects and Collections
The API provides the ability to retrieve models of the data objects and collections stored on an iRODS server. Similarly 
to the JSON that baton provides, the models do not contain the payloads. They do however provide access to all of the 
information that baton can retrieve about an entity, including Access Control Lists (ACLs), custom metadata (AVUs),
the content of collections and information about data object replicas. All methods provide the option to not load AVUs.
```python
from baton.models import DataObject, Collection, SpecificQuery, SearchCriterion, ComparisonOperator

# Get models of data objects or collections at the given path(s) in iRODS
irods.data_object.get_by_path("/collection/data_object", load_metadata=False)    # type: DataObject:
irods.collection.get_by_path(["/collection", "/other_collection"])   # type: Sequence[Collection]:

# Setup search for data objects or collections based on their metadata
search_criterion_1 = SearchCriterion("attribute", "match_value", ComparisonOperator.EQUALS)
search_criterion_2 = SearchCriterion("other_attribute", "other_match_value", ComparisonOperator.LESS_THAN)
# Do search to get models of data objects or collections
irods.data_object.get_by_metadata(search_criterion_1, zone="OptionalZoneRestriction")   # type: Sequence[DataObject]
irods.collection.get_by_metadata([search_criterion_1, search_criterion_2], load_metadata=False)   # type: Sequence[Collection]

# Get models of data objects or collections contained within a collection(s)
irods.collection.get_all_in_collection("/collection", load_metadata=False)    # type: Sequence[Collection]
irods.data_object.get_all_in_collection(["/collection", "/other_collection"])   # type: Sequence[DataObject]
```

#### Metadata
The API provides the ability to both retrieve and manipulate the custom metadata (AVUs) associated with data objects and
collections.

Although the type of metadata is the same for both data objects and collections, due to the way iRODS works, it is 
necessary to know the type of entity that a path corresponds to in order to retrieve metadata. 
```python
from baton.collections import IrodsMetadata

# Metadata (methods available for both `data_object` and `collection`)
metadata_examples = [
    IrodsMetadata({"key", (value, )}),
    IrodsMetadata({"another_key", (value_1, value_2)}),
]

irods.data_object.metadata.get_all("/collection/data_object")   # type: Sequence[IrodsMetadata]
irods.collection.metadata.get_all("/collection")   # type: Sequence[IrodsMetadata]

irods.data_object.metadata.add("/collection/data_object", metadata_examples[0])
irods.collection.metadata.add("/collection", metadata_examples)

irods.data_object.metadata.set("/collection/data_object", metadata_examples)
irods.collection.metadata.set("/collection", metadata_examples[1])

irods.data_object.metadata.remove("/collection/data_object", metadata_examples)
irods.collection.metadata.remove("/collection", metadata_examples[1])

irods.data_object.metadata.remove_all("/collection/data_object")
irods.collection.metadata.remove_all("/collection")
```

#### Custom objects via specific queries
iRODS supports specific queries which return new types of object. In order to use such custom objects in iRODS via this
library, a custom model of the object should to be made. Then, a subclass of `BatonCustomObjectMapper` needs to be 
defined to specify how a specific query (or number of specific queries) can be used to retrieve from and/or modify the
object in iRODS.

The API provides the ability to retrieve the queries that are installed on an iRODS server: 
```python
from baton.models import SpecificQuery

# Get specific queries that have been installed on the iRODS server
irods.specific_query.get_all(zone="OptionalZoneRestriction")  # type: Sequence[SpecificQuery]
```

#### JSON Serialization/Deserialization
There are JSON encoders and decoders for nearly all iRODS object models in this library. These can be used to convert 
models to/from their baton defined JSON representations. All serializers/deserializers extend `JSONEncoder` and
`JSONDecoder` (most through use of the [hgijson](https://github.com/wtsi-hgi/python-json/) library) meaning that they 
can be used with [Python's built in `json` package](https://docs.python.org/3/library/json.html):
```python
import json
from baton.json import DataObjectJSONEncoder, DataObjectJSONDecoder, CollectionJSONEncoder, CollectionJSONDecoder, IrodsMetadataJSONEncoder, IrodsMetadataJSONDecoder

data_object_as_json_string = json.dumps(data_object, cls=DataObjectJSONEncoder)
data_object = json.loads(data_object_as_json_string, cls=DataObjectJSONDecoder)

collection_as_json_string = json.dumps(collection, cls=CollectionJSONEncoder)
collection = json.loads(collection_as_json_string, cls=CollectionJSONDecoder)

metadata_as_json_string = json.dumps(metadata, cls=IrodsMetadataJSONEncoder)
metadata = json.loads(metadata_as_json_string, cls=IrodsMetadataJSONDecoder)
```


## How to develop
### Testing
#### Locally
To run the tests, use ``./scripts/run-tests.sh`` from the project's root directory. This script will use ``pip`` to 
install all requirements for running the tests (use `virtualenv` if necessary).
