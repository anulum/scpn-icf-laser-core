# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — hot-spot ignition condition

"""The hot-spot ignition condition in the forms a filed review prints.

R. S. Craxton et al., *Phys. Plasmas* **22** (2015) 110501, section
III B, states the condition four ways, and the value of carrying all
four is that they constrain each other:

- equation 3-5, the condition itself, as floors on the hot-spot areal
  density and ion temperature;
- equation 3-6, the same condition as a pressure floor that falls with
  hot-spot radius;
- equation 3-7, the same condition again in terms of the shell kinetic
  energy coupled into the hot spot, which is the form a designer uses;
- and the energy relation ``f_k E_k = 2 pi P_hs R_hs**3`` that carries
  equation 3-6 into equation 3-7.

Because the review prints the coefficient of each, the set can be
checked against itself rather than taken on trust, and the tests do
exactly that: equation 3-8's 40 micrometres follows from equation 3-6's
100 Gbar and equation 3-7's 250 Gbar, and the three close on the energy
relation to a fixed 0.53 %, which is the rounding of the printed
coefficients and not a disagreement about the physics.

Nothing here computes an implosion. These are the algebraic
requirements a design must satisfy, evaluated on declared numbers.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_laser_core.parameters import require_positive

IGNITION_AREAL_DENSITY_G_CM2: Final = 0.3
IGNITION_ION_TEMPERATURE_KEV: Final = 5.0
REFERENCE_HOT_SPOT_RADIUS_UM: Final = 100.0
HOT_SPOT_PRESSURE_AT_REFERENCE_GBAR: Final = 100.0
HOT_SPOT_PRESSURE_COEFFICIENT_GBAR: Final = 250.0
HOT_SPOT_ENERGY_SCALE_KJ: Final = 10.0
DT_PRESSURE_MASS_FACTOR: Final = 2.5
PROTON_MASS_KG: Final = 1.67262192369e-27
KEV_IN_JOULES: Final = 1.602176634e-16
GBAR_IN_PASCAL: Final = 1.0e14
MICROMETRE_IN_METRE: Final = 1.0e-6
KILOJOULE_IN_JOULES: Final = 1.0e3
GRAM_PER_CM3_IN_KG_PER_M3: Final = 1.0e3


def ignition_condition_met(
    areal_density_g_cm2: float, ion_temperature_kev: float
) -> bool:
    """Report whether a hot spot meets both floors of equation 3-5.

    Parameters
    ----------
    areal_density_g_cm2
        Hot-spot areal density ``rho R_hs``; strictly positive.
    ion_temperature_kev
        Hot-spot ion temperature ``T_i``; strictly positive.

    Returns
    -------
    bool
        ``True`` when both the areal density and the temperature reach
        their floors. The two are separate conditions in the source and
        are kept separate here; neither compensates for the other.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("areal_density_g_cm2", areal_density_g_cm2)
    require_positive("ion_temperature_kev", ion_temperature_kev)
    return (
        areal_density_g_cm2 >= IGNITION_AREAL_DENSITY_G_CM2
        and ion_temperature_kev >= IGNITION_ION_TEMPERATURE_KEV
    )


def dt_pressure_gbar(ion_temperature_kev: float, mass_density_g_cm3: float) -> float:
    """Pressure of equal-temperature DT at a given density.

    ``P = 2 T_i rho / (2.5 m_p)``, the relation the review uses to carry
    equation 3-5 into equation 3-6. Equal ion and electron temperatures
    are assumed, which is what the factor of two counts, and 2.5 proton
    masses is the mean mass per particle of a fully ionised equimolar DT
    plasma.

    Parameters
    ----------
    ion_temperature_kev
        Ion temperature; strictly positive.
    mass_density_g_cm3
        Mass density; strictly positive.

    Returns
    -------
    float
        The pressure in gigabar.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("ion_temperature_kev", ion_temperature_kev)
    require_positive("mass_density_g_cm3", mass_density_g_cm3)
    temperature_j = ion_temperature_kev * KEV_IN_JOULES
    density_si = mass_density_g_cm3 * GRAM_PER_CM3_IN_KG_PER_M3
    pascal = (
        2.0 * temperature_j * density_si / (DT_PRESSURE_MASS_FACTOR * PROTON_MASS_KG)
    )
    return pascal / GBAR_IN_PASCAL


def hot_spot_pressure_for_radius_gbar(hot_spot_radius_um: float) -> float:
    """Pressure floor of equation 3-6 at a given hot-spot radius.

    ``P_hs > 100 Gbar (100 um / R_hs)``.

    Parameters
    ----------
    hot_spot_radius_um
        Hot-spot radius in micrometres; strictly positive.

    Returns
    -------
    float
        The pressure floor in gigabar.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """
    require_positive("hot_spot_radius_um", hot_spot_radius_um)
    return (
        HOT_SPOT_PRESSURE_AT_REFERENCE_GBAR
        * REFERENCE_HOT_SPOT_RADIUS_UM
        / hot_spot_radius_um
    )


def hot_spot_pressure_floor_gbar(coupled_energy_kj: float) -> float:
    """Pressure floor of equation 3-7 for a coupled kinetic energy.

    ``P_hs > 250 Gbar (f_k E_k / 10 kJ)**(-1/2)``. The floor falls as the
    coupled energy rises, which is the point the review draws from it.

    Parameters
    ----------
    coupled_energy_kj
        The product ``f_k E_k`` — the fraction of the shell's kinetic
        energy converted into hot-spot internal energy at peak
        compression — in kilojoules; strictly positive.

    Returns
    -------
    float
        The pressure floor in gigabar.

    Raises
    ------
    DeviceConfigurationError
        If the energy is non-finite or not strictly positive.
    """
    require_positive("coupled_energy_kj", coupled_energy_kj)
    return HOT_SPOT_PRESSURE_COEFFICIENT_GBAR / math.sqrt(
        coupled_energy_kj / HOT_SPOT_ENERGY_SCALE_KJ
    )


def hot_spot_radius_ceiling_um(coupled_energy_kj: float) -> float:
    """Radius ceiling of equation 3-8 for a coupled kinetic energy.

    ``R_hs < 40 um sqrt(f_k E_k / 10 kJ)``. The coefficient is not an
    independent number: it is equation 3-6's reference radius scaled by
    the ratio of the two printed pressures, and a test recovers it.

    Parameters
    ----------
    coupled_energy_kj
        The product ``f_k E_k`` in kilojoules; strictly positive.

    Returns
    -------
    float
        The largest hot-spot radius that still ignites, in micrometres.

    Raises
    ------
    DeviceConfigurationError
        If the energy is non-finite or not strictly positive.
    """
    require_positive("coupled_energy_kj", coupled_energy_kj)
    return (
        REFERENCE_HOT_SPOT_RADIUS_UM
        * HOT_SPOT_PRESSURE_AT_REFERENCE_GBAR
        / HOT_SPOT_PRESSURE_COEFFICIENT_GBAR
        * math.sqrt(coupled_energy_kj / HOT_SPOT_ENERGY_SCALE_KJ)
    )


def hot_spot_energy_kj(pressure_gbar: float, hot_spot_radius_um: float) -> float:
    """Return the internal energy of a hot spot of that pressure and radius.

    ``f_k E_k = 2 pi P_hs R_hs**3``, the relation that carries equation
    3-6 into equation 3-7.

    Parameters
    ----------
    pressure_gbar
        Hot-spot pressure; strictly positive.
    hot_spot_radius_um
        Hot-spot radius in micrometres; strictly positive.

    Returns
    -------
    float
        The coupled energy in kilojoules.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("pressure_gbar", pressure_gbar)
    require_positive("hot_spot_radius_um", hot_spot_radius_um)
    pascal = pressure_gbar * GBAR_IN_PASCAL
    radius_m = hot_spot_radius_um * MICROMETRE_IN_METRE
    return 2.0 * math.pi * pascal * radius_m**3 / KILOJOULE_IN_JOULES
