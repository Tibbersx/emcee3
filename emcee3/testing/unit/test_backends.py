# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["test_hdf", "test_hdf_reload"]

import numpy as np
from ... import backends, Sampler, Ensemble
from ...compat import izip
from ..common import NormalWalker, TempHDFBackend


def run_sampler(backend, nwalkers=32, ndim=3, nsteps=5, seed=1234):
    rnd = np.random.RandomState()
    rnd.seed(seed)
    coords = rnd.randn(nwalkers, ndim)
    ensemble = Ensemble(NormalWalker(1.0), coords, random=rnd)
    sampler = Sampler(backend=backend)
    list(sampler.sample(ensemble, nsteps))
    return sampler


def test_hdf():
    # Run a sampler with the default backend.
    sampler1 = run_sampler(backends.DefaultBackend())

    with TempHDFBackend() as backend:
        sampler2 = run_sampler(backend)

        # Check all of the components.
        for k in ["coords", "lnprior", "lnlike", "lnprob",
                  "acceptance_fraction"]:
            a = getattr(sampler1, k)
            b = getattr(sampler2, k)
            assert np.allclose(a, b), "inconsistent {0}".format(k)


def test_hdf_reload():
    with TempHDFBackend() as backend1:
        run_sampler(backend1)

        # Load the file using a new backend object.
        backend2 = backends.HDFBackend(backend1.filename, backend1.name)

        # Check all of the components.
        for k in ["coords", "lnprior", "lnlike", "lnprob",
                  "acceptance_fraction"]:
            a = getattr(backend1, k)
            b = getattr(backend2, k)
            assert np.allclose(a, b), "inconsistent {0}".format(k)
