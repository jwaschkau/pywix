#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
from distutils.command.build import build as build_class

from setuptools import setup, Command, find_packages

import versioneer

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


class DownloadWixCommand(Command):
    """Download wix"""

    description = "downloads a wix release and adds it to the package"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def target_folder():
        from pywix.wix_download import wix_folder
        return wix_folder()

    def run(self):
        from pywix.wix_download import download_wix
        download_wix(target_folder=self.target_folder())

cmdclass = {'download_wix': DownloadWixCommand}
cmdclass.update(versioneer.get_cmdclass())
sdist_class = cmdclass['sdist']


class SourceDistCommand(sdist_class):
    def run(self):
        print('Removing WiX files')
        shutil.rmtree(DownloadWixCommand.target_folder(), ignore_errors=True)
        sdist_class.run(self)


class BuildCommand(build_class):
    def run(self):
        build_class.run(self)
        self.run_command('download_wix')


cmdclass['sdist'] = SourceDistCommand
cmdclass['build'] = BuildCommand

setup(
    name='pywix',
    version=versioneer.get_version(),
    url='https://github.com/xoviat/pywix',
    license = 'MIT',
    description='Thin wrapper for WiX modelled on pypandoc.',
    author='Mars Galactic',
    author_email='xoviat@noreply.users.github.com',
    packages=find_packages(),
    package_data={'pywix': ['files/*']},
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    install_requires = ['setuptools', 'pip>=8.1.0', 'wheel>=0.25.0'],
    classifiers=[],
    cmdclass=cmdclass)
