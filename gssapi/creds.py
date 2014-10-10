from gssapi.raw import creds as rcreds
from gssapi.raw import named_tuples as tuples
from gssapi._utils import import_gssapi_extension

rcred_imp_exp = import_gssapi_extension('cred_imp_exp')
rcred_s4u = import_gssapi_extension('s4u')

from gssapi import names


class Credentials(rcreds.Creds):
    __slots__ = ()

    def __new__(cls, base=None, token=None,
                desired_name=None, lifetime=None,
                desired_mechs=None, usage='both'):
        # TODO(directxman12): this is missing support for password
        #                     and cred_store (non-RFC methods)
        #                     as well as import_cred
        if base is not None:
            base_creds = base
        elif token is not None:
            if rcred_imp_exp is None:
                raise AttributeError("Your GSSAPI implementation does not "
                                     "have support for importing and "
                                     "exporting creditials")

            base_creds = rcred_imp_exp.import_cred(token)
        else:
            res = cls.acquire(desired_name, lifetime, desired_mechs, usage)
            base_creds = res.creds

        return super(Credentials, cls).__new__(cls, base_creds)

    @property
    def name(self):
        return self.inquire(name=True, lifetime=False,
                            usage=False, mechs=False).name

    @property
    def lifetime(self):
        return self.inquire(name=False, lifetime=True,
                            usage=False, mechs=False).lifetime

    @property
    def mechs(self):
        return self.inquire(name=False, lifetime=False,
                            usage=False, mechs=True).mechs

    @property
    def usage(self):
        return self.inquire(name=False, lifetime=False,
                            usage=True, mechs=False).usage

    @classmethod
    def acquire(cls, desired_name=None, lifetime=None,
                desired_mechs=None, usage='both'):
        res = rcreds.acquire_cred(desired_name, lifetime, desired_mechs, usage)

        return tuples.AcquireCredResult(cls(base=res.creds), res.mechs,
                                        res.lifetime)

    def impersonate(self, desired_name=None, lifetime=None,
                    desired_mechs=None, usage='initiate'):
        if rcred_s4u is None:
            raise AttributeError("Your GSSAPI implementation does not "
                                 "have support for S4U")

        res = rcred_s4u.acquire_cred_impersonate_name(self, desired_name,
                                                      lifetime, desired_mechs,
                                                      usage)

        return type(self)(base=res.creds)

    def inquire(self, name=True, lifetime=True, usage=True, mechs=True):
        res = rcreds.inquire_cred(self, name, lifetime, usage, mechs)

        if res.name is not None:
            res_name = names.Name(res.name)
        else:
            res_name = None

        return tuples.InquireCredResult(res_name, res.lifetime,
                                        res.usage, res.mechs)

    def inquire_by_mech(self, mech, name=True, init_lifetime=True,
                        accept_lifetime=True, usage=True):
        res = rcreds.inquire_cred_by_mech(self, mech, name, init_lifetime,
                                          accept_lifetime, usage)

        if res.name is not None:
            res_name = names.Name(res.name)
        else:
            res_name = None

        return tuples.InquireCredByMechResult(res_name,
                                              res.init_lifetime,
                                              res.accept_lifetime,
                                              res.usage)

    def add(self, desired_name, desired_mech, usage='both',
            init_lifetime=None, accept_lifetime=None, impersonator=None):
        if impersonator is not None:
            if rcred_s4u is None:
                raise AttributeError("Your GSSAPI implementation does not "
                                     "have support for S4U")
            return rcred_s4u.add_cred_impersonate_name(self, impersonator,
                                                       desired_name,
                                                       desired_mech,
                                                       usage, init_lifetime,
                                                       accept_lifetime)
        else:
            return rcreds.add_cred(self, desired_name, desired_mech, usage,
                                   init_lifetime, accept_lifetime)

    def export(self):
        if rcred_imp_exp is None:
            raise AttributeError("Your GSSAPI implementation does not "
                                 "have support for importing and exporting "
                                 "creditials")

        return rcred_imp_exp.export_cred(self)

    # pickle protocol support
    def __reduce__(self):
        # the unpickle arguments to new are (base=None, token=self.export())
        return (type(self), (None, self.export()))
