# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["Ensemble"]

import numpy as np

from .compat import izip
from .pools import DefaultPool


class Ensemble(object):
    """
    An :class:`Ensemble` is a set of walkers (usually subclasses of
    :class:`BaseWalker`).

    :param walker:
        The walker class.

    :param coords:
        The 2-D array of walker coordinate vectors. The shape of this array
        should be `(nwalkers, ndim)`.

    :param pool: (optional)
        A pool object that exposes a map function. This is especially useful
        for parallelization.

    :param random: (optional)
        A numpy-compatible random number generator. By default, this will be
        the built-in ``numpy.random`` module but if you want the ensemble to
        own its own state, you can supply an instance of
        ``numpy.random.RandomState``.

    .. note:: Any extra arguments or keyword arguments are pass along to the
              walker initialization.

    """
    def __init__(self, walker, coords, *args, **kwargs):
        self.pool = kwargs.pop("pool", DefaultPool())
        self.random = kwargs.pop("random", np.random.RandomState())

        # Interpret the dimensions of the ensemble.
        self._coords = np.atleast_1d(coords).astype(np.float64)
        if not len(self._coords.shape) == 2:
            raise ValueError("Invalid ensemble coordinate dimensions")
        self.nwalkers, self.ndim = self._coords.shape

        # Initialize the walkers at these coordinates.
        self.walkers = list(self.pool.map(_mapping_pickler(walker, "propose"),
                                          self._coords))

        # Save the initial prior and likelihood values.
        self._lnprior = np.empty(self.nwalkers, dtype=np.float64)
        self._lnlike = np.empty(self.nwalkers, dtype=np.float64)
        for i, w in enumerate(self.walkers):
            self._lnprior[i] = w.lnprior
            self._lnlike[i] = w.lnlike
        self.acceptance = np.ones(self.nwalkers, dtype=bool)

        # Check the initial probabilities.
        if not (np.all(np.isfinite(self._lnprior))
                and np.all(np.isfinite(self._lnlike))):
            raise ValueError("Invalid (un-allowed) initial coordinates")

    def propose(self, coords, slice=slice(None)):
        """
        Given a new set of coordinates return a list of new walkers evaluated
        at these locations.

        :param coords:
            The new coordinate matrix. It should be ``(nwalkers, ndim)``.

        :param slice: (optional)
            The update can optionally only be applied to a subset of the
            walkers. This should be a ``slice`` object that can be used to
            index the walkers list.

        """
        return list(self.pool.map(_mapping_zipper("propose"),
                                  izip(self.walkers[slice], coords)))

    def update(self):
        """
        Update the coordinate matrix and probability containers given the
        current list of walkers. Moves should call this after proposing and
        accepting the walkers.

        """
        for i, w in enumerate(self.walkers):
            self._coords[i, :] = w.coords
            self._lnprior[i] = w.lnprior
            self._lnlike[i] = w.lnlike

        # Check the probabilities and make sure that no invalid samples were
        # accepted.
        if not (np.all(np.isfinite(self._coords))
                and np.all(np.isfinite(self._lnprior))
                and np.all(np.isfinite(self._lnlike))):
            raise RuntimeError("An invalid proposal was accepted")

    def __getstate__(self):
        # In order to be generally picklable, we need to discard the pool
        # object before trying.
        d = self.__dict__
        d.pop("pool", None)
        return d

    def __setstate__(self, state):
        self.__dict__ = state
        self.pool = DefaultPool()

    def __len__(self):
        return self.nwalkers

    @property
    def coords(self):
        """The coordinate vectors of the walkers."""
        return self._coords

    @property
    def lnprior(self):
        """The ln-priors of the walkers up to a constant."""
        return self._lnprior

    @property
    def lnlike(self):
        """The ln-likelihoods of the walkers up to a constant."""
        return self._lnlike

    @property
    def lnprob(self):
        """The ln-probabilities of the walker up to a constant."""
        return self._lnprior + self._lnlike


class _mapping_zipper(object):
    """
    This is a picklable helper object for the parallel ensemble mapper.

    """
    def __init__(self, method):
        self.method = method

    def __call__(self, args):
        obj, a = args
        return getattr(obj, self.method)(a)


class _mapping_pickler(object):
    """
    This is a picklable helper object for the parallel ensemble mapper.

    """
    def __init__(self, obj, method):
        self.obj = obj
        self.method = method

    def __call__(self, args):
        return getattr(self.obj, self.method)(args)
