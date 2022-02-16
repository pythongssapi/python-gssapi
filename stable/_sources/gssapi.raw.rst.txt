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

.. autoapimodule:: gssapi.raw.names
    :members:
    :undoc-members:

Credentials
~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.creds
    :members:
    :undoc-members:

Security Contexts
~~~~~~~~~~~~~~~~~

.. autoapimodule::  gssapi.raw.sec_contexts
    :members:
    :undoc-members:

.. autoapimodule:: gssapi.raw.message
    :members:
    :undoc-members:

Misc
~~~~

.. autoapimodule:: gssapi.raw.oids
    :members:
    :undoc-members:

.. autoapimodule:: gssapi.raw.misc
    :members:
    :undoc-members:

.. autoapimodule:: gssapi.raw.types
    :members:
    :undoc-members:

.. autoapimodule:: gssapi.raw.chan_bindings
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

.. autoapimodule:: gssapi.raw.ext_rfc4178
    :members:
    :undoc-members:

:rfc:`5587` (GSS-API Extension for Mech Attributes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_rfc5587
    :members:
    :undoc-members:

:rfc:`5588` (GSS-API Extension for Storing Delegated Credentials)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_rfc5588
    :members:
    :undoc-members:

:rfc:`5801` (GSS-API SASL Extensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_rfc5801
    :members:
    :undoc-members:

Credential Store Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_cred_store
    :members:
    :undoc-members:

:rfc:`6680` (GSS-API Naming Extensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_rfc6680
    :members:
    :undoc-members:

Credentials Import-Export Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_cred_imp_exp
    :members:
    :undoc-members:

DCE (IOV/AEAD) Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_dce
    :members:
    :undoc-members:

..
    gssapi.raw.ext_dce_aead is imported with ext_dce so no need to double up.


IOV MIC Extensions
~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_iov_mic
    :members:
    :undoc-members:

Global Grid Forum (GGF) Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_ggf
    :members:
    :undoc-members:

Services4User Extensions
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_s4u
    :members:
    :undoc-members:

Acquiring Credentials With a Password Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_password
    :members:
    :undoc-members:

.. autoapimodule:: gssapi.raw.ext_password_add
    :members:
    :undoc-members:

Kerberos Specific Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_krb5
    :members:
    :undoc-members:

Other Extensions
~~~~~~~~~~~~~~~~

.. autoapimodule:: gssapi.raw.ext_set_cred_opt
    :members:
    :undoc-members:

Results
-------

..
    Use autoapimodule once
    https://github.com/readthedocs/sphinx-autoapi/issues/323 is resolved.

.. automodule:: gssapi.raw.named_tuples
    :members:
    :undoc-members:

Exceptions
----------

.. autoapimodule:: gssapi.raw.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
