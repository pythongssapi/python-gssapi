import typing as t

from gssapi.raw import creds as rcreds
from gssapi.raw import named_tuples as tuples
from gssapi.raw import names as rnames
from gssapi.raw import oids as roids
from gssapi._utils import import_gssapi_extension, _encode_dict

from gssapi import names

rcred_imp_exp = import_gssapi_extension('cred_imp_exp')
rcred_s4u = import_gssapi_extension('s4u')
rcred_cred_store = import_gssapi_extension('cred_store')
rcred_rfc5588 = import_gssapi_extension('rfc5588')


class Credentials(rcreds.Creds):
    """GSSAPI Credentials

    This class represents a set of GSSAPI credentials which may
    be used with and/or returned by other GSSAPI methods.

    It inherits from the low-level GSSAPI :class:`~gssapi.raw.creds.Creds`
    class, and thus may used with both low-level and high-level API methods.

    If your implementation of GSSAPI supports the credentials import-export
    extension, you may pickle and unpickle this object.

    The constructor either acquires or imports a set of GSSAPI
    credentials.

    If the `base` argument is used, an existing
    :class:`~gssapi.raw.creds.Creds` object from the low-level API is
    converted into a high-level object.

    If the `token` argument is used, the credentials
    are imported using the token, if the credentials import-export
    extension is supported (:requires-ext:`cred_imp_exp`).

    Otherwise, the credentials are acquired as per the
    :meth:`acquire` method.

    Raises:
        ~gssapi.exceptions.BadMechanismError
        ~gssapi.exceptions.BadNameTypeError
        ~gssapi.exceptions.BadNameError
        ~gssapi.exceptions.ExpiredCredentialsError
        ~gssapi.exceptions.MissingCredentialsError
    """

    __slots__ = ()

    def __new__(
        cls,
        base: t.Optional[rcreds.Creds] = None,
        token: t.Optional[bytes] = None,
        name: t.Optional[rnames.Name] = None,
        lifetime: t.Optional[int] = None,
        mechs: t.Optional[t.Iterable[roids.OID]] = None,
        usage: str = 'both',
        store: t.Optional[
            t.Dict[t.Union[bytes, str], t.Union[bytes, str]]
        ] = None,
    ) -> "Credentials":
        # TODO(directxman12): this is missing support for password
        #                     (non-RFC method)
        if base is not None:
            base_creds = base
        elif token is not None:
            if rcred_imp_exp is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for importing and "
                                          "exporting creditials")

            base_creds = rcred_imp_exp.import_cred(token)
        else:
            res = cls.acquire(name, lifetime, mechs, usage,
                              store=store)
            base_creds = res.creds

        return t.cast("Credentials",
                      super(Credentials, cls).__new__(cls, base_creds))

    @property
    def name(self) -> names.Name:
        """Get the name associated with these credentials"""
        return t.cast(names.Name,
                      self.inquire(name=True, lifetime=False, usage=False,
                                   mechs=False).name)

    @property
    def lifetime(self) -> int:
        """Get the remaining lifetime of these credentials, in seconds"""
        return t.cast(int,
                      self.inquire(name=False, lifetime=True,
                                   usage=False, mechs=False).lifetime)

    @property
    def mechs(self) -> t.Set[roids.OID]:
        """Get the mechanisms for these credentials"""
        return t.cast(t.Set[roids.OID],
                      self.inquire(name=False, lifetime=False,
                                   usage=False, mechs=True).mechs)

    @property
    def usage(self) -> str:
        """Get the usage (initiate, accept, or both) of these credentials"""
        return t.cast(str,
                      self.inquire(name=False, lifetime=False,
                                   usage=True, mechs=False).usage)

    @classmethod
    def acquire(
        cls,
        name: t.Optional[rnames.Name] = None,
        lifetime: t.Optional[int] = None,
        mechs: t.Optional[t.Iterable[roids.OID]] = None,
        usage: str = 'both',
        store: t.Optional[
            t.Dict[t.Union[bytes, str], t.Union[bytes, str]]
        ] = None,
    ) -> tuples.AcquireCredResult:
        """Acquire GSSAPI credentials

        This method acquires credentials.  If the `store` argument is
        used, the credentials will be acquired from the given
        credential store (if supported).  Otherwise, the credentials are
        acquired from the default store.

        The credential store information is a dictionary containing
        mechanisms-specific keys and values pointing to a credential store
        or stores.

        Using a non-default store requires support for the credentials store
        extension.

        Args:
            name (~gssapi.names.Name): the name associated with the
                credentials, or None for the default name
            lifetime (int): the desired lifetime of the credentials in seconds,
                or None for indefinite
            mechs (list): the desired :class:`MechType` OIDs to be used
                with the credentials, or None for the default set
            usage (str): the usage for the credentials -- either 'both',
                'initiate', or 'accept'
            store (dict): the credential store information pointing to the
                credential store from which to acquire the credentials,
                or None for the default store (:requires-ext:`cred_store`)

        Returns:
            AcquireCredResult: the acquired credentials and information about
            them

        Raises:
            ~gssapi.exceptions.BadMechanismError
            ~gssapi.exceptions.BadNameTypeError
            ~gssapi.exceptions.BadNameError
            ~gssapi.exceptions.ExpiredCredentialsError
            ~gssapi.exceptions.MissingCredentialsError
        """

        if store is None:
            res = rcreds.acquire_cred(name, lifetime,
                                      mechs, usage)
        else:
            if rcred_cred_store is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for manipulating "
                                          "credential stores")

            b_store = _encode_dict(store)

            res = rcred_cred_store.acquire_cred_from(b_store, name,
                                                     lifetime, mechs,
                                                     usage)

        return tuples.AcquireCredResult(cls(base=res.creds), res.mechs,
                                        res.lifetime)

    def store(
        self,
        store: t.Optional[
            t.Dict[t.Union[bytes, str], t.Union[bytes, str]]
        ] = None,
        usage: str = 'both',
        mech: t.Optional[roids.OID] = None,
        overwrite: bool = False,
        set_default: bool = False,
    ) -> tuples.StoreCredResult:
        """Store these credentials into the given store

        This method stores the current credentials into the specified
        credentials store.  If the default store is used, support for
        :rfc:`5588` is required.  Otherwise, support for the credentials
        store extension is required.

        :requires-ext:`rfc5588` or :requires-ext:`cred_store`

        Args:
            store (dict): the store into which to store the credentials,
                or None for the default store.
            usage (str): the usage to store the credentials with -- either
                'both', 'initiate', or 'accept'
            mech (~gssapi.OID): the :class:`MechType` to associate with the
                stored credentials
            overwrite (bool): whether or not to overwrite existing credentials
                stored with the same name, etc
            set_default (bool): whether or not to set these credentials as
                the default credentials for the given store.

        Returns:
            StoreCredResult: the results of the credential storing operation

        Raises:
            ~gssapi.exceptions.GSSError
            ~gssapi.exceptions.ExpiredCredentialsError
            ~gssapi.exceptions.MissingCredentialsError
            ~gssapi.exceptions.OperationUnavailableError
            ~gssapi.exceptions.DuplicateCredentialsElementError
        """

        if store is None:
            if rcred_rfc5588 is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for RFC 5588")

            return rcred_rfc5588.store_cred(self, usage, mech,
                                            overwrite, set_default)
        else:
            if rcred_cred_store is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for manipulating "
                                          "credential stores directly")

            b_store = _encode_dict(store)

            return rcred_cred_store.store_cred_into(b_store, self, usage, mech,
                                                    overwrite, set_default)

    def impersonate(
        self,
        name: t.Optional[rnames.Name] = None,
        lifetime: t.Optional[int] = None,
        mechs: t.Optional[t.Iterable[roids.OID]] = None,
        usage: str = 'initiate',
    ) -> "Credentials":
        """Impersonate a name using the current credentials

        This method acquires credentials by impersonating another
        name using the current credentials.

        :requires-ext:`s4u`

        Args:
            name (~gssapi.names.Name): the name to impersonate
            lifetime (int): the desired lifetime of the new credentials in
                seconds, or None for indefinite
            mechs (list): the desired :class:`MechType` OIDs for the new
                credentials
            usage (str): the desired usage for the new credentials -- either
                'both', 'initiate', or 'accept'.  Note that some mechanisms
                may only support 'initiate'.

        Returns:
            Credentials: the new credentials impersonating the given name
        """

        if rcred_s4u is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "have support for S4U")

        res = rcred_s4u.acquire_cred_impersonate_name(self, name,
                                                      lifetime, mechs,
                                                      usage)

        return type(self)(base=res.creds)

    def inquire(
        self,
        name: bool = True,
        lifetime: bool = True,
        usage: bool = True,
        mechs: bool = True,
    ) -> tuples.InquireCredResult:
        """Inspect these credentials for information

        This method inspects these credentials for information about them.

        Args:
            name (bool): get the name associated with the credentials
            lifetime (bool): get the remaining lifetime for the credentials
            usage (bool): get the usage for the credentials
            mechs (bool): get the mechanisms associated with the credentials

        Returns:
            InquireCredResult: the information about the credentials,
            with None used when the corresponding argument was False

        Raises:
            ~gssapi.exceptions.MissingCredentialsError
            ~gssapi.exceptions.InvalidCredentialsError
            ~gssapi.exceptions.ExpiredCredentialsError
        """

        res = rcreds.inquire_cred(self, name, lifetime, usage, mechs)

        if res.name is not None:
            res_name = names.Name(res.name)
        else:
            res_name = None

        return tuples.InquireCredResult(res_name, res.lifetime,
                                        res.usage, res.mechs)

    def inquire_by_mech(
        self,
        mech: roids.OID,
        name: bool = True,
        init_lifetime: bool = True,
        accept_lifetime: bool = True,
        usage: bool = True,
    ) -> tuples.InquireCredByMechResult:
        """Inspect these credentials for per-mechanism information

        This method inspects these credentials for per-mechanism information
        about them.

        Args:
            mech (~gssapi.OID): the mechanism for which to retrieve the
                information
            name (bool): get the name associated with the credentials
            init_lifetime (bool): get the remaining initiate lifetime for
                the credentials in seconds
            accept_lifetime (bool): get the remaining accept lifetime for
                the credentials in seconds
            usage (bool): get the usage for the credentials

        Returns:
            InquireCredByMechResult: the information about the credentials,
            with None used when the corresponding argument was False
        """

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

    def add(
        self,
        name: rnames.Name,
        mech: roids.OID,
        usage: str = 'both',
        init_lifetime: t.Optional[int] = None,
        accept_lifetime: t.Optional[int] = None,
        impersonator: t.Optional[rcreds.Creds] = None,
        store: t.Optional[
            t.Dict[t.Union[bytes, str], t.Union[bytes, str]]
        ] = None,
    ) -> "Credentials":
        """Acquire more credentials to add to the current set

        This method works like :meth:`acquire`, except that it adds the
        acquired credentials for a single mechanism to a copy of the current
        set, instead of creating a new set for multiple mechanisms.
        Unlike :meth:`acquire`, you cannot pass None desired name or
        mechanism.

        If the `impersonator` argument is used, the credentials will
        impersonate the given name using the impersonator credentials
        (:requires-ext:`s4u`).

        If the `store` argument is used, the credentials will be acquired
        from the given credential store (:requires-ext:`cred_store`).
        Otherwise, the credentials are acquired from the default store.

        The credential store information is a dictionary containing
        mechanisms-specific keys and values pointing to a credential store
        or stores.

        Note that the `store` argument is not compatible with the
        `impersonator` argument.

        Args:
            name (~gssapi.names.Name): the name associated with the
                credentials
            mech (~gssapi.OID): the desired :class:`MechType` to be used with
                the credentials
            usage (str): the usage for the credentials -- either 'both',
                'initiate', or 'accept'
            init_lifetime (int): the desired initiate lifetime of the
                credentials in seconds, or None for indefinite
            accept_lifetime (int): the desired accept lifetime of the
                credentials in seconds, or None for indefinite
            impersonator (Credentials): the credentials to use to impersonate
                the given name, or None to not acquire normally
                (:requires-ext:`s4u`)
            store (dict): the credential store information pointing to the
                credential store from which to acquire the credentials,
                or None for the default store (:requires-ext:`cred_store`)

        Returns:
            Credentials: the credentials set containing the current credentials
            and the newly acquired ones.

        Raises:
            ~gssapi.exceptions.BadMechanismError
            ~gssapi.exceptions.BadNameTypeError
            ~gssapi.exceptions.BadNameError
            ~gssapi.exceptions.DuplicateCredentialsElementError
            ~gssapi.exceptions.ExpiredCredentialsError
            ~gssapi.exceptions.MissingCredentialsError
        """

        if store is not None and impersonator is not None:
            raise ValueError('You cannot use both the `impersonator` and '
                             '`store` arguments at the same time')

        if store is not None:
            if rcred_cred_store is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for manipulating "
                                          "credential stores")
            b_store = _encode_dict(store)

            res = rcred_cred_store.add_cred_from(b_store, self, name, mech,
                                                 usage, init_lifetime,
                                                 accept_lifetime)
        elif impersonator is not None:
            if rcred_s4u is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not have support for S4U")
            res = rcred_s4u.add_cred_impersonate_name(self, impersonator,
                                                      name, mech, usage,
                                                      init_lifetime,
                                                      accept_lifetime)
        else:
            res = rcreds.add_cred(self, name, mech, usage, init_lifetime,
                                  accept_lifetime)

        return Credentials(res.creds)

    def export(self) -> bytes:
        """Export these credentials into a token

        This method exports the current credentials to a token that can
        then be imported by passing the `token` argument to the constructor.

        This is often used to pass credentials between processes.

        :requires-ext:`cred_imp_exp`

        Returns:
            bytes: the exported credentials in token form
        """

        if rcred_imp_exp is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "have support for importing and "
                                      "exporting creditials")

        return rcred_imp_exp.export_cred(self)

    # pickle protocol support
    def __reduce__(
        self,
    ) -> t.Tuple[t.Type["Credentials"], t.Tuple[None, bytes]]:
        # the unpickle arguments to new are (base=None, token=self.export())
        return (type(self), (None, self.export()))
