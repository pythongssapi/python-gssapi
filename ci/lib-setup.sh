#!/bin/bash

# We test Debian's cython.  el7's cython is too old, and Rawhide's virtualenv
# doesn't work right (usrmerge bugs) so we can only test Debian's cython.

setup::debian::install() {
    export DEBIAN_FRONTEND=noninteractive
    apt-get update

    if [ x"$KRB5_VER" = "xheimdal" ]; then
        apt-get -y install heimdal-{clients,dev,kdc}

        export GSSAPI_KRB5_MAIN_LIB="/usr/lib/x86_64-linux-gnu/libkrb5.so.26"
        export PATH="/usr/lib/heimdal-servers:${PATH}"
    else
        apt-get -y install krb5-{user,kdc,admin-server,multidev} libkrb5-dev \
                gss-ntlmssp

        export GSSAPI_KRB5_MAIN_LIB="/usr/lib/x86_64-linux-gnu/libkrb5.so"
    fi

    apt-get -y install gcc virtualenv python3-{virtualenv,dev} cython3

    virtualenv --system-site-packages -p $(which python3) .venv
    source ./.venv/bin/activate
}

setup::rh::yuminst() {
    # yum has no update-only verb.  Also: modularity just makes this slower.
    yum -y --nogpgcheck --disablerepo=\*modul\* install $@
}

setup::centos::install() {
    # Cython on el7 is too old - downstream patches
    setup::rh::yuminst python3-{virtualenv,devel}
    virtualenv -p $(which python3) .venv
    source ./.venv/bin/activate
    pip install --upgrade pip # el7 pip doesn't quite work right
    pip install --install-option='--no-cython-compile' cython
}

setup::fedora::install() {
    # path to binary here in case Rawhide changes it
    setup::rh::yuminst redhat-rpm-config \
        /usr/bin/virtualenv python3-{virtualenv,devel}
    virtualenv -p $(which python3) .venv
    source ./.venv/bin/activate
    pip install --install-option='--no-cython-compile' cython
}

setup::rh::install() {
    setup::rh::yuminst krb5-{devel,libs,server,workstation} \
                       which gcc findutils gssntlmssp
    export GSSAPI_KRB5_MAIN_LIB="/usr/lib64/libkrb5.so"

    if [ -f /etc/fedora-release ]; then
        setup::fedora::install
    else
        setup::centos::install
    fi
}

setup::macos::install() {
    sudo pip3 install virtualenv
    python3 -m virtualenv -p $(which python3) .venv
    source .venv/bin/activate
    pip install --install-option='--no-cython-compile' cython

    export GSSAPI_KRB5_MAIN_LIB="/System/Library/PrivateFrameworks/Heimdal.framework/Heimdal"

    # macOS's Heimdal version is buggy, it will only use KRB5_KTNAME if the
    # env var was set when GSSAPI creates the context. Setting it here to any
    # value solves that problem for CI.
    export KRB5_KTNAME=initial
}

setup::windows::install() {
    CHINST="choco install --no-progress --yes --ignore-detected-reboot --allow-downgrade"

    # Install the 32bit version if Python is 32bit
    if python -c "assert __import__('sys').maxsize <= 2**32"; then
        CHINST="$CHINST --x86"
        PF="Program Files (x86)"
    else
        PF="Program Files"
    fi

    # Install MIT Kerberos.  choco will fail despite the installation working.
    $CHINST mitkerberos --install-arguments "'ADDLOCAL=ALL'" || true

    # Update path to include it
    export PATH="/c/$PF/MIT/Kerberos/bin:$PATH"

    python -m pip install --upgrade pip
}

setup::install() {
    if [ -f /etc/debian_version ]; then
        setup::debian::install
    elif [ -f /etc/redhat-release ]; then
        setup::rh::install
    elif [ "$(uname)" == "Darwin" ]; then
        setup::macos::install
    elif [ "$OS_NAME" == "windows" ]; then
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
