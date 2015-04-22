#!/bin/sh

# build the docs
# the first run is for the docs build, so don't clean up
pip install -r docs-requirements.txt

# install dependencies so that sphinx doesn't have issues
# (this actually just installs the whole package in dev mode)
pip install -e .

# place in a non-standard location so that they don't get cleaned up
python setup.py build_sphinx --build-dir travis_docs_build

# for the tarball upload
# clean up
git clean -Xdf

# until this gets fixed in dpl
rm setuptools-*.zip

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

tar -czvf ./tag_build/${PKG_NAME_VER}.tar.gz --exclude='tag_build' --exclude='.git' --exclude='travis_docs_build' --exclude='.git' --transform "s,^\.,${PKG_NAME_VER}," .
sha512sum --binary ./tag_build/${PKG_NAME_VER}.tar.gz > ./tag_build/${PKG_NAME_VER}.sha512sum
