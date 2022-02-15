=============
Python-GSSAPI
=============

.. role:: python(code)
   :language: python

.. role:: bash(code)
   :language: bash

.. image:: https://badge.fury.io/gh/pythongssapi%2Fpython-gssapi.svg
    :target: http://badge.fury.io/gh/pythongssapi%2Fpython-gssapi

.. image:: https://badge.fury.io/py/gssapi.svg
    :target: http://badge.fury.io/py/gssapi

Python-GSSAPI provides both low-level and high level wrappers around the GSSAPI
C libraries.  While it focuses on the Kerberos mechanism, it should also be
useable with other GSSAPI mechanisms.

Documentation for the latest released version (including pre-release versions)
can be found at
`https://pythongssapi.github.io/python-gssapi/stable <https://pythongssapi.github.io/python-gssapi/stable>`_.

Documentation for the latest commit on main can be found at
`https://pythongssapi.github.io/python-gssapi/latest <https://pythongssapi.github.io/python-gssapi/latest>`_.

Requirements
============

Basic
-----

* A working implementation of GSSAPI (such as from MIT Kerberos)
  which supports delegation and includes header files

* a C compiler (such as GCC)

* Python 3.6+ (older releases support older versions, but are unsupported)

* the `decorator` python package

Compiling from Scratch
----------------------

To compile from scratch, you will need Cython >= 0.21.1.

For Running the Tests
---------------------

* the `k5test` package

To install test dependencies using pip:

.. code-block:: bash

    $ pip install -r test-requirements.txt # Optional, for running test suite

Installation
============

Easy Way
--------

.. code-block:: bash

    $ pip install gssapi

From the Git Repo
-----------------

After being sure to install all the requirements,

.. code-block:: bash

    $ git clone https://github.com/pythongssapi/python-gssapi.git
    $ python setup.py build
    $ python setup.py install

Tests
=====

The tests for for Python-GSSAPI live in `gssapi.tests`.  In order to
run the tests, you must have an MIT Kerberos installation (including
the KDC).  The tests create a self-contained Kerberos setup, so running
the tests will not interfere with any existing Kerberos installations.

Structure
=========

Python-GSSAPI is composed of two parts: a low-level C-style API which
thinly wraps the underlying RFC 2744 methods, and a high-level, Pythonic
API (which is itself a wrapper around the low-level API).  Examples may
be found in the `examples` directory.

Low-Level API
-------------

The low-level API lives in `gssapi.raw`.  The methods contained therein
are designed to match closely with the original GSSAPI C methods.  All
relevant methods and classes may be imported directly from `gssapi.raw`.
Extension methods will only be imported if they are present.  The low-level
API follows the given format:

* Names match the RFC 2744 specification, with the :python:`gssapi_`
  prefix removed

* Parameters which use C int constants as enums have
  :python:`enum.IntEnum` classes defined, and thus may be passed
  either the enum members or integers

* In cases where a specific constant is passed in the C API to represent
  a default value, :python:`None` should be passed instead

* In cases where non-integer constants would be used in the API (i.e.
  OIDs), enum-like objects have been defined containing named references
  to values specified in RFC 2744.

* Major and minor error codes are returned by raising
  :python:`gssapi.raw.GSSError`.  The major error codes have exceptions
  defined in in `gssapi.raw.exceptions` to make it easier to catch specific
  errors or categories of errors.

* All other relevant output values are returned via named tuples.

High-Level API
--------------

The high-level API lives directly under :python:`gssapi`.  The classes
contained in each file are designed to provide a more Pythonic, Object-Oriented
view of GSSAPI.  The exceptions from the low-level API, plus several additional
exceptions, live in `gssapi.exceptions`.  The rest of the classes may be
imported directly from `gssapi`.  Only classes are exported by `gssapi` --
all functions are methods of classes in the high-level API.

Please note that QoP is not supported in the high-level API, since it has been
deprecated.

Extensions
----------

In addition to RFC 2743/2744, Python-GSSAPI also has support for:

* RFC 4178 (GSS-API Negotiation Mechanism)

* RFC 5587 (Extended GSS Mechanism Inquiry APIs)

* RFC 5588 (GSS-API Extension for Storing Delegated Credentials)

* RFC 5801 (GSS-API SASL Extensions)

* (Additional) Credential Store Extension

* Services4User

* Credentials import-export

* RFC 6680 (GSS-API Naming Extensions)

* DCE and IOV MIC extensions

* `acquire_cred_with_password` and `add_cred_with_password`

* GGF Extensions

* Kerberos specific extensions

The Team
========

(GitHub usernames in parentheses)

* Jordan Borean (@jborean93) - current maintainer and developer
* Simo Sorce (@simo5) - developer
* Robbie Harwood (@frozencemetery) - author emeritus
* Solly Ross (@directxman12) - author emeritus
* Hugh Cole-Baker (@sigmaris) - author emeritus

Get Involved
============

We welcome new contributions in the form of Issues and Pull Requests on
Github.  If you would like to join our discussions, you can find us on
`libera.chat <https://libera.chat/>`_ IRC, channel `#python-gssapi
<irc://libera.chat/python-gssapi>`_.
