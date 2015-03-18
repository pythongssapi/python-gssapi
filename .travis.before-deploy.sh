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

PKG_NAME_VER="python-gssapi-${PYTHON_GSSAPI_VERSION}"

tar -czvf ./tag_build/${PKG_NAME_VER}.tar.gz --exclude='tag_build' --exclude='.git' --transform "s,^\.,${PKG_NAME_VER}," .
sha512sum --binary ./tag_build/${PKG_NAME_VER}.tar.gz > ./tag_build/${PKG_NAME_VER}.sha512sum

# for the docs deploy
pip install -r test-requirements.txt
