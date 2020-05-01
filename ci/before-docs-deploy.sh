#!/bin/bash -ex

source ./ci/lib-setup.sh
source ./ci/lib-deploy.sh

# GitHub Actions doesn't have a good concept of connected pipelines here, so
# just rebuild rather than trying to figure it out.
./ci/build.sh

setup::activate

deploy::build-docs
