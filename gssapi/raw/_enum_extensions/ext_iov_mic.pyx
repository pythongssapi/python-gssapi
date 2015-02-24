from gssapi.raw.cython_types cimport OM_uint32

from gssapi.raw import _enum_extensions as ext_registry


cdef extern from "python_gssapi_ext.h":
    OM_uint32 GSS_IOV_BUFFER_TYPE_MIC_TOKEN

ext_registry.register_value('IOVBufferType', 'mic_token',
                            GSS_IOV_BUFFER_TYPE_MIC_TOKEN)
