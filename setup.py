import os
import subprocess
import versioneer
import threading
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from go_msi import find_go_msi


def has_admin():
    if os.name == 'nt':
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            temp = os.listdir(
                os.sep.join(
                    [os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
        except Exception:
            return (os.environ['USERNAME'], False)
        else:
            return (os.environ['USERNAME'], True)
    else:
        if 'SUDO_USER' in os.environ and os.geteuid() == 0:
            return (os.environ['SUDO_USER'], True)
        else:
            return (os.environ['USERNAME'], False)


def write_commands(commands):
    powershell = subprocess.Popen(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass'],
        stdin=subprocess.PIPE,
        stdout=sys.stdout)

    def write_async(powershell, commands):
        powershell.stdin.write(b'\r\n'.join(commands + [b'exit']))
        powershell.stdin.write(b'\r\n\r\n')

    t = threading.Thread(target=write_async, args=(powershell, commands))
    t.start()
    powershell.wait(timeout=60)


class InstallCommand(install):
    """
    Installs the wix files using chocolatey.
    """

    def run(self):
        super().run()

        try:
            find_go_msi()
            return
        except RuntimeError:
            pass

        if not has_admin():
            raise RuntimeError(
                'pywix installation requires administrative rights')

        sets = [
            [
                b'iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex',
            ],
            [
                b'choco install -y --allow-empty-checksums wixtoolset',
                b'choco install -y --allow-empty-checksums go-msi',
            ],
        ]

        for commands in sets:
            write_commands(commands)


cmdclass = versioneer.get_cmdclass()
cmdclass['install'] = InstallCommand

setup(
    name='pywix',
    version=versioneer.get_version(),
    url='https://github.com/xoviat/pywix',
    license='MIT',
    description='Thin wrapper for WiX modelled on pypandoc.',
    author='Mars Galactic',
    author_email='xoviat@noreply.users.github.com',
    packages=find_packages(),
    # setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    install_requires=['setuptools', 'pip>=8.1.0', 'wheel>=0.25.0'],
    classifiers=[],
    cmdclass=cmdclass)
