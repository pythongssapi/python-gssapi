from gssapi._utils import import_gssapi_extension

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
