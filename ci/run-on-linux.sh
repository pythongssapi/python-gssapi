#!/bin/bash -ex

# GitHub's YAML parser doesn't support anchors, so this is a separate file
# https://github.community/t5/GitHub-Actions/Support-for-YAML-anchors/m-p/30336
sudo sed -i '1i 127.0.0.1 test.box' /etc/hosts
sudo hostname test.box

docker run \
       -v `pwd`:/tmp/build \
       -w /tmp/build \
       -e KRB5_VER=${KRB5_VER:-mit} \
       -e FLAKE=${FLAKE:-no} \
       $DISTRO \
       /bin/bash -ex $@
