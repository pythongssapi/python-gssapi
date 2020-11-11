High-Level API
==============

.. py:module:: gssapi

The high-level API contains three main classes for interacting with GSSAPI,
representing the primary abstractions that GSSAPI provides:
:class:`~gssapi.names.Name`, :class:`~gssapi.creds.Credentials`, and
:class:`~gssapi.sec_contexts.SecurityContext`.

.. note::

    Classes in the high-level API inherit from the corresponding classes in the
    low-level API, and thus may be passed in to low-level API functions.

.. warning::

    All methods in both the high-level and low-level APIs may throw the generic
    :class:`GSSError` exception.

Main Classes
------------

Names
"""""

.. automodule:: gssapi.names
    :members:
    :undoc-members:

Credentials
"""""""""""

.. automodule:: gssapi.creds
    :members:
    :undoc-members:

Security Contexts
"""""""""""""""""

.. automodule:: gssapi.sec_contexts
    :members:
    :undoc-members:

Enums and Helper Classes
------------------------

The following enumerations from the low-level API are also
used with the high-level API.  For convenience, they are
imported in the high-level API :mod:`gssapi` module:

.. autoclass:: gssapi.NameType
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: gssapi.MechType
    :members:
    :undoc-members:
    :show-inheritance:

.. TODO(directxman12): Sphinx doesn't document enums properly yet,
   so we need to figure out how to document them.

.. autoclass:: gssapi.RequirementFlag
    :show-inheritance:

The ``ok_as_delegate`` flag corresponds to the C level flag
``GSS_C_DELEG_POLICY_FLAG``. This flag is similar to ``delegate_to_peer``
except it only delegates if the KDC delegation policies for the service
principal allow it to use delegation. This is typically used on Microsoft
domain environments to control whether constrained or unconstrained delegation
is allowed for a service principal. By setting this flag, the delegation
process follows the same behaviour as delegation on SSPI/Windows.

Here are the four cases when either of these flags are set or not.

Neither flag set
   No delegation occurs.

delegate_to_peer
   Always try to delegate regardless of the KDC delegation policies.
   ``delegate_to_peer`` is set in the return flags if successful.

ok_as_delegate
   Try to delegate but only if the KDC trusts the service principal for
   delegation. ``delegate_to_peer`` and ``ok_as_delegate`` are set in the
   return flags if successful.

delegate_to_peer | ok_as_delegate
   Acts like ``delegate_to_peer`` being set but will also set
   ``ok_as_delegate`` in the return flags if the service principal was trusted
   for delegation by the KDC.


.. autoclass:: gssapi.AddressType
    :show-inheritance:

Similarly, there are a couple classes from the low-level API
that are imported into the high-level API module.  These classes
are less likely to be used directly by a user, but are returned
by several methods:

.. autoclass:: gssapi.OID
    :members:

.. autoclass:: gssapi.IntEnumFlagSet
    :members:
    :undoc-members:
    :show-inheritance:

Exceptions
----------

The high-level API can raise all of the exceptions that the low-level API
can raise in addition to several other high-level-specific exceptions:

.. automodule:: gssapi.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:

Utilities
---------

.. autofunction:: gssapi.set_encoding
