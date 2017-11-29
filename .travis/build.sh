#!/bin/bash -ex

# set up dependencies, etc
source ./.travis/lib-setup.sh
setup::install

# always build in-place so that Sphinx can find the modules
python setup.py build_ext --inplace
BUILD_RES=$?

if [ x"$KRB5_VER" = "xheimdal" ]; then
    # heimdal can't run the tests yet, so just exit
    exit $BUILD_RES
fi

if [ $BUILD_RES -ne 0 ]; then
    # if the build failed, don't run the tests
    exit $BUILD_RES
fi

python setup.py nosetests --verbosity=3
TEST_RES=$?

exit $TEST_RES
