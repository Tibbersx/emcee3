# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["HDFBackend"]

import numpy as np

try:
    import h5py
except ImportError:
    h5py = None

from .default import DefaultBackend


class HDFBackend(DefaultBackend):

    def __init__(self, filename, name, **kwargs):
        if h5py is None:
            raise ImportError("h5py")
        self.filename = filename
        self.name = name
        super(HDFBackend, self).__init__(**kwargs)

    def open(self, mode="r"):
        return h5py.File(self.filename, mode)

    def reset(self):
        """
        Clear the chain and reset it to its default state.

        """
        self.initialized = False
        self.nwalkers, self.ndim = None, None

    def extend(self, n):
        k, d = self.nwalkers, self.ndim
        if not self.initialized:
            with self.open("w") as f:
                g = f.create_group(self.name)
                g.attrs["niter"] = 0
                g.attrs["size"] = n
                g.create_dataset("coords", (n, k, d), dtype=np.float64,
                                 maxshape=(None, k, d))
                g.create_dataset("lnprior", (n, k), dtype=np.float64,
                                 maxshape=(None, k))
                g.create_dataset("lnlike", (n, k), dtype=np.float64,
                                 maxshape=(None, k))
                g.create_dataset("acceptance",
                                 data=np.zeros(k, dtype=np.uint64))

                md = g.create_group("metadata")
                for name, shape, dtype in self.metadata_spec:
                    md.create_dataset(name, (n, k) + shape, dtype=dtype)

            self.initialized = True

        else:
            with self.open("a") as f:
                g = f[self.name]

                # Update the size entry.
                niter = g.attrs["niter"]
                size = g.attrs["size"]
                l = niter + n
                g.attrs["size"] = size

                # Extend the arrays.
                g["coords"].resize(l, axis=0)
                g["lnprior"].resize(l, axis=0)
                g["lnlike"].resize(l, axis=0)

                md = g["metadata"]
                for name, _, _ in self.metadata_spec:
                    md[name].resize(l, axis=0)

    def update(self, ensemble):
        # Get the current file shape and dimensions.
        with self.open() as f:
            g = f[self.name]
            niter = g.attrs["niter"]
            size = g.attrs["size"]

        # Resize the chain if necessary.
        if niter >= size:
            self.extend(niter - size + 1)

        # Update the file.
        with self.open("a") as f:
            g = f[self.name]
            for w, walker in enumerate(ensemble.walkers):
                g["coords"][niter, w, :] = walker.coords
                g["lnprior"][niter, w] = walker.lnprior
                g["lnlike"][niter, w] = walker.lnlike
                md = g["metadata"]
                for name in md:
                    md[name][niter, w] = walker.metadata[name]
            g["acceptance"][:] += ensemble.acceptance
            g.attrs["niter"] = niter + 1

    def get_metadata(self, name):
        with self.open() as f:
            g = f[self.name]
            i = g.attrs["niter"]
            return g["metadata"][name][:i, :]

    @property
    def niter(self):
        with self.open() as f:
            return f[self.name].attrs["niter"]

    @property
    def coords(self):
        try:
            with self.open() as f:
                if self.name not in f:
                    return None
                g = f[self.name]
                i = g.attrs["niter"]
                return g["coords"][:i, :, :]

        except IOError:
            # This will happen if the file doesn't already exist.
            return None

    @property
    def lnprior(self):
        with self.open() as f:
            g = f[self.name]
            i = g.attrs["niter"]
            return g["lnprior"][:i, :]

    @property
    def lnlike(self):
        with self.open() as f:
            g = f[self.name]
            i = g.attrs["niter"]
            return g["lnlike"][:i, :]

    @property
    def acceptance(self):
        with self.open() as f:
            return f[self.name]["acceptance"][...]
