from typing import Iterable, List, NamedTuple, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from gssapi.raw.creds import Creds
    from gssapi.raw.names import Name
    from gssapi.raw.oids import OID
    from gssapi.raw.sec_contexts import SecurityContext
    from gssapi.raw.types import RequirementFlag


class AcquireCredResult(NamedTuple):
    """Credential result when acquiring a GSSAPI credential."""
    creds: "Creds"  #: GSSAPI credentials that were acquired
    mechs: Set["OID"]  #: Set of mechs the cred is for
    lifetime: int  #: Number of seconds for which the cred will remain valid


class InquireCredResult(NamedTuple):
    """Information about the credential."""
    name: Optional["Name"]  #: The principal associated with the credential
    lifetime: Optional[int]  #: Number of seconds which the cred is valid for
    usage: Optional[str]  #: How the credential can be used
    mechs: Optional[Set["OID"]]  #: Set of mechs the cred is for


class InquireCredByMechResult(NamedTuple):
    """Information about the credential for a specific mechanism."""
    name: Optional["Name"]  #: The principal associated with the credential
    init_lifetime: Optional[int]  #: Time valid for initiation
    accept_lifetime: Optional[int]  #: Time valid for accepting
    usage: Optional[str]  #: How the credential can be used


class AddCredResult(NamedTuple):
    """Result of adding to a GSSAPI credential."""
    creds: Optional["Creds"]  #: The credential that was generated
    mechs: Set["OID"]  #: Set of mechs the cred is for
    init_lifetime: int  #: Time valid for initiation
    accept_lifetime: int  #: Time valid for accepting


class DisplayNameResult(NamedTuple):
    """Textual representation of a GSSAPI name."""
    name: bytes  #: The representation of the GSSAPI name
    name_type: Optional["OID"]  #: The type of GSSAPI name


class WrapResult(NamedTuple):
    """Wrapped message result."""
    message: bytes  #: The wrapped message
    encrypted: bool  #: Whether the message is encrypted and not just signed


class UnwrapResult(NamedTuple):
    """Unwrapped message result."""
    message: bytes  #: The unwrapped message
    encrypted: bool  #: Whether the message was encrypted and not just signed
    qop: int  #: The quality of protection applied to the message


class AcceptSecContextResult(NamedTuple):
    """Result when accepting a security context by an initiator."""
    context: "SecurityContext"  #: The acceptor security context
    initiator_name: "Name"  #: The authenticated name of the initiator
    mech: "OID"  #: Mechanism with which the context was established
    token: Optional[bytes]  #: Token to be returned to the initiator
    flags: "RequirementFlag"  #: Services requested by the initiator
    lifetime: int  #: Seconds for which the context is valid for
    delegated_creds: Optional["Creds"]  #: Delegated credentials
    more_steps: bool  #: More input is required to complete the exchange


class InitSecContextResult(NamedTuple):
    """Result when initiating a security context"""
    context: "SecurityContext"  #: The initiator security context
    mech: "OID"  #: Mechanism used in the security context
    flags: "RequirementFlag"  #: Services available for the context
    token: Optional[bytes]  #: Token to be sent to the acceptor
    lifetime: int  #: Seconds for which the context is valid for
    more_steps: bool  #: More input is required to complete the exchange


class InquireContextResult(NamedTuple):
    """Information about the security context."""
    initiator_name: Optional["Name"]  #: Name of the initiator
    target_name: Optional["Name"]  #: Name of the acceptor
    lifetime: Optional[int]  #: Time valid for the security context
    mech: Optional["OID"]  #: Mech used to create the security context
    flags: Optional["RequirementFlag"]  #: Services available for the context
    locally_init: Optional[bool]  #: Context was initiated locally
    complete: Optional[bool]  #: Context has been established and ready to use


class StoreCredResult(NamedTuple):
    """Result of the credential storing operation."""
    mechs: List["OID"]  #: Mechs that were stored in the credential store
    usage: str  #: How the credential can be used


class IOVUnwrapResult(NamedTuple):
    """Unwrapped IOV message result."""
    encrypted: bool  #: Whether the message was encrypted and not just signed
    qop: int  #: The quality of protection applied to the message


class InquireNameResult(NamedTuple):
    """Information about a GSSAPI Name."""
    attrs: List[bytes]  #: Set of attribute names
    is_mech_name: bool  #: Name is a mechanism name
    mech: "OID"  #: The mechanism if is_name_mech is True


class GetNameAttributeResult(NamedTuple):
    """GSSAPI Name attribute values."""
    values: Iterable[bytes]  #: Raw values
    display_values: Iterable[bytes]  #: Human-readable values
    authenticated: bool  #: Attribute has been authenticated
    complete: bool  #: Attribute value is marked as complete


class InquireAttrsResult(NamedTuple):
    """Set of attributes supported and known by a mechanism."""
    mech_attrs: Set["OID"]  #: The mechanisms attributes
    known_mech_attrs: Set["OID"]  #: Known attributes of the mechanism


class DisplayAttrResult(NamedTuple):
    """Information about an attribute."""
    name: bytes  #: The mechanism name
    short_desc: bytes  #: Short description of the mechanism
    long_desc: bytes  #: Long description of the mechanism


class InquireSASLNameResult(NamedTuple):
    """SASL informmation about a GSSAPI Name."""
    sasl_mech_name: bytes  #: The SASL name
    mech_name: bytes  #: The mechanism name
    mech_description: bytes  #: The mechanism description


class Rfc1964KeyData(NamedTuple):
    """Security context key data based on RFC1964."""
    sign_alg: int  #: Signing algorithm identifier
    seal_alg: int  #: Sealing algorithm identifier
    key_type: int  #: Key encryption type identifier
    key: bytes  #: Encryption key data


class CfxKeyData(NamedTuple):
    """Securty context key data."""
    ctx_key_type: int  #: Context key encryption type identifier
    ctx_key: bytes  #: Context key data - session or sub-session key
    acceptor_subkey_type: Optional[int]  #: Acceptor key enc type identifier
    acceptor_subkey: Optional[bytes]  #: Acceptor key data
