from gssapi.raw.cython_types cimport OM_uint32

import gssapi.raw._enum_extensions as ext_registry


cdef extern from "python_gssapi_ext.h":
    OM_uint32 GSS_C_CHANNEL_BOUND_FLAG

ext_registry.register_value('RequirementFlag', 'channel_bound',
                            GSS_C_CHANNEL_BOUND_FLAG)
