# GAE SDK Path Fixer: detect AppEngine SDK and fix Python sys.path

## Overview

Does this look familiar?
```
>>> from google.appengine.ext import ndb
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named google.appengine.ext
```

If so, you're probably working with Google App Engine in Python and have some path setup to do!

(One notable case where this happens is attempting to run unit tests for a python GAE project)

You can fix your paths the hard way by copying the ugly `runner.py` script from the [Local Unit Testing for Python](https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting?csw=1) tutorial, or you can let `gae-sdk-path-fixer` take care of it for you in a consistent manner.

## Quickstart

First, install `gae-sdk-path-fixer` (e.g. in a virtualenv):
```
pip install gae-sdk-path-fixer
```

Then import the `gae_sdk_path_fixer` module and call `fix_paths()` (e.g. in `tests/__init__.py`):
```
import gae_sdk_path_fixer
gae_sdk_path_fixer.fix_paths()
```

Now, if you attempt to run your code and the appengine SDK isn't found, you'll get a helpful error message:
```
App Engine SDK not found!  Please do one of the following:
- Set $APPENGINE_SDK
- Make sure `dev_appserver.py` on $PATH
- Download the SDK to ./appengine_sdk: `download-gae-sdk [--version 1.9.56] [--dir appengine_sdk]`
```

Once you've followed the instructions in whatever manner works best for you, rerun the code and import appengine dependencies to your heart's content!

## Auto-downloading

If you'd rather make your tools just work without any user intervention, `gae-sdk-path-fixer` can be instructed to automatically download the SDK if it's not found:
```
import gae_sdk_path_fixer
gae_sdk_path_fixer.fix_paths(auto_download=True)
```

Optionally specify a version to download with e.g. `version='1.9.56'`.

## Additional options:

The `fix_paths` functions takes the following optional arguments:
- `auto_download`: if `True`, automatically download App Engine SDK if not found.
- `default_dir`: default directory to look in; defaults to `./appengine_sdk`.
- `version`: default version; defaults to `1.9.56`.
