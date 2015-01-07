#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/GSS.h>
#else
#ifdef HAS_GSSAPI_EXT_H
#include <gssapi/gssapi_ext.h>
#else
#include <gssapi/gssapi.h>
#endif
#endif
