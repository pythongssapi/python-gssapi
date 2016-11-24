#!/bin/bash -ex

if [ x"$PYTHON" = "x3" ]; then
    IS3="3"
else
    IS3=""
fi

# We test Debian's cython.  el7's cython is too old, and Rawhide's virtualenv
# doesn't work right (usrmerge bugs) so we can only test Debian's cython.

if [ -f /etc/debian_version ]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update

    if [ x"$KRB5_VER" = "xheimdal" ]; then
        apt-get -y install heimdal-dev
    else
        apt-get -y install krb5-{user,kdc,admin-server,multidev} libkrb5-dev
    fi

    apt-get -y install gcc virtualenv python$IS3-{virtualenv,dev} cython$IS3

    virtualenv --system-site-packages -p $(which python${PYTHON}) .venv
    source ./.venv/bin/activate
elif [ -f /etc/redhat-release ]; then
    # yum has no update-only verb

    yum -y install krb5-{devel,libs,server,workstation} which gcc findutils

    if [ -f /etc/fedora-release ]; then
        # path to binary here in case Rawhide changes it
        yum install -y redhat-rpm-config \
            /usr/bin/virtualenv python${PYTHON}-{virtualenv,devel}
        virtualenv -p $(which python${PYTHON}) .venv
        source ./.venv/bin/activate
        pip install --install-option='--no-cython-compile' cython
    else
        # Cython on el7 is too old - downstream patches
        yum install -y python$IS3-{virtualenv,devel}
        virtualenv -p $(which python$IS3) .venv
        source ./.venv/bin/activate
        pip install --upgrade pip # el7 pip doesn't quite work right
        pip install --install-option='--no-cython-compile' cython
    fi
else
    echo "Distro not found!"
    false
fi

pip install -r test-requirements.txt

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

flake8 setup.py
F8_SETUP=$?

flake8 gssapi
F8_PY=$?

# Cython requires special flags since it is not proper Python
# E225: missing whitespace around operator
# E226: missing whitespace around arithmetic operator
# E227: missing whitespace around bitwise or shift operator
# E402: module level import not at top of file
# E901: SyntaxError or IndentationError
# E999: Internal AST compilation error (flake8 specific)
flake8 gssapi --filename='*.pyx,*.pxd' --ignore=E225,E226,E227,E402,E901,E999
F8_MAIN_CYTHON=$?

python setup.py nosetests --verbosity=3
TEST_RES=$?

if [ $F8_SETUP -eq 0 -a $F8_PY -eq 0 -a $F8_MAIN_CYTHON -eq 0 -a $TEST_RES -eq 0 ]; then
    exit 0
else
    exit 1
fi
