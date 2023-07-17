from gssapi.raw.cython_types cimport OM_uint32

from gssapi.raw import _enum_extensions as ext_registry


cdef extern from "python_gssapi_ext.h":
    OM_uint32 GSS_C_DCE_STYLE
    OM_uint32 GSS_C_IDENTIFY_FLAG
    OM_uint32 GSS_C_EXTENDED_ERROR_FLAG

ext_registry.register_value('RequirementFlag', 'dce_style', GSS_C_DCE_STYLE)
ext_registry.register_value('RequirementFlag', 'identify', GSS_C_IDENTIFY_FLAG)
ext_registry.register_value('RequirementFlag', 'extended_error',
                            GSS_C_EXTENDED_ERROR_FLAG)
