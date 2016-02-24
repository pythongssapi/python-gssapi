#!/bin/sh -ex

pip install --install-option='--no-cython-compile' cython
pip install -r test-requirements.txt

sudo sed -i '1i 127.0.0.1 test.box' /etc/hosts
sudo hostname test.box

if [ x"$KRB5_VER" = "xheimdal" ]; then
    sudo apt-get update
    DEBIAN_FRONTEND=noninteractive sudo apt-get -y install heimdal-dev
    exit 0
elif [ x"$KRB5_VER" != "x1.12" ]; then
    sudo apt-add-repository -y ppa:rharwood/krb5-$KRB5_VER
fi

sudo apt-get update
DEBIAN_FRONTEND=noninteractive sudo apt-get install -y krb5-user krb5-kdc krb5-admin-server libkrb5-dev krb5-multidev
DEBIAN_FRONTEND=noninteractive sudo apt-get -y install krb5-greet-client || true
