#!/bin/bash -ex
#
# We're using this script for running the test job b/c GitHub's parser
# doesn't support yaml anchors originally used in .travis.yml, see:
# https://github.community/t5/GitHub-Actions/Support-for-YAML-anchors/m-p/30336
#

sudo sed -i '1i 127.0.0.1 test.box' /etc/hosts
sudo hostname test.box
source ./.ci/lib-util.sh
util::docker-run $DISTRO ./.ci/build.sh
