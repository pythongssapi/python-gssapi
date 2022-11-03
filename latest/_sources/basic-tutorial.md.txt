A Basic Introduction to GSSAPI
==============================

GSSAPI (which stands for "Generic Security Service API") is an
standard layer for interfacing with security services.  While it
supports multiple different mechanisms, it is most commonly used
with Kerberos 5 ("krb5" for short).

This tutorial will provide a basic introduction to interacting with
GSSAPI through Python.

*Note*: This file is designed to be runnable using
[YALPT](https://github.com/directxman12/yalpt).  You can also just
read it normally.

To start out, we'll import python-gssapi, and save the current FQDN
for later:

    >>> import gssapi, socket
    >>> FQDN = socket.getfqdn()
    >>>

Note that this assumes you have a KRB5 realm set up, and some relevant
functions available in the `REALM` object (see gssapi-console.py in
[gssapi_console](https://pypi.python.org/pypi/gssapi_console)), or
try `$ run-lit -e gssapi basic-tutorial.md` when you have both
gssapi_console and yalpt installed).  Any actions performed using the
`REALM` object are not part of the GSSAPI library; the `REALM` object
simply contains wrappers to krb5 commands generally run separately from
the application using GSSAPI.

Names and Credentials
---------------------

Two important concepts in GSSAPI are *names* and *credentials*.

*Names*, as the name suggests, identify different entities, be they
users or services.  GSSAPI has the concept of different *name types*.
These represent different types of names and corresponding syntax
for representing names as strings.

Suppose we wanted to refer to an HTTP server on the current host.
We could refer to it as a *host-based service*, or in the default
mechanism form (in this case, for krb5):

    >>> server_hostbased_name = gssapi.Name(f"HTTP@{FQDN}", name_type=gssapi.NameType.hostbased_service)
    >>> server_hostbased_name
    Name(b'HTTP@seton.mivehind.net', <OID 1.2.840.113554.1.2.1.4>)
    >>> server_name = gssapi.Name(f"HTTP/{FQDN}@")
    >>> server_name
    Name(b'HTTP/seton.mivehind.net@', None)
    >>>

These are both effectively the same, but if we *canonicalize* both
names with respect to krb5, we'll see that GSSAPI knows they're the
same:

    >>> server_name == server_hostbased_name
    False
    >>> server_canon_name = server_name.canonicalize(gssapi.MechType.kerberos)
    >>> server_hostbased_canon_name = server_hostbased_name.canonicalize(gssapi.MechType.kerberos)
    >>> server_canon_name == server_hostbased_canon_name
    True
    >>>

To compare two names of different name types, you should canonicalize
them first.

*Credentials* represent identification for a user or service.  In
order to establish secure communication with other entities, a user
or service first needs credentials.  For the krb5 mechanism,
credentials generally represent a handle to the TGT.

Credentials may be acquired for a particular name, or the default set
of credentials may be acquired.

For instance, suppose that we are writing a server, and wish to
communicate accept connections as the 'HTTP' service.  We would need
to acquire credentials as such:

    >>> REALM.addprinc('HTTP/%s@%s' % (FQDN, REALM.realm))
    >>> REALM.extract_keytab('HTTP/%s@%s' % (FQDN, REALM.realm), REALM.keytab)
    >>> server_creds = gssapi.Credentials(usage='accept', name=server_name)
    >>>

Note that for the krb5 mechanism, in order to acquire credentials with
the GSSAPI, the system must already have a way to access those credentials.
For users, this generally means that they have already performed a `kinit`
(i.e. have cached a TGT), while for services (like above), having a keytab
is sufficient.  This process is generally performed outside the application
using the GSSAPI.

Credentials have a *usage*: 'accept' for accepting security contexts,
'initiate' for initiating security contexts, or 'both' for
credentials used for both initiating and accepting security contexts.

Credentials also have an associated *name*, *lifetime* (which may
be `None` for indefinite), and set of *mechanisms* with which the
credentials are usable:

    >>> server_creds.usage
    'accept'
    >>> server_creds.name == server_name
    True
    >>> server_creds.lifetime is None
    True
    >>> gssapi.MechType.kerberos in server_creds.mechs
    True
    >>> gssapi.MechType.kerberos in server_creds.mechs
    True
    >>>

Each of these settings is setable from the constructor as `usage`,
`name`, `lifetime`, and `mechs`.

Security Contexts
-----------------

*Security contexts* represent active sessions between two different
entities.  Security contexts are used to verify identities, as well
as ensure *integrity* (message signing), *confidentiality* (message
encryption), or both for messages exchanged between the two parties.

When establishing a security context, the default credentials are
used unless otherwise specified.  This allows applications to use
the user's already acquired credentials:

    >>> client_ctx = gssapi.SecurityContext(name=server_name, usage='initiate')
    >>> initial_client_token = client_ctx.step()
    >>> client_ctx.complete
    False
    >>>

Just like credentials, security contexts are either initiating
contexts, or accepting contexts (they cannot be both).  Initiating
contexts must specify at least a target name.  In this case,
we indicate that we wish to establish a context with the HTTP server
from above.  The http server can then accept that context:

    >>> server_ctx = gssapi.SecurityContext(creds=server_creds, usage='accept')
    >>> initial_server_token = server_ctx.step(initial_client_token)
    >>>

As you can see, creating an accepting security context is similar.
Here, we specify a set of accepting credentials to use, although
this is optional (the defaults will be used if no credentials are
specified).

Let's finish up the exchange:

    >>> server_tok = initial_server_token
    >>>
    >>> while not (client_ctx.complete and server_ctx.complete):
    ...     client_tok = client_ctx.step(server_tok)
    ...     if not client_tok:
    ...         break
    ...     server_tok = server_ctx.step(client_tok)
    ...
    >>> client_ctx.complete and server_ctx.complete
    True
    >>>

We can now wrap and unwrap messages, using the `wrap` and `unwrap` methods
on `SecurityContext`:

    >>> message = b'some message here'
    >>> wrapped_message, msg_encrypted = client_ctx.wrap(message, True)
    >>> message not in wrapped_message
    True
    >>> msg_encrypted
    True
    >>> server_ctx.unwrap(wrapped_message)
    UnwrapResult(message=b'some message here', encrypted=True, qop=0)
    >>>

We can use the second parameter to control whether or not we encrypt the
messages, or just sign them:

    >>> signed_message, msg_encrypted = client_ctx.wrap(message, False)
    >>> msg_encrypted
    False
    >>> message in signed_message
    True
    >>> server_ctx.unwrap(signed_message)
    UnwrapResult(message=b'some message here', encrypted=False, qop=0)
    >>>

Manually passing in a second parameter and checking whether or not encryption
was used can get tedious, so python-gssapi provides two convenience methods
to help with this: `encrypt` and `decrypt`.  If the context is set up to use
encryption, they will call `wrap` with encryption.  If not, they will
call `wrap` without encryption.

    >>> encrypted_message = client_ctx.encrypt(message)
    >>> encrypted_message != message
    True
    >>> server_ctx.decrypt(encrypted_message)
    b'some message here'
    >>>

Notice that if we try to use `decrypt` a signed message, and exception will be raised,
since the context was set up to use encryption (the default):

    >>> signed_message, _ = client_ctx.wrap(message, False)
    >>> server_ctx.decrypt(signed_message)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<string>", line 2, in decrypt
      File "/usr/lib/python3.4/site-packages/gssapi/_utils.py", line 167, in check_last_err
        return func(self, *args, **kwargs)
      File "/usr/lib/python3.4/site-packages/gssapi/sec_contexts.py", line 295, in decrypt
        unwrapped_message=res.message)
    gssapi.exceptions.EncryptionNotUsed: Confidentiality was requested, but not used: The context was established with encryption, but unwrapped message was not encrypted.
    >>>

There you have it: the basics of GSSAPI.  You can use the `help` function
at the interpreter, or check the [docs](http://pythonhosted.org/gssapi/)
for more information.
