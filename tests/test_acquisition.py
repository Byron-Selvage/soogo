"""Test the acquisition functions."""

# Copyright (c) 2025 Alliance for Sustainable Energy, LLC

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__authors__ = ["Weslley S. Pereira"]
__contact__ = "weslley.dasilvapereira@nrel.gov"
__maintainer__ = "Weslley S. Pereira"
__email__ = "weslley.dasilvapereira@nrel.gov"
__credits__ = ["Weslley S. Pereira"]
__deprecated__ = False

import numpy as np
import pytest
from typing import Union, Tuple, Optional

from soogo.model.base import Surrogate
from soogo.acquisition import CycleSearch

class TestCycleSearch:
    """Test suite for the CycleSearch acquisition function."""

    class MockSurrogateModel(Surrogate):
        def __init__(self, X_train: np.ndarray, Y_train: np.ndarray):
            self._X = X_train.copy()
            self._Y = Y_train.copy()
            self._iindex = ()

        @property
        def X(self) -> np.ndarray:
            return self._X

        @property
        def Y(self) -> np.ndarray:
            return self._Y

        @property
        def iindex(self) -> np.ndarray:
            return self._iindex

        def reserve(self, n: int, dim: int, ntarget: int = 1) -> None:
            pass

        def __call__(
            self, x: np.ndarray, i: int = -1, **kwargs
        ) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
            """
            Return sum of coords (x + y).
            """
            x = np.atleast_2d(x)
            result = np.sum(x, axis=1)
            return result if len(result) > 1 else result[0]

        def update(self, x: np.ndarray, y: np.ndarray) -> None:
            pass

        def min_design_space_size(self, dim: int) -> int:
            pass

        def check_initial_design(self, sample: np.ndarray) -> bool:
            pass

        def eval_kernel(self, x: np.ndarray, y: Optional[np.ndarray] = None) -> np.ndarray:
            pass

        def reset_data(self) -> None:
            pass

    class MockEvaluabilitySurrogate(Surrogate):
        def __init__(self, X_train: np.ndarray, Y_train: np.ndarray):
            self._X = X_train.copy()
            self._Y = Y_train.copy()
            self._iindex = ()

        @property
        def X(self) -> np.ndarray:
            return self._X

        @property
        def Y(self) -> np.ndarray:
            return self._Y

        @property
        def iindex(self) -> np.ndarray:
            return self._iindex

        def reserve(self, n: int, dim: int, ntarget: int = 1) -> None:
            pass

        def __call__(
            self, x: np.ndarray, i: int = -1, **kwargs
        ) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
            """
            Return 1.0 except for the first coord which returns 0.1.
            """
            x = np.atleast_2d(x)
            result = np.ones(x.shape[0])
            result[0] = 0.1
            return result if len(result) > 1 else result[0]

        def update(self, x: np.ndarray, y: np.ndarray) -> None:
            pass

        def min_design_space_size(self, dim: int) -> int:
            pass

        def check_initial_design(self, sample: np.ndarray) -> bool:
            pass

        def eval_kernel(self, x: np.ndarray, y: Optional[np.ndarray] = None) -> np.ndarray:
            pass

        def reset_data(self) -> None:
            pass

    @pytest.mark.parametrize(["n_points", "dims"], [([1], [2, 5, 25])])
    def test_optimize_generates_expected_points(self, dims, n_points):
        """
        Test the output points of optimize().

        Ensures that the generated points are:
        - Within the specified bounds.
        - Have the expected shape (n_points, dims).
        - The amount requested.
        """
        for dim in dims:
            for n in n_points:
                bounds = np.array([[0, 1] for _ in range(dim)])
                X_train = np.array([[0.5 for _ in range(dim)]])
                Y_train = np.array([0.0])
                mock_surrogate = self.MockSurrogateModel(X_train, Y_train)
                cycle_search = CycleSearch()

                result = cycle_search.optimize(
                    mock_surrogate, bounds, n=n, scoreWeight=0.5)
                assert result.shape == (n, dim)
                assert np.all(result >= bounds[:, 0]) and np.all(result <= bounds[:, 1])

    def test_generate_candidates(self):
        """
        Tests that the generate_candidates() method:
        - Generates the expected number of candidates.
        - All candidates are within the specified bounds.
        """
        nCand = [200, 1000, 100000]
        bounds = np.array([[0, 10], [0, 10]])
        X_train = np.array([[5, 5]])
        Y_train = np.array([0.0])

        mock_surrogate = self.MockSurrogateModel(X_train, Y_train)
        cycle_search = CycleSearch()

        for n in nCand:
            candidates = cycle_search.generate_candidates(mock_surrogate, bounds, nCand=n)

            # Should generate 2 * nCand candidates (perturbations + uniform)
            expected_count = 2 * n
            assert len(candidates) == expected_count

            # All candidates should be within bounds
            assert np.all(candidates >= bounds[:, 0])
            assert np.all(candidates <= bounds[:, 1])

    def test_select_candidates(self):
        """
        Test that the select_candidates() method:
        - Chooses the candidate further from evaluated points when function
            values are the same.
        - Chooses the candidate with lower function value when distances are
            the same.
        - Removes candidates that are below the evaluability threshold.
        """
        X_train = np.array([[5, 5]])
        Y_train = np.array([0.0])
        bounds = np.array([[0, 10], [0, 10]])

        mock_surrogate = self.MockSurrogateModel(X_train, Y_train)
        mock_evaluability = self.MockEvaluabilitySurrogate(X_train, Y_train)
        cycle_search = CycleSearch()

        # Both tests would return [0.0, 0.0] if the evaluability filter fails
        # Test case 1: Same function values, different distances
        candidates = np.array([[0.0, 0.0], [9.0, 1.0], [4.0, 6.0]])
        point = cycle_search.select_candidates(mock_surrogate, candidates, bounds, n=1, scoreWeight=0.5, evaluabilitySurrogate=mock_evaluability)
        assert np.allclose(point, np.array([[9.0, 1.0]]))

        # Test case 2: Same distances, different function values
        candidates = np.array([[0.0, 0.0], [3.0, 5.0], [7.0, 5.0]])
        point = cycle_search.select_candidates(mock_surrogate, candidates, bounds, n=1, scoreWeight=0.5, evaluabilitySurrogate=mock_evaluability)
        assert np.allclose(point, np.array([[3.0, 5.0]]))

        # Test case 3: Weighted sum
        X_train = np.array([[5.0, 5.0], [6.0, 6.0], [3.0, 4.0]])
        Y_train = np.array([0.0, 1.0, 0.5])
        mock_surrogate = self.MockSurrogateModel(X_train, Y_train)
        mock_evaluability = self.MockEvaluabilitySurrogate(X_train, Y_train)
        candidates = np.array([[0.0, 0.0], [2.0, 6.0], [7.0, 0.5]])
        point = cycle_search.select_candidates(mock_surrogate, candidates, bounds, n=1, scoreWeight=0.75, evaluabilitySurrogate=mock_evaluability)
        assert np.allclose(point, np.array([[7.0, 0.5]]))
