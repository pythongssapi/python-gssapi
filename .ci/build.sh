#!/bin/bash -ex

# set up dependencies, etc
source ./.ci/lib-setup.sh
setup::install

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

# always build in-place so that Sphinx can find the modules
python setup.py build_ext --inplace $EXTRA_BUILDEXT
BUILD_RES=$?

if [ $BUILD_RES -ne 0 ]; then
    # if the build failed, don't run the tests
    exit $BUILD_RES
fi

if [ x"$KRB5_VER" = "xheimdal" ] || [ "$TRAVIS_OS_NAME" = "windows" ]; then
    # heimdal/Windows can't run the tests yet, so just make sure it imports and exit
    python -c "import gssapi"
    exit $?
fi

python setup.py nosetests --verbosity=3
TEST_RES=$?

exit $TEST_RES
