# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["izip", "imap", "iteritems", "xrange"]

try:
    from itertools import izip, imap

except ImportError:
    izip = zip
    imap = map

    def iteritems(d):
        return d.items()

else:
    def iteritems(d):
        return d.iteritems()

try:
    xrange = xrange
except NameError:
    xrange = range
