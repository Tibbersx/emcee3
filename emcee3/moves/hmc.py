# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["HamiltonianMove"]

import numpy as np

from ..compat import izip, xrange


class _hmc_vector(object):

    def __init__(self, cov):
        self.cov = cov
        self.inv_cov = 1.0 / cov

    def sample(self, random, *shape):
        return random.randn(*shape) * np.sqrt(self.inv_cov)

    def apply(self, x):
        return self.cov * x


class _hmc_matrix(object):

    def __init__(self, cov):
        self.cov = cov
        self.inv_cov = np.linalg.inv(self.cov)

    def sample(self, random, *shape):
        return random.multivariate_normal(np.zeros(shape[-1]),
                                          self.inv_cov,
                                          *(shape[:-1]))

    def apply(self, x):
        return np.dot(self.cov, x)


class _hmc_wrapper(object):

    def __init__(self, model, cov, epsilon, nsteps=None):
        self.model = model
        self.nsteps = nsteps
        self.epsilon = epsilon
        if len(np.atleast_1d(cov).shape) == 2:
            self.cov = _hmc_matrix(np.atleast_2d(cov))
        else:
            self.cov = _hmc_vector(np.asarray(cov))

    def __call__(self, args):
        current_state, current_p = args

        # Sample the initial momentum.
        current_q = current_state.coords
        q = current_q
        p = current_p

        # First take a half step in momentum.
        try:
            current_state.grad_lnprob
        except AttributeError:
            current_state = self.model.get_state(q, compute_grad=True)
        p = p + 0.5 * self.epsilon * current_state.grad_lnprob

        # Alternate full steps in position and momentum.
        for i in xrange(self.nsteps):
            # First, a full step in position.
            q = q + self.epsilon * self.cov.apply(p)

            # Then a full step in momentum.
            if i < self.nsteps - 1:
                state = self.model.get_state(q, compute_grad=True)
                p = p + self.epsilon * state.grad_lnprob

        # Finish with a half momentum step to synchronize with the position.
        state = self.model.get_state(q, compute_grad=True)
        p = p + 0.5 * self.epsilon * state.grad_lnprob

        # Negate the momentum. This step really isn't necessary but it doesn't
        # hurt to keep it here for completeness.
        p = -p

        # Automatically reject zero probability states.
        state.accepted = False
        if not np.isfinite(state.lnprob):
            return state, 0.0

        # Compute the acceptance probability factor.
        factor = 0.5 * np.dot(current_p, self.cov.apply(current_p))
        factor -= 0.5 * np.dot(p, self.cov.apply(p))
        return state, factor


class HamiltonianMove(object):
    """
    A Hamiltonian Monte Carlo (HMC) move based on the algorithm in Figure 2
    of Neal (2012; http://arxiv.org/abs/1206.1901). To use this method, your
    model must support the ``compute_grad`` keyword argument in the call to
    ``get_state``. By default, this can be computed numerically but this is
    unlikely to be efficient so it's best if you compute the gradients
    yourself.

    :param nsteps:
        The number of leapfrog steps to take when integrating the dynamics.
        If an integer is provided, the number of steps will be constant.
        Instead, you can also provide a tuple with two integers and these will
        be treated as lower and upper limits on the number of steps and the
        used value will be uniformly sampled within that range.

    :param epsilon:
        The step size used in the integration. Like ``nsteps`` a float can be
        given for a constant step size of a range can be given and the final
        value will be uniformly sampled.

    """

    _wrapper = _hmc_wrapper

    def __init__(self, nsteps, epsilon, nsplits=2, cov=1.0):
        self.nsteps = nsteps
        self.epsilon = epsilon
        self.nsplits = nsplits
        self.cov = cov

    def get_args(self, ensemble):
        # Randomize the stepsize if requested.
        rand = ensemble.random
        try:
            eps = float(self.epsilon)
        except TypeError:
            eps = rand.uniform(self.epsilon[0], self.epsilon[1])

        # Randomize the number of steps.
        try:
            L = int(self.nsteps)
        except TypeError:
            L = rand.randint(self.nsteps[0], self.nsteps[1])

        return eps, L

    def update(self, ensemble):
        """
        Execute a single step starting from the given :class:`Ensemble` and
        updating it in-place.

        :param ensemble:
            The starting :class:`Ensemble`.

        :return ensemble:
            The same ensemble updated in-place.

        """
        # Loop over splits.
        inds = np.arange(ensemble.nwalkers) % self.nsplits
        ensemble.random.shuffle(inds)
        for i in xrange(self.nsplits):
            S1 = inds == i
            S2 = inds != i

            if self.cov == "adapt":
                # Estimate the covariance matrix from the complementary
                # ensemble.
                c = ensemble.coords[S2]
                cov = np.cov(c, rowvar=0)
            else:
                cov = self.cov

            # Set up the integrator and sample the initial momenta.
            integrator = self._wrapper(ensemble.model, cov,
                                       *(self.get_args(ensemble)))
            momenta = integrator.cov.sample(ensemble.random, np.sum(S1),
                                            ensemble.ndim)

            # Integrate the dynamics in parallel.
            res = ensemble.pool.map(integrator, izip(
                (ensemble.walkers[i] for i in np.arange(len(S1))[S1]),
                momenta
            ))

            # Loop over the walkers and update them accordingly.
            states = []
            for i, (j, (state, factor)) in enumerate(izip(
                    np.arange(len(ensemble))[S1], res)):
                lnpdiff = factor + state.lnprob - ensemble.walkers[j].lnprob
                if lnpdiff > np.log(ensemble.random.rand()):
                    state.accepted = True
                states.append(state)

            ensemble.update(states, slice=S1)
        return ensemble
