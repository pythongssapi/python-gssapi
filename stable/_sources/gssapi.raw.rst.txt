Low-Level API
=============

.. py:module:: gssapi.raw

The low-level API contains a variety of Python functions that map directly
to the corresponding C functions.  Additionally, it contains several basic
wrapper classes that wrap underlying C structs and automatically deallocate
them when the Python object itself is deallocated.

.. warning::

    All methods in both the high-level and low-level APIs may throw the generic
    GSSError exception.

Core RFC 2744
-------------

Names
~~~~~

.. note::
    Some functions in the following section will refer to
    "mechanism names".  These are not names of mechanisms.
    Instead, they are a special form of name specific to
    a given mechanism.

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

Additional RFCs and Extensions
------------------------------

The following is a list of GSSAPI extensions supported by the low-level API.

.. note::
    While all of these extensions have bindings, they may not be supported
    by your particularly GSSAPI implementation.  In this case, they will not
    be compiled, and will simply not be available in the :mod:`gssapi.raw`
    namespace.

:rfc:`4178` (GSS-API Negotiation Mechanism)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc4178
    :members:
    :undoc-members:

:rfc:`5587` (GSS-API Extension for Mech Attributes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc5587
    :members:
    :undoc-members:

:rfc:`5588` (GSS-API Extension for Storing Delegated Credentials)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc5588
    :members:
    :undoc-members:

:rfc:`5801` (GSS-API SASL Extensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_rfc5801
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

.. automodule:: gssapi.raw.ext_dce_aead
    :members:
    :undoc-members:

IOV MIC Extensions
~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_iov_mic
    :members:
    :undoc-members:

Global Grid Forum (GGF) Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_ggf
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

Kerberos Specific Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_krb5
    :members:
    :undoc-members:

Other Extensions
~~~~~~~~~~~~~~~~

.. automodule:: gssapi.raw.ext_set_cred_opt
    :members:
    :undoc-members:

Results
-------

.. automodule:: gssapi.raw.named_tuples
    :members:
    :undoc-members:

Exceptions
----------

.. automodule:: gssapi.raw.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
