#!/bin/bash -ex

source ./ci/lib-setup.sh
source ./ci/lib-deploy.sh

./ci/build.sh

setup::activate

yum -y install tar git

# build the docs
deploy::build-docs

# NB(directxman12): this is a *terrible* hack, but basically,
# `twine` gets called like this:
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

tag=$(git describe --tags)
if [ x"${tag#v[0-9]}" = "x${tag}" ]; then
    PYTHON_GSSAPI_VERSION=${tag}
else
    PYTHON_GSSAPI_VERSION=${tag#v}
fi

PKG_NAME_VER="python-gssapi-${PYTHON_GSSAPI_VERSION}"

tar -cvf ./tag_build/${PKG_NAME_VER}.tar \
    --exclude='dist' \
    --exclude='tag_build' \
    --exclude='.git' \
    --exclude='travis_docs_build' \
    --exclude='README.rst' \
    --transform="s,^\.,${PKG_NAME_VER}," .

# --transform clobbers symlink so add it last using Python
python - << EOF
import tarfile

with tarfile.open("tag_build/${PKG_NAME_VER}.tar", mode="a:") as tf:
    tf.add("README.rst", arcname="${PKG_NAME_VER}/README.rst")
EOF

gzip ./tag_build/${PKG_NAME_VER}.tar

sha512sum --binary ./tag_build/${PKG_NAME_VER}.tar.gz > ./tag_build/${PKG_NAME_VER}.sha512sum
