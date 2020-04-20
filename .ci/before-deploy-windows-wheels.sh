#!/bin/bash -ex

# See before-deploy.sh for anything unexplained

source ./.ci/lib-setup.sh
source ./.ci/lib-deploy.sh

./.ci/build.sh

# Sigh, go find paths again
PYPATH="/c/Python${PYENV:0:1}${PYENV:2:1}"
export PATH="$PYPATH:$PYPATH/Scripts:/c/Program Files/MIT/Kerberos/bin:$PATH"

# build the wheel
python -m pip install wheel
python setup.py bdist_wheel

cd dist

# Rename and checksum the wheel
if [ x"${TRAVIS_TAG#v[0-9]}" = "x${TRAVIS_TAG}" ]; then
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG}
else
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG#v}
fi

PKG_NAME_VER=$(ls *.whl | sed "s/gssapi-[^-]*-\(.*\)\.whl/python-gssapi-${PYTHON_GSSAPI_VERSION}-\1/")

cp *.whl "${PKG_NAME_VER}.whl"

sha512sum --binary ./${PKG_NAME_VER}.whl > ./${PKG_NAME_VER}.sha512sum

cd ..
