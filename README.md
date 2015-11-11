# baton Python Wrapper
Based on: https://github.com/wtsi-hgi/metadata-check/blob/9cd5c41b0f2e254fc1d6249a14752bd428587bb7/irods_baton/baton_wrapper.py


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