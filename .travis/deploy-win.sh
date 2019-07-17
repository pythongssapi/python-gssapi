#!/bin/bash -ex

# Temporary hack while issue DPL issue persists
# Manually upload wheels via twine for windows
# https://github.com/travis-ci/dpl/issues/1009

python -m pip install twine

python -m twine upload -u $PIP_USER -p $PIP_PASSWORD --repository-url https://pypi.org/ dist/*
