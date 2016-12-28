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
# Adding a new platform means implementing unpacking in "DownloadPandocCommand"
# and adding the URL here
PANDOC_URLS = {
    "win32": "https://www.nuget.org/api/v2/package/WiX",
}

INCLUDED_PANDOC_VERSION = "3.10.3"

DEFAULT_TARGET_FOLDER = {
    "win32": "~\\AppData\\Local\\WiX",
}


def _handle_win32(filename, targetfolder):
    print("* Unpacking %s to tempfolder..." % (filename))

    tempfolder = tempfile.mkdtemp()

    with zipfile.ZipFile(filename) as file:
        file.extractall(tempfolder)

    tools_dir = os.path.join(tempfolder, 'tools')

    for file in os.listdir(tools_dir):
        shutil.move(os.path.join(tools_dir, file), targetfolder)

    # remove temporary dir
    shutil.rmtree(tempfolder)

    print("* Done.")


def download_wix(url=None, targetfolder=None):
    """Download and unpack pandoc

    Downloads prebuild binaries for pandoc from `url` and unpacks it into
    `targetfolder`.

    :param str url: URL for the to be downloaded pandoc binary distribution for
        the platform under which this python runs. If no `url` is give, uses
        the latest available release at the time pywix was released.

    :param str targetfolder: directory, where the binaries should be installed
        to. If no `targetfolder` is give, uses a platform specific user
        location: `~/bin` on Linux, `~/Applications/pandoc` on Mac OS X, and
        `~\\AppData\\Local\\Pandoc` on Windows.
    """
    pf = sys.platform

    if pf not in PANDOC_URLS:
        raise RuntimeError("Can't handle your platform (only Windows).")

    if url is None:
        url = PANDOC_URLS[pf]

    filename = url.split("/")[-1]
    if os.path.isfile(filename):
        print("* Using already downloaded file %s" % (filename))
    else:
        print("* Downloading pandoc from %s ..." % url)
        # https://stackoverflow.com/questions/30627937/tracebaclk-attributeerroraddinfourl-instance-has-no-attribute-exit
        response = urlopen(url)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    if targetfolder is None:
        targetfolder = DEFAULT_TARGET_FOLDER[pf]
    targetfolder = os.path.expanduser(targetfolder)

    # Make sure target folder exists...
    try:
        os.makedirs(targetfolder)
    except OSError:
        pass  # dir already exists...

    unpack = globals().get("_handle_" + pf)
    assert unpack is not None, "Can't handle download, only Windows is supported."
    unpack(filename, targetfolder)
