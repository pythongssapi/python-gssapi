#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/gssapi_krb5.h>

/* These functions are "private" in macOS GSS. They need to be redeclared so
 * Cython can see them. */
OM_uint32
__ApplePrivate_gsskrb5_extract_authtime_from_sec_context(OM_uint32 *minor,
                                                         gss_ctx_id_t context,
                                                         void *authtime);

OM_uint32 __ApplePrivate_gss_krb5_import_cred(OM_uint32 *minor_status,
                                              void *id,
                                              void *keytab_principal,
                                              void *keytab,
                                              gss_cred_id_t *cred);

OM_uint32 __ApplePrivate_gss_krb5_get_tkt_flags(OM_uint32 *minor_status,
                                                gss_ctx_id_t context_handle,
                                                void *tkt_flags);

#elif defined(__MINGW32__) && defined(__MSYS__)
#include <gss.h>
#else
#include <gssapi/gssapi_krb5.h>
#endif
