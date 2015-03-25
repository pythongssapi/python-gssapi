#!/bin/sh

# clean up
git clean -Xdf

# make the dir
mkdir ./tag_build

# create and checksum the tarball

# no bashisms for portability
if [ x"${TRAVIS_TAG#v[0-9]}" = "x${TRAVIS_TAG}" ]; then
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG}
else
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG#v}
fi


tar -czvf ./tag_build/${TRAVIS_TAG}.tar.gz --exclude='tag_build' --exclude='.git' --transform "s,^\.,python-gssapi-${PYTHON_GSSAPI_VERSION}," .
sha512sum --binary ./tag_build/${TRAVIS_TAG}.tar.gz > ./tag_build/${TRAVIS_TAG}.sha512sum
