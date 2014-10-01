from gssapi.raw.cython_types cimport gss_OID, gss_OID_set, gss_OID_desc
from gssapi.raw.cython_types cimport OM_uint32

from gssapi.raw.types import MechType, NameType


cdef gss_OID_set c_get_mech_oid_set(object mechs)
cdef gss_OID c_get_name_type_oid(object name_type)
cdef object c_create_name_type(gss_OID name_type)
cdef inline bint c_compare_oids(gss_OID a, gss_OID b)
cdef object c_create_mech_list(gss_OID_set mech_set, bint free=*)
cdef inline OM_uint32 c_py_ttl_to_c(object ttl)
cdef inline object c_c_ttl_to_py(OM_uint32 ttl)
