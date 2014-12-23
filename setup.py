#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist
from setuptools.extension import Extension
import re
import sys
import os


SKIP_CYTHON_FILE = '__dont_use_cython__.txt'

if os.path.exists(SKIP_CYTHON_FILE):
    print("In distributed package, building from C files...", file=sys.stderr)
    SOURCE_EXT = 'c'
else:
    try:
        from Cython.Build import cythonize
        print("Building from Cython files...", file=sys.stderr)
        SOURCE_EXT = 'pyx'
    except ImportError:
        print("Cython not found, building from Cython files...",
              file=sys.stderr)
        SOURCE_EXT = 'c'

get_output = None

try:
    import commands
    get_output = commands.getoutput
except ImportError:
    import subprocess

    def _get_output(*args, **kwargs):
        res = subprocess.check_output(*args, shell=True, **kwargs)
        decoded = res.decode('utf-8')
        return decoded.strip()

    get_output = _get_output

# get the compile and link args
link_args = os.environ.get('GSSAPI_LINKER_ARGS', None)
compile_args = os.environ.get('GSSAPI_COMPILER_ARGS', None)

if link_args is None:
    link_args = get_output('krb5-config --libs gssapi')

if compile_args is None:
    compile_args = get_output('krb5-config --cflags gssapi')

link_args = link_args.split()
compile_args = compile_args.split()

ENABLE_SUPPORT_DETECTION = \
    (os.environ.get('GSSAPI_SUPPORT_DETECT', 'true').lower() == 'true')

if ENABLE_SUPPORT_DETECTION:
    main_lib = os.environ.get('GSSAPI_MAIN_LIB', None)
    if main_lib is None:
        for opt in link_args:
            if opt.startswith('-lgssapi'):
                main_lib = 'lib%s.so' % opt[2:]

    if main_lib is None:
        raise Exception("Could not find main GSSAPI shared libary.  Please "
                        "try setting GSSAPI_MAIN_LIB yourself or setting "
                        "ENABLE_SUPPORT_DETECTION to 'false'")

    import ctypes
    GSSAPI_LIB = ctypes.CDLL(main_lib)


class build_gssapi_ext(build_ext):
    def run(self):
        if not self.dry_run:
            # optionally fake gssapi_ext.h using gssapi.h
            prefix = get_output('krb5-config gssapi --prefix')
            gssapi_ext_h = os.path.join(prefix, 'include/gssapi/gssapi_ext.h')

            if not os.path.exists(gssapi_ext_h):
                target_dir = os.path.join(self.build_temp, 'c_include')
                gssapi_dir = os.path.join(target_dir, 'gssapi')
                if not os.path.exists(gssapi_dir):
                    os.makedirs(gssapi_dir)

                target_file = os.path.join(target_dir, 'gssapi/gssapi_ext.h')
                if not os.path.exists(target_file):
                    with open(target_file, 'w') as header:
                        header.write('#include "gssapi.h"')

                for ext in self.extensions:
                    ext.extra_compile_args.append("-I%s" %
                                                  os.path.abspath(target_dir))

        build_ext.run(self)


# add in the flag that causes us not to compile from Cython when
# installing from an sdist
class sdist_gssapi(sdist):
    def run(self):
        if not self.dry_run:
            with open(SKIP_CYTHON_FILE, 'w') as flag_file:
                flag_file.write('COMPILE_FROM_C_ONLY')

            sdist.run(self)

            os.remove(SKIP_CYTHON_FILE)


# detect support
def main_file(module):
    return Extension('gssapi.raw.%s' % module,
                     extra_link_args=link_args,
                     extra_compile_args=compile_args,
                     sources=['gssapi/raw/%s.%s' % (module, SOURCE_EXT)])


def extension_file(module, canary):
    if ENABLE_SUPPORT_DETECTION and not hasattr(GSSAPI_LIB, canary):
        return None
    else:
        return Extension('gssapi.raw.ext_%s' % module,
                         extra_link_args=link_args,
                         extra_compile_args=compile_args,
                         sources=['gssapi/raw/ext_%s.%s' % (module,
                                                            SOURCE_EXT)])


def gssapi_modules(lst):
    # filter out missing files
    res = [mod for mod in lst if mod is not None]

    # add in supported mech files
    MECHS_SUPPORTED = os.environ.get('GSSAPI_MECHS', 'krb5').split(',')
    for mech in MECHS_SUPPORTED:
        res.append(Extension('gssapi.raw.mech_%s' % mech,
                             extra_link_args=link_args,
                             extra_compile_args=compile_args,
                             sources=['gssapi/raw/mech_%s.%s' % (mech,
                                                                 SOURCE_EXT)]))

    if SOURCE_EXT == 'pyx':
        res = cythonize(res)

    return res

long_desc = re.sub('\.\. role:: \w+\(code\)\s*\n\s*.+', '',
                   re.sub(r':(python|bash|code):', '',
                          re.sub(r'\.\. code-block:: \w+', '::',
                                 open('README.txt').read())))

setup(
    name='gssapi',
    version='1.0.0',
    author='The Python GSSAPI Team',
    author_email='sross@redhat.com',
    packages=['gssapi', 'gssapi.raw', 'gssapi.tests'],
    description='Python GSSAPI Wrapper',
    long_description=long_desc,
    license='LICENSE.txt',
    url="https://github.com/pythongssapi/python-gssapi",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Cython',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'build_ext': build_gssapi_ext, 'sdist': sdist_gssapi},
    ext_modules=gssapi_modules([
        main_file('misc'),
        main_file('exceptions'),
        main_file('creds'),
        main_file('names'),
        main_file('sec_contexts'),
        main_file('types'),
        main_file('message'),
        main_file('oids'),
        main_file('cython_converters'),
        main_file('chan_bindings'),
        extension_file('s4u', 'gss_acquire_cred_impersonate_name'),
        extension_file('cred_store', 'gss_store_cred_into'),
        extension_file('rfc5588', 'gss_store_cred'),
        extension_file('cred_imp_exp', 'gss_import_cred'),
    ]),
    keywords=['gssapi', 'security'],
    install_requires=[
        'enum34',
        'decorator',
        'six'
    ],
    tests_require=[
        'tox'
    ]
)
