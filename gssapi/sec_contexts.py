from gssapi.raw import sec_contexts as rsec_contexts
from gssapi.raw import message as rmessage
from gssapi.raw import named_tuples as tuples
from gssapi.raw.types import RequirementFlag, IntEnumFlagSet

import gssapi.exceptions as excs
from gssapi import _utils
from gssapi.names import Name
from gssapi.creds import Credentials


class SecurityContext(rsec_contexts.SecurityContext):
    # TODO(directxman12): do we want to use __slots__ here?
    def __new__(cls, base=None, token=None,
                name=None, creds=None, desired_lifetime=None, flags=None,
                mech_type=None, channel_bindings=None, usage=None):

        if token is not None:
            base = rsec_contexts.import_sec_context(token)

        return super(SecurityContext, cls).__new__(cls, base)

    def __init__(self, base=None, token=None,
                 name=None, creds=None, desired_lifetime=None, flags=None,
                 mech_type=None, channel_bindings=None, usage=None):

        # determine the usage ('initiate' vs 'accept')
        if base is None and token is None:
            # this will be a new context
            if usage is not None:
                if usage not in ('initiate', 'accept'):
                    msg = "Usage must be either 'initiate' or 'accept'"
                    raise excs.UnknownUsageError(msg, obj="security context")

                self.usage = usage
            elif creds is not None and creds.usage != 'both':
                self.usage = creds.usage
            elif name is not None:
                # if we pass a name, assume the usage is 'initiate'
                self.usage = 'initiate'
            else:
                # if we don't pass a name, assume the usage is 'accept'
                self.usage = 'accept'

            # check for appropriate arguments
            if self.usage == 'initiate':
                # takes: creds?, target_name, mech_type?, flags?,
                #        channel_bindings?
                # TODO(directxman12): should we check for this?
                if name is None:
                    raise TypeError("You must pass the 'name' argument when "
                                    "creating an initiating security context")
                self._target_name = name
                self._mech_type = mech_type
                self._desired_flags = IntEnumFlagSet(RequirementFlag, flags)
                self._desired_lifetime = desired_lifetime
            else:
                # takes creds?
                if (name is not None or flags is not None or
                        mech_type is not None or desired_lifetime is not None):
                    raise TypeError("You must pass at most the 'creds' "
                                    "argument when creating an accepting "
                                    "security context")

            self._channel_bindings = channel_bindings
            self._creds = creds

            self.delegated_creds = None

        else:
            # we already have a context in progress, just inspect it
            if self.locally_initiated:
                self.usage = 'initiate'
            else:
                self.usage = 'accept'

    # TODO(directxman12): implement flag properties

    def get_mic(self, message):
        # TODO(directxman12): check flags?
        return rmessage.get_mic(self, message)

    def verify_mic(self, message, mic):
        # TODO(directxman12): implement supplementary?
        return rmessage.verify_mic(self, message, mic)

    def wrap(self, message, encrypt=True):
        res = rmessage.wrap(self, message, encrypt)

        if encrypt and not res.encrypted:
            raise excs.EncryptionNotUsed("Wrapped message was not encrypted")

        return res.message

    def unwrap(self, message):
        # TODO(directxman12): should we raise our own error here if we
        #                     expected a QoP or encryption and didn't get it?
        #                     (maybe just for decrypt?)
        # TODO(directman12): implement supplementary
        res = rmessage.unwrap(self, message)

        if (not res.encrypted and
                self.actual_flags & RequirementFlag.confidentiality):
            raise excs.EncryptionNotUsage("The context was established with "
                                          "encryption, but unwrapped message "
                                          "was not encrypted")

        return res.message

    def get_wrap_size_limit(self, desired_output_size,
                            encrypted=True):
        return rmessage.wrap_size_limit(self, desired_output_size,
                                        encrypted)

    def process_token(self, token):
        rsec_contexts.process_context_token(self, token)

    def export(self):
        return rsec_contexts.export_sec_context(self)

    INQUIRE_ARGS = ('initiator_name', 'target_name', 'lifetime',
                    'mech_type', 'flags', 'locally_init', 'complete')

    def _inquire(self, **kwargs):
        if not kwargs:
            default_val = True
        else:
            default_val = False

        for arg in self.INQUIRE_ARGS:
            kwargs[arg] = kwargs.get(arg, default_val)

        res = rsec_contexts.inquire_context(self, **kwargs)

        if (kwargs.get('initiator_name', False) and
                res.initiator_name is not None):
            init_name = Name(res.initiator_name)
        else:
            init_name = None

        if (kwargs.get('target_name', False) and
                res.target_name is not None):
            target_name = Name(res.target_name)
        else:
            target_name = None

        return tuples.InquireContextResult(init_name, target_name,
                                           res.lifetime, res.mech_type,
                                           res.flags, res.locally_init,
                                           res.complete)

    @property
    def lifetime(self):
        # TODO(directxman12): is this in any way different from what's
        #                     returned by inquire?
        return rsec_contexts.context_time(self)

    initiator_name = _utils.inquire_property('initiator_name')
    target_name = _utils.inquire_property('target_name')
    mech_type = _utils.inquire_property('mech_type')
    actual_flags = _utils.inquire_property('flags')
    locally_initiated = _utils.inquire_property('locally_init')

    @property
    def complete(self):
        if self._started:
            return self._inquire(complete=True).complete
        else:
            return False

    def step(self, token=None):
        if self.usage == 'accept':
            return self._acceptor_step(token=token)
        else:
            return self._initiator_step(token=token)

    def _acceptor_step(self, token):
        res = rsec_contexts.accept_sec_context(token, self._creds,
                                               self, self._channel_bindings)

        self.delegated_creds = Credentials(res.delegated_creds)

        return res.token

    def _initiator_step(self, token=None):
        # TODO(directxman12): should we have these all be properties,
        #                     or should some of them be arguments?
        res = rsec_contexts.init_sec_context(self._target_name, self._creds,
                                             self, self._mech_type,
                                             self._desired_flags,
                                             self._desired_lifetime,
                                             self._channel_bindings,
                                             token)

        return res.token

    # TODO(directxman12): add a method to force delete?

    # pickle protocol support
    def __reduce__(self):
        # the unpickle arguments to new are (base=None, token=self.export())
        return (type(self), (None, self.export()))
