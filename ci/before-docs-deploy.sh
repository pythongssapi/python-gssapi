#!/bin/bash -ex

source ./ci/lib.sh

lib::setup::install

lib::deploy::build_docs
