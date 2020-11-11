#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup
from setuptools import Distribution
from setuptools.command.sdist import sdist
from setuptools.extension import Extension
import subprocess
import platform
import re
import sys
import os
import shutil
import shlex


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
        print("Cython not found, building from C files...",
              file=sys.stderr)
        SOURCE_EXT = 'c'


def get_output(*args, **kwargs):
    res = subprocess.check_output(*args, shell=True, **kwargs)
    decoded = res.decode('utf-8')
    return decoded.strip()


# get the compile and link args
posix = os.name != 'nt'
link_args, compile_args = [
    shlex.split(os.environ[e], posix=posix) if e in os.environ else None
    for e in ['GSSAPI_LINKER_ARGS', 'GSSAPI_COMPILER_ARGS']
]

osx_has_gss_framework = False
if sys.platform == 'darwin':
    mac_ver = [int(v) for v in platform.mac_ver()[0].split('.')]
    osx_has_gss_framework = (mac_ver >= [10, 7, 0])

winkrb_path = None
if os.name == 'nt':
    # Try to find location of MIT kerberos
    # First check program files of the appropriate architecture
    _pf_path = os.path.join(os.environ['ProgramFiles'], 'MIT', 'Kerberos')
    if os.path.exists(_pf_path):
        winkrb_path = _pf_path
    else:
        # Try to detect kinit in PATH
        _kinit_path = shutil.which('kinit')
        if _kinit_path is None:
            print("Failed find MIT kerberos!")
        else:
            winkrb_path = os.path.dirname(os.path.dirname(_kinit_path))

    # Monkey patch distutils if it throws errors getting msvcr.
    # For MinGW it won't need it.
    from distutils import cygwinccompiler
    try:
        cygwinccompiler.get_msvcr()
    except ValueError:
        cygwinccompiler.get_msvcr = lambda *a, **kw: []

if link_args is None:
    if osx_has_gss_framework:
        link_args = ['-framework', 'GSS']
    elif winkrb_path:
        _libs = os.path.join(
            winkrb_path, 'lib', 'amd64' if sys.maxsize > 2 ** 32 else 'i386'
        )
        link_args = (
            ['-L%s' % _libs]
            + ['-l%s' % os.path.splitext(lib)[0] for lib in os.listdir(_libs)]
        )
    elif os.environ.get('MINGW_PREFIX'):
        link_args = ['-lgss']
    else:
        link_args = shlex.split(get_output('krb5-config --libs gssapi'))

if compile_args is None:
    if osx_has_gss_framework:
        compile_args = ['-framework', 'GSS', '-DOSX_HAS_GSS_FRAMEWORK']
    elif winkrb_path:
        compile_args = [
            '-I%s' % os.path.join(winkrb_path, 'include'),
            '-DMS_WIN64'
        ]
    elif os.environ.get('MINGW_PREFIX'):
        compile_args = ['-fPIC']
    else:
        compile_args = shlex.split(get_output('krb5-config --cflags gssapi'))

# add in the extra workarounds for different include structures
if winkrb_path:
    prefix = winkrb_path
else:
    try:
        prefix = get_output('krb5-config gssapi --prefix')
    except Exception:
        print("WARNING: couldn't find krb5-config; assuming prefix of %s"
              % str(sys.prefix))
        prefix = sys.prefix
gssapi_ext_h = os.path.join(prefix, 'include/gssapi/gssapi_ext.h')
if os.path.exists(gssapi_ext_h):
    compile_args.append("-DHAS_GSSAPI_EXT_H")

# Create a define to detect msys in the headers
if sys.platform == 'msys':
    compile_args.append('-D__MSYS__')

# ensure that any specific directories are listed before any generic system
# directories inserted by setuptools
# Also separate out specified libraries as MSBuild requires different args
_link_args = link_args
library_dirs, libraries, link_args = [], [], []
for arg in _link_args:
    if arg.startswith('-L'):
        library_dirs.append(arg[2:])
    elif arg.startswith('-l'):
        libraries.append(arg[2:])
    else:
        link_args.append(arg)

ENABLE_SUPPORT_DETECTION = \
    (os.environ.get('GSSAPI_SUPPORT_DETECT', 'true').lower() == 'true')

if ENABLE_SUPPORT_DETECTION:
    import ctypes.util

    main_lib = os.environ.get('GSSAPI_MAIN_LIB', None)
    main_path = ""
    if main_lib is None and osx_has_gss_framework:
        main_lib = ctypes.util.find_library('GSS')
    elif os.environ.get('MINGW_PREFIX'):
        main_lib = os.environ.get('MINGW_PREFIX')+'/bin/libgss-3.dll'
    elif sys.platform == 'msys':
        # Plain msys, not running in MINGW_PREFIX. Try to get the lib from one
        _main_lib = (
            '/mingw%d/bin/libgss-3.dll'
            % (64 if sys.maxsize > 2 ** 32 else 32)
        )
        if os.path.exists(_main_lib):
            main_lib = _main_lib
            os.environ['PATH'] += os.pathsep + os.path.dirname(main_lib)
    elif main_lib is None:
        for opt in libraries:
            if opt.startswith('gssapi'):
                if os.name == 'nt':
                    main_lib = '%s.dll' % opt
                    if winkrb_path:
                        main_path = os.path.join(winkrb_path, 'bin')
                else:
                    main_lib = 'lib%s.so' % opt
        for opt in link_args:
            # To support Heimdal on Debian, read the linker path.
            if opt.startswith('-Wl,/'):
                main_path = opt[4:] + "/"

    if main_lib is None:
        raise Exception("Could not find main GSSAPI shared library.  Please "
                        "try setting GSSAPI_MAIN_LIB yourself or setting "
                        "ENABLE_SUPPORT_DETECTION to 'false'")

    GSSAPI_LIB = ctypes.CDLL(os.path.join(main_path, main_lib))


# add in the flag that causes us not to compile from Cython when
# installing from an sdist
class sdist_gssapi(sdist):
    def run(self):
        if not self.dry_run:
            with open(SKIP_CYTHON_FILE, 'w') as flag_file:
                flag_file.write('COMPILE_FROM_C_ONLY')

            sdist.run(self)

            os.remove(SKIP_CYTHON_FILE)


DONT_CYTHONIZE_FOR = ('clean',)


class GSSAPIDistribution(Distribution, object):
    def run_command(self, command):
        self._last_run_command = command
        Distribution.run_command(self, command)

    @property
    def ext_modules(self):
        if SOURCE_EXT != 'pyx':
            return getattr(self, '_ext_modules', None)

        if getattr(self, '_ext_modules', None) is None:
            return None

        if getattr(self, '_last_run_command', None) in DONT_CYTHONIZE_FOR:
            return self._ext_modules

        if getattr(self, '_cythonized_ext_modules', None) is None:
            self._cythonized_ext_modules = cythonize(
                self._ext_modules,
                language_level=2,
            )

        return self._cythonized_ext_modules

    @ext_modules.setter
    def ext_modules(self, mods):
        self._cythonized_ext_modules = None
        self._ext_modules = mods

    @ext_modules.deleter
    def ext_modules(self):
        del self._ext_modules
        del self._cythonized_ext_modules


def make_extension(name_fmt, module, **kwargs):
    """Helper method to remove the repetition in extension declarations."""
    source = name_fmt.replace('.', '/') % module + '.' + SOURCE_EXT
    if not os.path.exists(source):
        raise OSError(source)
    return Extension(
        name_fmt % module,
        extra_link_args=link_args,
        extra_compile_args=compile_args,
        library_dirs=library_dirs,
        libraries=libraries,
        sources=[source],
        **kwargs
    )


# detect support
def main_file(module):
    return make_extension('gssapi.raw.%s', module)


ENUM_EXTS = []


def extension_file(module, canary):
    if ENABLE_SUPPORT_DETECTION and not hasattr(GSSAPI_LIB, canary):
        print('Skipping the %s extension because it '
              'is not supported by your GSSAPI implementation...' % module)
        return

    try:
        ENUM_EXTS.append(
            make_extension('gssapi.raw._enum_extensions.ext_%s', module,
                           include_dirs=['gssapi/raw/'])
        )
    except OSError:
        pass

    return make_extension('gssapi.raw.ext_%s', module)


def gssapi_modules(lst):
    # filter out missing files
    res = [mod for mod in lst if mod is not None]

    # add in supported mech files
    res.extend(
        make_extension('gssapi.raw.mech_%s', mech)
        for mech in os.environ.get('GSSAPI_MECHS', 'krb5').split(',')
    )

    # add in any present enum extension files
    res.extend(ENUM_EXTS)

    return res


long_desc = re.sub(r'\.\. role:: \w+\(code\)\s*\n\s*.+', '',
                   re.sub(r':(python|bash|code):', '',
                          re.sub(r'\.\. code-block:: \w+', '::',
                                 open('README.txt').read())))

install_requires = [
    'decorator',
]

setup(
    name='gssapi',
    version='1.6.10',
    author='The Python GSSAPI Team',
    author_email='rharwood@redhat.com',
    packages=['gssapi', 'gssapi.raw', 'gssapi.raw._enum_extensions',
              'gssapi.tests'],
    description='Python GSSAPI Wrapper',
    long_description=long_desc,
    license='LICENSE.txt',
    url="https://github.com/pythongssapi/python-gssapi",
    python_requires=">=3.6.*",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Cython',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    distclass=GSSAPIDistribution,
    cmdclass={'sdist': sdist_gssapi},
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
        extension_file('rfc4178', 'gss_set_neg_mechs'),
        extension_file('rfc5587', 'gss_indicate_mechs_by_attrs'),
        extension_file('rfc5588', 'gss_store_cred'),
        extension_file('rfc5801', 'gss_inquire_saslname_for_mech'),
        extension_file('cred_imp_exp', 'gss_import_cred'),
        extension_file('dce', 'gss_wrap_iov'),
        extension_file('iov_mic', 'gss_get_mic_iov'),
        extension_file('ggf', 'gss_inquire_sec_context_by_oid'),
        extension_file('set_cred_opt', 'gss_set_cred_option'),

        # see ext_rfc6680_comp_oid for more information on this split
        extension_file('rfc6680', 'gss_display_name_ext'),
        extension_file('rfc6680_comp_oid', 'GSS_C_NT_COMPOSITE_EXPORT'),

        # see ext_password{,_add}.pyx for more information on this split
        extension_file('password', 'gss_acquire_cred_with_password'),
        extension_file('password_add', 'gss_add_cred_with_password'),
    ]),
    keywords=['gssapi', 'security'],
    install_requires=install_requires
)
