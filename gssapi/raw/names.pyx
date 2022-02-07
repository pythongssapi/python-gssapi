GSSAPI="BASE"  # this ensures that a full module is generated by Cython

from gssapi.raw.cython_types cimport *
from gssapi.raw.oids cimport OID

from gssapi.raw.misc import GSSError
from gssapi.raw.named_tuples import DisplayNameResult


cdef extern from "python_gssapi.h":
    OM_uint32 gss_import_name(OM_uint32 *min_stat,
                              const gss_buffer_t input_buffer,
                              const gss_OID name_type,
                              gss_name_t *output_name) nogil

    OM_uint32 gss_display_name(OM_uint32 *min_stat,
                               const gss_name_t name,
                               gss_buffer_t output_buffer,
                               gss_OID *output_name_type) nogil

    OM_uint32 gss_compare_name(OM_uint32 *min_stat,
                               const gss_name_t name1,
                               const gss_name_t name2,
                               int *is_equal) nogil

    OM_uint32 gss_export_name(OM_uint32 *min_stat,
                              const gss_name_t name,
                              gss_buffer_t output_buffer) nogil

    OM_uint32 gss_canonicalize_name(OM_uint32 *min_stat,
                                    const gss_name_t input_name,
                                    const gss_OID mech_type,
                                    gss_name_t *output_name) nogil

    OM_uint32 gss_duplicate_name(OM_uint32 *min_stat,
                                 const gss_name_t input_name,
                                 gss_name_t *output_name) nogil

    OM_uint32 gss_release_name(OM_uint32 *min_stat,
                               gss_name_t *name) nogil


cdef class Name:
    # defined in pxd
    # cdef gss_name_t raw_name

    def __cinit__(self, Name cpy=None):
        if cpy is not None:
            self.raw_name = cpy.raw_name
            cpy.raw_name = GSS_C_NO_NAME
        else:
            self.raw_name = GSS_C_NO_NAME

    def __dealloc__(self):
        # essentially just releaseName(self), but it is unsafe to call
        # methods
        cdef OM_uint32 maj_stat, min_stat
        if self.raw_name is not GSS_C_NO_NAME:
            maj_stat = gss_release_name(&min_stat, &self.raw_name)
            if maj_stat != GSS_S_COMPLETE:
                raise GSSError(maj_stat, min_stat)
            self.raw_name = NULL


def import_name(name not None, OID name_type=None):
    cdef gss_OID nt
    if name_type is None:
        nt = GSS_C_NO_OID
    else:
        nt = &name_type.raw_oid

    # GSS_C_EMPTY_BUFFER
    cdef gss_buffer_desc name_buffer = gss_buffer_desc(0, NULL)
    name_buffer.length = len(name)
    name_buffer.value = name

    cdef gss_name_t output_name

    cdef OM_uint32 maj_stat, min_stat

    with nogil:
        maj_stat = gss_import_name(&min_stat, &name_buffer,
                                   nt, &output_name)

    cdef Name on = Name()
    if maj_stat == GSS_S_COMPLETE:
        on.raw_name = output_name
        return on
    else:
        raise GSSError(maj_stat, min_stat)


def display_name(Name name not None, name_type=True):
    # GSS_C_EMPTY_BUFFER
    cdef gss_buffer_desc output_buffer = gss_buffer_desc(0, NULL)

    cdef gss_OID output_name_type
    cdef gss_OID *output_name_type_ptr
    if name_type:
        output_name_type_ptr = &output_name_type
    else:
        output_name_type_ptr = NULL

    cdef OM_uint32 maj_stat, min_stat

    maj_stat = gss_display_name(&min_stat, name.raw_name,
                                &output_buffer, output_name_type_ptr)

    cdef OID py_name_type
    if maj_stat == GSS_S_COMPLETE:
        text = (<char*>output_buffer.value)[:output_buffer.length]
        gss_release_buffer(&min_stat, &output_buffer)
        if name_type:
            if output_name_type == GSS_C_NO_OID:
                # whoops, an implementation was being lazy...
                py_name_type = None
            else:
                py_name_type = OID()
                py_name_type.raw_oid = output_name_type[0]
        else:
            py_name_type = None

        return DisplayNameResult(text, py_name_type)
    else:
        raise GSSError(maj_stat, min_stat)


def compare_name(Name name1=None, Name name2=None):
    # check for either value being None
    if name1 is None and name2 is None:
        return True
    elif name1 is None or name2 is None:
        return False

    cdef int is_equal

    cdef OM_uint32 maj_stat, min_stat

    maj_stat = gss_compare_name(&min_stat, name1.raw_name,
                                name2.raw_name, &is_equal)

    if maj_stat == GSS_S_COMPLETE:
        return <bint>is_equal
    else:
        raise GSSError(maj_stat, min_stat)


def export_name(Name name not None):
    # GSS_C_EMPTY_BUFFER
    cdef gss_buffer_desc exported_name = gss_buffer_desc(0, NULL)

    cdef OM_uint32 maj_stat, min_stat

    maj_stat = gss_export_name(&min_stat, name.raw_name, &exported_name)

    if maj_stat == GSS_S_COMPLETE:
        # force conversion to a python string with the specified length
        # (we use the slice to tell cython that we know the length already)
        res = (<char*>exported_name.value)[:exported_name.length]
        gss_release_buffer(&min_stat, &exported_name)
        return res
    else:
        raise GSSError(maj_stat, min_stat)


def canonicalize_name(Name name not None, OID mech not None):
    cdef gss_name_t canonicalized_name

    cdef OM_uint32 maj_stat, min_stat

    with nogil:
        maj_stat = gss_canonicalize_name(&min_stat, name.raw_name,
                                         &mech.raw_oid,
                                         &canonicalized_name)

    cdef Name cn = Name()
    if maj_stat == GSS_S_COMPLETE:
        cn.raw_name = canonicalized_name
        return cn
    else:
        raise GSSError(maj_stat, min_stat)


def duplicate_name(Name name not None):
    cdef gss_name_t new_name

    cdef OM_uint32 maj_stat, min_stat

    maj_stat = gss_duplicate_name(&min_stat, name.raw_name, &new_name)

    cdef Name on = Name()
    if maj_stat == GSS_S_COMPLETE:
        on.raw_name = new_name
        return on
    else:
        raise GSSError(maj_stat, min_stat)


def release_name(Name name not None):
    cdef OM_uint32 maj_stat, min_stat
    maj_stat = gss_release_name(&min_stat, &name.raw_name)
    if maj_stat != GSS_S_COMPLETE:
        raise GSSError(maj_stat, min_stat)
    name.raw_name = NULL
