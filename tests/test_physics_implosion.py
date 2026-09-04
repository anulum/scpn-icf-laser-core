# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — shell implosion figure tests

"""Tests of the shell implosion definitions."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_ABLATOR_THICKNESS_UM,
    PRINTED_ABSORBED_FRACTION,
    PRINTED_HYDRODYNAMIC_EFFICIENCY,
    PRINTED_ICE_THICKNESS_UM,
    PRINTED_INCIDENT_ENERGY_MJ,
    PRINTED_SHELL_KINETIC_ENERGY_KJ,
    PRINTED_TARGET_RADIUS_UM,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.physics.implosion import (
    DT_ADIABAT_COEFFICIENT,
    absorbed_energy_kj,
    convergence_ratio,
    dt_adiabat,
    hydrodynamic_efficiency,
    ifar_evaluation_radius_um,
    in_flight_aspect_ratio,
    require_fraction,
)

DESIGN_INNER_RADIUS_UM = (
    PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM - PRINTED_ICE_THICKNESS_UM
)


def test_the_designs_inner_radius_follows_exactly_from_its_printed_layers() -> None:
    """Three printed lengths give the inner radius as the same double.

    1700, 37 and 160 micrometres are all exactly representable, so this
    is an equality rather than a closeness, and the evaluation radius
    two thirds of the way in lands on 1002 exactly as well — which is
    not automatic, since two thirds is not exact in binary.
    """
    assert DESIGN_INNER_RADIUS_UM == 1503.0
    assert ifar_evaluation_radius_um(DESIGN_INNER_RADIUS_UM) == 1002.0


def test_the_evaluation_radius_is_two_thirds_of_the_inner_radius() -> None:
    """The review fixes where the aspect ratio is read."""
    assert ifar_evaluation_radius_um(300.0) == pytest.approx(200.0)


def test_the_absorbed_energy_of_the_design_is_exact() -> None:
    """95 % of 1.5 MJ is 1425 kJ, and lands on that double exactly."""
    assert (
        absorbed_energy_kj(PRINTED_INCIDENT_ENERGY_MJ, PRINTED_ABSORBED_FRACTION)
        == 1425.0
    )


def test_the_printed_efficiency_reproduces_the_printed_kinetic_energy() -> None:
    """The design's three printed energies are mutually consistent.

    The review prints an incident energy of 1.5 MJ, an absorbed fraction
    of 95 %, a hydrodynamic efficiency of 6.7 % and a shell kinetic
    energy it words as "~100 kJ". Taking the first three gives 95.5 kJ,
    which is that "~100 kJ" to the one significant figure it is stated
    with. Going the other way, 100 kJ over 1425 kJ is 7.0 %, which
    rounds away from the printed 6.7 % — so the chain closes in the
    direction the review's own precision supports and not in the other,
    and the test asserts only the direction that holds.
    """
    absorbed = absorbed_energy_kj(PRINTED_INCIDENT_ENERGY_MJ, PRINTED_ABSORBED_FRACTION)
    reconstructed = PRINTED_HYDRODYNAMIC_EFFICIENCY * absorbed
    assert reconstructed == pytest.approx(95.5, abs=0.1)
    assert round(reconstructed, -2) == PRINTED_SHELL_KINETIC_ENERGY_KJ
    reverse = hydrodynamic_efficiency(PRINTED_SHELL_KINETIC_ENERGY_KJ, absorbed)
    assert reverse == pytest.approx(0.0702, abs=0.0001)
    assert reverse > PRINTED_HYDRODYNAMIC_EFFICIENCY


def test_the_adiabat_is_one_at_the_degenerate_pressure() -> None:
    """The relation is normalised so that the degenerate limit is one."""
    density = 3.0
    degenerate = DT_ADIABAT_COEFFICIENT * math.pow(density, 5.0 / 3.0)
    assert dt_adiabat(degenerate, density) == pytest.approx(1.0)


def test_the_adiabat_falls_as_the_shell_is_compressed_at_fixed_pressure() -> None:
    """Entropy is what the adiabat measures, not pressure alone."""
    assert dt_adiabat(100.0, 20.0) < dt_adiabat(100.0, 10.0)


def test_the_adiabat_rises_with_shell_pressure_at_fixed_density() -> None:
    """A stronger shock at the same density means more entropy added."""
    assert dt_adiabat(200.0, 10.0) == pytest.approx(2.0 * dt_adiabat(100.0, 10.0))


def test_a_thinner_shell_has_a_larger_aspect_ratio() -> None:
    """The aspect ratio is what the review's stability discussion turns on."""
    assert in_flight_aspect_ratio(1002.0, 20.0) > in_flight_aspect_ratio(1002.0, 40.0)


def test_a_shell_thicker_than_its_radius_is_refused() -> None:
    """Such a shell has no inner surface."""
    with pytest.raises(DeviceConfigurationError, match="has no inner surface"):
        in_flight_aspect_ratio(100.0, 200.0)


def test_a_shell_exactly_as_thick_as_its_radius_is_admitted() -> None:
    """The boundary is a solid sphere, with an aspect ratio of one."""
    assert in_flight_aspect_ratio(100.0, 100.0) == 1.0


def test_the_convergence_ratio_is_the_radius_ratio() -> None:
    """Initial inner radius over the radius at peak compression."""
    assert convergence_ratio(1503.0, 1503.0 / 23.0) == pytest.approx(23.0)


def test_an_implosion_that_expands_is_refused() -> None:
    """A stagnation radius above the initial one is not an implosion."""
    with pytest.raises(DeviceConfigurationError, match="an implosion converges"):
        convergence_ratio(100.0, 200.0)


def test_an_implosion_that_does_not_move_converges_by_one() -> None:
    """The boundary case is admitted and reports unity."""
    assert convergence_ratio(100.0, 100.0) == 1.0


def test_a_shell_cannot_carry_more_energy_than_the_target_absorbed() -> None:
    """The efficiency is bounded above by one, by refusal not by clamping."""
    with pytest.raises(DeviceConfigurationError, match="exceeds the absorbed energy"):
        hydrodynamic_efficiency(200.0, 100.0)


def test_an_efficiency_of_one_is_the_boundary() -> None:
    """Absorbing everything into shell motion is admitted and reports one."""
    assert hydrodynamic_efficiency(100.0, 100.0) == 1.0


@pytest.mark.parametrize("fraction", [0.0, -0.1, 1.1])
def test_a_fraction_outside_its_interval_is_refused(fraction: float) -> None:
    """A fraction is refused rather than clamped, in both directions."""
    with pytest.raises(DeviceConfigurationError):
        require_fraction("absorbed_fraction", fraction)


def test_a_fraction_of_exactly_one_is_admitted() -> None:
    """Full absorption is a boundary, not a violation."""
    assert require_fraction("absorbed_fraction", 1.0) == 1.0


def test_a_non_finite_fraction_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_fraction("absorbed_fraction", math.inf)


@pytest.mark.parametrize(
    ("pressure", "density"), [(0.0, 10.0), (100.0, 0.0), (-1.0, 10.0)]
)
def test_the_adiabat_refuses_impossible_input(pressure: float, density: float) -> None:
    """A shell has a positive pressure and a positive density."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        dt_adiabat(pressure, density)


def test_a_non_positive_incident_energy_is_refused() -> None:
    """The rejection names the field."""
    with pytest.raises(DeviceConfigurationError, match="incident_energy_mj"):
        absorbed_energy_kj(0.0, 0.95)


def test_a_non_positive_evaluation_radius_is_refused() -> None:
    """The rejection names the field."""
    with pytest.raises(DeviceConfigurationError, match="initial_inner_radius_um"):
        ifar_evaluation_radius_um(0.0)
