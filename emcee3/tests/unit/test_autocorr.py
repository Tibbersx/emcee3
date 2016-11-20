# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pytest
import numpy as np
from ...autocorr import integrated_time, AutocorrError

__all__ = ["test_nd", "test_too_short"]


def get_chain(seed=1234, ndim=3, N=100000):
    np.random.seed(seed)
    a = 0.9
    x = np.empty((N, ndim))
    x[0] = np.zeros(ndim)
    for i in range(1, N):
        x[i] = x[i-1] * a + np.random.rand(ndim)
    return x


def test_1d(seed=1234, ndim=1, N=150000, c=6):
    x = get_chain(seed=seed, ndim=ndim, N=N)
    tau, M = integrated_time(x, c=c, full_output=True)
    assert np.all(M > c * tau)
    assert np.all(np.abs(tau - 19.0) / 19. < 0.2)


def test_nd(seed=1234, ndim=3, N=150000):
    x = get_chain(seed=seed, ndim=ndim, N=N)
    tau = integrated_time(x)
    assert np.all(np.abs(tau - 19.0) / 19. < 0.2)


def test_too_short(seed=1234, ndim=3, N=500):
    x = get_chain(seed=seed, ndim=ndim, N=N)
    with pytest.raises(AutocorrError):
        integrated_time(x)
    with pytest.raises(AutocorrError):
        integrated_time(x, low=100)
    tau = integrated_time(x, quiet=True)
