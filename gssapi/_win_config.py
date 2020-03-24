"""
Using GSSAPI on Windows requires having an installation of Kerberos for Windows
(KfW) available in the user's PATH. This module should be imported before
anything else to check for that installation, add it to the PATH if necessary,
and throw any errors before they manifest as cryptic missing DLL errors later
down the import tree.
"""

import os
import ctypes

#: Path to normal KfW installed bin folder
KFW_BIN = os.path.join(
    os.environ.get('ProgramFiles', r'C:\Program Files'),
    'MIT', 'Kerberos', 'bin',
)
#: Download location for KfW
KFW_DL = "https://web.mit.edu/KERBEROS/dist"


def k4w_in_path():
    """Return if the main GSSAPI DLL for KfW is available in the PATH"""
    try:  # to load the main GSSAPI DLL
        ctypes.WinDLL('gssapi64.dll')
    except OSError:  # DLL is not in PATH
        return False
    else:  # DLL is in PATH, everything should work
        return True


def error_not_found():
    """Raise an OSError detailing that KfW is missing and how to get it"""
    raise OSError(
        "Could not find KfW installation. Please download and install "
        "the 64bit Kerberos for Windows MSI from %s and ensure the "
        "'bin' folder (%s) is in your PATH."
        % (KFW_DL, KFW_BIN)
    )


def configure_windows():
    """
    Validate that KfW appears to be installed correctly and add it to the
    PATH if necessary. In the case that it can't be located, raise an error.
    """
    if k4w_in_path():
        return  # All set, necessary DLLs should be available
    if os.path.exists(KFW_BIN):  # In standard location
        os.environ['PATH'] += os.pathsep + KFW_BIN
        if k4w_in_path():
            return
    error_not_found()


if os.name == 'nt':  # Make sure we have the required DLLs
    configure_windows()
