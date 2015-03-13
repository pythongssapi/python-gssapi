#!/usr/bin/env python

# interactive console with easy access to krb5 test harness stuff

import code
import os
import sys
import copy

from gssapi.tests import k5test


READLINE_SRC = """
# python startup file
import readline
import rlcompleter
import atexit
import os

completer = rlcompleter.Completer(globals())
readline.set_completer(completer.complete)

# tab completion
readline.parse_and_bind('Control-space: complete')
# history file
histfile = os.path.join(os.environ['HOME'], '.pythonhistory')
try:
    readline.read_history_file(histfile)
except IOError:
    pass

atexit.register(readline.write_history_file, histfile)
del os, histfile, readline, rlcompleter
"""

BANNER = """GSSAPI Interactive console
Python {ver} on {platform}
Type "help", "copyright", "credits" or "license" for more information about Python.

mechansim: {mech}, realm: {realm}, user: {user}, host: {host}
(functions for controlling the realm available in `REALM`)"""


class GSSAPIConsole(code.InteractiveConsole):
    def __init__(self, use_readline=True, realm_args={}, *args, **kwargs):
        code.InteractiveConsole.__init__(self, *args, **kwargs)

        self.realm = self._create_realm(realm_args)
        self.locals['REALM'] = self.realm

        self.runsource('import gssapi')
        self.runsource('import gssapi.raw as gb')

        if use_readline:
            self._add_readline()

        if os.environ.get('LD_LIBRARY_PATH'):
            self.realm.env['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']

    def _create_realm(self):
        return None

    def _add_readline(self):
        res = self.runsource(READLINE_SRC, '<readline setup>', 'exec')


class Krb5Console(GSSAPIConsole):
    def _create_realm(self, realm_args):
        return k5test.K5Realm(**realm_args)


MECH_MAP = {'krb5': Krb5Console}


import argparse
parser = argparse.ArgumentParser(description='An interactive Python console with krb5 setup')
parser.add_argument('file', metavar='FILE', nargs='?',
                    help='a file to run', default=None)
parser.add_argument('-i', default=False, dest='force_interactive',
                    action='store_const', const=True,
                    help='Force interactive mode when running with a file')
parser.add_argument('--realm-args', default=None,
                    help='A comma-separated list of key=(true|false) values to '
                         'pass to the realm constructor')
parser.add_argument('--mech', default='krb5',
                    help='Which environment to setup up '
                         '(supports krb5 [default])')

PARSED_ARGS = parser.parse_args()


if PARSED_ARGS.mech not in MECH_MAP:
    sys.exit('The %s environment is not supported by the '
             'GSSAPI console' % PARSED_ARGS.mech)


realm_args = {}
if PARSED_ARGS.realm_args:
    for arg in PARSED_ARGS.realm_args.split(','):
        key, raw_val = arg.split('=')
        realm_args[key] = (raw_val.lower() == 'true')

console = MECH_MAP[PARSED_ARGS.mech](realm_args=realm_args)
SAVED_ENV = None

try:
    # create the banner
    banner_text = BANNER.format(ver=sys.version, platform=sys.platform,
                                mech=PARSED_ARGS.mech,
                                realm=console.realm.realm,
                                user=console.realm.user_princ,
                                host=console.realm.host_princ)

    # import the env
    SAVED_ENV = copy.deepcopy(os.environ)
    for k,v in console.realm.env.items():
        os.environ[k] = v

    INTER = True
    # run the interactive interpreter
    if PARSED_ARGS.file is not None:
        if not PARSED_ARGS.force_interactive:
            INTER = False

        with open(PARSED_ARGS.file) as src:
            console.runsource(src.read(), src.name, 'exec')

    if INTER:
        console.interact(banner_text)

except (KeyboardInterrupt, EOFError):
    pass
finally:
    # restore the env
    if SAVED_ENV is not None:
        for k in copy.deepcopy(os.environ):
            if k in SAVED_ENV:
                os.environ[k] = SAVED_ENV[k]
            else:
                del os.environ[k]

    console.realm.stop()
