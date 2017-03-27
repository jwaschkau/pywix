import subprocess
import os


def find_go_msi():
    path = os.path.join(os.environ["ProgramFiles"], 'go-msi', 'go-msi.exe')
    if not os.path.isfile(path):
        raise RuntimeError('cannot find go-msi')

    return path


def call_go_msi(args):
    return subprocess.check_output([find_go_msi()] + args)