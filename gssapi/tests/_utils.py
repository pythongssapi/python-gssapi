from gssapi._utils import import_gssapi_extension


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
