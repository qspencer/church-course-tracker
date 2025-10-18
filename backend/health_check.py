#!/usr/bin/env python3
import urllib.request
import sys

try:
    response = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
    if response.getcode() == 200:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception:
    sys.exit(1)
