# -*- coding: utf-8 -*-

from __future__ import division, print_function

import numpy as np

try:
    from scipy.stats import gaussian_kde
except ImportError:
    gaussian_kde = None

from .red_blue import RedBlueMove

__all__ = ["KDEMove"]


class KDEMove(RedBlueMove):
    """
    Use a continuously evolving KDE proposal. This is a simplified version of
    the method used in `kombine <https://github.com/bfarr/kombine>`_. If you
    use this proposal, you should use *a lot* of walkers in your ensemble.

    :param bw_method:
        The bandwidth estimation method. See `the scipy docs
        <http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html>`_
        for allowed values.

    """
    def __init__(self, bw_method=None, **kwargs):
        if gaussian_kde is None:
            raise ImportError("you need scipy.stats.gaussian_kde to use the "
                              "KDEMove")
        self.bw_method = bw_method
        super(KDEMove, self).__init__(**kwargs)

    def get_proposal(self, ens, s, c):
        kde = gaussian_kde(c.T, bw_method=self.bw_method)
        q = kde.resample(len(s))
        factor = np.log(kde.evaluate(s.T)) - np.log(kde.evaluate(q))
        return q.T, factor
