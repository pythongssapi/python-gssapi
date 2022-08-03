#!/bin/bash -ex

source ./ci/lib.sh

lib::setup::install

yum -y install tar git

# Git complains if this isn't owned by the user which is the case when running
# through the run-on-linux.sh
if [ -f /.dockerenv ]; then
    git config --global --add safe.directory "${PWD}"
fi

# build the docs
lib::deploy::build_docs

# Save the sdist and venv dirs before the clean
mv dist dist_saved
mv .venv /tmp/.venv

# for the tarball upload
# clean up
git clean -Xdf

# restore the saved "dist"/".venv" directory
mv dist_saved dist
mv /tmp/.venv .venv

# make the dir
rm -rf ./tag_build || true
mkdir ./tag_build

# create and checksum the tarball

set +e
tag=$(git describe --tags)
if [ "${?}" -ne 0 ]; then
    tag=$(git rev-parse --short HEAD)
fi
set -e

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
    --exclude='ci_docs_build' \
    --exclude='.venv' \
    --exclude='README.rst' \
    --transform="s,^\.,${PKG_NAME_VER}," .

# --transform clobbers symlink so add it last using Python
python - << EOF
import tarfile

with tarfile.open("tag_build/${PKG_NAME_VER}.tar", mode="a:") as tf:
    tf.add("README.rst", arcname="${PKG_NAME_VER}/README.rst")
EOF

pushd ./tag_build
gzip ${PKG_NAME_VER}.tar

sha512sum --binary ${PKG_NAME_VER}.tar.gz > ${PKG_NAME_VER}.sha512sum
popd
