import os
import subprocess

from gssapi._utils import import_gssapi_extension


def get_output(*args, **kwargs):
    res = subprocess.check_output(*args, shell=True, **kwargs)
    decoded = res.decode('utf-8')
    return decoded.strip()


def _extension_test(extension_name, extension_text):
    def make_ext_test(func):
        def ext_test(self, *args, **kwargs):
            if import_gssapi_extension(extension_name) is None:
                self.skipTest("The %s GSSAPI extension is not supported by "
                              "your GSSAPI implementation" % extension_text)
            else:
                func(self, *args, **kwargs)

        return ext_test

    return make_ext_test


_KRB_VERSION = None


def _minversion_test(target_version, problem):
    global _KRB_VERSION
    if _KRB_VERSION is None:
        _KRB_VERSION = get_output("krb5-config --version")
        _KRB_VERSION = _KRB_VERSION.split(' ')[-1].split('.')

    def make_ext_test(func):
        def ext_test(self, *args, **kwargs):
            if _KRB_VERSION < target_version.split('.'):
                self.skipTest("Your GSSAPI (version %s) is known to have "
                              "problems with %s" % (_KRB_VERSION, problem))
            else:
                func(self, *args, **kwargs)
        return ext_test

    return make_ext_test


_PLUGIN_DIR = None


def _find_plugin_dir():
    global _PLUGIN_DIR
    if _PLUGIN_DIR is not None:
        return _PLUGIN_DIR

    # if we've set a LD_LIBRARY_PATH, use that first
    ld_path_raw = os.environ.get('LD_LIBRARY_PATH')
    if ld_path_raw is not None:
        # first, try assuming it's just a normal install

        ld_paths = [path for path in ld_path_raw.split(':') if path]

        for ld_path in ld_paths:
            if not os.path.exists(ld_path):
                continue

            _PLUGIN_DIR = _decide_plugin_dir(
                _find_plugin_dirs_installed(ld_path))
            if _PLUGIN_DIR is None:
                _PLUGIN_DIR = _decide_plugin_dir(
                    _find_plugin_dirs_src(ld_path))

            if _PLUGIN_DIR is not None:
                break

    # if there was no LD_LIBRARY_PATH, or the above failed
    if _PLUGIN_DIR is None:
        # if we don't have a LD_LIBRARY_PATH, just search in
        # $prefix/lib

        lib_dir = os.path.join(get_output('krb5-config --prefix'), 'lib')
        _PLUGIN_DIR = _decide_plugin_dir(_find_plugin_dirs_installed(lib_dir))

    if _PLUGIN_DIR is not None:
        _PLUGIN_DIR = os.path.normpath(_PLUGIN_DIR)
        return _PLUGIN_DIR
    else:
        return None


def _decide_plugin_dir(dirs):
    if dirs is None:
        return None

    # the shortest path is probably more correct
    shortest_first = sorted(dirs, key=len)

    for path in shortest_first:
        # check to see if it actually contains .so files
        if get_output('find %s -name "*.so"' % path):
            return path

    return None


def _find_plugin_dirs_installed(search_path):
    options_raw = get_output('find %s/ -type d '
                             '-path "*/krb5/plugins"' % search_path)

    if options_raw:
        return options_raw.split('\n')
    else:
        return None


def _find_plugin_dirs_src(search_path):
    options_raw = get_output('find %s/../ -type d -name plugins' % search_path)

    if options_raw:
        return options_raw.split('\n')
    else:
        return None


def _requires_krb_plugin(plugin_type, plugin_name):
    plugin_path = os.path.join(_find_plugin_dir(),
                               plugin_type, '%s.so' % plugin_name)

    def make_krb_plugin_test(func):
        def krb_plugin_test(self, *args, **kwargs):
            if not os.path.exists(plugin_path):
                self.skipTest("You do not have the GSSAPI {type}"
                              "plugin {name} installed".format(
                                  type=plugin_type, name=plugin_name))
            else:
                func(self, *args, **kwargs)

        return krb_plugin_test

    return make_krb_plugin_test
