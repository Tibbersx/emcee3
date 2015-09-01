# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["test_normal_hmc", "test_normal_hmc_nd"]

from ... import moves
from .test_proposal import _test_normal


def test_normal_hmc(**kwargs):
    _test_normal(moves.HMCMove(100, 0.05), nsteps=200, check_acceptance=False)


def test_normal_hmc_nd(**kwargs):
    _test_normal(moves.HMCMove(100, 0.05), ndim=3, nsteps=200,
                 check_acceptance=False)
