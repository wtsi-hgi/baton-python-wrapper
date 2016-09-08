[![Build Status](https://travis-ci.org/wtsi-hgi/python-common.svg)](https://travis-ci.org/wtsi-hgi/python-baton-wrapper)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-baton-wrapper/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/python-baton-wrapper)
# baton Python Wrapper


## Introduction
Python 3 Wrapper for [baton](https://github.com/wtsi-npg/baton), superseding a [previous implementation in 
metadata-check]
(https://github.com/wtsi-hgi/metadata-check/blob/9cd5c41b0f2e254fc1d6249a14752bd428587bb7/irods_baton/baton_wrapper.py).

The wrapper provides access to most of baton's functionality.


## How to use
### Prerequisites
- Python >= 3.5.2
- baton >= 0.16.4
- iRODS >= 4.1.9

*Note: Although older version of baton/iRODS will probably work, the library is only aimed at the versions specified
above.*

### Installation
Stable releases can be installed via [PyPI](https://pypi.python.org/pypi?name=baton&:action=display):
```bash
$ pip3 install baton
```

Bleeding edge versions can be installed directly from GitHub:
```bash
$ pip3 install git+https://github.com/wtsi-hgi/python-baton-wrapper.git@<commit_id_or_branch_or_tag>#egg=baton
```

To declare this library as a dependency of your project, add it to your `requirement.txt` file.


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
from baton.models import DataObject, Collection, SearchCriterion, ComparisonOperator

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

#### Metadata (AVUs)
The API provides the ability to both retrieve and manipulate the custom metadata (AVUs) associated with data objects and
collections.

*Warning: there is currently no support for reading/writing the unit property of AVUs.*

Although the type of metadata is the same for both data objects and collections, due to the way iRODS works, it is 
necessary to know the type of entity that a path corresponds to in order to retrieve metadata. 
```python
from baton.collections import IrodsMetadata

metadata_1 = IrodsMetadata({"key": {"value_1"}})
metadata_2 = IrodsMetadata({"another_key": {"value_1", "value_2"}})

# Metadata (methods available for both `data_object` and `collection`)
irods.data_object.metadata.get_all("/collection/data_object")   # type: IrodsMetadata
irods.collection.metadata.get_all(["/collection", "/other_collection"])   # type: Sequence[IrodsMetadata]

# `metadata_1` is added to the data object with the first path in the list and `metadata_2` is added to the second
irods.data_object.metadata.add(["/collection/data_object", "/other_data_object"], [metadata_1, metadata_2])
irods.collection.metadata.add("/collection", metadata_1)

irods.data_object.metadata.set("/collection/data_object", metadata_1)
# `metadata_1` is added to both collections in the list
irods.collection.metadata.set(["/collection", "/other_collection"], metadata_1)

irods.data_object.metadata.remove(["/collection/data_object", "/other_data_object"], [metadata_1, metadata_2])
irods.collection.metadata.remove("/collection", metadata_1)

irods.data_object.metadata.remove_all("/collection/data_object")
irods.collection.metadata.remove_all(["/collection", "/other_collection"])
```

#### Access Control Lists (ACLs)
The API provides the ability to both retrieve and manipulate the access control lists (ACLs) associated with data 
objects and collections.
```python
from baton.models import AccessControl

# ACLs. Note: it is implied that the owner is in the same zone as the entity to which the access control is applied
acl_examples = [
    AccessControl(User("user_1", "zone_user_is_in"), AccessControl.Level.READ),
    AccessControl(User("group_1", "zone_group_is_in"), AccessControl.Level.WRITE),
    AccessControl("user_1#zone_user_is_in", AccessControl.Level.OWN)
]

irods.data_object.access_control.get_all("/collection/data_object") # type: Set[AccessControl]
irods.collection.access_control.get_all(["/collection", "/another/collection"])  # type: List[Set[AccessControl]]

irods.data_object.access_control.add_or_replace(["/collection/data_object", "/another/data_object"], acl_examples[0])
irods.collection.access_control.add_or_replace("/collection", acl_examples, recursive=True)

irods.data_object.access_control.set("/collection/data_object", acl_examples[1])
irods.collection.access_control.set(["/collection", "/another/collection"], acl_examples[0], recursive=False)

irods.data_object.access_control.revoke(["/collection/data_object", "/another/data_object"], acl_examples)
irods.collection.access_control.revoke("/collection", acl_examples[1], recursive=True)

irods.data_object.access_control.revoke_all(["/collection/data_object", "/another/data_object"])
irods.collection.access_control.revoke_all("/collection", recursive=True)
```

#### Custom objects via specific queries
iRODS supports specific queries which return new types of object. In order to use such custom objects in iRODS via this
library, a custom model of the object should to be made. Then, a subclass of `BatonCustomObjectMapper` needs to be 
defined to specify how a specific query (or number of specific queries) can be used to retrieve from and/or modify the
object in iRODS.

The API provides the ability to retrieve the queries that are installed on an iRODS server (ironically, by use of a 
specific query!):
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
from baton.json import DataObjectJSONEncoder, DataObjectJSONDecoder, CollectionJSONEncoder, CollectionJSONDecoder, IrodsMetadataJSONEncoder, IrodsMetadataJSONDecoder, AccessControlJSONEncoder, AccessControlJSONDecoder

data_object_as_json_string = json.dumps(data_object, cls=DataObjectJSONEncoder)     # type: str
data_object = json.loads(data_object_as_json_string, cls=DataObjectJSONDecoder)     # type: DataObject

collection_as_json_string = json.dumps(collection, cls=CollectionJSONEncoder)   # type: str
collection = json.loads(collection_as_json_string, cls=CollectionJSONDecoder)   # type: Collection

metadata_as_json_string = json.dumps(metadata, cls=IrodsMetadataJSONEncoder)    # type: str
metadata = json.loads(metadata_as_json_string, cls=IrodsMetadataJSONDecoder)    # type: IrodsMetadata

acl_as_json_string = json.dumps(metadata, cls=AccessControlJSONEncoder)     # type: str
acl = json.loads(acl_as_json_string, cls=AccessControlJSONDecoder)  # type: List[AccessControl]
```


## Development
### Setup
Install both library dependencies and the dependencies needed for testing:
```bash
$ pip3 install -q -r requirements.txt
$ pip3 install -q -r test_requirements.txt
```
*A baton installation is not required.*

Some tests use [Docker](https://www.docker.com) therefore a Docker daemon must be running on the test machine, with the 
environment variables `DOCKER_TLS_VERIFY`, `DOCKER_HOST` and `DOCKER_CERT_PATH` set.

### Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v --cover-inclusive --tests baton/tests, baton/tests/_baton
```

To generate a test coverage report with nosetests:
```bash
$ nosetests -v --with-coverage --cover-package=baton --cover-inclusive --tests baton/tests, baton/tests/_baton
```


## License
[LGPL license](LICENSE.txt).

Copyright (c) 2015, 2016 Genome Research Limited
