FROM python:3.4-wheezy
MAINTAINER hgi@sanger.ac.uk

COPY . /baton-python-wrapper
WORKDIR baton-python-wrapper

RUN ./scripts/pip-install-requirements.sh

CMD ["./scripts/run-tests.sh"]