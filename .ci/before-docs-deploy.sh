#!/bin/bash -ex

source ./.ci/lib-setup.sh
source ./.ci/lib-deploy.sh

# build again since I can't figure out how to get travis to recognize the old
# build in the new container.  The other alternative (besides actually solving
# the issue) is to run the docs build and tarball generation every time.

./.ci/build.sh

setup::activate

deploy::build-docs
