deploy::build-docs() {
    # the first run is for the docs build, so don't clean up
    pip install -r docs-requirements.txt

    # install dependencies so that sphinx doesn't have issues
    # (this actually just installs the whole package in dev mode)
    pip install -e .

    # place in a non-standard location so that they don't get cleaned up
    python setup.py build_sphinx --build-dir travis_docs_build

    echo "travis_docs_build"
}
