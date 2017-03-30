import os
import subprocess
import versioneer
import sys

from multiprocessing import Process
from setuptools import setup, find_packages
from setuptools.command.install import install
from go_msi import find_go_msi, find_wix_toolset


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

    for command in commands:
        subprocess.call(
            [
                b'powershell', b'-NoProfile', b'-NoLogo', b'-ExecutionPolicy',
                b'Bypass', b'-c', command
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
            timeout=120)


class InstallCommand(install):
    """
    Installs the wix files using chocolatey.
    """

    def run(self):
        super().run()

        commands = []

        try:
            find_go_msi()
        except RuntimeError:
            commands.append(b'choco install -y --allow-empty-checksums go-msi')

        try:
            find_wix_toolset()
        except RuntimeError:
            commands.append(
                b'choco install -y --allow-empty-checksums wixtoolset')

        if commands:
            if not has_admin():
                raise RuntimeError(
                    'pywix installation requires administrative rights')

            write_commands([
                b'iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex',
            ] + commands)


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
