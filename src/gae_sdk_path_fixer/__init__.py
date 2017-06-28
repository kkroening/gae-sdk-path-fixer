from distutils.spawn import find_executable
from StringIO import StringIO
from textwrap import dedent
from zipfile import ZipFile
import os
import shutil
import subprocess
import sys


DEFAULT_DIR = os.path.join('.', 'appengine_sdk')
DEFAULT_VERSION = '1.9.56'
DOWNLOAD_URL_FORMAT = 'https://storage.googleapis.com/appengine-sdks/featured/google_appengine_{}.zip'


def _download_with_progress(url, width=80):
    try:
        # Python 2
        from urllib2 import urlopen
    except ImportError:
        # Python 3
        from urllib.request import urlopen

    response = urlopen(url)
    total_size = response.headers.get('content-length')
    if total_size is None:
        data = response.read()
    else:
        total_size = int(total_size)
        data = ''
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            data += chunk
            done_percentage = float(len(data)) / float(total_size)
            done_bars = int(width * done_percentage)
            empty_bars = width - done_bars
            sys.stderr.write('\r[{}{}] {:.2f} / {:.2f} MB'.format('=' * done_bars, ' ' * empty_bars,
                float(len(data)) / (1024**2), (float(total_size) / (1024**2))))
            sys.stderr.flush()
    sys.stderr.write('\n')
    return data


def download_sdk(directory=DEFAULT_DIR, version=DEFAULT_VERSION):
    if os.path.exists(directory):
        sys.stderr.write("File or directory already exists: {}\n".format(directory))
    else:
        url = DOWNLOAD_URL_FORMAT.format(version)
        sys.stderr.write('Downloading appengine SDK from {}\n'.format(url))
        data = _download_with_progress(url)
        sys.stderr.write('Extracting to {}\n'.format(directory))
        ZipFile(StringIO(data)).extractall(directory)

        appengine_dir = os.path.join(directory, 'google_appengine')
        for file in os.listdir(appengine_dir):
            shutil.move(os.path.join(appengine_dir, file), directory)
        os.rmdir(appengine_dir)


def _get_error_message(version, default_dir):
    return dedent('''
        App Engine SDK not found!  Please do one of the following:
        - Set $APPENGINE_SDK
        - Make sure `dev_appserver.py` on $PATH
        - Download the SDK to {default_dir}: `download-gae-sdk [--version {version}] [directory]`
    '''.format(version=version, default_dir=default_dir))


def _check_env_var():
    sdk_path = os.environ.get('APPENGINE_SDK')
    if sdk_path is not None:
        if not os.path.exists(sdk_path):
            sys.stderr.write('Warning: $APPENGINE_SDK path environment variable points to invalid location: {}\n'
                .format(sdk_path))
            sdk_path = None
    return sdk_path


def _check_path():
    sdk_path = None
    das_path = find_executable('dev_appserver.py')
    das_path = das_path and os.path.realpath(das_path) # apt repository install of sdk creates symlinks in /usr/bin
    if das_path is not None:
        das_dir = os.path.dirname(das_path)
        gcloud_path = os.path.join(das_dir, 'gcloud')

        if os.path.exists(gcloud_path):
            # Deal with cloud-sdk (which keeps appengine SDK directory in a different place relative to
            # dev_appserver.py).
            das_dir = os.path.join(das_dir, '..', 'platform', 'google_appengine')
            if not os.path.exists(das_dir):
                sys.stderr.write('Warning: found gcloud dev_appserver.py but gcloud is missing appengine SDK; '
                    'running `gcloud components install app-engine-python...\n')
                sdk_path = None
                subprocess.check_call([gcloud_path, 'components', 'install', 'app-engine-python'])

            if os.path.exists(das_dir):
                sdk_path = das_dir
        else:
            sdk_path = das_dir
    return sdk_path


def _check_default_dir(auto_download, default_dir, version):
    sdk_path = None
    if os.path.exists(default_dir):
        sdk_path = default_dir
    elif auto_download:
        download_sdk(default_dir, version)
        assert os.path.exists(default_dir), 'Download failed'
        sdk_path = default_dir
    return sdk_path


def _find_or_download_sdk(auto_download, default_dir, version):
    sdk_path = _check_env_var()
    if sdk_path is None:
        sdk_path = _check_path()
    if sdk_path is None:
        sdk_path = _check_default_dir(auto_download, default_dir, version)
    return sdk_path


# From https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting?csw=1
def _fixup_paths(path):
    """Adds GAE SDK path to system path and appends it to the google path
    if that already exists."""
    # Not all Google packages are inside namespace packages, which means
    # there might be another non-namespace package named `google` already on
    # the path and simply appending the App Engine SDK to the path will not
    # work since the other package will get discovered and used first.
    # This emulates namespace packages by first searching if a `google` package
    # exists by importing it, and if so appending to its module search path.
    try:
        import google
        google.__path__.append("{0}/google".format(path))
    except ImportError:
        pass

    sys.path.insert(0, path)


def fix_paths(auto_download=False, default_dir=DEFAULT_DIR, version=DEFAULT_VERSION):
    sdk_path = _find_or_download_sdk(auto_download, default_dir, version)
    assert sdk_path is not None, _get_error_message(version, default_dir)

    os.environ['APPENGINE_SDK'] = sdk_path

    if sdk_path not in sys.path:
        _fixup_paths(sdk_path)

    already_fixed = os.path.join(sdk_path, 'lib', 'simplejson') in sys.path
    if not already_fixed:
        import dev_appserver
        sys.path[1:1] = dev_appserver._PATHS.script_paths('dev_appserver.py')  # for cherrypy, portpicker, etc.
        dev_appserver.fix_sys_path()

        from google.appengine.ext import vendor
        vendor.add(sys.prefix, index=0)
        sys.path.insert(0, '.')  # FIXME

    return sdk_path


__all__ = [
    'DEFAULT_DIR',
    'DEFAULT_VERSION',
    'download_sdk',
    'fix_paths',
]
