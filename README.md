# baton Python Wrapper


## Introduction
Python 3 Wrapper for [baton](https://github.com/wtsi-npg/baton), based on [previous implementation in meta-datacheck]
(https://github.com/wtsi-hgi/metadata-check/blob/9cd5c41b0f2e254fc1d6249a14752bd428587bb7/irods_baton/baton_wrapper.py).

The wrapper does not currently provide access to all of baton's functionality.


## How to use in your project
### Including required libraries
In ``/requirements.txt`` or in your ``/setup.py`` script:
```
git+https://github.com/wtsi-hgi/baton-python-wrapper.git@master#egg=baton
git+https://github.com/wtsi-hgi/common-python.git@master#egg=hgicommon
```
*See more about using libraries for git repositories in the 
[pip documentation](https://pip.readthedocs.org/en/1.1/requirements.html#git).*


### API
```python
from baton import connect_to_irods_with_baton, Connection, IrodsFile, IrodsMetadata
from hgicommon import SearchCriteria, SearchCriterion, ComparisonOperator

# Setup connection to iRODS using baton
irods = connect_to_irods_with_baton("/where/baton/binaries/are/installed/", "irods_query_zone") # type: Connection

# Get metadata corresponding to the given file(s)
irods.metadata.get_by_file_path("collection/data_object")    # type: List[IrodsMetadata]:
irods.metadata.get_by_file_path(["collection/data_object", "collection/other_data_object_"])    # type: List[IrodsMetadata]:

# Setup metadata search
search_criterion_1 = SearchCriterion("attribute", "match_value", ComparisonOperator.EQUALS)
search_criterion_2 = SearchCriterion("other_attribute", "other_match_value", ComparisonOperator.LESS_THAN)
search_criteria = SearchCriteria([search_criterion_1, search_criterion_2])  # Collection of SearchCriterion

# Do file search based on metadata attribute values
# Note: File objects are not populated with the contents of the file on iRODS
irods.file.get_by_metadata_attribute(search_criteria)   # type: List[IrodsFile]
```


## How to develop
### Testing
#### Locally
To run the tests, use ``./scripts/run-tests.sh`` from the project's root directory. This script will use ``pip`` to 
install all requirements for running the tests (use `virtualenv` if necessary).

#### Using Docker
From the project's root directory:
```
$ docker build -t wtsi-hgi/baton-python-wrapper/test -f docker/tests/Dockerfile .
$ docker run wtsi-hgi/baton-python-wrapper/test
```