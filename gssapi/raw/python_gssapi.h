#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/GSS.h>
#elif defined(__MINGW32__) && defined(__MSYS__)
#include <gss.h>
#else
#include <gssapi/gssapi.h>
#endif
