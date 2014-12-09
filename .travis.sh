#!/bin/sh

flake8 setup.py
F8_SETUP=$?

flake8 gssapi
F8_PY=$?

flake8 gssapi --filename='*.pyx,*.pxd' --ignore=E225,E226,E227,E901
F8_MAIN_CYTHON=$?

python setup.py nosetests
TEST_RES=$?

if [ $F8_SETUP -eq 0 -a $F8_PY -eq 0 -a $F8_MAIN_CYTHON -eq 0 -a $TEST_RES -eq 0 ]; then
    exit 0
else
    exit 1
fi
