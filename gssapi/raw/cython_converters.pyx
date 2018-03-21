from gssapi.raw.cython_types cimport *
from gssapi.raw.oids cimport OID

from gssapi.raw.types import MechType, NameType


cdef OID c_make_oid(gss_OID oid):
    """Create an OID from a C OID struct pointer"""
    cdef OID res = OID()
    res.raw_oid = oid[0]
    return res


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


cdef object c_create_oid_set(gss_OID_set mech_set, bint free=True):
    """Convert a GSS OID set struct to a set of OIDs"""

    if mech_set == GSS_C_NO_OID_SET:
        # return the empty set if the we get passed the C equivalent
        # (it could be argued that the C equivalent is closer to None,
        # but returning None would make the API harder to work with,
        # without much value)
        return set()

    py_set = set()
    cdef i
    for i in range(mech_set.count):
        mech_type = OID()
        mech_type._copy_from(mech_set.elements[i])
        py_set.add(mech_type)

    cdef OM_uint32 tmp_min_stat
    if free:
        gss_release_oid_set(&tmp_min_stat, &mech_set)

    return py_set
