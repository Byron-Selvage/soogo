"""soogo models"""

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

# Surrogate models
from .base import Surrogate
from .gp import GaussianProcess
from .rbf import RbfModel, MedianLpfFilter

# Surrogate model kernels
from .rbf_kernel import (
    LinearRadialBasisFunction,
    CubicRadialBasisFunction,
    ThinPlateRadialBasisFunction,
)

__all__ = [
    "Surrogate",
    "GaussianProcess",
    "RbfModel",
    "MedianLpfFilter",
    "LinearRadialBasisFunction",
    "CubicRadialBasisFunction",
    "ThinPlateRadialBasisFunction",
]
