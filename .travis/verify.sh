#!/bin/bash -ex

# set up dependencies, etc
source ./.travis/lib-setup.sh
setup::install

source ./.travis/lib-verify.sh
verify::flake8
