#!/bin/bash -ex

# If we try to use a normal Github Actions container with
# github-pages-deploy-action, it will fail due to inability to find git.

docker run -h test.box \
       -v `pwd`:/tmp/build -w /tmp/build \
       -e KRB5_VER=${KRB5_VER:-mit} \
       -e FLAKE=${FLAKE:no} \
       $DISTRO /bin/bash -ex $@
