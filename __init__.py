#!/usr/bin/env python3
# import dwdopendata

from ._version import get_versions
v = get_versions()
__version__ = v['version']
del get_versions, v

# module level docsting
__doc__ = """ a library for python3 to integrate data from https://opendata.dwd.de/

"""