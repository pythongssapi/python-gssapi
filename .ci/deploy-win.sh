#!/bin/bash -e

# Temporary hack while issue DPL issue persists
# Manually upload wheels via twine for windows
# https://github.com/travis-ci/dpl/issues/1009

success="yes"

# Sigh, go find paths again
PYPATH="/c/Python${PYENV:0:1}${PYENV:2:1}"
export PATH="$PYPATH:$PYPATH/Scripts:/c/Program Files/MIT/Kerberos/bin:$PATH"

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
