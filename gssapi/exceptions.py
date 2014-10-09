# non-GSS exceptions
class GeneralError(Exception):
    MAJOR_MESSAGE = "General error"
    FMT_STR = "{maj}: {min}."

    def __init__(self, minor_message, **kwargs):
        maj_str = self.MAJOR_MESSAGE.format(**kwargs)
        err_str = self.FMT_STR.format(maj=maj_str, min=minor_message)
        super(GeneralError, self).__init__(err_str)


class UnknownUsageError(GeneralError):
    MAJOR_MESSAGE = "Unable to determine {obj} usage"


class EncryptionNotUsed(GeneralError):
    MAJOR_MESSAGE = "Confidentiality was requested, but not used"
