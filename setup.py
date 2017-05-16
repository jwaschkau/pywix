import os
import subprocess
import sys
import textwrap

from setuptools import setup, find_packages
from setuptools.command.install import install
from distutils.core import Command

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

        if (sys.version_info > (3, 2)):
            # only python > 3.2 has the timeout parameter
            subprocess.call(
                [
                    'powershell', '-NoProfile', '-NoLogo', '-ExecutionPolicy',
                    'Bypass', '-c', command
                ],
                stdout=sys.stdout,
                stderr=sys.stderr,
                timeout=200)
        else:
            subprocess.call(
                [
                    'powershell', '-NoProfile', '-NoLogo', '-ExecutionPolicy',
                    'Bypass', '-c', command
                ],
                stdout=sys.stdout,
                stderr=sys.stderr)


class InstallCommand(install):
    """
    Installs the wix files using chocolatey.
    """

    def run(self):
        from go_msi import find_go_msi, find_wix_toolset
        install.run(self)  # Compatibility with python2 because class is oldstyle with py2

        commands = []

        try:
            find_go_msi()
        except RuntimeError:
            commands.append('choco install -y --allow-empty-checksums go-msi')

        try:
            find_wix_toolset()
        except RuntimeError:
            commands.append(
                'choco install -y --allow-empty-checksums wixtoolset')

        if commands:
            if not has_admin():
                raise RuntimeError(
                    textwrap.dedent('''
                    pywix needs to install the WiX toolset and/or go_msi, which 
                    requires administrative rights
                    ''').strip())

            write_commands([
                'iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex',
            ] + commands)

            # now these should work; fail fast
            find_go_msi()
            find_wix_toolset()


class FakeBdistWheelCommand(Command):
    """Fails the bdist_wheel command"""

    def run(self):
        raise Exception('bdist_wheel is unsupported')


setup(
    name='pywix',
    url='https://github.com/xoviat/pywix',
    license='MIT',
    description='Thin wrapper for WiX modelled on pypandoc.',
    author='Mars Galactic',
    author_email='xoviat@noreply.users.github.com',
    long_description_markdown_filename='README.md',
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=[
        'setuptools-markdown',
        'setuptools_scm',
    ],
    install_requires=[
        'setuptools',
        'pip>=8.1.0',
        'wheel>=0.25.0',
        'backports.functools_lru_cache;python_version<"3.0"',
    ],
    cmdclass={
        'bdist_wheel': FakeBdistWheelCommand,
        'install': InstallCommand,
    })
