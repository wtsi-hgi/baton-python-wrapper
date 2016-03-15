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
```python
from baton.api import connect_to_irods_with_baton, Connection
from baton.models import IrodsEntity, DataObject, Collection, SpecificQuery, SearchCriterion, ComparisonOperator
from baton.collections import IrodsMetadata

# Setup connection to iRODS using baton
irods = connect_to_irods_with_baton("/where/baton/binaries/are/installed/", skip_baton_binaries_validation=False) # type: Connection

# Get information about the data objects or collections at the given path(s) in iRODS
irods.data_object.get_by_path("/collection/data_object")    # type: Sequence[DataObject]:
irods.collection.get_by_path(["/collection", "/other_collection"])   # type: Sequence[Collection]:

# Setup search for data objects or collections based on their metadata
search_criterion_1 = SearchCriterion("attribute", "match_value", ComparisonOperator.EQUALS)
search_criterion_2 = SearchCriterion("other_attribute", "other_match_value", ComparisonOperator.LESS_THAN)
# Do search
irods.data_object.get_by_metadata(search_criterion_1, zone="OptionalZoneRestriction")   # type: Sequence[DataObject]
irods.collection.get_by_metadata([search_criterion_1, search_criterion_2])   # type: Sequence[Collection]

# Get data objects in a collection(s)
irods.data_object.get_in_collection("/collection")    # type: Sequence[DataObject]
irods.data_object.get_in_collection(["/collection", "/other_collection"])   # type: Sequence[DataObject]

# Get specific queries that have been installed on the iRODS server
irods.specific_query.get_all(zone="OptionalZoneRestriction")  # type: Sequence[SpecificQuery]
```

### JSON Serialization/Deserialization
There are JSON encoders and decoders for nearly all iRODS object models in this library. These can be used to convert 
models to/from their baton defined JSON representations. All serializers/deserializers extend `JSONEncoder` and
`JSONDecoder` (most through use of the [hgijson](https://github.com/wtsi-hgi/python-json/) library) meaning that they 
can be used with [Python's built in `json` package](https://docs.python.org/3/library/json.html):
```python
import json
from baton.json import DataObjectJSONEncoder, DataObjectJSONDecoder, CollectionJSONEncoder, CollectionJSONDecoder

data_object_as_json_string = json.dumps(data_object, cls=DataObjectJSONEncoder)
data_object = json.loads(data_object_as_json_string, cls=DataObjectJSONDecoder)

collection_as_json_string = json.dumps(collection, cls=CollectionJSONEncoder)
collection = json.loads(collection_as_json_string, cls=CollectionJSONDecoder)

```


## How to develop
### Testing
#### Locally
To run the tests, use ``./scripts/run-tests.sh`` from the project's root directory. This script will use ``pip`` to 
install all requirements for running the tests (use `virtualenv` if necessary).
