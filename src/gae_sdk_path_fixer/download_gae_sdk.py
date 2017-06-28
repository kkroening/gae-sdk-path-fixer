#!/usr/bin/env python
import argparse
from . import DEFAULT_DIR, DEFAULT_VERSION, download_sdk


parser = argparse.ArgumentParser(description='Download App Engine SDK')
parser.add_argument('--dir', help='Directory to download to', default=DEFAULT_DIR)
parser.add_argument('--version', help='Version string', default=DEFAULT_VERSION)


def main():
    args = parser.parse_args()
    download_sdk(args.dir, args.version)


if __name__ == '__main__':
    main()
