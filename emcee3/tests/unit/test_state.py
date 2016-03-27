# -*- coding: utf-8 -*-

from __future__ import division, print_function

import numpy as np

from ...state import State

__all__ = ["test_dtype"]


def test_dtype(seed=1234):
    np.random.seed(seed)

    dtype = [
        ("__coords__", np.float64, (4, )),
        ("__log_prior__", np.float64),
        ("__log_likelihood__", np.float64),
        ("__accepted__", bool)
    ]

    coords = np.random.randn(4)
    state = State(coords)
    assert state.dtype == np.dtype(dtype)

    state = State(coords, face=10.0, blah="string", _hidden=None)
    dtype += [
        ("blah", np.unicode_, 6),
        ("face", np.float64),
    ]
    assert state.dtype == np.dtype(dtype)


def test_serialization(seed=1234):
    np.random.seed(seed)
    coords = np.random.randn(4)
    state = State(coords, 0.0, -1.5, True, face="blah")
    array = state.to_array()
    assert np.allclose(array["__coords__"], coords)
    new_state = State.from_array(array)
    assert state == new_state
