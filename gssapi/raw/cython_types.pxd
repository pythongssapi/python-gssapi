from libc.stdint cimport uint32_t


cdef extern from "gssapi.h":
    # basic types
    ctypedef uint32_t OM_uint32

    # int type aliases
    ctypedef int gss_cred_usage_t
    ctypedef OM_uint32 gss_qop_t

    # struct types
    ctypedef struct gss_OID_desc:
        OM_uint32 length
        void *elements
    ctypedef gss_OID_desc* gss_OID

    ctypedef struct gss_OID_set_desc:
        size_t count
        gss_OID elements
    ctypedef gss_OID_set_desc* gss_OID_set

    ctypedef struct gss_buffer_desc:
        size_t length
        char *value
    ctypedef gss_buffer_desc* gss_buffer_t

    cdef struct gss_name_struct:
        pass
    ctypedef gss_name_struct* gss_name_t

    cdef struct gss_cred_id_struct:
        pass
    ctypedef gss_cred_id_struct* gss_cred_id_t

    cdef struct gss_ctx_id_struct:
        pass
    ctypedef gss_ctx_id_struct* gss_ctx_id_t

    ctypedef struct gss_channel_bindings_struct:
        OM_uint32 initiator_addrtype
        gss_buffer_desc initiator_address
        OM_uint32 acceptor_addrtype
        gss_buffer_desc acceptor_address
        gss_buffer_desc application_data
    ctypedef gss_channel_bindings_struct* gss_channel_bindings_t

    # util methods
    OM_uint32 gss_release_buffer(OM_uint32 *min_stat, gss_buffer_t buff)
    OM_uint32 gss_create_empty_oid_set(OM_uint32 *min_stat,
                                       gss_OID_set *target_set)
    OM_uint32 gss_release_oid_set(OM_uint32 *min_stat,
                                  gss_OID_set *target_set)
    OM_uint32 gss_add_oid_set_member(OM_uint32 *min_stat,
                                     const gss_OID member,
                                     gss_OID_set *target_set)
    OM_uint32 gss_test_oid_set_member(OM_uint32 *min_stat,
                                      const gss_OID member,
                                      const gss_OID_set target_set,
                                      int *present)

    # misc int constants
    # status code types
    int GSS_C_GSS_CODE
    int GSS_C_MECH_CODE
    # status code constants
    OM_uint32 GSS_S_COMPLETE
    OM_uint32 GSS_S_CONTINUE_NEEDED
    OM_uint32 GSS_S_DUPLICATE_TOKEN

    # cred_usage constants
    gss_cred_usage_t GSS_C_BOTH
    gss_cred_usage_t GSS_C_INITIATE
    gss_cred_usage_t GSS_C_ACCEPT

    # null/default constants
    gss_OID GSS_C_NO_OID
    # NB(sross): because of how Cython creates variables, this is useless
    # gss_buffer_desc GSS_C_EMPTY_BUFFER
    gss_name_t GSS_C_NO_NAME   # TODO(sross): actually check for this
    OM_uint32 GSS_C_INDEFINITE
    gss_buffer_t GSS_C_NO_BUFFER
    gss_OID_set GSS_C_NO_OID_SET
    gss_channel_bindings_t GSS_C_NO_CHANNEL_BINDINGS
    gss_qop_t GSS_C_QOP_DEFAULT
    gss_ctx_id_t GSS_C_NO_CONTEXT
    gss_cred_id_t GSS_C_NO_CREDENTIAL

    # OID constants
    # OID name types
    gss_OID GSS_C_NT_HOSTBASED_SERVICE
    gss_OID GSS_C_NT_USER_NAME
    gss_OID GSS_C_NT_ANONYMOUS
    gss_OID GSS_C_NT_MACHINE_UID_NAME
    gss_OID GSS_C_NT_STRING_UID_NAME
    gss_OID GSS_C_NT_EXPORT_NAME

    # flag constants
    OM_uint32 GSS_C_DELEG_FLAG
    OM_uint32 GSS_C_MUTUAL_FLAG
    OM_uint32 GSS_C_REPLAY_FLAG
    OM_uint32 GSS_C_SEQUENCE_FLAG
    OM_uint32 GSS_C_CONF_FLAG
    OM_uint32 GSS_C_INTEG_FLAG
    OM_uint32 GSS_C_ANON_FLAG
    OM_uint32 GSS_C_TRANS_FLAG


cdef extern from "gssapi/gssapi_krb5.h":
    gss_OID gss_mech_krb5
    gss_OID GSS_KRB5_NT_PRINCIPAL_NAME
