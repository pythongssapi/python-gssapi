#!/bin/bash -ex

# set up dependencies, etc
source ./ci/lib.sh

if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
    echo "::group::Installing Requirements"
fi

lib::setup::install

if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
    echo "::endgroup::"
    echo "::group::Running Sanity Checks"
fi

if [ x"$FLAKE" = "xyes" ]; then
    flake8 setup.py
    F8_SETUP=$?

    flake8 gssapi
    F8_PY=$?

    # Cython requires special flags since it is not proper Python:
    # - E225: missing whitespace around operator
    # - E226: missing whitespace around arithmetic operator
    # - E227: missing whitespace around bitwise or shift operator
    # - E402: module level import not at top of file (needed for the `GSSAPI="blah" lines)
    # - E901: SyntaxError or IndentationError
    # - E999: Internal AST compilation error (flake8 specific)
    flake8 gssapi --filename='*.pyx,*.pxd' --ignore=E225,E226,E227,E402,E901,E999
    F8_MAIN_CYTHON=$?

    if [ $F8_SETUP -ne 0 -o $F8_PY -ne 0 -o $F8_MAIN_CYTHON -ne 0 ]; then
        exit 1
    fi
fi

python -m mypy .
MYPY_RES=$?
if [ $MYPY_RES -ne 0 ]; then
    exit $MYPY_RES
fi

if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
    echo "::endgroup::"
    echo "::group::Running Tests"
fi

# Ensure we don't run in the normal dir so that unittest imports our installed
# package and not the source code
pushd gssapi/tests

# Only call exit on failures so we can source this script
if [ "$OS_NAME" = "windows" ]; then
    # Windows can't run the tests yet, so just make sure it imports and exit
    python -c "import gssapi" || exit $?
else
    python -m unittest -v || exit $?
fi

popd

if [ x"${GITHUB_ACTIONS}" = "xtrue" ]; then
    echo "::endgroup::"
fi
