from collections import namedtuple


AcquireCredResult = namedtuple('AcquireCredResult',
                               ['creds', 'mechs', 'lifetime'])


InquireCredResult = namedtuple('InquireCredResult',
                               ['name', 'lifetime', 'usage',
                                'mechs'])


InquireCredByMechResult = namedtuple('InquireCredByMechResult',
                                     ['name', 'init_lifetime',
                                      'accept_lifetime', 'usage'])


AddCredResult = namedtuple('AddCredResult',
                           ['creds', 'mechs', 'init_lifetime',
                            'accept_lifetime'])


DisplayNameResult = namedtuple('DisplayNameResult',
                               ['name', 'name_type'])


VerifyMICResult = namedtuple('VerifyMICResult',
                             ['valid', 'qop', 'major_status',
                              'minor_status'])


WrapResult = namedtuple('WrapResult',
                        ['message', 'encrypted'])


UnwrapResult = namedtuple('UnwrapResult',
                          ['message', 'encrypted', 'qop'])


AcceptSecContextResult = namedtuple('AcceptSecContextResult',
                                    ['context', 'initiator_name',
                                     'mech', 'token', 'flags', 'lifetime',
                                     'delegated_creds', 'more_steps'])


InitSecContextResult = namedtuple('InitSecContextResult',
                                  ['context', 'mech', 'flags', 'token',
                                   'lifetime', 'more_steps'])


InquireContextResult = namedtuple('InquireContextResult',
                                  ['initiator_name', 'target_name',
                                   'lifetime', 'mech', 'flags',
                                   'locally_init', 'complete'])

StoreCredResult = namedtuple('StoreCredResult',
                             ['mechs', 'usage'])
