import collections

import six

from gssapi.raw import names as rname
from gssapi.raw import NameType
from gssapi.raw import named_tuples as tuples
from gssapi import _utils

rname_rfc6680 = _utils.import_gssapi_extension('rfc6680')
rname_rfc6680_comp_oid = _utils.import_gssapi_extension('rfc6680_comp_oid')


class Name(rname.Name):
    """GSSAPI Name

    This class represents a GSSAPI name which may be used with
    used with and/or returned by other GSSAPI methods.

    It inherits from the low-level GSSAPI :class:`~gssapi.raw.names.Name`
    class, and thus may used with both low-level and high-level API methods.

    This class may be pickled and unpickled, as well as copied.

    The :func:`str` and :func:`bytes` methods may be used to retrieve the
    text of the name.
    """

    __slots__ = ('_attr_obj')

    def __new__(cls, base=None, name_type=None, token=None,
                composite=False):
        if token is not None:
            if composite:
                if rname_rfc6680 is None:
                    raise NotImplementedError(
                        "Your GSSAPI implementation does not support RFC 6680 "
                        "(the GSSAPI naming extensions)")

                if rname_rfc6680_comp_oid is not None:
                    base_name = rname.import_name(token,
                                                  NameType.composite_export)
                    displ_name = rname.display_name(base_name, name_type=True)
                    if displ_name.name_type == NameType.composite_export:
                        # NB(directxman12): there's a bug in MIT krb5 <= 1.13
                        # where GSS_C_NT_COMPOSITE_EXPORT doesn't trigger
                        # immediate import logic.  However, we can just use
                        # the normal GSS_C_NT_EXPORT_NAME in this case.
                        base_name = rname.import_name(token, NameType.export)
                else:
                    # NB(directxman12): some older versions of MIT krb5 don't
                    # have support for the GSS_C_NT_COMPOSITE_EXPORT, but do
                    # support composite tokens via GSS_C_NT_EXPORT_NAME.
                    base_name = rname.import_name(token, NameType.export)
            else:
                base_name = rname.import_name(token, NameType.export)
        elif isinstance(base, rname.Name):
            base_name = base
        else:
            if isinstance(base, six.text_type):
                base = base.encode(_utils._get_encoding())

            base_name = rname.import_name(base, name_type)

        return super(Name, cls).__new__(cls, base_name)

    def __init__(self, base=None, name_type=None, token=None, composite=False):
        """Create or import a GSSAPI name

        The constructor either creates or imports a GSSAPI name.

        If a :python:`~gssapi.raw.names.Name` object from the low-level API
        is passed as the `base` argument, it will be converted into a
        high-level object.

        If the `token` argument is used, the name will be imported using
        the token.  If the token was exported as a composite token,
        pass `composite=True`.

        Otherwise, a new name will be created, using the `base` argument as
        the string and the `name_type` argument to denote the name type.

        Raises:
            BadNameTypeError
            BadNameError
            BadMechanismError
        """

        if rname_rfc6680 is not None:
            self._attr_obj = _NameAttributeMapping(self)
        else:
            self._attr_obj = None

    def __str__(self):
        if issubclass(str, six.text_type):
            # Python 3 -- we should return unicode
            return bytes(self).decode(_utils._get_encoding())
        else:
            # Python 2 -- we should return a string
            return self.__bytes__()

    def __unicode__(self):
        # Python 2 -- someone asked for unicode
        return self.__bytes__().encode(_utils._get_encoding())

    def __bytes__(self):
        # Python 3 -- someone asked for bytes
        return rname.display_name(self, name_type=False).name

    def display_as(self, name_type):
        """
        Display the current name as the given name type.

        This method attempts to display the current Name using
        the syntax of the given NameType, if possible.

        Args:
            name_type (OID): the NameType to use to display the given name

        Returns:
            str: the displayed name

        Raises:
            OperationUnavailableError
        """

        if rname_rfc6680 is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")
        return rname_rfc6680.display_name_ext(self, name_type).encode(
            _utils.get_encoding())

    @property
    def name_type(self):
        """Get the name type of this name"""
        return rname.display_name(self, name_type=True).name_type

    def __eq__(self, other):
        if not isinstance(other, rname.Name):
            # maybe something else can compare this
            # to other classes, but we certainly can't
            return NotImplemented
        else:
            return rname.compare_name(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        disp_res = rname.display_name(self, name_type=True)
        return "Name({name}, {name_type})".format(name=disp_res.name,
                                                  name_type=disp_res.name_type)

    def export(self, composite=False):
        """Export the name

        This method exports the name into a byte string which can then be
        imported by using the `token` argument of the constructor.

        Returns:
            bytes: the exported name in token form

        Raises:
            MechanismNameRequiredError
            BadNameTypeError
            BadNameError
        """

        if composite:
            if rname_rfc6680 is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not support RFC 6680 (the GSSAPI "
                                          "naming extensions)")

            return rname_rfc6680.export_name_composite(self)
        else:
            return rname.export_name(self)

    def canonicalize(self, mech):
        """Canonicalize a name with respect to a mechanism

        This method returns a new Name that is canonicalized according to
        the given mechanism.

        Args:
            mech (OID): the mechanism type to use

        Returns:
            Name: the canonicalized name

        Raises:
            BadMechanismError
            BadNameTypeError
            BadNameError
        """

        return type(self)(rname.canonicalize_name(self, mech))

    def __copy__(self):
        return type(self)(rname.duplicate_name(self))

    def __deepcopy__(self, memo):
        return type(self)(rname.duplicate_name(self))

    def _inquire(self, **kwargs):
        """Inspect the name for information

        This method inspects the name for information.

        If no keyword arguments are passed, all available information
        is returned.  Otherwise, only the keyword arguments that
        are passed and set to `True` are returned.

        Args:
            mech_name (bool): get whether this is a mechanism name,
                and, if so, the associated mechanism
            attrs (bool): get the attributes names for this name

        Returns:
            InquireNameResult: the results of the inquiry, with unused
                fields set to None

        Raises:
            GSSError
        """

        if rname_rfc6680 is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")

        if not kwargs:
            default_val = True
        else:
            default_val = False

        attrs = kwargs.get('attrs', default_val)
        mech_name = kwargs.get('mech_name', default_val)

        return rname_rfc6680.inquire_name(self, mech_name=mech_name,
                                          attrs=attrs)

    @property
    def is_mech_name(self):
        return self._inquire(mech_name=True).is_mech_name

    @property
    def mech(self):
        return self._inquire(mech_name=True).mech

    @property
    def attributes(self):
        if self._attr_obj is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")

        return self._attr_obj


class _NameAttributeMapping(collections.MutableMapping):

    """Provides dict-like access to RFC 6680 Name attributes."""
    def __init__(self, name):
        self._name = name

    def __getitem__(self, key):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        res = rname_rfc6680.get_name_attribute(self._name, key)
        return tuples.GetNameAttributeResult(frozenset(res.values),
                                             frozenset(res.display_values),
                                             res.authenticated,
                                             res.complete)

    def __setitem__(self, key, value):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        rname_rfc6680.delete_name_attribute(self._name, key)

        if isinstance(value, tuples.GetNameAttributeResult):
            complete = value.complete
            value = value.values
        elif isinstance(value, tuple) and len(value) == 2:
            complete = value[1]
            value = value[0]
        else:
            complete = False

        if (isinstance(value, (six.string_types, bytes)) or
                not isinstance(value, collections.Iterable)):
            # NB(directxman12): this allows us to easily assign a single
            # value, since that's a common case
            value = [value]

            rname_rfc6680.set_name_attribute(self._name, key, value,
                                             complete=complete)

    def __delitem__(self, key):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        rname_rfc6680.delete_name_attribute(self._name, key)

    def __iter__(self):
        return iter(self._name._inquire(attrs=True).attrs)

    def __len__(self):
        return len(self._name._inquire(attrs=True).attrs)
