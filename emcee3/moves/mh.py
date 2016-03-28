# -*- coding: utf-8 -*-

from __future__ import division, print_function
import numpy as np

__all__ = ["MHMove"]


class MHMove(object):
    """
    A general Metropolis-Hastings proposal.

    :param proposal:
        The proposal function. It should take 2 arguments: a numpy-compatible
        random number generator and a ``(K, ndim)`` list of coordinate
        vectors. This function should return the proposed position and the
        log-ratio of the proposal probabilities (:math:`\ln q(x;\,x^\prime) -
        \ln q(x^\prime;\,x)` where :math:`x^\prime` is the proposed
        coordinate).

    :param ndim: (optional)
        If this proposal is only valid for a specific dimension of parameter
        space, set that here.

    """
    def __init__(self, proposal_function, ndim=None):
        self.ndim = ndim
        self.proposal = proposal_function

    def update(self, ensemble):
        """
        Execute a single step starting from the given :class:`Ensemble` and
        updating it in-place.

        :param ensemble:
            The starting :class:`Ensemble`.

        :return ensemble:
            The same ensemble updated in-place.

        """
        # Check to make sure that the dimensions match.
        ndim = ensemble.ndim
        if self.ndim is not None and self.ndim != ndim:
            raise ValueError("Dimension mismatch in proposal")

        # Compute the proposal.
        q, factor = self.proposal(ensemble.random, ensemble.coords)
        states = ensemble.propose(q)

        # Loop over the walkers and update them accordingly.
        for i, state in enumerate(states):
            lnpdiff = (
                state.log_probability -
                ensemble.walkers[i].log_probability +
                factor[i]
            )
            if lnpdiff > 0.0 or ensemble.random.rand() < np.exp(lnpdiff):
                state.accepted = True

        # Update the ensemble's coordinates and log-probabilities.
        ensemble.update(states)
        return ensemble
