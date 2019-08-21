Common Values for Credentials Store Extensions
==============================================

The credentials store extension is an extension introduced by the MIT krb5
library implementation of GSSAPI.  It allows for finer control of credentials
from within a GSSAPI application.  Each mechanism can define keywords to
manipulate various aspects of their credentials for storage or retrieval
operations.

.. note:

   Only mechanisms that implement keywords can use them: some mechanisms may
   share the same or similar keywords, but their meaning is always local to a
   specific mechanism.

.. note:

   `None` is not a permitted value and will raise exceptions.  Phrased
   differently, values must be strings, not empty.

The krb5 mechanism in MIT libraries
-----------------------------------

The krb5 mechanism as implemented by MIT libraries supports the credentials
store extension with a number of keywords.

client_keytab
"""""""""""""

The `client_keytab` keyword can be used in a credential store when it is used
with the :func:`gssapi.raw.ext_cred_store.acquire_cred_from` /
:func:`gssapi.raw.ext_cred_store.add_cred_from` functions to indicate a custom
location for a keytab containing client keys.  It is not used in the context
of calls used to store credentials.

The value is a string in the form **type:residual** where **type** can be any
keytab storage type understood by the implementation and **residual** is the
keytab identifier (usually something like a path).  If the string is a path,
then the type is defaulted to `FILE`.

keytab
""""""

The `keytab` keyword can be used in a credential store when it is used with
the :func:`gssapi.raw.ext_cred_store.acquire_cred_from` /
:func:`gssapi.raw.ext_cred_store.add_cred_from` functions to indicate a custom
location for a keytab containing service keys.  It is not used in the context
of calls used to store credentials.

The value is a string in the form **type:residual** where **type** can be any
keytab storage type understood by the implementation and **residual** is the
keytab identifier (usually something like a path).  If the string is a path,
then the type is defaulted to `FILE`.

ccache
""""""

The `ccache` keyword can be used to reference a specific credential storage.
It can be used both to indicate the source of existing credentials for the
:func:`gssapi.raw.ext_cred_store.acquire_cred_from` /
:func:`gssapi.raw.ext_cred_store.add_cred_from` functions, as well as the
destination storage for the :func:`gssapi.raw.ext_cred_store.store_cred_into`
function.

The value is a string in the form **type:residual** where **type** can be any
credential cache storage type understood by the implementation and
**residual** is the ccache identifier.  If the string is a path, then the type
is defaulted to `FILE`.  Other commonly used types are `DIR`, `KEYRING`,
`KCM`, and `MEMORY`.  Each type has a different format for the **residual**;
refer to the MIT krb5 documentation for more details.

rcache
""""""

The `rcache` keyword can be used to reference a custom replay cache storage.
It is used only with the :func:`gssapi.raw.ext_cred_store.acquire_cred_from` /
:func:`gssapi.raw.ext_cred_store.add_cred_from` functions for credentials used
to accept context establishments, not to initiate contexts.

The value is a string in the form **type:residual** where **type** can be any
replay cache storage type understood by the implementation and **residual** is
the cache identifier (usually something like a path).  If the string is a
path, then the type is defaulted to `FILE`.

The krb5 mechanism in Heimdal
-----------------------------

Heimdal has recently implemented the credential store extensions with the same
interface as MIT krb5.  However, it is not yet present in any released
version.
