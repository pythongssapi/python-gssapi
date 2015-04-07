#!/bin/sh

# clean up
git clean -Xdf

# make the dir
mkdir ./tag_build

# create and checksum the tarball
tar -czvf ./tag_build/${TRAVIS_TAG}.tar.gz --exclude='tag_build' --exclude='.git' --transform "s,^\.,python-gssapi-${TRAVIS_TAG}," .
sha512sum --binary ./tag_build/${TRAVIS_TAG}.tar.gz > ./tag_build/${TRAVIS_TAG}.sha512sum
