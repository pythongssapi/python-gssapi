from libc.stdlib cimport calloc, free

from gssapi.raw.cython_types cimport *

cdef class ChannelBindings:
    # defined in pxd file
    # cdef public object initiator_address_type
    # cdef public bytes initiator_address

    # cdef public object acceptor_address_type
    # cdef public bytes acceptor_address

    # cdef public bytes application_data

    def __init__(ChannelBindings self, initiator_address_type=None,
                 initiator_address=None, acceptor_address_type=None,
                 acceptor_address=None, application_data=None):
        self.initiator_address_type = initiator_address_type
        self.initiator_address = initiator_address

        self.acceptor_address_type = acceptor_address_type
        self.acceptor_address = acceptor_address

        self.application_data = application_data

    cdef gss_channel_bindings_t __cvalue__(ChannelBindings self) except NULL:
        """Get the C struct version of the channel bindings"""
        cdef gss_channel_bindings_t res
        res = <gss_channel_bindings_t>calloc(1, sizeof(res[0]))

        # NB(directxman12): an addrtype of 0 as set by calloc is equivalent
        #                   to GSS_C_AF_UNSPEC as per RFC 2744

        if self.initiator_address_type is not None:
            res.initiator_addrtype = self.initiator_address_type

        if self.initiator_address is not None:
            res.initiator_address.value = self.initiator_address
            res.initiator_address.length = len(self.initiator_address)

        if self.acceptor_address_type is not None:
            res.acceptor_addrtype = self.acceptor_address_type

        if self.acceptor_address is not None:
            res.acceptor_address.value = self.acceptor_address
            res.acceptor_address.length = len(self.acceptor_address)

        if self.application_data is not None:
            res.application_data.value = self.application_data
            res.application_data.length = len(self.application_data)

        return res
