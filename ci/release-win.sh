#!/bin/bash -e

source ./ci/lib-setup.sh
source ./ci/lib-deploy.sh

./ci/build.sh

# Sigh, go find paths again
export PATH="/c/Program Files/MIT/Kerberos/bin:$PATH"

# build the wheel
python -m pip install wheel
python setup.py bdist_wheel

cd dist

tag=$(git describe --tags)

# Rename and checksum the wheel
if [ x"${tag#v[0-9]}" = "x${tag}" ]; then
    PYTHON_GSSAPI_VERSION=${tag}
else
    PYTHON_GSSAPI_VERSION=${tag#v}
fi

PKG_NAME_VER=$(ls *.whl | sed "s/gssapi-[^-]*-\(.*\)\.whl/python-gssapi-${PYTHON_GSSAPI_VERSION}-\1/")

cp *.whl "${PKG_NAME_VER}.whl"

sha512sum --binary ./${PKG_NAME_VER}.whl > ./${PKG_NAME_VER}.sha512sum

cd ..

# Hack around https://github.com/pypa/gh-action-pypi-publish/issues/32

echo 'Running: python -m pip install twine ...'
python -m pip install twine

echo 'Running: set +x; python -m twine upload...'
# Please note this cannot be set -x or passwords will leak!
set +x

python -m twine upload -u $TWINE_USER -p $TWINE_PASSWORD dist/gssapi* > out.log 2>&1 || true

# and restore...
set -x
egrep -i 'fail|error' out.log && cat out.log && exit 1

exit 0
