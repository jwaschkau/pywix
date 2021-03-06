import os
import subprocess


def program_files_list():
    x86 = os.environ["ProgramFiles(x86)"]
    x64 = os.environ["ProgramFiles"]

    if ' (x86)' in x64:
        # We're on 32 bit
        x86 = x64
        x64 = x64.replace(' (x86)', '')

    return [x86, x64]


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def find_wix_toolset():
    path = ''
    for program_files in program_files_list():

        try:
            wix = [
                folder for folder in os.listdir(program_files)
                if folder.startswith('WiX Toolset')
            ][0]

            path = os.path.join(program_files, wix, 'bin', 'candle.exe')

            print('trying: {}'.format(path))

            if os.path.isfile(path):
                break
        except IndexError:
            pass

    # if not found, check the path
    if not path or not os.path.isfile(path):
        path = which('candle.exe')

    if not path or not os.path.isfile(path):
        raise RuntimeError('cannot find wix toolset')

    return os.path.dirname(path)


def find_go_msi():
    path = ''
    for program_files in program_files_list():
        path = os.path.join(program_files, 'go-msi', 'go-msi.exe')

        print('trying: {}'.format(path))

        if os.path.isfile(path):
            break

    # if not found, check the path
    if not path or not os.path.isfile(path):
        path = which('go-msi.exe')

    if not path or not os.path.isfile(path):
        raise RuntimeError('cannot find go-msi')

    return path


def call_go_msi(args):
    env = os.environ.copy()
    env['PATH'] += ';{}'.format(find_wix_toolset())

    return subprocess.check_output([find_go_msi()] + args, env=env)


def call_go_msi_command(command, params):
    args = [command]
    for key, value in params.items():
        args.append('--{}'.format(key))
        if value != True:
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


def to_rtf(**kwargs):
    """
    NAME:
    go-msi to-rtf - Write RTF formatted file

    USAGE:
    go-msi to-rtf [command options] [arguments...]

    OPTIONS:
    --src value, -s value  Path to a text file
    --out value, -o value  Path to the RTF generated file
    --reencode, -e         Also re encode UTF-8 to Windows1252 charset
    """
    return call_go_msi_command('to-rtf', kwargs)


from ._version import get_versions

__version__ = get_versions()['version']
del get_versions
