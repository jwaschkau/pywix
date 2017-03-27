import subprocess
import versioneer

from setuptools import setup, find_packages
from setuptools.command.install import install


class InstallCommand(install):
    """
    Installs the wix files using chocolatey.
    """

    def run(self):
        commands = [
            'Set-ExecutionPolicy RemoteSigned',
            'iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex',
            'choco install -y wixtoolset',
            'choco install -y go-msi',
            'exit',
        ]

        powershell = subprocess.Popen(['powershell'])
        powershell.stdin.writelines(commands)
        powershell.stdin.write('\n')


cmdclass = versioneer.get_cmdclass()
cmdclass['install'] = install

setup(
    name='pywix',
    version=versioneer.get_version(),
    url='https://github.com/xoviat/pywix',
    license='MIT',
    description='Thin wrapper for WiX modelled on pypandoc.',
    author='Mars Galactic',
    author_email='xoviat@noreply.users.github.com',
    packages=find_packages(),
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    install_requires=['setuptools', 'pip>=8.1.0', 'wheel>=0.25.0'],
    classifiers=[],
    cmdclass=cmdclass)
