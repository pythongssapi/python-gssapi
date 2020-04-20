#!/bin/bash -ex

source ./.ci/lib-setup.sh
source ./.ci/lib-deploy.sh

# build again since I can't figure out how to get travis to recognize the old
# build in the new container.  The other alternative (besides actually solving
# the issue) is to run the docs build and tarball generation every time.

./.ci/build.sh

setup::activate

yum -y install tar git

# build the docs
deploy::build-docs

# NB(directxman12): this is a *terrible* hack, but basically,
# dpl (the Travis deployer) uses `twine` instead of `setup.py sdist upload`.
# like this:
# - python setup.py $PYPI_DISTRIBUTIONS
# - twine upload -r pypi dist/*
# - [some other stuff]
#
# so if we set $PYPI_DISTRIBUTIONS to something harmless, like `check`,
# and then build the dist ourselves (and save it from the cleanup),
# dpl will upload that

# build the sdist
python setup.py sdist
mv dist dist_saved

# for the tarball upload
# clean up
git clean -Xdf

# restore the saved "dist" directory
mv dist_saved dist

# make the dir
rm -rf ./tag_build || true
mkdir ./tag_build

# create and checksum the tarball

if [ x"${TRAVIS_TAG#v[0-9]}" = "x${TRAVIS_TAG}" ]; then
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG}
else
    PYTHON_GSSAPI_VERSION=${TRAVIS_TAG#v}
fi

PKG_NAME_VER="python-gssapi-${PYTHON_GSSAPI_VERSION}"

tar -czvf ./tag_build/${PKG_NAME_VER}.tar.gz --exclude='dist' --exclude='tag_build' --exclude='.git' --exclude='travis_docs_build' --exclude='.git' --transform "s,^\.,${PKG_NAME_VER}," .
sha512sum --binary ./tag_build/${PKG_NAME_VER}.tar.gz > ./tag_build/${PKG_NAME_VER}.sha512sum
