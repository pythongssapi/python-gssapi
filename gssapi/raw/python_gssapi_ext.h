#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/GSS.h>

/*
 * Starting in macOS 10.7, Apple's GSS defines these in
 * gssapi_private.h. However, that header isn't present on the host, so we
 * need to explicitly define them.  The originals can be found at:
 * https://opensource.apple.com/source/Heimdal/Heimdal-172.18/lib/gssapi/gssapi/gssapi_spi.h.auto.html
 */

OM_uint32 __ApplePrivate_gss_unwrap_iov(OM_uint32 *minor_status,
                                        gss_ctx_id_t context_handle,
                                        int *conf_state, gss_qop_t *qop_state,
                                        gss_iov_buffer_desc *iov,
                                        int iov_count);

OM_uint32 __ApplePrivate_gss_wrap_iov(OM_uint32 *minor_status,
                                      gss_ctx_id_t context_handle,
                                      int conf_req_flag, gss_qop_t qop_req,
                                      int *conf_state,
                                      gss_iov_buffer_desc *iov,
                                      int iov_count);

OM_uint32 __ApplePrivate_gss_wrap_iov_length(OM_uint32 *minor_status,
                                             gss_ctx_id_t context_handle,
                                             int conf_req_flag,
                                             gss_qop_t qop_req,
                                             int *conf_state,
                                             gss_iov_buffer_desc *iov,
                                             int iov_count);

OM_uint32 __ApplePrivate_gss_release_iov_buffer(OM_uint32 *minor_status,
                                                gss_iov_buffer_desc *iov,
                                                int iov_count);

#else /* !OSX_HAS_GSS_FRAMEWORK */

#if defined(__MINGW32__) && defined(__MSYS__)
#include <gss.h>
#else
#ifdef HAS_GSSAPI_EXT_H
#include <gssapi/gssapi_ext.h>
#else
#include <gssapi/gssapi.h>
#endif
#endif

#endif /* !OSX_HAS_GSS_FRAMEWORK */
