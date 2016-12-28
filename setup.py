#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import sys

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

    def run(self):
        from pywix.wix_download import download_wix
        targetfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pywix", "files")
        download_wix(targetfolder=targetfolder)

is_build_wheel = ("bdist_wheel" in sys.argv)

if is_build_wheel:
    # we need to make sure that bdist_wheel is after is_download_wix,
    # otherwise we don't include wix in the wheel... :-(
    sys.argv.insert(1, "download_wix")
    is_download_wix = True
    pos_bdist_wheel = sys.argv.index("bdist_wheel")
    if is_download_wix:
        pos_download_wix = sys.argv.index("download_wix")
        if pos_bdist_wheel < pos_download_wix:
            raise RuntimeError("'download_wix' needs to be before 'bdist_wheel'.")
    # we also need to make sure that this version of bdist_wheel supports
    # the --plat-name argument
    try:
        import wheel
        from distutils.version import StrictVersion

        if not StrictVersion(wheel.__version__) >= StrictVersion("0.27"):
            msg = "Including wix in wheel needs wheel >=0.27 but found %s.\nPlease update wheel!"
            raise RuntimeError(msg % wheel.__version__)
    except ImportError:
        # the real error will happen further down...
        print("No wheel installed, please install 'wheel'...")
    print("forcing platform specific wheel name...")
    from distutils.util import get_platform

    sys.argv.insert(pos_bdist_wheel + 1, '--plat-name')
    sys.argv.insert(pos_bdist_wheel + 2, get_platform())

cmdclass = {'download_wix': DownloadWixCommand}
cmdclass.update(versioneer.get_cmdclass())

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
    long_description_markdown_filename='README.md'
    install_requires = ['setuptools', 'pip>=8.1.0', 'wheel>=0.25.0'],
    classifiers=[],
    cmdclass=cmdclass)
