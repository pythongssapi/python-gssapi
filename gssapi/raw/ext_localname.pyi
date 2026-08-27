import typing as t

if t.TYPE_CHECKING:
    from gssapi.raw.names import Name
    from gssapi.raw.oids import OID


def localname(
    name: "Name",
    mech: t.Optional["OID"] = None,
) -> bytes:
    """Get the local name for a GSSAPI name.

    This method determines the local name associated with a GSSAPI
    name, optionally for a given mechanism.

    Args:
        name (Name): the GSSAPI name to map to a local name
        mech (~gssapi.OID): the mechanism to use for the mapping
            (or None for the default)

    Returns:
        bytes: the local name

    Raises:
        ~gssapi.exceptions.GSSError
    """


def userok(
    name: "Name",
    username: t.Union[bytes, str],
) -> bool:
    """Determine whether a GSSAPI name is authorized to act as a local user.

    This method determines whether a given GSSAPI name is authorized
    to act as the given local username.  This is a simple wrapper
    around :func:`authorize_localname` that only supports system
    usernames as local names.

    Args:
        name (Name): the GSSAPI name to check
        username (Union[bytes, str]): the local username to check against

    Returns:
        bool: whether or not the name is authorized to act as the user
    """


def authorize_localname(
    name: "Name",
    user: "Name",
) -> bool:
    """Determine whether a GSSAPI name is authorized to act as a local name.

    This method determines whether a given GSSAPI name is authorized
    to act as the given local name.

    Args:
        name (Name): the mechanism name to check
        user (Name): the local name to check against

    Returns:
        bool: whether or not the name is authorized

    Raises:
        ~gssapi.exceptions.GSSError
    """
