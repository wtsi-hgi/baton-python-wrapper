# baton Python Wrapper
[![Build Status](https://travis-ci.org/wtsi-hgi/baton-python-wrapper.svg)](https://travis-ci.org/wtsi-hgi/baton-python-wrapper)

## Introduction
Python 3 Wrapper for [baton](https://github.com/wtsi-npg/baton), based on [previous implementation in meta-datacheck](https://github.com/wtsi-hgi/metadata-check/blob/9cd5c41b0f2e254fc1d6249a14752bd428587bb7/irods_baton/baton_wrapper.py).

The wrapper does not currently provide access to all of baton's functionality.


## How to use in your project
### Including the `baton` library
In ``/requirements.txt`` or in your ``/setup.py`` script:
```
git+https://github.com/wtsi-hgi/baton-python-wrapper.git@master#egg=baton
```
*See more about using libraries for git repositories in the 
[pip documentation](https://pip.readthedocs.org/en/1.1/requirements.html#git).*


## API
```python
from baton import Baton, SearchCriteria, SearchCriterion, ComparisonOperator

# Setup baton
baton = Baton("/where/baton/binary/is/installed/baton", "irods_query_zone")

# Change the query zone that baton uses
baton.irods_query_zone = "other_irods_query_zone"

# Get metadata corresponding to the given file(s)
baton.get_metadata_by_file_path("collection/data_object")    # type: List[Tuple(str, str)]:
baton.get_metadata_by_file_path(["collection/data_object", "collection/other_data_object_"])    # type: List[Tuple(str, str)]:

# Search for metadata
# Setup metadata search
search_criteria = SearchCriteria()  # Collection of SearchCriteria (subclass of `list`)
search_criteria.append(SearchCriterion("attribute", "match_value", ComparisonOperator.EQUALS))
search_criteria.append(SearchCriterion("other_attribute", "other_match_value", ComparisonOperator.LESS_THAN))
# Do metadata search
baton.get_metadata_by_attribute(search_criteria)    # type: List[Tuple(str, str)]:
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