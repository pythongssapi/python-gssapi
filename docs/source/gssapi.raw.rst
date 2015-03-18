Low-Level API
=============

The low-level API contains a variety of functions that map directly to the
corresponding C functions.  Additionally, it contains several basic wrapper
classes that wrap underlying C structs and automatically deallocate them
when the Python object itself is deallocated.

Core RFC 2744
-------------

Names
~~~~~

.. automodule:: gssapi.raw.names
    :members:
    :undoc-members:

Credentials
~~~~~~~~~~~

.. automodule:: gssapi.raw.creds
    :members:
    :undoc-members:

Security Contexts
~~~~~~~~~~~~~~~~~

.. automodule::  gssapi.raw.sec_contexts
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.message
    :members:
    :undoc-members:

Misc
~~~~

.. automodule:: gssapi.raw.oids
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.misc
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.types
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.chan_bindings
    :members:
    :undoc-members:

Extensions
----------

The following is a list of GSSAPI extensions supported by the low-level API.
Ones supported by the high-level API are marked as such.  Note that while
all of these extensions have bindings, they may not be supported by your
particularly GSSAPI implementation, in which case they will simply not be
compiled.

:rfc:`5588` (GSS-API Extension for Storing Delegated Credentials)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc5588
    :members:
    :undoc-members:

Credential Store Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_cred_store
    :members:
    :undoc-members:

:rfc:`6680` (GSS-API Naming Extensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc6680
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.ext_rfc6680_comp_oid
    :members:
    :undoc-members:

Credentials Import-Export Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_cred_imp_exp
    :members:
    :undoc-members:

DCE (IOV/AEAD) Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_dce
    :members:
    :undoc-members:

IOV MIC Extensions
~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_iov_mic
    :members:
    :undoc-members:

Services4User Extensions
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_s4u
    :members:
    :undoc-members:

Acquiring Credentials With a Password Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_password
    :members:
    :undoc-members:

.. automodule:: gssapi.raw.ext_password_add
    :members:
    :undoc-members:

Exceptions
----------

.. automodule:: gssapi.raw.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
