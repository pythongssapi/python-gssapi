#!/bin/bash -ex

# NB (very important): BE VERY CAREFUL WITH `set -x` FOR THIS FILE.
# The GitHub token is sensitive information, and should never
# be displayed on in the clear.

source_directory=${1?need <source dir> <target dir> <target repo> [<target branch, default: gh-pages>]}
target_directory=${2?need <source dir> <target dir> <target repo> [<target branch, default: gh-pages>]}
target_repo=${3?need <source dir> <target dir> <target repo> [<target branch, default: gh-pages>]}
target_branch=${4:-gh-pages}

desc=$(git describe --tags)

scratch_dir=$(mktemp -d)

set +x # IMPORTANT
echo "cloning https://<elided>@github.com/${target_repo}.git#${target_branch} in to ${scratch_dir}/docs..."
git clone https://${GITHUB_TOKEN}@github.com/${target_repo}.git ${scratch_dir}/docs -b ${target_branch}
set -x

mkdir -p ${scratch_dir}/docs/${target_directory}
cp -r ${source_directory}/. ${scratch_dir}/docs/${target_directory}
echo $desc > ${scratch_dir}/docs/${target_directory}/.from
pushd $scratch_dir/docs
git config user.email "deploy@travis-ci.org"
git config user.name "Deployment Bot (from Travis CI)"

if [[ $(git status --porcelain | wc -l) -eq 0 ]]; then
    echo "no docs changes in the latest commit"
    exit 0
fi

git add ${target_directory}
git commit -m "Update ${target_directory} docs in based on ${desc}"

set +x # IMPORTANT
echo "pushing to https://<elided>@github.com/${target_repo}.git#${target_branch}"
git push --quiet --force-with-lease origin ${target_branch}:${target_branch}
set -x

popd
rm -rf ${scratch_dir}
echo "done!"
