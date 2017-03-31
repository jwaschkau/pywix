import os
import subprocess

from go_msi import find_wix_toolset


def call_wix_command(args):
    """
    this function is deprecated.
    """

    executable = os.path.join(find_wix_toolset(), args[0])
    if not executable.endswith('.exe'):
        executable += '.exe'
    args[0] = executable

    return subprocess.check_call(args)