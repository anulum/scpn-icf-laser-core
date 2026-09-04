# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — level-0 physics anchors and builders

"""Anchors and builders shared by the level-0 physics tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

Every constant here whose name begins ``PRINTED_`` is read from
R. S. Craxton et al., *Phys. Plasmas* **22** (2015) 110501, filed in this
repository's internal papers directory. The equations were read off the
rendered pages; the text layer of that document drops the exponent from
equation 3-7, which turns a falling pressure floor into a rising one.

The design those constants describe is the review's 1.5 MJ triple-picket
ignition design for a large laser facility, section III A. It is used
because the review prints its geometry, its energies and several derived
figures, which is what lets a test show a printed number is recoverable
from the built record rather than stored beside it.

Three of the review's own numbers are **not** reproduced by its own
equations, and the tests say so rather than adjusting anything: see
``test_physics_ignition.py`` for the worked pressure range and
``test_physics_yield_and_gain.py`` for the gain.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_laser_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_icf_laser_core.parameters import LaserDriver, TargetDeclaration
from scpn_icf_laser_core.physics.level0 import (
    CapsuleDeclaration,
    ImplosionDeclaration,
)

# --- Craxton et al. 2015, Sec. III A: the reference design's geometry ---
PRINTED_INCIDENT_ENERGY_MJ: Final = 1.5
PRINTED_TARGET_RADIUS_UM: Final = 1700.0
PRINTED_ABLATOR_THICKNESS_UM: Final = 37.0
PRINTED_ICE_THICKNESS_UM: Final = 160.0
PRINTED_VAPOUR_DENSITY_MG_CM3: Final = 0.6
PRINTED_WAVELENGTH_UM: Final = 0.35
PRINTED_PEAK_INTENSITY_W_CM2: Final = 8.0e14

# --- Craxton et al. 2015, Sec. III A: derived figures the review states ---
PRINTED_SHELL_KINETIC_ENERGY_KJ: Final = 100.0
PRINTED_ABSORBED_FRACTION: Final = 0.95
PRINTED_HYDRODYNAMIC_EFFICIENCY: Final = 0.067
PRINTED_IFAR: Final = 24.3
PRINTED_CONVERGENCE_RATIO: Final = 23.0
PRINTED_MASS_AVERAGED_ADIABAT: Final = 1.6
PRINTED_BURNUP_FRACTION: Final = 0.20
PRINTED_ONE_DIMENSIONAL_GAIN: Final = 48.0
PRINTED_HOT_SPOT_PRESSURE_GBAR: Final = 215.0
PRINTED_COUPLED_FRACTION_RANGE: Final = (0.4, 0.5)

# --- Craxton et al. 2015, Sec. III B: the equation coefficients ---
PRINTED_EQ36_COEFFICIENT_GBAR: Final = 100.0
PRINTED_EQ36_REFERENCE_RADIUS_UM: Final = 100.0
PRINTED_EQ37_COEFFICIENT_GBAR: Final = 250.0
PRINTED_EQ38_COEFFICIENT_UM: Final = 40.0
PRINTED_ENERGY_SCALE_KJ: Final = 10.0

# --- Not printed by this review; a standard value, declared as such ---
SOLID_DT_DENSITY_G_CM3: Final = 0.25

# --- Synthetic; pins nothing ---
SYNTHETIC_REGISTRY_VERSION: Final = "1.0.0"
SYNTHETIC_REGISTRY_DIGEST: Final = "0" * 64
# Not printed by the review. Declared so the in-flight relations have an
# input, and chosen to reproduce the printed aspect ratio and convergence
# ratio when the record is built; neither number is attributed to the
# design's simulation.
DECLARED_IN_FLIGHT_THICKNESS_UM: Final = 1002.0 / PRINTED_IFAR
DECLARED_STAGNATION_RADIUS_UM: Final = 1503.0 / PRINTED_CONVERGENCE_RATIO
DECLARED_SHELL_PRESSURE_MBAR: Final = 100.0
DECLARED_SHELL_DENSITY_G_CM3: Final = 10.0
DECLARED_PULSE_DURATION_NS: Final = 10.0


def registry_binding() -> RegistryBinding:
    """Build the synthetic registry pin the fixtures share.

    Returns
    -------
    RegistryBinding
        A well-formed pin; its digest is synthetic and pins nothing.
    """
    return RegistryBinding(
        version=SYNTHETIC_REGISTRY_VERSION,
        digest_sha256=SYNTHETIC_REGISTRY_DIGEST,
    )


def anchor_configuration(
    *, identifier: str = "laser_icf_direct_drive"
) -> DeviceConfiguration:
    """Build the configuration the anchors are evaluated on.

    Parameters
    ----------
    identifier
        Which owned configuration to build; the default is the
        direct-drive scheme the review's design uses.

    Returns
    -------
    DeviceConfiguration
        A configuration carrying the review's printed driver energy,
        wavelength and capsule radius.
    """
    return DeviceConfiguration(
        identifier=identifier,
        driver=LaserDriver(
            driver_energy_mj=PRINTED_INCIDENT_ENERGY_MJ,
            pulse_duration_ns=DECLARED_PULSE_DURATION_NS,
            wavelength_nm=PRINTED_WAVELENGTH_UM * 1.0e3,
        ),
        target=TargetDeclaration(
            capsule_radius_um=PRINTED_TARGET_RADIUS_UM,
            hohlraum=identifier == "laser_icf_indirect_drive",
            ignitor_pulse=identifier == "laser_icf_fast_or_shock_ignition",
        ),
        registry=registry_binding(),
    )


def anchor_capsule() -> CapsuleDeclaration:
    """Build the capsule layering the review prints.

    Returns
    -------
    CapsuleDeclaration
        The plastic ablator and the solid fuel layer inside it. The fuel
        density is a standard value the review does not print, and the
        tests that use it say so.
    """
    return CapsuleDeclaration(
        ablator_thickness_um=PRINTED_ABLATOR_THICKNESS_UM,
        fuel_thickness_um=PRINTED_ICE_THICKNESS_UM,
        fuel_density_g_cm3=SOLID_DT_DENSITY_G_CM3,
    )


def anchor_implosion(*, coupled_fraction: float = 0.4) -> ImplosionDeclaration:
    """Build the declared implosion the anchors are evaluated on.

    Parameters
    ----------
    coupled_fraction
        The fraction ``f_k``; the review states a range and the default
        is its lower end.

    Returns
    -------
    ImplosionDeclaration
        The declared outcome.
    """
    return ImplosionDeclaration(
        absorbed_fraction=PRINTED_ABSORBED_FRACTION,
        shell_kinetic_energy_kj=PRINTED_SHELL_KINETIC_ENERGY_KJ,
        coupled_fraction=coupled_fraction,
        in_flight_shell_thickness_um=DECLARED_IN_FLIGHT_THICKNESS_UM,
        stagnation_inner_radius_um=DECLARED_STAGNATION_RADIUS_UM,
        shell_pressure_mbar=DECLARED_SHELL_PRESSURE_MBAR,
        shell_density_g_cm3=DECLARED_SHELL_DENSITY_G_CM3,
        burnup_fraction=PRINTED_BURNUP_FRACTION,
    )
