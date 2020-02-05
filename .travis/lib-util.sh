#!/bin/bash

util::docker-run() {
    local distro=$1
    shift

    docker run \
    -v `pwd`:/tmp/build \
    -w /tmp/build \
    -e TRAVIS_TAG=$TRAVIS_TAG \
    -e PKG_NAME_VER=$PKG_NAME_VER \
    -e KRB5_VER=$KRB5_VER \
    -e PYTHON=$PYTHON \
    -e FLAKE=$FLAKE \
    $distro \
    /bin/bash -ex $@
}
