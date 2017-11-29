#!/bin/bash

verify::flake8() {
    flake8 setup.py
    F8_SETUP=$?

    flake8 gssapi
    F8_PY=$?

    # Cython requires special flags since it is not proper Python
    # E225: missing whitespace around operator
    # E226: missing whitespace around arithmetic operator
    # E227: missing whitespace around bitwise or shift operator
    # E402: module level import not at top of file
    # E901: SyntaxError or IndentationError
    # E999: Internal AST compilation error (flake8 specific)
    flake8 gssapi --filename='*.pyx,*.pxd' --ignore=E225,E226,E227,E402,E901,E999
    F8_MAIN_CYTHON=$?

    if [ $F8_SETUP -eq 0 -a $F8_PY -eq 0 -a $F8_MAIN_CYTHON -eq 0 ]; then
        return 0
    else
        return 1
    fi
}
