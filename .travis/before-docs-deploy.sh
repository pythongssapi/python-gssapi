#!/bin/bash -ex

source ./.travis/lib-setup.sh
source ./.travis/lib-deploy.sh

# build again since I can't figure out how to get travis to recognize the old
# build in the new container.  The other alternative (besides actually solving
# the issue) is to run the docs build and tarball generation every time.

./.travis/build.sh

setup::activate

deploy::build-docs
