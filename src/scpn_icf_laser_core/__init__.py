# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device configuration model package

"""Device configuration model of the SCPN laser-ICF device family.

Public surface of the ``device_configuration_model`` capability at
``computational_prototype`` maturity: validated parameter objects,
documented consistency estimates, canonical serialisation with SHA-256
digests, and a data-only pin to the SPO reactor registry. No claim about
any real machine is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_laser_core.configuration import (
    DIRECT_DRIVE_LPI_BOUND_W_CM2,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import LaserDriver, TargetDeclaration

__version__: Final = "0.1.0.dev0"

__all__ = [
    "DIRECT_DRIVE_LPI_BOUND_W_CM2",
    "OWNED_CONFIGURATIONS",
    "ConsistencyFinding",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "LaserDriver",
    "RegistryBinding",
    "TargetDeclaration",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
]
