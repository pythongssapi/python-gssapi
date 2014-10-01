# NB(sross): something causes Python to segfault if we try to
#            `from collections import namedtuple`
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
                           ['mechs', 'init_lifetime',
                            'accept_lifetime'])

DisplayNameResult = namedtuple('DisplayNameResult',
                               ['name', 'name_type'])
