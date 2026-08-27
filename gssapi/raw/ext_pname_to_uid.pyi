import typing as t

if t.TYPE_CHECKING:
    from gssapi.raw.names import Name
    from gssapi.raw.oids import OID


def pname_to_uid(
    name: "Name",
    mech: t.Optional["OID"] = None,
) -> int:
    """Get the local UID for a GSSAPI name.

    This method determines the local UID associated with a GSSAPI
    name, optionally for a given mechanism.

    Note:
        This function is not available on Windows.

    Args:
        name (Name): the GSSAPI name to map to a local UID
        mech (~gssapi.OID): the mechanism to use for the mapping
            (or None for the default)

    Returns:
        int: the local UID

    Raises:
        ~gssapi.exceptions.GSSError
    """
