GSSAPI="BASE"

from gssapi.raw.cython_types cimport *
from gssapi.raw.ext_buffer_sets cimport *
from gssapi.raw.cython_converters cimport c_get_mech_oid_set
from gssapi.raw.misc import GSSError
from gssapi.raw.oids cimport OID
from gssapi.raw.sec_contexts cimport SecurityContext

cdef extern from "python_gssapi_ext.h":
    OM_uint32 gss_inquire_sec_context_by_oid(OM_uint32 *min_stat,
                                  const gss_ctx_id_t context_handle,
                                  const gss_OID desired_object,
                                  gss_buffer_set_t *data_set) nogil


def inquire_sec_context_by_oid(SecurityContext context not None, OID mech not None):
    """
    Args:
      context (SecurityContext): the security context to update, or
          None to create a new context
      mech (MechType): the mechanism type for this security context,
          or None for the default mechanism type
    """
    cdef gss_buffer_set_t *output_token_buffer_ptr = NULL
    cdef gss_buffer_set_t output_token_buffer = GSS_C_NO_BUFFER_SET;
    cdef OM_uint32 maj_stat, min_stat

    output_token_buffer_ptr = &output_token_buffer

    cdef gss_OID_set desired_mechs

    with nogil:
        maj_stat = gss_inquire_sec_context_by_oid(&min_stat, context.raw_ctx, &mech.raw_oid, output_token_buffer_ptr)

    if maj_stat == GSS_S_COMPLETE:
        py_token = []

        if output_token_buffer != GSS_C_NO_BUFFER_SET:
            for i in range(output_token_buffer.count):
                token = output_token_buffer.elements[i]
                py_token.append(token.value[:token.length])

            gss_release_buffer_set(&min_stat, &output_token_buffer)
            return py_token
    else:
        raise GSSError(maj_stat, min_stat)
