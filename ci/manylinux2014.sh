#!/bin/bash -ex

source ./ci/lib-setup.sh
source ./ci/lib-deploy.sh

setup::rh::yuminst krb5-devel

for python in /opt/python/*/bin/python; do
    if [[ $python == *35* ]]; then
        continue
    fi

    $python -m pip install --install-option='--no-cython-compile' cython
    $python setup.py bdist_wheel
done

for whl in dist/*.whl; do
    auditwheel repair $whl
done

python=/opt/python/cp38-cp38/bin/python
$python -m pip install twine

echo 'Running: set +x, python -m twine upload...'
set +x
$python -m twine upload -u $TWINE_USER -p $TWINE_PASSWORD wheelhouse/*.whl \
       >out.log 2>&1 || true
set -x

egrep -i 'fail|error' out.log && cat.out.log && exit 1

exit 0
