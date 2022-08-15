#!/bin/bash

lib::setup::debian_install() {
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

    apt-get -y install gcc python3-{venv,dev}

    python3 -m venv .venv
    source ./.venv/bin/activate
}

lib::setup::rh_dnfinst() {
    # dnf has no update-only verb.  Also: modularity just makes this slower.
    dnf -y --nogpgcheck --disablerepo=\*modul\* install $@
}

lib::setup::centos_install() {
    lib::setup::rh_dnfinst python3-devel
    python3 -m venv .venv
    source ./.venv/bin/activate
}

lib::setup::fedora_install() {
    # path to binary here in case Rawhide changes it
    lib::setup::rh_dnfinst redhat-rpm-config \
        python3-devel
    python3 -m venv .venv
    source ./.venv/bin/activate
}

lib::setup::gssntlmssp_install() {
    lib::setup::rh_dnfinst dnf-plugins-core
    dnf config-manager --set-enabled crb

    lib::setup::rh_dnfinst autoconf automake gettext libtool \
                    libunistring-devel openssl-devel zlib-devel

    curl -L -s https://github.com/gssapi/gss-ntlmssp/releases/download/v1.1.0/gssntlmssp-1.1.0.tar.gz --output /tmp/gssntlmssp.tar.gz
    tar xf /tmp/gssntlmssp.tar.gz -C /tmp

    pushd /tmp/gssntlmssp-1.1.0

    autoreconf -f -i
    ./configure --with-wbclient=no --with-manpages=no
    make
    make install

    popd

    echo "gssntlmssp_v1    1.3.6.1.4.1.311.2.2.10    /usr/local/lib/gssntlmssp/gssntlmssp.so" > /etc/gss/mech.d/gssntlmssp.conf
}

lib::setup::rh_install() {
    lib::setup::rh_dnfinst krb5-{devel,libs,server,workstation} \
                    which gcc findutils

    if grep -q 'release 9' /etc/redhat-release; then
        # CentOS 9 Stream doesn't have a dnf package for gssntlmssp
        lib::setup::gssntlmssp_install
    else
        lib::setup::rh_dnfinst gssntlmssp
    fi

    export GSSAPI_KRB5_MAIN_LIB="/usr/lib64/libkrb5.so"

    if [ -f /etc/fedora-release ]; then
        lib::setup::fedora_install
    else
        lib::setup::centos_install
    fi
}

lib::setup::macos_install() {
    python3 -m venv .venv
    source .venv/bin/activate

    export GSSAPI_KRB5_MAIN_LIB="/System/Library/PrivateFrameworks/Heimdal.framework/Heimdal"

    # macOS's Heimdal version is buggy, it will only use KRB5_KTNAME if the
    # env var was set when GSSAPI creates the context. Setting it here to any
    # value solves that problem for CI.
    export KRB5_KTNAME=initial
}

lib::setup::windows_install() {
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
}

lib::setup::install() {
    if [ -f /etc/debian_version ]; then
        lib::setup::debian_install
    elif [ -f /etc/redhat-release ]; then
        lib::setup::rh_install
    elif [ "$(uname)" == "Darwin" ]; then
        lib::setup::macos_install
    elif [ "$OS_NAME" == "windows" ]; then
        lib::setup::windows_install
    else
        echo "Distro not found!"
        false
    fi

    # Get the explicit version to force pip to install from our local dir in
    # case this is a pre-release and/or PyPi has a later version
    echo "Installing gssapi"
    GSSAPI_VER="$( grep 'version=' setup.py | cut -d "'" -f2 )"

    if [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ]; then
        DIST_LINK_PATH="$( echo "${PWD}/dist" | sed -e 's/^\///' -e 's/\//\\/g' -e 's/^./\0:/' )"
    else
        DIST_LINK_PATH="${PWD}/dist"
    fi

    python -m pip install gssapi=="${GSSAPI_VER}" \
        --find-links "file://${DIST_LINK_PATH}" \
        --verbose

    echo "Installing dev dependencies"
    python -m pip install -r test-requirements.txt
}

lib::deploy::build_docs() {
    # the first run is for the docs build, so don't clean up
    pip install -r docs-requirements.txt

    # Don't run in root to make sure the local copies aren't imported
    pushd docs

    # place in a non-standard location so that they don't get cleaned up
    sphinx-build source ../ci_docs_build -a -W -n

    popd

    echo "docs_build"
}
