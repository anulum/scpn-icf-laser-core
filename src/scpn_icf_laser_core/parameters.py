# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — laser-ICF parameter model

"""Validated parameter objects of a laser-ICF configuration.

The derived quantity implements one standard estimate and nothing more:
the sphere-averaged on-target intensity ``I = E / (tau 4 pi R^2)``. It
is a rough consistency instrument with documented applicability bounds
(direct-drive laser-plasma-instability regime; R. S. Craxton et al.,
Phys. Plasmas 22 (2015) 110501); no claim about any real machine follows
from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scpn_icf_laser_core.errors import DeviceConfigurationError


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class LaserDriver:
    """Laser-driver parameters of an ICF configuration.

    Parameters
    ----------
    driver_energy_mj
        Total driver energy in megajoules; strictly positive.
    pulse_duration_ns
        Main-pulse duration in nanoseconds; strictly positive.
    wavelength_nm
        Laser wavelength in nanometres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    driver_energy_mj: float
    pulse_duration_ns: float
    wavelength_nm: float

    def __post_init__(self) -> None:
        """Validate the driver invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("driver_energy_mj", self.driver_energy_mj)
        require_positive("pulse_duration_ns", self.pulse_duration_ns)
        require_positive("wavelength_nm", self.wavelength_nm)


@dataclass(frozen=True, slots=True)
class TargetDeclaration:
    """Target declaration of a laser-ICF configuration.

    Parameters
    ----------
    capsule_radius_um
        Capsule outer radius in micrometres; strictly positive.
    hohlraum
        Whether the capsule sits in a radiation enclosure (indirect
        drive).
    ignitor_pulse
        Whether a separate ignitor pulse is part of the drive scheme
        (fast or shock ignition).

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """

    capsule_radius_um: float
    hohlraum: bool
    ignitor_pulse: bool

    def __post_init__(self) -> None:
        """Validate the target invariants.

        Raises
        ------
        DeviceConfigurationError
            If the radius is non-finite or not strictly positive.
        """
        require_positive("capsule_radius_um", self.capsule_radius_um)

    def on_target_intensity_w_cm2(self, driver: LaserDriver) -> float:
        """Sphere-averaged on-target intensity of the given driver.

        Parameters
        ----------
        driver
            Validated laser driver supplying energy and pulse duration.

        Returns
        -------
        float
            ``I = E / (tau 4 pi R^2)`` in watts per square centimetre.
        """
        energy_j = driver.driver_energy_mj * 1.0e6
        duration_s = driver.pulse_duration_ns * 1.0e-9
        radius_cm = self.capsule_radius_um * 1.0e-4
        area_cm2 = 4.0 * math.pi * radius_cm**2
        return energy_j / (duration_s * area_cm2)
