import os
import subprocess

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

__wix_path = None


def _ensure_wix_path():
    global __wix_path

    if __wix_path is None:
        __wix_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")


def call_wix_command(args):
    _ensure_wix_path()
    executable = os.path.join(__wix_path, args[0])
    if not executable.endswith('.exe'):
        executable += '.exe'
    args[0] = executable

    return subprocess.check_call(args)
