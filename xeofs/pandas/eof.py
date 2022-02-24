from typing import Optional, Tuple, Union, List

import numpy as np
import pandas as pd

from ..models._eof_base import _EOF_base
from xeofs.pandas._dataframe_transformer import _DataFrameTransformer


class EOF(_EOF_base):
    '''EOF analysis of a single ``pd.DataFrame``.

    Parameters
    ----------
    X : pd.DataFrame
        Data to be decpomposed.
    axis : int
        Axis along which variance should be maximsed (the default is 0).
    n_modes : Optional[int]
        Number of modes to compute. Computing less modes can results in
        performance gains. If None, then the maximum number of modes is
        equivalent to ``min(n_samples, n_features)`` (the default is None).
    norm : bool
        Normalize each feature (e.g. grid cell) by its temporal standard
        deviation (the default is False).


    Examples
    --------

    Import package and create data:

    >>> import pandas as pd
    >>> from xeofs.pandas import EOF
    >>> rng = np.random.default_rng(7)
    >>> X = rng.standard_normal((4, 3))
    >>> df = pd.DataFrame(X)

    Initialize standardized EOF analysis and compute the first 2 modes:

    >>> model = EOF(df, norm=True, n_modes=2)
    >>> model.solve()

    Get explained variance:

    >>> model.explained_variance()
    ...     	explained_variance
    ...     mode
    ...     1	2.562701
    ...     2	1.167054

    Get EOFs:

    >>> model.eofs()
    ... mode	1	2
    ... 0	0.626041	-0.428431
    ... 1	0.677121	-0.115737
    ... 2	0.386755	0.896132

    Get PCs:

    >>> model.pcs()
    ... mode	1	2
    ... 0	0.495840	-0.221963
    ... 1	-2.254508	-0.470420
    ... 2	1.516900	-0.876695
    ... 3	0.241768	1.569078

    '''

    def __init__(
        self,
        X: pd.DataFrame,
        axis : int = 0,
        n_modes : Optional[int] = None,
        norm : bool = False,
        weights : Optional[np.ndarray] = None
    ):

        if(np.logical_not(isinstance(X, pd.DataFrame))):
            raise ValueError('This interface is for `pandas.DataFrame` only.')

        self._tf = _DataFrameTransformer()
        X = self._tf.fit_transform(X)
        weights = self._tf.transform_weights(weights)

        super().__init__(
            X=X,
            n_modes=n_modes,
            norm=norm,
            weights=weights
        )
        self._idx_mode = pd.Index(range(1, self.n_modes + 1), name='mode')

    def singular_values(self) -> pd.DataFrame:
        svalues = super().singular_values()
        svalues = pd.DataFrame(
            svalues,
            columns=['singular_values'],
            index=self._idx_mode
        )
        return svalues

    def explained_variance(self) -> pd.DataFrame:
        expvar = super().explained_variance()
        expvar = pd.DataFrame(
            expvar,
            columns=['explained_variance'],
            index=self._idx_mode
        )
        return expvar

    def explained_variance_ratio(self) -> pd.DataFrame:
        expvar = super().explained_variance_ratio()
        expvar = pd.DataFrame(
            expvar,
            columns=['explained_variance_ratio'],
            index=self._idx_mode
        )
        return expvar

    def eofs(self, scaling : int = 0) -> pd.DataFrame:
        eofs = super().eofs(scaling=scaling)
        eofs = self._tf.back_transform_eofs(eofs)
        eofs.columns = self._idx_mode
        return eofs

    def pcs(self, scaling : int = 0) -> pd.DataFrame:
        pcs = super().pcs(scaling=scaling)
        pcs = self._tf.back_transform_pcs(pcs)
        pcs.columns = self._idx_mode
        return pcs

    def eofs_as_correlation(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        corr, pvals = super().eofs_as_correlation()
        corr = self._tf.back_transform_eofs(corr)
        pvals = self._tf.back_transform_eofs(pvals)
        corr.columns = self._idx_mode
        pvals.columns = self._idx_mode
        return corr, pvals

    def reconstruct_X(
        self,
        mode : Optional[Union[int, List[int], slice]] = None
    ) -> pd.DataFrame:
        Xrec = super().reconstruct_X(mode)
        Xrec = self._tf.back_transform(Xrec)
        Xrec.index = self._tf.index_samples
        return Xrec
