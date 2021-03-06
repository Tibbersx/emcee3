# -*- coding: utf-8 -*-

from __future__ import division, print_function

from ... import moves
from .test_proposal import _test_normal, _test_uniform

__all__ = ["test_normal_stretch", "test_uniform_stretch",
           "test_nsplits_stretch"]


def test_normal_stretch(**kwargs):
    _test_normal(moves.StretchMove(), **kwargs)


def test_uniform_stretch(**kwargs):
    _test_uniform(moves.StretchMove(), **kwargs)


def test_nsplits_stretch(**kwargs):
    _test_normal(moves.StretchMove(nsplits=5), **kwargs)


def test_randomize_stretch(**kwargs):
    _test_normal(moves.StretchMove(randomize_split=True), **kwargs)
