import copy
import os
import socket
import sys
import pickle

import should_be.all  # noqa
import six
from nose_parameterized import parameterized

from gssapi import creds as gsscreds
from gssapi import names as gssnames
from gssapi import sec_contexts as gssctx
from gssapi import raw as gb
from gssapi.tests import k5test as kt
from gssapi._utils import import_gssapi_extension


TARGET_SERVICE_NAME = b'host'
FQDN = socket.getfqdn().encode('utf-8')
SERVICE_PRINCIPAL = TARGET_SERVICE_NAME + b'/' + FQDN


class _GSSAPIKerberosTestCase(kt.KerberosTestCase):
    @classmethod
    def setUpClass(cls):
        super(_GSSAPIKerberosTestCase, cls).setUpClass()
        svc_princ = SERVICE_PRINCIPAL.decode("UTF-8")

        cls.realm.kinit(svc_princ, flags=['-k'])

        cls._init_env()

        cls.USER_PRINC = cls.realm.user_princ.split('@')[0].encode("UTF-8")
        cls.ADMIN_PRINC = cls.realm.admin_princ.split('@')[0].encode("UTF-8")

    @classmethod
    def _init_env(cls):
        cls._saved_env = copy.deepcopy(os.environ)
        for k, v in cls.realm.env.items():
            os.environ[k] = v

    @classmethod
    def _restore_env(cls):
        for k in copy.deepcopy(os.environ):
            if k in cls._saved_env:
                os.environ[k] = cls._saved_env[k]
            else:
                del os.environ[k]

        cls._saved_env = None

    @classmethod
    def tearDownClass(cls):
        super(_GSSAPIKerberosTestCase, cls).tearDownClass()
        cls._restore_env()


def _perms_cycle(elem, rest, old_d):
    if elem is None:
        name_str = "with_params_"
        true_keys = [k for (k, v) in old_d.items() if v]
        if not true_keys:
            name_str += 'none'
        else:
            name_str += '_'.join(true_keys)

        return [(name_str, old_d)]
    else:
        if len(rest) > 0:
            next_elem = rest.pop()
        else:
            next_elem = None

        res = []
        for v in (True, False):
            new_d = copy.deepcopy(old_d)
            new_d[elem] = v
            res.extend(_perms_cycle(next_elem, copy.deepcopy(rest), new_d))

        return res


def exist_perms(**kwargs):
    all_elems = list(kwargs.keys())
    curr_elems = copy.deepcopy(all_elems)

    perms = _perms_cycle(curr_elems.pop(), curr_elems, {})
    res = []
    for name_str, perm in perms:
        args = dict([(k, v) for (k, v) in kwargs.items() if perm[k]])
        res.append((name_str, args))

    return parameterized.expand(res)


def true_false_perms(*all_elems_tuple):
    all_elems = list(all_elems_tuple)
    curr_elems = copy.deepcopy(all_elems)

    perms = _perms_cycle(curr_elems.pop(), curr_elems, {})
    return parameterized.expand(perms)


# NB(directxman12): MIT Kerberos completely ignores input TTLs for
#                   credentials.  I suspect this is because the TTL
#                   is actually set when kinit is called.
# NB(directxman12): the above note used to be wonderfully sarcastic
class CredsTestCase(_GSSAPIKerberosTestCase):
    def setUp(self):
        super(CredsTestCase, self).setUp()
        self.name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)

    @exist_perms(lifetime=30, desired_mechs=[gb.MechType.kerberos],
                 usage='both')
    def test_acquire_by_init(self, str_name, kwargs):
        creds = gsscreds.Credentials(desired_name=self.name, **kwargs)

        creds.lifetime.should_be_an_integer()

        del creds

    @exist_perms(lifetime=30, desired_mechs=[gb.MechType.kerberos],
                 usage='both')
    def test_acquire_by_method(self, str_name, kwargs):
        cred_resp = gsscreds.Credentials.acquire(desired_name=self.name,
                                                 **kwargs)

        cred_resp.shouldnt_be_none()

        (creds, actual_mechs, ttl) = cred_resp

        creds.shouldnt_be_none()
        creds.should_be_a(gsscreds.Credentials)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        ttl.should_be_an_integer()

        del creds

    def test_create_from_other(self):
        self.skipTest("Not Yet Implemented")

    @true_false_perms('name', 'lifetime', 'usage', 'mechs')
    def test_inquire(self, str_name, kwargs):
        creds = gsscreds.Credentials(desired_name=self.name)
        resp = creds.inquire(**kwargs)

        if kwargs['name']:
            resp.name.should_be(self.name)
        else:
            resp.name.should_be_none()

        if kwargs['lifetime']:
            resp.lifetime.should_be_an_integer()
        else:
            resp.lifetime.should_be_none()

        if kwargs['usage']:
            resp.usage.should_be('both')
        else:
            resp.usage.should_be_none()

        if kwargs['mechs']:
            resp.mechs.shouldnt_be_empty()
            resp.mechs.should_include(gb.MechType.kerberos)
        else:
            resp.mechs.should_be_none()

    @true_false_perms('name', 'init_lifetime', 'accept_lifetime', 'usage')
    def test_inquire_by_mech(self, str_name, kwargs):
        creds = gsscreds.Credentials(desired_name=self.name)
        resp = creds.inquire_by_mech(mech=gb.MechType.kerberos, **kwargs)

        if kwargs['name']:
            resp.name.should_be(self.name)
        else:
            resp.name.should_be_none()

        if kwargs['init_lifetime']:
            resp.init_lifetime.should_be_an_integer()
        else:
            resp.init_lifetime.should_be_none()

        if kwargs['accept_lifetime']:
            resp.accept_lifetime.should_be_an_integer()
        else:
            resp.accept_lifetime.should_be_none()

        if kwargs['usage']:
            resp.usage.should_be('both')
        else:
            resp.usage.should_be_none()

    def test_add(self):
        self.skipTest("Not Yet Implemented")

    def test_export(self):
        if import_gssapi_extension('cred_imp_exp') is None:
            self.skipTest("The credentials import-export GSSAPI "
                          "extension is not supported by your "
                          "GSSAPI implementation")
        else:
            creds = gsscreds.Credentials(desired_name=self.name)
            token = creds.export()
            token.should_be(bytes)

    def test_import_by_init(self):
        if import_gssapi_extension('cred_imp_exp') is None:
            self.skipTest("The credentials import-export GSSAPI "
                          "extension is not supported by your "
                          "GSSAPI implementation")
        else:
            creds = gsscreds.Credentials(desired_name=self.name)
            token = creds.export()
            imported_creds = gsscreds.Credentials(token=token)

            imported_creds.lifetime.should_be(creds.lifetime)
            imported_creds.name.should_be(creds.name)

    def test_pickle_unpickle(self):
        if import_gssapi_extension('cred_imp_exp') is None:
            self.skipTest("The credentials import-export GSSAPI "
                          "extension is not supported by your "
                          "GSSAPI implementation")
        else:
            creds = gsscreds.Credentials(desired_name=self.name)
            pickled_creds = pickle.dumps(creds)
            unpickled_creds = pickle.loads(pickled_creds)

            unpickled_creds.lifetime.should_be(creds.lifetime)
            unpickled_creds.name.should_be(creds.name)

    @exist_perms(lifetime=30, desired_mechs=[gb.MechType.kerberos],
                 usage='initiate')
    def test_impersonate(self, str_name, kwargs):
        if import_gssapi_extension('s4u') is None:
            self.skipTest("The S4U GSSAPI extension is not supported "
                          "by your GSSAPI implementation")
        else:
            target_name = gssnames.Name(TARGET_SERVICE_NAME,
                                        gb.NameType.hostbased_service)
            # TODO(directxman12): make this use the high-level SecurityContext
            client_ctx_resp = gb.initSecContext(target_name)
            client_token = client_ctx_resp[3]
            del client_ctx_resp  # free everything but the token

            server_name = self.name
            server_creds = gsscreds.Credentials(desired_name=server_name,
                                                usage='both')
            server_ctx_resp = gb.acceptSecContext(client_token,
                                                  acceptor_cred=server_creds)

            imp_creds = server_creds.impersonate(server_ctx_resp[1], **kwargs)

            imp_creds.shouldnt_be_none()
            imp_creds.should_be_a(gsscreds.Credentials)

    def test_add_with_impersonate(self):
        if import_gssapi_extension('s4u') is None:
            self.skipTest("The S4U GSSAPI extension is not supported "
                          "by your GSSAPI implementation")
        else:
            self.skipTest("Not Yet Implemented")


class NamesTestCase(_GSSAPIKerberosTestCase):
    def test_create_from_other(self):
        self.skipTest("Not Yet Implemented")

    def test_create_from_name_no_type(self):
        name = gssnames.Name(SERVICE_PRINCIPAL)

        name.shouldnt_be_none()

    def test_create_from_name_and_type(self):
        name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)

        name.shouldnt_be_none()
        name.name_type.should_be(gb.NameType.principal)

    def test_create_from_token(self):
        name1 = gssnames.Name(TARGET_SERVICE_NAME,
                              gb.NameType.hostbased_service)
        exported_name = name1.canonicalize(gb.MechType.kerberos).export()
        name2 = gssnames.Name(token=exported_name)

        name2.shouldnt_be_none()
        name2.name_type.should_be(gb.NameType.principal)

    def test_to_str(self):
        name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)

        name_str = str(name)

        name_str.should_be_a(str)
        if sys.version_info[0] == 2:
            target_val = SERVICE_PRINCIPAL
        else:
            target_val = SERVICE_PRINCIPAL.encode(gssnames.STRING_ENCODING)

        name_str.should_be(target_val)

    def test_to_unicode(self):
        name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)

        name_str = six.text_type(name)

        name_str.should_be_a(six.text_type)
        name_str.should_be(SERVICE_PRINCIPAL.encode(gssnames.STRING_ENCODING))

    def test_to_bytes(self):
        name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)

        # NB(directxman12): bytes only calles __bytes__ on Python 3+
        name_bytes = name.__bytes__()

        name_bytes.should_be_a(bytes)
        name_bytes.should_be(SERVICE_PRINCIPAL)

    def test_compare(self):
        name1 = gssnames.Name(SERVICE_PRINCIPAL)
        name2 = gssnames.Name(SERVICE_PRINCIPAL)
        name3 = gssnames.Name(TARGET_SERVICE_NAME,
                              gb.NameType.hostbased_service)

        name1.should_be(name2)
        name1.shouldnt_be(name3)

    def test_canoncialize_and_export(self):
        name = gssnames.Name(SERVICE_PRINCIPAL, gb.NameType.principal)
        canonical_name = name.canonicalize(gb.MechType.kerberos)
        exported_name = canonical_name.export()

        exported_name.should_be_a(bytes)

    def test_canonicalize(self):
        name = gssnames.Name(TARGET_SERVICE_NAME,
                             gb.NameType.hostbased_service)

        canonicalized_name = name.canonicalize(gb.MechType.kerberos)
        canonicalized_name.should_be_a(gssnames.Name)
        str(canonicalized_name).should_be(SERVICE_PRINCIPAL + '@')

    def test_copy(self):
        name1 = gssnames.Name(SERVICE_PRINCIPAL)
        name2 = copy.copy(name1)

        name1.should_be(name2)


class SecurityContextTestCase(_GSSAPIKerberosTestCase):
    def setUp(self):
        super(SecurityContextTestCase, self).setUp()
        self.client_name = gssnames.Name(self.USER_PRINC)
        self.client_creds = gsscreds.Credentials(desired_name=None,
                                                 usage='initiate')

        self.target_name = gssnames.Name(TARGET_SERVICE_NAME,
                                         gb.NameType.hostbased_service)

        self.server_name = gssnames.Name(SERVICE_PRINCIPAL)
        self.server_creds = gsscreds.Credentials(desired_name=self.server_name,
                                                 usage='accept')

    def _create_client_ctx(self, **kwargs):
        return gssctx.SecurityContext(name=self.target_name, **kwargs)

    def test_process_token(self):
        self.skipTest("Not Yet Implemented")

    def test_create_from_other(self):
        self.skipTest("Not Yet Implemented")

    @exist_perms(desired_lifetime=30, flags=[],
                 mech_type=gb.MechType.kerberos,
                 channel_bindings=None)
    def test_create_new_init(self, str_name, kwargs):
        client_ctx = gssctx.SecurityContext(name=self.target_name,
                                            creds=self.client_creds,
                                            **kwargs)
        client_ctx.usage.should_be('initiate')

        client_ctx = self._create_client_ctx(**kwargs)
        client_ctx.usage.should_be('initiate')

    def test_create_new_accept(self):
        server_ctx = gssctx.SecurityContext(creds=self.server_creds)
        server_ctx.usage.should_be('accept')

    def test_init_throws_error_on_invalid_args(self):
        def create_sec_context():
            gssctx.SecurityContext(usage='accept', name=self.target_name)

        create_sec_context.should_raise(TypeError)

    def _create_completed_contexts(self):
        client_ctx = self._create_client_ctx(desired_lifetime=400)

        client_token = client_ctx.step()
        client_token.should_be_a(bytes)

        server_ctx = gssctx.SecurityContext(creds=self.server_creds)
        server_token = server_ctx.step(client_token)
        server_token.should_be_a(bytes)

        client_ctx.step(server_token)

        return (client_ctx, server_ctx)

    def test_initiate_accept_steps(self):
        client_ctx, server_ctx = self._create_completed_contexts()

        server_ctx.lifetime.should_be_at_most(400)
        server_ctx.initiator_name.should_be(client_ctx.initiator_name)
        server_ctx.mech_type.should_be_a(gb.OID)
        server_ctx.actual_flags.should_be_a(gb.IntEnumFlagSet)
        server_ctx.locally_initiated.should_be_false()
        server_ctx.complete.should_be_true()

        client_ctx.lifetime.should_be_at_most(400)
        client_ctx.target_name.should_be(self.target_name)
        client_ctx.mech_type.should_be_a(gb.OID)
        client_ctx.actual_flags.should_be_a(gb.IntEnumFlagSet)
        client_ctx.locally_initiated.should_be_true()
        client_ctx.complete.should_be_true()

    def test_export_create_from_token(self):
        client_ctx, server_ctx = self._create_completed_contexts()
        token = client_ctx.export()

        token.should_be_a(bytes)

        imported_ctx = gssctx.SecurityContext(token=token)

        imported_ctx.usage.should_be('initiate')
        imported_ctx.target_name.should_be(self.target_name)

    def test_pickle_unpickle(self):
        client_ctx, server_ctx = self._create_completed_contexts()
        pickled_ctx = pickle.dumps(client_ctx)

        unpickled_ctx = pickle.loads(pickled_ctx)

        unpickled_ctx.should_be_a(gssctx.SecurityContext)
        unpickled_ctx.usage.should_be('initiate')
        unpickled_ctx.target_name.should_be(self.target_name)

    def test_wrap_unwrap(self):
        client_ctx, server_ctx = self._create_completed_contexts()

        wrapped_message = client_ctx.wrap(b'test message')
        wrapped_message.should_be_a(bytes)

        unwrapped_message = server_ctx.unwrap(wrapped_message)
        unwrapped_message.should_be_a(bytes)
        unwrapped_message.should_be(b'test message')

    def test_get_wrap_size_limit(self):
        client_ctx, server_ctx = self._create_completed_contexts()

        with_conf = client_ctx.get_wrap_size_limit(100)
        without_conf = client_ctx.get_wrap_size_limit(100, encrypted=True)

        with_conf.should_be_an_integer()
        without_conf.should_be_an_integer()

        with_conf.should_be_at_most(100)
        without_conf.should_be_at_most(100)

    def test_get_mic(self):
        client_ctx, server_ctx = self._create_completed_contexts()
        mic_token = client_ctx.get_mic(b'some message')

        mic_token.should_be_a(bytes)
        mic_token.shouldnt_be_empty()

    def test_verify_mic_raise(self):
        client_ctx, server_ctx = self._create_completed_contexts()
        mic_token = client_ctx.get_mic(b'some message')

        server_ctx.verify_mic(b'some message', mic_token)

        server_ctx.verify_mic.should_raise(gb.GSSError,
                                           b'other message', mic_token)

    def test_verify_mic_bool(self):
        client_ctx, server_ctx = self._create_completed_contexts()
        mic_token = client_ctx.get_mic(b'some message')

        server_ctx.verify_mic(b'some message',
                              mic_token,
                              return_bool=True).valid.should_be_true()
        server_ctx.verify_mic(b'other message',
                              mic_token,
                              return_bool=True).valid.should_be_false()
