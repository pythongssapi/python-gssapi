#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/gssapi_krb5.h>
#elif defined(__MINGW32__) && defined(__MSYS__)
#include <gss.h>
#else
#include <gssapi/gssapi_krb5.h>
#endif
