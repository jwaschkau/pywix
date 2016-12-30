# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import sys
import tempfile
import zipfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

# Uses sys.platform keys, but removes the 2 from linux2
# Adding a new platform means implementing unpacking in 'DownloadPandocCommand'
# and adding the URL here
PANDOC_URLS = {
    'win32': 'https://www.nuget.org/api/v2/package/WiX',
}

INCLUDED_PANDOC_VERSION = '3.10.3'

DEFAULT_TARGET_FOLDER = {
    'win32': '~\\AppData\\Local\\WiX',
}


def find_installed_dir(remove_existing=False):
    # Find the Program Files folder
    if sys.platform == 'win32':
        if 'PROGRAMFILES(x86)' in os.environ:
            program_files = os.environ['PROGRAMFILES(x86)']
        else:
            program_files = os.environ['PROGRAMFILES']

        for program_folder in os.listdir(program_files):
            if program_folder.startswith('WiX Toolset'):
                wix_folder = os.path.join(program_files, program_folder)
                break

        if not wix_folder:
            wix_folder = DEFAULT_TARGET_FOLDER[sys.platform]
            if wix_folder.startswith('~\\'):
                wix_folder = os.path.join(os.environ['UserProfile'], wix_folder[2:])

            if remove_existing:
                shutil.rmtree(wix_folder, ignore_errors=True)

        return wix_folder
    else:
        raise RuntimeError('Cannot handle your platform (only Windows).')


def _handle_win32(filename, target_folder):
    print('* Unpacking %s to tempfolder...' % (filename))

    tempfolder = tempfile.mkdtemp()

    with zipfile.ZipFile(filename) as file:
        file.extractall(tempfolder)

    tools_dir = os.path.join(tempfolder, 'tools')

    for file in os.listdir(tools_dir):
        shutil.move(os.path.join(tools_dir, file), target_folder)

    # remove temporary dir
    shutil.rmtree(tempfolder)

    print('* Done.')


def download_wix(url=None, target_folder=None, refresh=False):
    '''Download and unpack pandoc

    Downloads prebuild binaries for pandoc from `url` and unpacks it into
    `target_folder`.

    :param str url: URL for the to be downloaded pandoc binary distribution for
        the platform under which this python runs. If no `url` is give, uses
        the latest available release at the time pywix was released.

    :param str target_folder: directory, where the binaries should be installed
        to. If no `target_folder` is give, uses a platform specific user
        location: `~/bin` on Linux, `~/Applications/pandoc` on Mac OS X, and
        `~\\AppData\\Local\\Pandoc` on Windows.
    '''
    if os.path.exists(target_folder):
        if refresh:
            shutil.rmtree(target_folder)
        else:
            return

    pf = sys.platform

    if pf not in PANDOC_URLS:
        raise RuntimeError('Cannot handle your platform (only Windows).')

    if url is None:
        url = PANDOC_URLS[pf]

    filename = url.split('/')[-1]
    if os.path.isfile(filename):
        print('* Using already downloaded file %s' % (filename))
    else:
        print('* Downloading pandoc from %s ...' % url)
        # https://stackoverflow.com/questions/30627937/tracebaclk-attributeerroraddinfourl-instance-has-no-attribute-exit
        response = urlopen(url)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    if target_folder is None:
        target_folder = DEFAULT_TARGET_FOLDER[pf]
    target_folder = os.path.expanduser(target_folder)

    # Make sure target folder exists...
    try:
        os.makedirs(target_folder)
    except OSError:
        pass  # dir already exists...

    unpack = globals().get('_handle_' + pf)
    assert unpack is not None, 'Cannot handle download, only Windows is supported.'
    unpack(filename, target_folder)

    os.remove(filename)
