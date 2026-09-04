# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — fuel inventory, yield and gain tests

"""Tests of the fuel inventory, the burn yield and the target gain."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_ABLATOR_THICKNESS_UM,
    PRINTED_BURNUP_FRACTION,
    PRINTED_ICE_THICKNESS_UM,
    PRINTED_INCIDENT_ENERGY_MJ,
    PRINTED_ONE_DIMENSIONAL_GAIN,
    PRINTED_TARGET_RADIUS_UM,
    SOLID_DT_DENSITY_G_CM3,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.physics.yield_and_gain import (
    dt_specific_energy_j_per_g,
    fusion_yield_mj,
    spherical_shell_mass_mg,
    target_gain,
)


def test_the_dt_specific_energy_is_built_from_its_parts() -> None:
    """The constant is derived, so it can be checked rather than trusted.

    17.6 MeV per deuteron-triton pair, over the mass of that pair, is
    3.376e11 joules per gram. A wrong nuclear mass or a wrong reaction
    energy moves this number, which is the point of building it rather
    than quoting it.
    """
    assert dt_specific_energy_j_per_g() == pytest.approx(3.3759e11, rel=1.0e-4)


def test_a_thin_shell_approaches_its_surface_times_thickness() -> None:
    """The exact difference of cubes tends to the thin-shell product."""
    outer, thickness, density = 1000.0, 0.01, 1.0
    exact = spherical_shell_mass_mg(outer, thickness, density)
    approximate = (
        4.0 * math.pi * (outer * 1.0e-4) ** 2 * (thickness * 1.0e-4) * density * 1.0e3
    )
    assert exact == pytest.approx(approximate, rel=1.0e-4)


def test_a_shell_filling_its_sphere_weighs_the_whole_sphere() -> None:
    """As the thickness approaches the radius the cavity vanishes."""
    outer, density = 100.0, 2.0
    nearly_solid = spherical_shell_mass_mg(outer, outer * (1.0 - 1.0e-9), density)
    whole = 4.0 / 3.0 * math.pi * (outer * 1.0e-4) ** 3 * density * 1.0e3
    assert nearly_solid == pytest.approx(whole, rel=1.0e-6)


def test_the_yield_is_linear_in_mass_and_in_burnup() -> None:
    """Both factors enter once."""
    base = fusion_yield_mj(1.0, 0.2)
    assert fusion_yield_mj(2.0, 0.2) == pytest.approx(2.0 * base)
    assert fusion_yield_mj(1.0, 0.4) == pytest.approx(2.0 * base)


def test_the_gain_is_the_yield_over_the_incident_energy() -> None:
    """The review states that a design is named by its incident energy."""
    assert target_gain(72.0, 1.5) == pytest.approx(48.0)


def test_the_printed_gain_is_not_recovered_from_the_printed_geometry() -> None:
    """A recorded non-recovery, kept as a test so it cannot be lost.

    The review prints, for one design, an ice layer 160 micrometres thick
    under a 37 micrometre ablator inside a 1700 micrometre capsule, a
    burnup fraction of 20 %, an incident energy of 1.5 MJ, and a
    one-dimensional gain of 48. Reconstructing the gain from the first
    four, with solid DT at its standard density, gives about 57 — some
    18 % high.

    The gap is not arithmetic and is not a defect in these relations. A
    quoted burnup fraction applies to the fuel that assembles and burns,
    and part of the printed inventory is not in that state at peak
    compression; the review's own text describes shell material still in
    free fall at stagnation. The reconstruction is therefore **not** used
    as an anchor anywhere, and this test exists so that the discrepancy
    stays measured and visible instead of being discovered again later
    by someone who assumes it should close.
    """
    fuel_outer = PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM
    mass = spherical_shell_mass_mg(
        fuel_outer, PRINTED_ICE_THICKNESS_UM, SOLID_DT_DENSITY_G_CM3
    )
    released = fusion_yield_mj(mass, PRINTED_BURNUP_FRACTION)
    reconstructed = target_gain(released, PRINTED_INCIDENT_ENERGY_MJ)
    assert mass == pytest.approx(1.2607, abs=0.0005)
    assert reconstructed == pytest.approx(56.75, abs=0.05)
    assert reconstructed > PRINTED_ONE_DIMENSIONAL_GAIN
    assert reconstructed / PRINTED_ONE_DIMENSIONAL_GAIN == pytest.approx(1.18, abs=0.01)


def test_a_shell_at_least_as_thick_as_its_radius_is_refused() -> None:
    """Such a shell has no cavity, so it is not a shell."""
    with pytest.raises(DeviceConfigurationError, match="no cavity"):
        spherical_shell_mass_mg(100.0, 100.0, 0.25)


def test_a_burnup_fraction_above_one_is_refused() -> None:
    """More fuel cannot burn than was there."""
    with pytest.raises(DeviceConfigurationError, match="must not exceed one"):
        fusion_yield_mj(1.0, 1.1)


def test_a_complete_burn_is_admitted() -> None:
    """A burnup fraction of exactly one is the boundary, not a violation."""
    assert fusion_yield_mj(1.0, 1.0) > fusion_yield_mj(1.0, 0.5)


@pytest.mark.parametrize(
    ("outer", "thickness", "density"),
    [(0.0, 10.0, 0.25), (100.0, 0.0, 0.25), (100.0, 10.0, 0.0)],
)
def test_the_shell_mass_refuses_impossible_input(
    outer: float, thickness: float, density: float
) -> None:
    """Every length and the density are strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        spherical_shell_mass_mg(outer, thickness, density)


def test_a_non_positive_fuel_mass_is_refused() -> None:
    """The rejection names the field."""
    with pytest.raises(DeviceConfigurationError, match="fuel_mass_mg"):
        fusion_yield_mj(0.0, 0.2)


def test_a_non_positive_burnup_fraction_is_refused() -> None:
    """A shot that burns nothing has no yield to report."""
    with pytest.raises(DeviceConfigurationError, match="burnup_fraction"):
        fusion_yield_mj(1.0, 0.0)


@pytest.mark.parametrize(("released", "incident"), [(0.0, 1.5), (72.0, 0.0)])
def test_the_gain_refuses_impossible_input(released: float, incident: float) -> None:
    """Both energies are strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        target_gain(released, incident)


def test_a_non_finite_density_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        spherical_shell_mass_mg(100.0, 10.0, math.nan)
