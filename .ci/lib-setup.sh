#!/bin/bash

setup::python-suffix() {
    if [ x"$PYTHON" = "x3" ]; then
        echo "3"
    else
        echo ""
    fi
}

# We test Debian's cython.  el7's cython is too old, and Rawhide's virtualenv
# doesn't work right (usrmerge bugs) so we can only test Debian's cython.

setup::debian::install() {
    local IS3=$(setup::python-suffix)

    export DEBIAN_FRONTEND=noninteractive
    apt-get update

    if [ x"$KRB5_VER" = "xheimdal" ]; then
        apt-get -y install heimdal-dev
    else
        apt-get -y install krb5-{user,kdc,admin-server,multidev} libkrb5-dev \
                gss-ntlmssp
    fi

    apt-get -y install gcc virtualenv python$IS3-{virtualenv,dev} cython$IS3

    virtualenv --system-site-packages -p $(which python${PYTHON}) .venv
    source ./.venv/bin/activate
}

setup::rh::yuminst() {
    # yum has no update-only verb.  Also: modularity just makes this slower.
    yum -y --nogpgcheck --disablerepo=\*modul\* install $@
}

setup::centos::install() {
    local IS3=$(setup::python-suffix)

    # Cython on el7 is too old - downstream patches
    setup::rh::yuminst python$IS3-{virtualenv,devel}
    virtualenv -p $(which python$IS3) .venv
    source ./.venv/bin/activate
    pip install --upgrade pip # el7 pip doesn't quite work right
    pip install --install-option='--no-cython-compile' cython
}

setup::fedora::install() {
    # path to binary here in case Rawhide changes it
    setup::rh::yuminst redhat-rpm-config \
        /usr/bin/virtualenv python${PYTHON}-{virtualenv,devel}
    virtualenv -p $(which python${PYTHON}) .venv
    source ./.venv/bin/activate
    pip install --install-option='--no-cython-compile' cython
}

setup::rh::install() {
    setup::rh::yuminst krb5-{devel,libs,server,workstation} \
                       which gcc findutils gssntlmssp

    if [ -f /etc/fedora-release ]; then
        setup::fedora::install
    else
        setup::centos::install
    fi
}

setup::macos::install() {
    # Install Python from pyenv so we know what version is being used.  This
    # doesn't work for newer macos.
    pyenv install $PYENV
    pyenv global $PYENV
    virtualenv -p $(pyenv which python) .venv
    source ./.venv/bin/activate
    pip install --install-option='--no-cython-compile' cython
}

setup::windows::install() {
    # Install the right Python version and MIT Kerberos
    choco install python"${PYENV:0:1}" --version $PYENV || true
    choco install mitkerberos --install-arguments "'ADDLOCAL=ALL'" || true
    PYPATH="/c/Python${PYENV:0:1}${PYENV:2:1}"
    # Update path to include them
    export PATH="$PYPATH:$PYPATH/Scripts:/c/Program Files/MIT/Kerberos/bin:$PATH"

    python -m pip install --upgrade pip
}

setup::install() {
    if [ -f /etc/debian_version ]; then
        setup::debian::install
    elif [ -f /etc/redhat-release ]; then
        setup::rh::install
    elif [ "$(uname)" == "Darwin" ]; then
        setup::macos::install
    elif [ "$TRAVIS_OS_NAME" == "windows" ]; then
        setup::windows::install
    else
        echo "Distro not found!"
        false
    fi

    pip install -r test-requirements.txt
}

setup::activate() {
    # remove (and restore) set -x to avoid log-spam the source
    # script, which we don't care about
    wastrace=${-//[^x]/}
    set +x
    source .venv/bin/activate
    if [[ -n "$wastrace" ]]; then set -x; fi
}
