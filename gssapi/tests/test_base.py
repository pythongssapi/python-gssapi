import collections
import copy
import os
import socket

import should_be.all  # noqa

import gssapi.raw as gb
from gssapi.tests import k5test as kt


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


class TestBaseUtilities(_GSSAPIKerberosTestCase):
    def test_indicate_mechs(self):
        mechs = gb.indicate_mechs()

        mechs.shouldnt_be_none()
        mechs.should_be_a(list)
        mechs.shouldnt_be_empty()

        mechs.should_include(gb.MechType.kerberos)

    def test_import_name(self):
        imported_name = gb.import_name(TARGET_SERVICE_NAME)

        imported_name.shouldnt_be_none()
        imported_name.should_be_a(gb.Name)

        gb.release_name(imported_name)

    def test_canonicalize_export_name(self):
        imported_name = gb.import_name(self.ADMIN_PRINC,
                                       gb.NameType.kerberos_principal)

        canonicalized_name = gb.canonicalize_name(imported_name,
                                                  gb.MechType.kerberos)

        canonicalized_name.shouldnt_be_none()
        canonicalized_name.should_be_a(gb.Name)

        exported_name = gb.export_name(canonicalized_name)

        exported_name.shouldnt_be_none()
        exported_name.should_be_a(bytes)
        exported_name.shouldnt_be_empty()

    def test_duplicate_name(self):
        orig_name = gb.import_name(TARGET_SERVICE_NAME)
        new_name = gb.duplicate_name(orig_name)

        new_name.shouldnt_be_none()
        gb.compare_name(orig_name, new_name).should_be_true()

    def test_display_name(self):
        imported_name = gb.import_name(TARGET_SERVICE_NAME,
                                       gb.NameType.hostbased_service)
        displ_resp = gb.display_name(imported_name)

        displ_resp.shouldnt_be_none()

        (displayed_name, out_type) = displ_resp

        displayed_name.shouldnt_be_none()
        displayed_name.should_be_a(bytes)
        displayed_name.should_be(TARGET_SERVICE_NAME)

        out_type.shouldnt_be_none()
        out_type.should_be(gb.NameType.hostbased_service)

    def test_compare_name(self):
        service_name1 = gb.import_name(TARGET_SERVICE_NAME)
        service_name2 = gb.import_name(TARGET_SERVICE_NAME)
        init_name = gb.import_name(self.ADMIN_PRINC,
                                   gb.NameType.kerberos_principal)

        gb.compare_name(service_name1, service_name2).should_be_true()
        gb.compare_name(service_name2, service_name1).should_be_true()

        gb.compare_name(service_name1, init_name).should_be_false()

        gb.release_name(service_name1)
        gb.release_name(service_name2)
        gb.release_name(init_name)

    def test_display_status(self):
        status_resp = gb._display_status(0, False)
        status_resp.shouldnt_be_none()

        (status, ctx, cont) = status_resp

        status.should_be_a(bytes)
        status.shouldnt_be_empty()

        ctx.should_be_an_integer()

        cont.should_be_a(bool)
        cont.should_be_false()

    def test_acquire_creds(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        cred_resp = gb.acquire_cred(name)
        cred_resp.shouldnt_be_none()

        (creds, actual_mechs, ttl) = cred_resp

        creds.shouldnt_be_none()
        creds.should_be_a(gb.Creds)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        ttl.should_be_an_integer()

        gb.release_name(name)
        gb.release_cred(creds)

    def test_context_time(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(target_name)

        client_token1 = ctx_resp[3]
        client_ctx = ctx_resp[0]
        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(client_token1,
                                            acceptor_cred=server_creds)
        server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(target_name,
                                           context=client_ctx,
                                           input_token=server_tok)
        ctx = client_resp2[0]

        ttl = gb.context_time(ctx)

        ttl.should_be_an_integer()
        ttl.should_be_greater_than(0)

    def test_inquire_context(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(target_name)

        client_token1 = ctx_resp[3]
        client_ctx = ctx_resp[0]
        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(client_token1,
                                            acceptor_cred=server_creds)
        server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(target_name,
                                           context=client_ctx,
                                           input_token=server_tok)
        ctx = client_resp2[0]

        inq_resp = gb.inquire_context(ctx)
        inq_resp.shouldnt_be_none()

        (src_name, target_name, ttl, mech_type,
         flags, local_est, is_open) = inq_resp

        src_name.shouldnt_be_none()
        src_name.should_be_a(gb.Name)

        target_name.shouldnt_be_none()
        target_name.should_be_a(gb.Name)

        ttl.should_be_an_integer()

        mech_type.shouldnt_be_none()
        mech_type.should_be(gb.MechType.kerberos)

        flags.shouldnt_be_none()
        flags.should_be_a(collections.Set)
        flags.shouldnt_be_empty()

        local_est.should_be_a(bool)
        local_est.should_be_true()

        is_open.should_be_a(bool)
        is_open.should_be_true()

    def test_process_context_token(self):
        # TODO(sross): figure out how to write a test for this
        pass

    def test_add_cred_impersonate_name(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        client_ctx_resp = gb.init_sec_context(target_name)
        client_token = client_ctx_resp[3]
        del client_ctx_resp  # free all the things (except the token)!

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name, cred_usage='both')[0]
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_cred=server_creds)

        input_creds = gb.Creds()
        imp_resp = gb.add_cred_impersonate_name(input_creds,
                                                server_creds,
                                                server_ctx_resp[1],
                                                gb.MechType.kerberos)

        imp_resp.shouldnt_be_none()

        new_creds, actual_mechs, output_init_ttl, output_accept_ttl = imp_resp

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_init_ttl.should_be_a(int)
        output_accept_ttl.should_be_a(int)

        new_creds.should_be_a(gb.Creds)

    def test_acquire_creds_impersonate_name(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        client_ctx_resp = gb.init_sec_context(target_name)
        client_token = client_ctx_resp[3]
        del client_ctx_resp  # free all the things (except the token)!

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name, cred_usage='both')[0]
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_cred=server_creds)

        imp_resp = gb.acquire_cred_impersonate_name(server_creds,
                                                    server_ctx_resp[1])

        imp_resp.shouldnt_be_none()

        imp_creds, actual_mechs, output_ttl = imp_resp

        imp_creds.shouldnt_be_none()
        imp_creds.should_be_a(gb.Creds)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_ttl.should_be_a(int)
        # no need to explicitly release any more -- we can just rely on
        # __dealloc__ (b/c cython)

    def test_store_cred_acquire_cred(self):
        self.skipTest("Not Yet Implemented")

    def test_store_cred_into_acquire_cred(self):
        CCACHE = 'FILE:{tmpdir}/other_ccache'.format(tmpdir=self.realm.tmpdir)
        KT = '{tmpdir}/other_keytab'.format(tmpdir=self.realm.tmpdir)
        store = {b'ccache': CCACHE.encode('UTF-8'),
                 b'keytab': KT.encode('UTF-8')}

        princ_name = 'service/cs@' + self.realm.realm
        self.realm.addprinc(princ_name)
        self.realm.extract_keytab(princ_name, KT)
        self.realm.kinit(princ_name, None, ['-k', '-t', KT])

        initial_creds = gb.acquire_cred(None, cred_usage='initiate').creds

        # NB(sross): overwrite because the ccache doesn't exist yet
        store_res = gb.store_cred_into(store, initial_creds, overwrite=True)

        store_res.mech_types.shouldnt_be_none()
        store_res.usage.should_be('initiate')

        name = gb.import_name(princ_name.encode('UTF-8'))
        retrieve_res = gb.acquire_cred_from(store, name)

        retrieve_res.shouldnt_be_none()
        retrieve_res.creds.shouldnt_be_none()
        retrieve_res.creds.should_be_a(gb.Creds)

        retrieve_res.mechs.shouldnt_be_empty()
        retrieve_res.mechs.should_include(gb.MechType.kerberos)

        retrieve_res.lifetime.should_be_an_integer()

    def test_inquire_creds(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        cred = gb.acquire_cred(name).creds

        inq_resp = gb.inquire_cred(cred)

        inq_resp.shouldnt_be_none()

        inq_resp.name.should_be_a(gb.Name)
        assert gb.compare_name(name, inq_resp.name)

        inq_resp.lifetime.should_be_an_integer()

        inq_resp.usage.should_be('both')

        inq_resp.mechs.shouldnt_be_empty()
        inq_resp.mechs.should_include(gb.MechType.kerberos)

    def test_create_oid_from_bytes(self):
        kerberos_bytes = gb.MechType.kerberos.__bytes__()
        new_oid = gb.OID(elements=kerberos_bytes)

        new_oid.should_be(gb.MechType.kerberos)

        del new_oid  # make sure we can dealloc

    def test_error_dispatch(self):
        err_code1 = gb.ParameterReadError.CALLING_CODE
        err_code2 = gb.BadNameError.ROUTINE_CODE
        err = gb.GSSError(err_code1 | err_code2, 0)

        err.should_be_a(gb.NameReadError)
        err.maj_code.should_be(err_code1 | err_code2)


class TestInitContext(_GSSAPIKerberosTestCase):
    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)

    def tearDown(self):
        gb.release_name(self.target_name)

    def test_basic_init_default_ctx(self):
        ctx_resp = gb.init_sec_context(self.target_name)
        ctx_resp.shouldnt_be_none()

        (ctx, out_mech_type,
         out_req_flags, out_token, out_ttl, cont_needed) = ctx_resp

        ctx.shouldnt_be_none()
        ctx.should_be_a(gb.SecurityContext)

        out_mech_type.should_be(gb.MechType.kerberos)

        out_req_flags.should_be_a(collections.Set)
        out_req_flags.should_be_at_least_length(2)

        out_token.shouldnt_be_empty()

        out_ttl.should_be_greater_than(0)

        cont_needed.should_be_a(bool)

        gb.delete_sec_context(ctx)


class TestAcceptContext(_GSSAPIKerberosTestCase):

    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name)

        self.client_token = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.client_ctx.shouldnt_be_none()

        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]

        self.server_ctx = None

    def tearDown(self):
        gb.release_name(self.target_name)
        gb.release_name(self.server_name)
        gb.release_cred(self.server_creds)
        gb.delete_sec_context(self.client_ctx)

        if self.server_ctx is not None:
            gb.delete_sec_context(self.server_ctx)

    def test_basic_accept_context(self):
        server_resp = gb.accept_sec_context(self.client_token,
                                            acceptor_cred=self.server_creds)
        server_resp.shouldnt_be_none()

        (self.server_ctx, name, mech_type, out_token,
         out_req_flags, out_ttl, delegated_cred, cont_needed) = server_resp

        self.server_ctx.shouldnt_be_none()
        self.server_ctx.should_be_a(gb.SecurityContext)

        name.shouldnt_be_none()
        name.should_be_a(gb.Name)

        mech_type.should_be(gb.MechType.kerberos)

        out_token.shouldnt_be_empty()

        out_req_flags.should_be_a(collections.Set)
        out_req_flags.should_be_at_least_length(2)

        out_ttl.should_be_greater_than(0)

        if delegated_cred is not None:
            delegated_cred.should_be_a(gb.Creds)

        cont_needed.should_be_a(bool)


class TestWrapUnwrap(_GSSAPIKerberosTestCase):
    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name)

        self.client_token1 = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]
        server_resp = gb.accept_sec_context(self.client_token1,
                                            acceptor_cred=self.server_creds)
        self.server_ctx = server_resp[0]
        self.server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(self.target_name,
                                           context=self.client_ctx,
                                           input_token=self.server_tok)
        self.client_token2 = client_resp2[3]
        self.client_ctx = client_resp2[0]

    def tearDown(self):
        gb.release_name(self.target_name)
        gb.release_name(self.server_name)
        gb.release_cred(self.server_creds)
        gb.delete_sec_context(self.client_ctx)
        gb.delete_sec_context(self.server_ctx)

    def test_import_export_sec_context(self):
        tok = gb.export_sec_context(self.client_ctx)

        tok.shouldnt_be_none()
        tok.should_be_a(bytes)
        tok.shouldnt_be_empty()

        imported_ctx = gb.import_sec_context(tok)
        imported_ctx.shouldnt_be_none()
        imported_ctx.should_be_a(gb.SecurityContext)

        self.client_ctx = imported_ctx  # ensure that it gets deleted

    def test_get_mic(self):
        mic_token = gb.get_mic(self.client_ctx, b"some message")

        mic_token.shouldnt_be_none()
        mic_token.should_be_a(bytes)
        mic_token.shouldnt_be_empty()

    def test_basic_verify_mic(self):
        mic_token = gb.get_mic(self.client_ctx, b"some message")

        qop_used = gb.verify_mic(self.server_ctx, b"some message", mic_token)

        qop_used.should_be_an_integer()

        # test a bad MIC
        gb.verify_mic.should_raise(gb.GSSError, self.server_ctx,
                                   b"some other message", b"some invalid mic")

    def test_wrap_size_limit(self):
        with_conf = gb.wrap_size_limit(self.client_ctx, 100)
        without_conf = gb.wrap_size_limit(self.client_ctx, 100,
                                          confidential=False)

        with_conf.should_be_an_integer()
        without_conf.should_be_an_integer()

        without_conf.should_be_less_than(100)
        with_conf.should_be_less_than(100)

    def test_basic_wrap_unwrap(self):
        (wrapped_message, conf) = gb.wrap(self.client_ctx, b'test message')

        conf.should_be_a(bool)
        conf.should_be_true()

        wrapped_message.should_be_a(bytes)
        wrapped_message.shouldnt_be_empty()
        wrapped_message.should_be_longer_than('test message')

        (unwrapped_message, conf, qop) = gb.unwrap(self.server_ctx,
                                                   wrapped_message)
        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_an_integer()
        qop.should_be_at_least(0)

        unwrapped_message.should_be_a(bytes)
        unwrapped_message.shouldnt_be_empty()
        unwrapped_message.should_be(b'test message')
