import sys


def import_gssapi_extension(name):
    try:
        path = 'gssapi.raw.ext_{0}'.format(name)
        __import__(path)
        return sys.modules[path]
    except ImportError:
        return None


def flag_property(flag):
    def setter(self, val):
        if val:
            self.flags.add(flag)
        else:
            self.flags.discard(flag)

    def getter(self):
        return flag in self.flags

    return property(getter, setter)


def inquire_property(name):
    def inquire_property(self):
        if not self._started:
            msg = ("Cannot read {0} from a security context whose "
                   "establishment has not yet been started.")
            raise AttributeError(msg)

        return getattr(self._inquire(**{name: True}), name)

    return property(inquire_property)
