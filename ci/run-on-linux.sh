#!/bin/bash -ex

docker run \
    --rm \
    --hostname test.krbtest.com \
    --volume "$( pwd )":/tmp/build \
    --workdir /tmp/build \
    --env KRB5_VER=${KRB5_VER:-mit} \
    --env FLAKE=${FLAKE:no} \
    ${DISTRO} /bin/bash -ex $@
