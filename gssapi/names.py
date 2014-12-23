import six

from gssapi.raw import names as rname
from gssapi.raw import NameType
from gssapi import _utils


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

    __slots__ = ()

    def __new__(cls, base=None, name_type=None, token=None):
        """Create or import a GSSAPI name

        The constructor either creates or imports a GSSAPI name.

        If a :python:`~gssapi.raw.names.Name` object from the low-level API
        is passed as the `base` argument, it will be converted into a
        high-level object.

        If the `token` argument is used, the name will be imported using
        the token.

        Otherwise, a new name will be created, using the `base` argument as
        the string and the `name_type` argument to denote the name type.
        """

        if token is not None:
            base_name = rname.import_name(token, NameType.export)
        elif isinstance(base, rname.Name):
            base_name = base
        else:
            if isinstance(base, six.text_type):
                base = base.encode(_utils._get_encoding())

            base_name = rname.import_name(base, name_type)

        return super(Name, cls).__new__(cls, base_name)

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

    def export(self):
        """Export the name

        This method exports the name into a byte string which can then be
        imported by using the `token` argument of the constructor.

        Returns:
            bytes: the exported name in token form
        """

        return rname.export_name(self)

    def canonicalize(self, mech):
        """Canonicalize a name with respect to a mechanism

        This method returns a new Name that is canonicalized according to
        the given mechanism.

        Args:
            mech (OID): the mechanism type to use

        Returns:
            Name: the canonicalized name
        """

        return type(self)(rname.canonicalize_name(self, mech))

    def __copy__(self):
        return type(self)(rname.duplicate_name(self))

    def __deepcopy__(self, memo):
        return type(self)(rname.duplicate_name(self))
