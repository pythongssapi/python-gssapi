"""
Using GSSAPI on Windows requires having an installation of Kerberos for Windows
(KfW) available in the user's PATH. This module should be imported before
anything else to check for that installation, add it to the PATH if necessary,
and throw any errors before they manifest as cryptic missing DLL errors later
down the import tree.
"""

import os
import shutil
import ctypes

#: Path to normal KfW installed bin folder
KFW_BIN = os.path.join(
    os.environ.get('ProgramFiles', r'C:\Program Files'),
    'MIT', 'Kerberos', 'bin',
)
#: Download location for KfW
KFW_DL = "https://web.mit.edu/KERBEROS/dist"


def kfw_available():
    """Return if the main GSSAPI DLL for KfW can be loaded"""
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
    DLL directories/PATH if necessary. In the case that it can't be located,
    raise an error.
    """
    if kfw_available():
        return  # All set, necessary DLLs should be available

    if os.path.exists(KFW_BIN):  # In standard location
        try:  # to use Python 3.8's DLL handling
            os.add_dll_directory(KFW_BIN)
        except AttributeError:  # <3.8, use PATH
            os.environ['PATH'] += os.pathsep + KFW_BIN
        if kfw_available():
            return

    # Check if kinit is in the PATH which should lead us to the bin folder
    kinit_path = shutil.which('kinit')  # KfW provided binary
    if kinit_path:  # Non-standard install location
        try:  # Most likely >=3.8, otherwise it would have been found already
            os.add_dll_directory(os.path.dirname(kinit_path))
        except AttributeError:  # <3.8, corrupted installation?
            pass
        else:
            if kfw_available():
                return

    error_not_found()


if os.name == 'nt':  # Make sure we have the required DLLs
    configure_windows()
