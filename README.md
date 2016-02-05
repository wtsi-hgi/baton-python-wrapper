# baton Python Wrapper


## Introduction
Python 3 Wrapper for [baton](https://github.com/wtsi-npg/baton), superseding a 
[previous implementation in meta-datacheck]
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
from baton import connect_to_irods_with_baton, Connection, IrodsEntity, IrodsMetadata, DataObject, Collection, SpecificQuery
from hgicommon import SearchCriteria, SearchCriterion, ComparisonOperator

# Setup connection to iRODS using baton
irods = connect_to_irods_with_baton("/where/baton/binaries/are/installed/", "irods_query_zone") # type: Connection

# Get information about the data objects or collections at the given path(s) in iRODS
irods.data_object.get_by_path("/collection/data_object")    # type: List[DataObject]:
irods.collection.get_by_path(["/collection", "/other_collection"])   # type: List[Collection]:

# Setup search for data objects or collections based on their metadata
search_criterion_1 = SearchCriterion("attribute", "match_value", ComparisonOperator.EQUALS)
search_criterion_2 = SearchCriterion("other_attribute", "other_match_value", ComparisonOperator.LESS_THAN)
search_criteria = SearchCriteria({search_criterion_1, search_criterion_2})  # Collection of `SearchCriterion`
# Do search
irods.data_object.get_by_metadata(search_criteria)   # type: List[DataObject]
irods.collection.get_by_metadata(search_criteria)   # type: List[Collection]

# Get data objects in a collection(s)
irods.data_object.get_in_collection("/collection")    # type: List[DataObject]
irods.data_object.get_in_collection(["/collection", "/other_collection"])   # type: List[DataObject]

# Get specific queries that have been installed on the iRODS server
irods.specific_query.get_all()  # type: List[SpecificQuery]
```


## How to develop
### Testing
#### Locally
To run the tests, use ``./scripts/run-tests.sh`` from the project's root directory. This script will use ``pip`` to 
install all requirements for running the tests (use `virtualenv` if necessary).
