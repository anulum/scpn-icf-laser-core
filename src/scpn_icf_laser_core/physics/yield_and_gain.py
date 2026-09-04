# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — fuel inventory, yield and target gain

"""Fuel inventory of a capsule, its burn yield, and the target gain.

Three definitions and one physical constant. The constant is the energy
DT releases per unit mass, built from the reaction energy and the masses
of the two nuclei rather than quoted as a number, so that it can be
read and checked instead of trusted.

**A recorded non-recovery.** The filed review states, for its reference
design, a burnup fraction of 20 % and a one-dimensional gain of 48. That
gain is *not* recovered by this module from the design's printed
geometry: the ice layer the review prints, at the standard density of
solid DT, burnt at the printed 20 %, gives a gain near 57. The gap is
about 18 % and it is not arithmetic. A quoted burnup fraction applies to
the fuel that actually assembles and burns, and some of the printed
inventory is not in that state at peak compression. The relations here
are therefore definitions, and the review's gain is deliberately **not**
used as an anchor. Recording the failed reconstruction is the honest
result; presenting the two numbers as agreeing would not be.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import require_positive

DT_FUSION_ENERGY_MEV: Final = 17.6
DEUTERON_MASS_U: Final = 2.0141018
TRITON_MASS_U: Final = 3.0160492
ATOMIC_MASS_UNIT_KG: Final = 1.66053906660e-27
MEV_IN_JOULES: Final = 1.602176634e-13
MICROMETRE_IN_CM: Final = 1.0e-4
GRAM_IN_MILLIGRAM: Final = 1.0e3
JOULE_IN_MEGAJOULE: Final = 1.0e-6


def dt_specific_energy_j_per_g() -> float:
    """Return the energy an equimolar DT mixture releases per gram burnt.

    The reaction energy divided by the mass of one deuteron-triton pair.
    Built from its parts rather than quoted, so the value can be checked
    against the constants above.

    Returns
    -------
    float
        Joules per gram of DT consumed.
    """
    pair_mass_g = (DEUTERON_MASS_U + TRITON_MASS_U) * ATOMIC_MASS_UNIT_KG * 1.0e3
    return DT_FUSION_ENERGY_MEV * MEV_IN_JOULES / pair_mass_g


def spherical_shell_mass_mg(
    outer_radius_um: float, thickness_um: float, density_g_cm3: float
) -> float:
    """Return the mass of one spherical shell of fuel.

    Parameters
    ----------
    outer_radius_um
        Outer radius of the shell in micrometres; strictly positive.
    thickness_um
        Radial thickness in micrometres; strictly positive and smaller
        than the outer radius.
    density_g_cm3
        Mass density in grams per cubic centimetre; strictly positive.

    Returns
    -------
    float
        The shell mass in milligrams.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive, or if the
        shell is at least as thick as its outer radius, which leaves no
        cavity inside it.
    """
    require_positive("outer_radius_um", outer_radius_um)
    require_positive("thickness_um", thickness_um)
    require_positive("density_g_cm3", density_g_cm3)
    if thickness_um >= outer_radius_um:
        raise DeviceConfigurationError(
            f"thickness_um: {thickness_um!r} um is not smaller than the outer "
            f"radius {outer_radius_um!r} um; the shell would have no cavity"
        )
    outer_cm = outer_radius_um * MICROMETRE_IN_CM
    inner_cm = (outer_radius_um - thickness_um) * MICROMETRE_IN_CM
    volume_cm3 = 4.0 / 3.0 * math.pi * (outer_cm**3 - inner_cm**3)
    return volume_cm3 * density_g_cm3 * GRAM_IN_MILLIGRAM


def fusion_yield_mj(fuel_mass_mg: float, burnup_fraction: float) -> float:
    """Return the fusion energy released by burning part of a fuel mass.

    Parameters
    ----------
    fuel_mass_mg
        Fuel inventory in milligrams; strictly positive.
    burnup_fraction
        Fraction of that inventory consumed, inside ``(0, 1]``.

    Returns
    -------
    float
        The yield in megajoules.

    Raises
    ------
    DeviceConfigurationError
        If the mass is not strictly positive or the fraction leaves its
        interval.
    """
    require_positive("fuel_mass_mg", fuel_mass_mg)
    require_positive("burnup_fraction", burnup_fraction)
    if burnup_fraction > 1.0:
        raise DeviceConfigurationError(
            f"burnup_fraction: must not exceed one, got {burnup_fraction!r}"
        )
    mass_g = fuel_mass_mg / GRAM_IN_MILLIGRAM
    return mass_g * burnup_fraction * dt_specific_energy_j_per_g() * JOULE_IN_MEGAJOULE


def target_gain(fusion_yield_value_mj: float, incident_energy_mj: float) -> float:
    """Return the target gain of a shot.

    Fusion yield divided by **incident** laser energy. The filed review
    states explicitly that the energy a design is named by is the
    incident energy, so a gain quoted against absorbed or delivered
    energy is a different number under the same name.

    Parameters
    ----------
    fusion_yield_value_mj
        Fusion energy released, in megajoules; strictly positive.
    incident_energy_mj
        Incident laser energy in megajoules; strictly positive.

    Returns
    -------
    float
        The dimensionless target gain.

    Raises
    ------
    DeviceConfigurationError
        If either energy is non-finite or not strictly positive.
    """
    require_positive("fusion_yield_value_mj", fusion_yield_value_mj)
    require_positive("incident_energy_mj", incident_energy_mj)
    return fusion_yield_value_mj / incident_energy_mj
