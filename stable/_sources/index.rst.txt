.. Python-GSSAPI documentation master file, created by
   sphinx-quickstart on Tue Jul  2 19:01:09 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python-GSSAPI: Python bindings for GSSAPI
=========================================

Python-GSSAPI provides Python bindings for the GSSAPI C bindings as defined
by :rfc:`2744`, as well as several extensions.

The package is organized into two parts: a high-level API and a low-level API.
The high-level API resides in :mod:`gssapi`, and presents an object-oriented
API around GSSAPI.

The other part of Python-GSSAPI is the low-level API, which resides in
:mod:`gssapi.raw`.  The low-level API provides thin wrappers around the
corresponding C functions.  The high-level API makes use of the low-level API
to access underlying GSSAPI functionality.  Additionally certain extensions
are currently only available from the low-level API.

To get started, check out the :doc:`tutorials page <tutorials>` or jump
straight into the :doc:`high-level API documentation <gssapi>`.

.. toctree::
   :hidden:
   :maxdepth: 3

   gssapi.rst
   gssapi.raw.rst
   otherdoc.rst
   tutorials.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

