#!/usr/bin/env bash
pip install -q -r requirements.txt
pip install -q -r test_requirements.txt

nosetests -v --tests baton/tests --tests baton/tests/_baton