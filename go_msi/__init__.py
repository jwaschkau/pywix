import subprocess
import os


def find_go_msi():
    path = os.path.join(os.environ["ProgramFiles"], 'go-msi', 'go-msi.exe')
    if not os.path.isfile(path):
        raise RuntimeError('cannot find go-msi')

    return path


def call_go_msi(args):
    return subprocess.check_output([find_go_msi()] + args)


def call_go_msi_command(command, params):
    args = [command]
    for key, value in params.items():
        args.append('--{}'.format(key))
        args.append(value)

    return call_go_msi(args)


def make(**kwargs):
    """
    NAME:
    go-msi make - All-in-one command to make MSI files

    USAGE:
    go-msi make [command options] [arguments...]

    OPTIONS:
    --path value, -p value     Path to the wix manifest file (default: "wix.json")
    --src value, -s value      Directory path to the wix templates files (default: "/home/mh-cbon/gow/bin/templates")
    --out value, -o value      Directory path to the generated wix cmd file (default: "/tmp/go-msi492954495")
    --arch value, -a value     A target architecture, amd64 or 386 (ia64 is not handled)
    --msi value, -m value      Path to write resulting msi file to
    --version value            The version of your program
    --license value, -l value  Path to the license file
    --keep, -k                 Keep output directory containing build files (useful for debug)
    """
    return call_go_msi_command('make', kwargs)


def choco(**kwargs):
    """
    NAME:
    go-msi choco - Generate a chocolatey package of your msi files

    USAGE:
    go-msi choco [command options] [arguments...]

    OPTIONS:
    --path value, -p value           Path to the wix manifest file (default: "wix.json")
    --src value, -s value            Directory path to the wix templates files (default: "/home/mh-cbon/gow/bin/templates/choco")
    --version value                  The version of your program
    --out value, -o value            Directory path to the generated chocolatey build file (default: "/tmp/go-msi341502273")
    --input value, -i value          Path to the msi file to package into the chocolatey package
    --changelog-cmd value, -c value  A command to generate the content of the changlog in the package
    --keep, -k                       Keep output directory containing build files (useful for debug)
    """
    return call_go_msi_command('choco', kwargs)


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
