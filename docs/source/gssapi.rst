High-Level API
==============

The high-level API contains three main classes for interacting with GSSAPI,
representing the primary abstractions that GSSAPI provides:
:class:`~gssapi.names.Name`, :class:`~gssapi.creds.Credentials`, and
:class:`~gssapi.sec_contexts.SecurityContext`.  Note that classes in
the high-level API inherit from the corresponding classes in the
low-level API, and thus may be passed in to low-level API functions.

Main Classes
------------

.. automodule:: gssapi.names
    :members:
    :undoc-members:
    :inherited-members:

.. automodule:: gssapi.creds
    :members:
    :undoc-members:
    :inherited-members:

.. automodule:: gssapi.sec_contexts
    :members:
    :undoc-members:
    :inherited-members:

Enums and Helper Classes
------------------------

The following enumerations from the low-level API are also
used with the high-level API.  For convienience, the are
imported in the high-level API :mod:`gssapi` module:

.. autoclass:: gssapi.raw.types.NameType
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

.. autoclass:: gssapi.raw.types.MechType
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

.. TODO(directxman12): Sphinx doesn't document enums properly yet,
   so we need to figure out how to document them.

.. autoclass:: gssapi.raw.types.RequirementFlag
    :show-inheritance:
    :noindex:

.. autoclass:: gssapi.raw.types.AddressType
    :show-inheritance:
    :noindex:

Similiarly, there are a couple classes from the low-level API
that are imported into the high-level API module.  These classes
are less likely to be used directly by a user, but are returned
by several methods:

.. autoclass:: gssapi.raw.oids.OID
    :members:
    :noindex:

.. autoclass:: gssapi.raw.types.IntEnumFlagSet
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

Exceptions
----------

The high-level API can raise all of the exceptions that the low-level API
can raise in addition to several other high-level-specific exceptions:

.. automodule:: gssapi.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:
