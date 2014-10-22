#!/usr/bin/env python
from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext
import sys
import re

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

link_args = get_output('krb5-config --libs gssapi')
compile_args = get_output('krb5-config --cflags gssapi').split(),

ext_module_misc = Extension(
    'gssapi.raw.misc',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/misc.pyx',
    ]
)

ext_module_exceptions = Extension(
    'gssapi.raw.exceptions',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/exceptions.pyx',
    ]
)

ext_module_creds = Extension(
    'gssapi.raw.creds',
    extra_link_args = get_output('krb5-config --libs gssapi').split() + ['-g'],
    extra_compile_args = get_output('krb5-config --cflags gssapi').split() + ['-g'],
    sources = [
        'gssapi/raw/creds.pyx',
    ]
)

ext_module_s4u = Extension(
    'gssapi.raw.ext_s4u',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/ext_s4u.pyx',
    ]
)

ext_module_cred_store = Extension(
    'gssapi.raw.ext_cred_store',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/ext_cred_store.pyx',
    ]
)

ext_module_rfc5588 = Extension(
    'gssapi.raw.ext_rfc5588',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/ext_rfc5588.pyx',
    ]
)

ext_module_names = Extension(
    'gssapi.raw.names',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split() + ['-g'],
    sources = [
        'gssapi/raw/names.pyx',
    ]
)

ext_module_oids = Extension(
    'gssapi.raw.oids',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/oids.pyx',
    ]
)

ext_module_sec_contexts = Extension(
    'gssapi.raw.sec_contexts',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/sec_contexts.pyx',
    ]
)

ext_module_types = Extension(
    'gssapi.raw.types',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/types.pyx',
    ]
)

ext_module_message = Extension(
    'gssapi.raw.message',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split(),
    sources = [
        'gssapi/raw/message.pyx',
    ]
)

ext_module_cython_converters = Extension(
    'gssapi.raw.cython_converters',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split() + ['-g'],
    sources = [
        'gssapi/raw/cython_converters.pyx',
    ]
)

mech_module_krb5 = Extension(
    'gssapi.raw.mech_krb5',
    extra_link_args = get_output('krb5-config --libs gssapi').split(),
    extra_compile_args = get_output('krb5-config --cflags gssapi').split() + ['-g'],
    sources = [
        'gssapi/raw/mech_krb5.pyx',
    ]
)

long_desc = re.sub('\.\. role:: \w+\(code\)\s*\n\s*.+', '',
                   re.sub(r':(python|bash|code):', '',
                          re.sub(r'\.\. code-block:: \w+', '::',
                                 open('README.txt').read())))

setup(
    name='PyGSSAPI',
    version='1.0.0',
    author='Solly Ross',
    author_email='sross@redhat.com',
    packages=['gssapi', 'gssapi.raw', 'gssapi.tests'],
    description='Python GSSAPI Wrapper',
    long_description=long_desc,
    license='LICENSE.txt',
    url="https://github.com/pythongssapi/python-gssapi",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        ext_module_misc,
        ext_module_exceptions,
        ext_module_creds,
        ext_module_names,
        ext_module_sec_contexts,
        ext_module_types,
        ext_module_message,
        ext_module_oids,
        ext_module_cython_converters,
        ext_module_s4u,
        ext_module_cred_store,
        ext_module_rfc5588,
        mech_module_krb5,
    ],
    install_requires=[
        'flufl.enum >= 4.0'
    ],
    tests_require=[
        'tox'
    ]
)
