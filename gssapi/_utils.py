import sys


def import_gssapi_extension(name):
    try:
        path = 'gssapi.raw.ext_{0}'.format(name)
        __import__(path)
        return sys.modules[path]
    except ImportError:
        return None
