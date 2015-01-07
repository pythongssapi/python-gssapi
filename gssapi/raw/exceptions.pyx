from gssapi.raw.cython_types cimport OM_uint32

from gssapi.raw.misc import GSSError

"""Specific exceptions for GSSAPI errors"""


cdef extern from "python_gssapi.h":
    # calling errors
    OM_uint32 GSS_S_CALL_INACCESSIBLE_READ
    OM_uint32 GSS_S_CALL_INACCESSIBLE_WRITE
    OM_uint32 GSS_S_CALL_BAD_STRUCTURE

    # routine errors
    OM_uint32 GSS_S_BAD_MECH
    OM_uint32 GSS_S_BAD_NAME
    OM_uint32 GSS_S_BAD_NAMETYPE
    OM_uint32 GSS_S_BAD_BINDINGS
    OM_uint32 GSS_S_BAD_STATUS
    OM_uint32 GSS_S_BAD_SIG
    # NB(directxman12): BAD_MIC == BAD_SIG, so skip it
    OM_uint32 GSS_S_NO_CRED
    OM_uint32 GSS_S_NO_CONTEXT
    OM_uint32 GSS_S_DEFECTIVE_TOKEN
    OM_uint32 GSS_S_DEFECTIVE_CREDENTIAL
    OM_uint32 GSS_S_CREDENTIALS_EXPIRED
    OM_uint32 GSS_S_CONTEXT_EXPIRED
    # OM_uint32 GSS_S_FAILURE
    OM_uint32 GSS_S_BAD_QOP
    OM_uint32 GSS_S_UNAUTHORIZED
    OM_uint32 GSS_S_UNAVAILABLE
    OM_uint32 GSS_S_DUPLICATE_ELEMENT
    OM_uint32 GSS_S_NAME_NOT_MN

    # supplementary bits
    # OM_uint32 GSS_S_CONTINUE_NEEDED
    OM_uint32 GSS_S_DUPLICATE_TOKEN
    OM_uint32 GSS_S_OLD_TOKEN
    OM_uint32 GSS_S_UNSEQ_TOKEN
    OM_uint32 GSS_S_GAP_TOKEN


# Generic calling code errors
class ParameterReadError(GSSError):
    CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ


class ParameterWriteError(GSSError):
    CALLING_CODE = GSS_S_CALL_INACCESSIBLE_WRITE


class MalformedParameterError(GSSError):
    CALLING_CODE = GSS_S_CALL_BAD_STRUCTURE


# generic routine errors
class BadMechanismError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_MECH


class BadNameError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_NAME


class BadNameTypeError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_NAMETYPE


class BadChannelBindingsError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_BINDINGS


class BadStatusError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_STATUS


class BadMICError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_SIG


class MissingCredentialsError(GSSError):
    ROUTINE_CODE = GSS_S_NO_CRED


class MissingContextError(GSSError):
    ROUTINE_CODE = GSS_S_NO_CONTEXT


class InvalidTokenError(GSSError):
    ROUTINE_CODE = GSS_S_DEFECTIVE_TOKEN


class InvalidCredentialsError(GSSError):
    ROUTINE_CODE = GSS_S_DEFECTIVE_CREDENTIAL


class ExpiredCredentialsError(GSSError):
    ROUTINE_CODE = GSS_S_CREDENTIALS_EXPIRED


class ExpiredContextError(GSSError):
    ROUTINE_CODE = GSS_S_CONTEXT_EXPIRED


# NB(directxman12): since GSS_S_FAILURE is generic,
#                   we just use GSSError for it


class BadQoPError(GSSError):
    ROUTINE_CODE = GSS_S_BAD_QOP


class UnauthorizedError(GSSError):
    ROUTINE_CODE = GSS_S_UNAUTHORIZED


class OperationUnavailableError(GSSError):
    ROUTINE_CODE = GSS_S_UNAVAILABLE


class DuplicateCredentialsElementError(GSSError):
    ROUTINE_CODE = GSS_S_DUPLICATE_ELEMENT


class MechanismNameRequiredError(GSSError):
    ROUTINE_CODE = GSS_S_NAME_NOT_MN


# specific calling | routine errors
class NameReadError(ParameterReadError, BadNameError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ
    # ROUTINE_CODE = GSS_S_BAD_NAME
    pass


class NameTypeReadError(ParameterReadError, BadNameTypeError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ
    # ROUTINE_CODE = GSS_S_BAD_NAMETYPE
    pass


class TokenReadError(ParameterReadError, InvalidTokenError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ
    # ROUTINE_CODE = GSS_S_DEFECTIVE_TOKEN
    pass


class ContextReadError(ParameterReadError, MissingContextError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ
    # ROUTINE_CODE = GSS_S_NO_CONTEXT
    pass


class CredentialsReadError(ParameterReadError, MissingCredentialsError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_READ
    # ROUTINE_CODE = GSS_S_NO_CRED
    pass


class ContextWriteError(ParameterWriteError, MissingContextError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_WRITE
    # ROUTINE_CODE = GSS_S_NO_CONTEXT
    pass


class CredentialsWriteError(ParameterWriteError, MissingCredentialsError):
    # CALLING_CODE = GSS_S_CALL_INACCESSIBLE_WRITE
    # ROUTINE_CODE = GSS_S_NO_CRED
    pass


# generic supplementary bits errors
class SupplementaryError(GSSError):
    # to make it easy for people to catch all supplementary errors
    pass


class DuplicateTokenError(SupplementaryError):
    SUPPLEMENTARY_CODE = GSS_S_DUPLICATE_TOKEN


class ExpiredTokenError(SupplementaryError):
    SUPPLEMENTARY_CODE = GSS_S_OLD_TOKEN


class TokenOutOfSequenceError(SupplementaryError):
    pass


class TokenTooLateError(TokenOutOfSequenceError):
    SUPPLEMENTARY_CODE = GSS_S_UNSEQ_TOKEN


class TokenTooEarlyError(TokenOutOfSequenceError):
    SUPPLEMENTARY_CODE = GSS_S_GAP_TOKEN
