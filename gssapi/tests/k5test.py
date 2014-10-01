# Copyright (C) 2014 by Solly Ross
# Copyright (C) 2010 by the Massachusetts Institute of Technology.
# All rights reserved.

# Export of this software from the United States of America may
#   require a specific license from the United States Government.
#   It is the responsibility of any person or organization contemplating
#   export to obtain such a license before exporting.
#
# WITHIN THAT CONSTRAINT, permission to use, copy, modify, and
# distribute this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both that copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of M.I.T. not be used in advertising or publicity pertaining
# to distribution of the software without specific, written prior
# permission.  Furthermore if you modify this software you must label
# your software as modified software and not distribute it in such a
# fashion that it might be confused with the original M.I.T. software.
# M.I.T. makes no representations about the suitability of
# this software for any purpose.  It is provided "as is" without express
# or implied warranty.

# Changes from original: modified to work with Python's unittest
from __future__ import print_function

import copy
import os
import signal
import socket
import string
import subprocess
import tempfile
import unittest

import six


def _cfg_merge(cfg1, cfg2):
    if not cfg2:
        return cfg1
    if not cfg1:
        return cfg2
    result = copy.deepcopy(cfg1)
    for key, value2 in cfg2.items():
        if value2 is None or key not in result:
            result[key] = copy.deepcopy(value2)
        else:
            value1 = result[key]
            if isinstance(value1, dict):
                if not isinstance(value2, dict):
                    raise TypeError("value at key '{key}' not dict: "
                                    "{type}".format(key=key,
                                                    type=type(value2)))
                result[key] = _cfg_merge(value1, value2)
            else:
                result[key] = copy.deepcopy(value2)
    return result


_default_krb5_conf = {
    'libdefaults': {
        'default_realm': '$realm',
        'dns_lookup_kdc': 'false'},
    'realms': {
        '$realm': {
            'kdc': '$hostname:$port0',
            'admin_server': '$hostname:$port1',
            'kpasswd_server': '$hostname:$port2'}}}


_default_kdc_conf = {
    'realms': {
        '$realm': {
            'database_module': 'db',
            'iprop_port': '$port4',
            'key_stash_file': '$tmpdir/stash',
            'acl_file': '$tmpdir/acl',
            'dictfile': '$tmpdir/dictfile',
            'kadmind_port': '$port1',
            'kpasswd_port': '$port2',
            'kdc_ports': '$port0',
            'kdc_tcp_ports': '$port0',
            'database_name': '$tmpdir/db'}},
    'dbmodules': {
        'db': {'db_library': 'db2', 'database_name': '$tmpdir/db'}},
    'logging': {
        'admin_server': 'FILE:$tmpdir/kadmind5.log',
        'kdc': 'FILE:$tmpdir/kdc.log',
        'default': 'FILE:$tmpdir/others.log'}}


class K5Realm(object):
    """An object representing a functional krb5 test realm."""
    def __init__(self, realm='KRBTEST.COM', portbase=61000,
                 krb5_conf=None, kdc_conf=None, create_kdb=True,
                 krbtgt_keysalt=None, create_user=True, get_creds=True,
                 create_host=True, start_kdc=True, start_kadmind=False,
                 **paths):

        self.tmpdir = tempfile.mkdtemp(suffix='-krbtest')

        self.realm = realm
        self.portbase = portbase
        self.user_princ = 'user@' + self.realm
        self.admin_princ = 'user/admin@' + self.realm
        self.host_princ = 'host/%s@%s' % (self.hostname, self.realm)
        self.nfs_princ = 'nfs/%s@%s' % (self.hostname, self.realm)
        self.krbtgt_princ = 'krbtgt/%s@%s' % (self.realm, self.realm)
        self.keytab = os.path.join(self.tmpdir, 'keytab')
        self.client_keytab = os.path.join(self.tmpdir, 'client_keytab')
        self.ccache = os.path.join(self.tmpdir, 'ccache')
        self.kadmin_ccache = os.path.join(self.tmpdir, 'kadmin_ccache')
        self._krb5_conf = _cfg_merge(_default_krb5_conf, krb5_conf)
        self._kdc_conf = _cfg_merge(_default_kdc_conf, kdc_conf)
        self._kdc_proc = None
        self._kadmind_proc = None
        krb5_conf_path = os.path.join(self.tmpdir, 'krb5.conf')
        kdc_conf_path = os.path.join(self.tmpdir, 'kdc.conf')
        self.env = self._make_env(krb5_conf_path, kdc_conf_path)

        self._daemons = []

        self._init_paths(**paths)

        self._devnull = open(os.devnull, 'r')

        self._create_conf(self._krb5_conf, krb5_conf_path)
        self._create_conf(self._kdc_conf, kdc_conf_path)
        self._create_acl()
        self._create_dictfile()

        if create_kdb:
            self.create_kdb()
        if krbtgt_keysalt and create_kdb:
            self.run_kadminl('cpw -randkey -e %s %s' %
                             (krbtgt_keysalt, self.krbtgt_princ))
        if create_user and create_kdb:
            self.addprinc(self.user_princ, self.password('user'))
            self.addprinc(self.admin_princ, self.password('admin'))
        if create_host and create_kdb:
            self.addprinc(self.host_princ)
            self.extract_keytab(self.host_princ, self.keytab)
        if start_kdc and create_kdb:
            self.start_kdc()
        if start_kadmind and create_kdb:
            self.start_kadmind()
        if get_creds and create_kdb and create_user and start_kdc:
            self.kinit(self.user_princ, self.password('user'))
            self.klist()

    def _init_paths(self, **paths):
        self.kdb5_util = paths.get('kdb5_util', '/usr/sbin/kdb5_util')
        self.krb5kdc = paths.get('krb5kdc', '/usr/sbin/krb5kdc')
        self.kadmin_local = paths.get('kadmin_local', '/usr/sbin/kadmin.local')
        self.kprop = paths.get('kprop', '/usr/sbin/kprop')
        self.kadmind = paths.get('kadmind', '/usr/sbin/kadmind')

        self._kinit = paths.get('kinit', '/usr/bin/kinit')
        self._klist = paths.get('klist', '/usr/bin/klist')

    def _create_conf(self, profile, filename):
        with open(filename, 'w') as conf_file:
            for section, contents in profile.items():
                conf_file.write('[%s]\n' % section)
                self._write_cfg_section(conf_file, contents, 1)

    def _write_cfg_section(self, conf_file, contents, indent_level):
        indent = '\t' * indent_level
        for name, value in contents.items():
            name = self._subst_cfg_value(name)
            if isinstance(value, dict):
                # A dictionary value yields a list subsection.
                conf_file.write('%s%s = {\n' % (indent, name))
                self._write_cfg_section(conf_file, value, indent_level + 1)
                conf_file.write('%s}\n' % indent)
            elif isinstance(value, list):
                # A list value yields multiple values for the same name.
                for item in value:
                    item = self._subst_cfg_value(item)
                    conf_file.write('%s%s = %s\n' % (indent, name, item))
            elif isinstance(value, six.string_types):
                # A string value yields a straightforward variable setting.
                value = self._subst_cfg_value(value)
                conf_file.write('%s%s = %s\n' % (indent, name, value))
            elif value is not None:
                raise TypeError("Unknown config type at key '{key}': "
                                "{type}".format(key=name, type=type(value)))

    @property
    def hostname(self):
        return socket.getfqdn()

    def _subst_cfg_value(self, value):
        template = string.Template(value)
        return template.substitute(realm=self.realm,
                                   tmpdir=self.tmpdir,
                                   hostname=self.hostname,
                                   port0=self.portbase,
                                   port1=self.portbase + 1,
                                   port2=self.portbase + 2,
                                   port3=self.portbase + 3,
                                   port4=self.portbase + 4,
                                   port5=self.portbase + 5,
                                   port6=self.portbase + 6,
                                   port7=self.portbase + 7,
                                   port8=self.portbase + 8,
                                   port9=self.portbase + 9)

    def _create_acl(self):
        filename = os.path.join(self.tmpdir, 'acl')
        with open(filename, 'w') as acl_file:
            acl_file.write('%s *\n' % self.admin_princ)
            acl_file.write('kiprop/%s@%s p\n' % (self.hostname, self.realm))

    def _create_dictfile(self):
        filename = os.path.join(self.tmpdir, 'dictfile')
        with open(filename, 'w') as dict_file:
            dict_file.write('weak_password\n')

    def _make_env(self, krb5_conf_path, kdc_conf_path):
        env = {}
        env['KRB5_CONFIG'] = krb5_conf_path
        env['KRB5_KDC_PROFILE'] = kdc_conf_path or os.devnull
        env['KRB5CCNAME'] = self.ccache
        env['KRB5_KTNAME'] = self.keytab
        env['KRB5_CLIENT_KTNAME'] = self.client_keytab
        env['KRB5RCACHEDIR'] = self.tmpdir
        env['KPROPD_PORT'] = six.text_type(self.kprop_port())
        env['KPROP_PORT'] = six.text_type(self.kprop_port())
        return env

    def run(self, args, env=None, input=None, expected_code=0):
        if env is None:
            env = self.env

        if input:
            infile = subprocess.PIPE
        else:
            infile = self._devnull

        proc = subprocess.Popen(args, stdin=infile, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, env=env)
        if input:
            inbytes = input.encode()
        else:
            inbytes = None
        (outdata, blank_errdata) = proc.communicate(inbytes)
        code = proc.returncode
        cmd = ' '.join(args)
        outstr = outdata.decode()
        print('[OUTPUT FROM `{args}`]\n{output}\n'.format(args=cmd,
                                                          output=outstr))
        if code != expected_code:
            raise Exception("Unexpected return code "
                            "for command `{args}`: {code}".format(args=cmd,
                                                                  code=code))

        return outdata

    def __del__(self):
        self._devnull.close()

    def kprop_port(self):
        return self.portbase + 3

    def server_port(self):
        return self.portbase + 5

    def create_kdb(self):
        self.run([self.kdb5_util, 'create', '-W', '-s', '-P', 'master'])

    def _start_daemon(self, args, env, sentinel):
        proc = subprocess.Popen(args, stdin=self._devnull,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, env=env)
        cmd = ' '.join(args)
        while True:
            line = proc.stdout.readline().decode()
            if line == "":
                code = proc.wait()
                raise Exception('`{args}` failed to start '
                                'with code {code}'.format(args=cmd,
                                                          code=code))
            else:
                print('[OUTPUT FROM `{args}`]\n'
                      '{output}\n'.format(args=cmd, output=line))

            if sentinel in line:
                break

        self._daemons.append(proc)

        return proc

    def start_kdc(self, args=[], env=None):
        if env is None:
            env = self.env
        assert(self._kdc_proc is None)
        self._kdc_proc = self._start_daemon([self.krb5kdc, '-n'] + args, env,
                                            'starting...')

    def _stop_daemon(self, proc):
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait()
        self._daemons.remove(proc)

    def stop_kdc(self):
        assert(self._kdc_proc is not None)
        self._stop_daemon(self._kdc_proc)
        self._kdc_proc = None

    def start_kadmind(self, env=None):
        if env is None:
            env = self.env
        assert(self._kadmind_proc is None)
        dump_path = os.path.join(self.tmpdir, 'dump')
        self._kadmind_proc = self._start_daemon([self.kadmind, '-nofork', '-W',
                                                 '-p', self.kdb5_util,
                                                 '-K', self.kprop,
                                                 '-F', dump_path], env,
                                                'starting...')

    def stop_kadmind(self):
        assert(self._kadmind_proc is not None)
        self.stop_daemon(self._kadmind_proc)
        self._kadmind_proc = None

    def stop(self):
        if self._kdc_proc:
            self.stop_kdc()
        if self._kadmind_proc:
            self.stop_kadmind()

    def addprinc(self, princname, password=None):
        if password:
            self.run_kadminl('addprinc -pw %s %s' % (password, princname))
        else:
            self.run_kadminl('addprinc -randkey %s' % princname)

    def extract_keytab(self, princname, keytab):
        self.run_kadminl('ktadd -k %s -norandkey %s' % (keytab, princname))

    def kinit(self, princname, password=None, flags=[], verbose=True,
              **keywords):
        if password:
            input = password + "\n"
        else:
            input = None

        cmd = [self._kinit]
        if verbose:
            cmd.append('-V')
        cmd.extend(flags)
        cmd.append(princname)
        return self.run(cmd, input=input, **keywords)

    def klist(self, ccache=None, **keywords):
        if ccache is None:
            ccache = self.ccache
        ccachestr = ccache
        if len(ccachestr) < 2 or ':' not in ccachestr[2:]:
            ccachestr = 'FILE:' + ccachestr
        return self.run([self._klist, ccache], **keywords)

    def klist_keytab(self, keytab=None, **keywords):
        if keytab is None:
            keytab = self.keytab
        output = self.run([self._klist, '-k', keytab], **keywords)
        return output

    def run_kadminl(self, query, env=None):
        return self.run([self.kadmin_local, '-q', query], env=env)

    def password(self, name):
        """Get a weakly random password from name, consistent across calls."""
        return name + six.text_type(os.getpid())

    def prep_kadmin(self, princname=None, pw=None, flags=[]):
        if princname is None:
            princname = self.admin_princ
            pw = self.password('admin')
        return self.kinit(princname, pw,
                          flags=['-S', 'kadmin/admin',
                                 '-c', self.kadmin_ccache] + flags)

    def run_kadmin(self, query, **keywords):
        return self.run([self.kadmin, '-c', self.kadmin_ccache, '-q', query],
                        **keywords)

    def special_env(self, name, has_kdc_conf, krb5_conf=None, kdc_conf=None):
        krb5_conf_path = os.path.join(self.tmpdir, 'krb5.conf.%s' % name)
        krb5_conf = _cfg_merge(self._krb5_conf, krb5_conf)
        self._create_conf(krb5_conf, krb5_conf_path)
        if has_kdc_conf:
            kdc_conf_path = os.path.join(self.tmpdir, 'kdc.conf.%s' % name)
            kdc_conf = _cfg_merge(self._kdc_conf, kdc_conf)
            self._create_conf(kdc_conf, kdc_conf_path)
        else:
            kdc_conf_path = None
        return self._make_env(krb5_conf_path, kdc_conf_path)

    def kill_daemons(self):
        # clean up daemons
        for proc in self._daemons:
            os.kill(proc.pid, signal.SIGTERM)


class KerberosTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.realm = K5Realm()

    @classmethod
    def tearDownClass(cls):
        cls.realm.stop()
        del cls.realm
