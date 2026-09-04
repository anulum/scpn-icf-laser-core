# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — hot-spot ignition condition tests

"""Tests of the hot-spot ignition condition."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_COUPLED_FRACTION_RANGE,
    PRINTED_ENERGY_SCALE_KJ,
    PRINTED_EQ36_COEFFICIENT_GBAR,
    PRINTED_EQ36_REFERENCE_RADIUS_UM,
    PRINTED_EQ37_COEFFICIENT_GBAR,
    PRINTED_EQ38_COEFFICIENT_UM,
    PRINTED_SHELL_KINETIC_ENERGY_KJ,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.physics.ignition import (
    IGNITION_AREAL_DENSITY_G_CM2,
    IGNITION_ION_TEMPERATURE_KEV,
    dt_pressure_gbar,
    hot_spot_energy_kj,
    hot_spot_pressure_floor_gbar,
    hot_spot_pressure_for_radius_gbar,
    hot_spot_radius_ceiling_um,
    ignition_condition_met,
)

# Measured, not chosen: the three printed coefficients close on the energy
# relation to this same relative offset at every energy from 1 kJ to 1 MJ.
# It is the rounding of the printed coefficients, not a disagreement.
CLOSURE_OFFSET = 0.005310
CLOSURE_TOLERANCE = 1.0e-5


def test_equation_thirty_eight_coefficient_is_recovered_exactly() -> None:
    """The 40 micrometres of equation 3-8 is not an independent number.

    It is equation 3-6's reference radius scaled by the ratio of the two
    printed pressures, 100 Gbar over 250 Gbar. The review prints all
    three, so one can be recovered from the other two — and here it is
    recovered as the same IEEE double, so the test asserts an equality
    rather than a closeness.
    """
    recovered = (
        PRINTED_EQ36_REFERENCE_RADIUS_UM
        * PRINTED_EQ36_COEFFICIENT_GBAR
        / PRINTED_EQ37_COEFFICIENT_GBAR
    )
    assert recovered == PRINTED_EQ38_COEFFICIENT_UM
    assert hot_spot_radius_ceiling_um(PRINTED_ENERGY_SCALE_KJ) == (
        PRINTED_EQ38_COEFFICIENT_UM
    )


def test_the_reference_pressure_is_reproduced_at_the_reference_radius() -> None:
    """Equation 3-6 returns its own coefficient at its own radius."""
    assert hot_spot_pressure_for_radius_gbar(PRINTED_EQ36_REFERENCE_RADIUS_UM) == (
        PRINTED_EQ36_COEFFICIENT_GBAR
    )


def test_the_scale_energy_reproduces_the_coefficient_of_equation_thirty_seven() -> None:
    """Equation 3-7 returns its own coefficient at its own energy scale."""
    assert hot_spot_pressure_floor_gbar(PRINTED_ENERGY_SCALE_KJ) == (
        PRINTED_EQ37_COEFFICIENT_GBAR
    )


@pytest.mark.parametrize("scale", [0.1, 1.0, 4.0, 5.0, 25.0, 100.0])
def test_the_three_equations_close_on_the_energy_relation(scale: float) -> None:
    """Equations 3-7 and 3-8 put back the energy they were derived from.

    Taking both at equality and substituting into ``f_k E_k = 2 pi P R^3``
    must return the energy they were evaluated at. It returns it 0.53 %
    high, at every energy over three decades and by the same relative
    amount — which is what rounding three coefficients to one or two
    significant figures does, and is not a disagreement about the
    physics. A test that demanded exactness here would be demanding
    something the printed numbers cannot supply.
    """
    energy = PRINTED_ENERGY_SCALE_KJ * scale
    pressure = hot_spot_pressure_floor_gbar(energy)
    radius = hot_spot_radius_ceiling_um(energy)
    closed = hot_spot_energy_kj(pressure, radius)
    assert math.isclose(
        closed / energy - 1.0, CLOSURE_OFFSET, abs_tol=CLOSURE_TOLERANCE
    )


def test_the_pressure_floor_falls_as_the_coupled_energy_rises() -> None:
    """The point the review draws from equation 3-7."""
    floors = [hot_spot_pressure_floor_gbar(e) for e in (10.0, 40.0, 100.0, 400.0)]
    assert floors == sorted(floors, reverse=True)


def test_the_radius_ceiling_rises_as_the_coupled_energy_rises() -> None:
    """The point the review draws from equation 3-8."""
    ceilings = [hot_spot_radius_ceiling_um(e) for e in (10.0, 40.0, 100.0, 400.0)]
    assert ceilings == sorted(ceilings)


def test_the_reviews_worked_pressure_range_is_not_reproduced() -> None:
    """A recorded non-recovery, kept visible rather than smoothed away.

    The review works equation 3-7 for its own design — about 100 kJ of
    shell kinetic energy with f_k between 0.4 and 0.5 — and states that
    the required hot-spot pressure exceeds "120 to 180 Gbar". Its own
    equation gives 112 to 125 Gbar at those inputs. The lower end is
    close; the 180 is not produced by any f_k in the stated range, and
    would need about 19 kJ of coupled energy.

    Nothing here is adjusted to make the numbers meet. The equation is
    implemented as printed, this test states what it yields, and the
    discrepancy stays a property of the source.
    """
    low, high = PRINTED_COUPLED_FRACTION_RANGE
    at_low = hot_spot_pressure_floor_gbar(low * PRINTED_SHELL_KINETIC_ENERGY_KJ)
    at_high = hot_spot_pressure_floor_gbar(high * PRINTED_SHELL_KINETIC_ENERGY_KJ)
    assert at_low == pytest.approx(125.0, abs=0.5)
    assert at_high == pytest.approx(111.8, abs=0.5)
    assert at_high < at_low < 180.0


def test_the_pressure_coefficient_follows_from_the_ignition_condition() -> None:
    """Equation 3-6's coefficient is the DT pressure at the ignition point.

    Equation 3-5 requires 0.3 g/cm2 and 5 keV. Spread over a hot spot of
    the reference radius that areal density is 30 g/cm3, and the DT
    pressure relation the review states gives 115 Gbar there. The review
    prints 100 Gbar — one significant figure, and 15 % below the value
    its own inputs give. The implementation carries the printed
    coefficient; this test carries the arithmetic, so the rounding is
    recorded rather than discovered later.
    """
    density = IGNITION_AREAL_DENSITY_G_CM2 / (PRINTED_EQ36_REFERENCE_RADIUS_UM * 1.0e-4)
    assert density == 30.0
    computed = dt_pressure_gbar(IGNITION_ION_TEMPERATURE_KEV, density)
    assert computed == pytest.approx(114.95, abs=0.01)
    assert computed > PRINTED_EQ36_COEFFICIENT_GBAR


def test_both_ignition_floors_must_be_met() -> None:
    """Equation 3-5 is two conditions, and neither compensates for the other."""
    assert ignition_condition_met(0.3, 5.0)
    assert ignition_condition_met(1.0, 10.0)
    assert not ignition_condition_met(0.29, 10.0)
    assert not ignition_condition_met(1.0, 4.9)


def test_the_dt_pressure_rises_with_temperature_and_density() -> None:
    """Both factors enter linearly."""
    base = dt_pressure_gbar(5.0, 30.0)
    assert dt_pressure_gbar(10.0, 30.0) == pytest.approx(2.0 * base)
    assert dt_pressure_gbar(5.0, 60.0) == pytest.approx(2.0 * base)


@pytest.mark.parametrize(
    ("areal_density", "temperature"), [(0.0, 5.0), (-0.1, 5.0), (0.3, 0.0)]
)
def test_the_ignition_condition_refuses_impossible_input(
    areal_density: float, temperature: float
) -> None:
    """A hot spot has a positive density and a positive temperature."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        ignition_condition_met(areal_density, temperature)


def test_a_non_finite_temperature_is_refused() -> None:
    """Non-finite input is rejected, never clamped."""
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        dt_pressure_gbar(math.nan, 30.0)


def test_a_non_positive_density_is_refused() -> None:
    """The rejection names the field."""
    with pytest.raises(DeviceConfigurationError, match="mass_density_g_cm3"):
        dt_pressure_gbar(5.0, 0.0)


def test_a_hot_spot_of_no_size_is_refused() -> None:
    """Equation 3-6 divides by the radius."""
    with pytest.raises(DeviceConfigurationError, match="hot_spot_radius_um"):
        hot_spot_pressure_for_radius_gbar(0.0)


@pytest.mark.parametrize("energy", [0.0, -1.0])
def test_a_non_positive_coupled_energy_is_refused(energy: float) -> None:
    """Both energy-driven forms refuse it."""
    with pytest.raises(DeviceConfigurationError, match="coupled_energy_kj"):
        hot_spot_pressure_floor_gbar(energy)
    with pytest.raises(DeviceConfigurationError, match="coupled_energy_kj"):
        hot_spot_radius_ceiling_um(energy)


@pytest.mark.parametrize(
    ("pressure", "radius"), [(0.0, 40.0), (250.0, 0.0), (-1.0, 40.0)]
)
def test_the_energy_relation_refuses_impossible_input(
    pressure: float, radius: float
) -> None:
    """A hot spot has a positive pressure and a positive radius."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        hot_spot_energy_kj(pressure, radius)
