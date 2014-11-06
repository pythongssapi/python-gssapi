import sys
import types

import six
import decorator as deco

from gssapi.raw.misc import GSSError


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


# use UTF-8 as the default encoding, like Python 3
_ENCODING = 'UTF-8'


def _get_encoding():
    return _ENCODING


def set_encoding(enc):
    global _ENCODING
    _ENCODING = enc


def _encode_dict(d):
    def enc(x):
        if isinstance(x, six.text_type):
            return x.encode(_ENCODING)
        else:
            return x

    return dict((enc(k), enc(v)) for k, v in six.iteritems(d))


@deco.decorator
def catch_and_return_token(func, self, *args, **kwargs):
    try:
        return func(self, *args, **kwargs)
    except GSSError as e:
        if e.token is not None and self.__DEFER_STEP_ERRORS__:
            self._last_err = e
            self._last_tb = sys.exc_info()[2]

            return e.token
        else:
            six.reraise(*sys.exc_info())


@deco.decorator
def check_last_err(func, self, *args, **kwargs):
    if self._last_err is not None:
        try:
            six.reraise(type(self._last_err), self._last_err, self._last_tb)
        finally:
            del self._last_tb  # in case of cycles, break glass
            self._last_err = None
    else:
        return func(self, *args, **kwargs)


class CheckLastError(type):
    def __new__(cls, name, parents, attrs):
        attrs['__DEFER_STEP_ERRORS__'] = True

        for attr_name in attrs:
            attr = attrs[attr_name]

            # wrap only methods
            if not isinstance(attr, types.FunctionType):
                continue

            if attr_name[0] != '_':
                attrs[attr_name] = check_last_err(attr)

        return super(CheckLastError, cls).__new__(cls, name, parents, attrs)
