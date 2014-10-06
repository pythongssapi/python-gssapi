from libc.string cimport memcmp

from gssapi.raw.cython_types cimport *
from gssapi.raw.oids cimport OID

from gssapi.raw.types import MechType, NameType


cdef gss_OID_set c_get_mech_oid_set(object mechs):
    """Convert a list of MechType values into an OID set."""

    cdef gss_OID_set res_set
    cdef OM_uint32 min_stat
    gss_create_empty_oid_set(&min_stat, &res_set)

    cdef gss_OID oid
    for mech in mechs:
        oid = &(<OID>mech).raw_oid
        gss_add_oid_set_member(&min_stat, oid, &res_set)

    return res_set


cdef inline bint c_compare_oids(gss_OID a, gss_OID b):
    """Compare two OIDs to see if they are the same."""

    return (a.length == b.length and
            not memcmp(a.elements, b.elements, a.length))


cdef object c_create_mech_list(gss_OID_set mech_set, bint free=True):
    """Convert a set of GSS mechanism OIDs to a list of MechType values."""

    l = []
    cdef i
    for i in range(mech_set.count):
        mech_type = OID()
        mech_type._copy_from(mech_set.elements[i])
        l.append(mech_type)

    cdef OM_uint32 tmp_min_stat
    if free:
        gss_release_oid_set(&tmp_min_stat, &mech_set)

    return l


cdef inline OM_uint32 c_py_ttl_to_c(object ttl):
    """Converts None to GSS_C_INDEFINITE, otherwise returns input."""
    if ttl is None:
        return GSS_C_INDEFINITE
    else:
        return <OM_uint32>ttl


cdef inline object c_c_ttl_to_py(OM_uint32 ttl):
    """Converts GSS_C_INDEFINITE to None, otherwise return input."""
    if ttl == GSS_C_INDEFINITE:
        return None
    else:
        return ttl
