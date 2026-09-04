# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — shell implosion figures

"""Figures that characterise an imploding shell, as a filed review defines them.

R. S. Craxton et al., *Phys. Plasmas* **22** (2015) 110501 defines four
quantities that a one-dimensional design is usually quoted by, and each
definition is carried here exactly as the review words it, because each
carries a condition that is easy to lose:

- the **adiabat** is the shell pressure over the Fermi-degenerate
  pressure at the shell density, and for DT the review prints the
  coefficient (equation 3-1);
- the **in-flight aspect ratio** is not the aspect ratio at any moment
  one likes. It is evaluated where the ablation front has reached two
  thirds of the shell's initial inner radius, and this module carries
  that fraction rather than leaving it to the caller;
- the **convergence ratio** is the initial inner radius over the inner
  radius at peak compression *with alpha-particle deposition turned
  off*, which is a statement about how it must be computed, recorded
  here in the docstring because no code can enforce it;
- the **hydrodynamic efficiency** is shell kinetic energy over
  **absorbed** laser energy, not incident, and the two differ by the
  absorbed fraction.

None of these is simulated. Each is a definition evaluated on declared
numbers.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import require_positive

DT_ADIABAT_COEFFICIENT: Final = 2.2
FERMI_DEGENERATE_EXPONENT: Final = 5.0 / 3.0
IFAR_EVALUATION_RADIUS_FRACTION: Final = 2.0 / 3.0
MJ_IN_KJ: Final = 1.0e3


def require_fraction(name: str, value: float) -> float:
    """Return a fraction that lies inside ``(0, 1]``.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Fraction under validation.

    Returns
    -------
    float
        The validated fraction.

    Raises
    ------
    DeviceConfigurationError
        If the fraction is not strictly positive or exceeds one. A
        fraction above one is refused rather than clamped: it is not a
        fraction of the quantity it is said to be a fraction of.
    """
    require_positive(name, value)
    if value > 1.0:
        raise DeviceConfigurationError(f"{name}: must not exceed one, got {value!r}")
    return value


def dt_adiabat(shell_pressure_mbar: float, shell_density_g_cm3: float) -> float:
    """Return the DT shell adiabat of equation 3-1.

    ``alpha_DT = P_shell / (2.2 rho**(5/3))``, with the pressure in
    megabar and the density in grams per cubic centimetre. The units are
    part of the relation: the coefficient 2.2 carries them, and the
    result is meaningless in any other pair.

    Parameters
    ----------
    shell_pressure_mbar
        Shell pressure in megabar; strictly positive.
    shell_density_g_cm3
        Shell mass density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        The adiabat, a measure of the entropy added to the fuel by
        shocks and radiation. One is the fully degenerate limit.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("shell_pressure_mbar", shell_pressure_mbar)
    require_positive("shell_density_g_cm3", shell_density_g_cm3)
    # math.pow rather than the ** operator: raising a float to a float is
    # typed as returning Any, and silencing that would be the wrong fix.
    degenerate = math.pow(shell_density_g_cm3, FERMI_DEGENERATE_EXPONENT)
    return shell_pressure_mbar / (DT_ADIABAT_COEFFICIENT * degenerate)


def ifar_evaluation_radius_um(initial_inner_radius_um: float) -> float:
    """Return the ablation-front radius the in-flight aspect ratio is read at.

    Two thirds of the shell's initial inner radius. The review fixes this
    point, and an aspect ratio read anywhere else is a different number
    that should not be called an IFAR.

    Parameters
    ----------
    initial_inner_radius_um
        Initial inner radius of the shell in micrometres; strictly
        positive.

    Returns
    -------
    float
        The evaluation radius in micrometres.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """
    require_positive("initial_inner_radius_um", initial_inner_radius_um)
    return IFAR_EVALUATION_RADIUS_FRACTION * initial_inner_radius_um


def in_flight_aspect_ratio(
    ablation_front_radius_um: float, shell_thickness_um: float
) -> float:
    """Return the in-flight aspect ratio of a shell.

    The ablation-front radius divided by the shell thickness, both taken
    at the evaluation point :func:`ifar_evaluation_radius_um` fixes. A
    large value means a thin shell, which implodes efficiently and is
    less stable; the review discusses that trade in its stability
    section.

    Parameters
    ----------
    ablation_front_radius_um
        Ablation-front radius in micrometres; strictly positive.
    shell_thickness_um
        In-flight shell thickness in micrometres; strictly positive.

    Returns
    -------
    float
        The dimensionless aspect ratio.

    Raises
    ------
    DeviceConfigurationError
        If either length is non-finite or not strictly positive, or if
        the shell is thicker than the radius it sits at, which is not a
        shell.
    """
    require_positive("ablation_front_radius_um", ablation_front_radius_um)
    require_positive("shell_thickness_um", shell_thickness_um)
    if shell_thickness_um > ablation_front_radius_um:
        raise DeviceConfigurationError(
            f"shell_thickness_um: {shell_thickness_um!r} um exceeds the "
            f"ablation-front radius {ablation_front_radius_um!r} um; a shell "
            "thicker than its own radius has no inner surface"
        )
    return ablation_front_radius_um / shell_thickness_um


def convergence_ratio(
    initial_inner_radius_um: float, stagnation_inner_radius_um: float
) -> float:
    """Return the convergence ratio of an implosion.

    The initial inner radius of the shell divided by the inner radius at
    peak compression. The review's definition adds a condition no code
    can check: the stagnation radius is the one computed **with
    alpha-particle deposition turned off**. A ratio taken from a burning
    calculation is a different number under the same name.

    Parameters
    ----------
    initial_inner_radius_um
        Initial inner radius in micrometres; strictly positive.
    stagnation_inner_radius_um
        Inner radius at peak compression in micrometres; strictly
        positive.

    Returns
    -------
    float
        The dimensionless convergence ratio.

    Raises
    ------
    DeviceConfigurationError
        If either radius is non-finite or not strictly positive, or if
        the shell is said to end wider than it began.
    """
    require_positive("initial_inner_radius_um", initial_inner_radius_um)
    require_positive("stagnation_inner_radius_um", stagnation_inner_radius_um)
    if stagnation_inner_radius_um > initial_inner_radius_um:
        raise DeviceConfigurationError(
            f"stagnation_inner_radius_um: {stagnation_inner_radius_um!r} um "
            f"exceeds the initial inner radius {initial_inner_radius_um!r} um; "
            "an implosion converges"
        )
    return initial_inner_radius_um / stagnation_inner_radius_um


def absorbed_energy_kj(incident_energy_mj: float, absorbed_fraction: float) -> float:
    """Return the laser energy a target absorbs.

    Parameters
    ----------
    incident_energy_mj
        Incident laser energy in megajoules; strictly positive. The
        review states explicitly that the energy a design is named by is
        the incident energy.
    absorbed_fraction
        Fraction absorbed, inside ``(0, 1]``.

    Returns
    -------
    float
        The absorbed energy in kilojoules.

    Raises
    ------
    DeviceConfigurationError
        If the energy is not strictly positive or the fraction leaves
        its interval.
    """
    require_positive("incident_energy_mj", incident_energy_mj)
    require_fraction("absorbed_fraction", absorbed_fraction)
    return incident_energy_mj * MJ_IN_KJ * absorbed_fraction


def hydrodynamic_efficiency(
    shell_kinetic_energy_kj: float, absorbed_energy_value_kj: float
) -> float:
    """Return the hydrodynamic efficiency of an implosion.

    The kinetic energy of the imploding shell divided by the **absorbed**
    laser energy. Dividing by the incident energy instead gives a
    smaller number under the same name, and the two differ by the
    absorbed fraction.

    Parameters
    ----------
    shell_kinetic_energy_kj
        Shell kinetic energy in kilojoules; strictly positive.
    absorbed_energy_value_kj
        Absorbed laser energy in kilojoules; strictly positive.

    Returns
    -------
    float
        The efficiency as a fraction.

    Raises
    ------
    DeviceConfigurationError
        If either energy is non-finite or not strictly positive, or if
        the shell is said to carry more energy than the target absorbed.
    """
    require_positive("shell_kinetic_energy_kj", shell_kinetic_energy_kj)
    require_positive("absorbed_energy_value_kj", absorbed_energy_value_kj)
    if shell_kinetic_energy_kj > absorbed_energy_value_kj:
        raise DeviceConfigurationError(
            f"shell_kinetic_energy_kj: {shell_kinetic_energy_kj!r} kJ exceeds "
            f"the absorbed energy {absorbed_energy_value_kj!r} kJ"
        )
    return shell_kinetic_energy_kj / absorbed_energy_value_kj
