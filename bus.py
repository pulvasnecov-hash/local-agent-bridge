#!/usr/bin/env python3
"""Compatibility entry point for the shared local message board."""
import sys

from bridge import main

if __name__ == "__main__":
    raise SystemExit(main(["bus", *sys.argv[1:]]))
