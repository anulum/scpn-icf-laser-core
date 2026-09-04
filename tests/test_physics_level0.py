# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — level-0 physics record tests

"""Tests of the composed level-0 physics record."""

from __future__ import annotations

import json

import pytest

from physics_fixtures import (
    PRINTED_ABLATOR_THICKNESS_UM,
    PRINTED_CONVERGENCE_RATIO,
    PRINTED_ICE_THICKNESS_UM,
    PRINTED_IFAR,
    PRINTED_INCIDENT_ENERGY_MJ,
    PRINTED_SHELL_KINETIC_ENERGY_KJ,
    PRINTED_TARGET_RADIUS_UM,
    SOLID_DT_DENSITY_G_CM3,
    anchor_capsule,
    anchor_configuration,
    anchor_implosion,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.physics.ignition import (
    hot_spot_pressure_floor_gbar,
    hot_spot_radius_ceiling_um,
)
from scpn_icf_laser_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CapsuleDeclaration,
    ImplosionDeclaration,
    initial_inner_radius_um,
    level0_physics,
)


def test_the_inner_radius_is_recovered_from_the_configuration_and_the_layers() -> None:
    """The record measures the cavity rather than being told it.

    The capsule's outer radius lives in the configuration and the two
    thicknesses in the declaration, so the inner radius exists in
    neither and has to be built. All three lengths are exactly
    representable, so this is an equality.
    """
    record = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    )
    assert record.operating_point.initial_inner_radius_um == 1503.0
    assert record.operating_point.ifar_evaluation_radius_um == 1002.0


def test_the_declared_implosion_reproduces_the_printed_shape_figures() -> None:
    """Both figures the review quotes its design's shape by come back.

    The in-flight thickness and the stagnation radius are declared, not
    computed here — the review does not print either. They are declared
    to be what the printed aspect ratio and convergence ratio imply, so
    what this test proves is that the record composes the definitions
    the right way round, not that the design was reproduced.
    """
    point = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    ).operating_point
    assert point.in_flight_aspect_ratio == pytest.approx(PRINTED_IFAR)
    assert point.convergence_ratio == pytest.approx(PRINTED_CONVERGENCE_RATIO)


def test_the_energy_chain_reaches_the_hot_spot_floors() -> None:
    """Absorbed, then kinetic, then coupled, then the two ignition bounds."""
    implosion = anchor_implosion(coupled_fraction=0.4)
    point = level0_physics(
        anchor_configuration(), anchor_capsule(), implosion
    ).operating_point
    assert point.absorbed_energy_kj == 1425.0
    assert point.coupled_energy_kj == pytest.approx(
        0.4 * PRINTED_SHELL_KINETIC_ENERGY_KJ
    )
    assert point.hot_spot_pressure_floor_gbar == hot_spot_pressure_floor_gbar(
        point.coupled_energy_kj
    )
    assert point.hot_spot_radius_ceiling_um == hot_spot_radius_ceiling_um(
        point.coupled_energy_kj
    )


def test_more_coupled_energy_relaxes_both_ignition_bounds() -> None:
    """Raising the coupled fraction lowers the floor and lifts the ceiling."""
    low = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion(coupled_fraction=0.4)
    ).operating_point
    high = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion(coupled_fraction=0.5)
    ).operating_point
    assert high.hot_spot_pressure_floor_gbar < low.hot_spot_pressure_floor_gbar
    assert high.hot_spot_radius_ceiling_um > low.hot_spot_radius_ceiling_um


def test_the_fuel_layer_sits_under_the_ablator() -> None:
    """The fuel's outer radius is the capsule's, less the ablator."""
    point = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    ).operating_point
    expected_outer = PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM
    assert expected_outer == 1663.0
    assert point.fuel_mass_mg == pytest.approx(1.2607, abs=0.0005)


def test_the_gain_reported_is_the_reconstruction_not_the_printed_figure() -> None:
    """The record reports what its inputs give, and nothing is tuned.

    The review prints a gain of 48 for this design; the reconstruction
    from its printed geometry gives about 57. The record carries the
    reconstruction, because that is what its declared inputs imply, and
    the discrepancy is recorded in the yield-and-gain tests rather than
    hidden by adjusting an input until the numbers meet.
    """
    point = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    ).operating_point
    assert point.target_gain == pytest.approx(56.75, abs=0.05)
    assert point.fusion_yield_mj == pytest.approx(
        point.target_gain * PRINTED_INCIDENT_ENERGY_MJ
    )


def test_the_intensity_comes_from_the_configuration_unchanged() -> None:
    """The record does not recompute what the configuration already carries."""
    configuration = anchor_configuration()
    point = level0_physics(
        configuration, anchor_capsule(), anchor_implosion()
    ).operating_point
    assert point.on_target_intensity_w_cm2 == configuration.on_target_intensity_w_cm2()


@pytest.mark.parametrize(
    "identifier",
    [
        "laser_icf_direct_drive",
        "laser_icf_indirect_drive",
        "laser_icf_fast_or_shock_ignition",
    ],
)
def test_every_owned_configuration_composes_a_record(identifier: str) -> None:
    """All three drive schemes carry a capsule and an implosion."""
    record = level0_physics(
        anchor_configuration(identifier=identifier),
        anchor_capsule(),
        anchor_implosion(),
    )
    assert record.operating_point.initial_inner_radius_um == 1503.0


def test_a_layering_that_does_not_fit_is_refused() -> None:
    """Layers thicker than the capsule describe a different capsule."""
    oversized = CapsuleDeclaration(
        ablator_thickness_um=1000.0,
        fuel_thickness_um=900.0,
        fuel_density_g_cm3=SOLID_DT_DENSITY_G_CM3,
    )
    with pytest.raises(DeviceConfigurationError, match="leave no cavity"):
        level0_physics(anchor_configuration(), oversized, anchor_implosion())


def test_a_layering_that_exactly_fills_the_capsule_is_refused() -> None:
    """The boundary leaves no cavity either, so it is refused too."""
    exact = CapsuleDeclaration(
        ablator_thickness_um=PRINTED_ABLATOR_THICKNESS_UM,
        fuel_thickness_um=PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM,
        fuel_density_g_cm3=SOLID_DT_DENSITY_G_CM3,
    )
    with pytest.raises(DeviceConfigurationError, match="leave no cavity"):
        initial_inner_radius_um(anchor_configuration(), exact)


@pytest.mark.parametrize(
    ("ablator", "fuel", "density"),
    [(0.0, 160.0, 0.25), (37.0, 0.0, 0.25), (37.0, 160.0, 0.0)],
)
def test_the_capsule_declaration_refuses_impossible_input(
    ablator: float, fuel: float, density: float
) -> None:
    """Every declared quantity is strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        CapsuleDeclaration(
            ablator_thickness_um=ablator,
            fuel_thickness_um=fuel,
            fuel_density_g_cm3=density,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "absorbed_fraction",
        "coupled_fraction",
        "burnup_fraction",
        "shell_kinetic_energy_kj",
        "in_flight_shell_thickness_um",
        "stagnation_inner_radius_um",
        "shell_pressure_mbar",
        "shell_density_g_cm3",
    ],
)
def test_every_declared_implosion_field_is_validated(field_name: str) -> None:
    """The declaration validates each field where it is declared.

    A record can never be built from a set the relations would have
    refused one at a time, so each is checked here as well as inside the
    relation that consumes it.

    Parameters
    ----------
    field_name
        The field set to zero for this case.
    """
    baseline = anchor_implosion()
    values = {
        name: getattr(baseline, name)
        for name in (
            "absorbed_fraction",
            "shell_kinetic_energy_kj",
            "coupled_fraction",
            "in_flight_shell_thickness_um",
            "stagnation_inner_radius_um",
            "shell_pressure_mbar",
            "shell_density_g_cm3",
            "burnup_fraction",
        )
    }
    values[field_name] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field_name):
        ImplosionDeclaration(**values)


@pytest.mark.parametrize(
    "field_name", ["absorbed_fraction", "coupled_fraction", "burnup_fraction"]
)
def test_a_declared_fraction_above_one_is_refused(field_name: str) -> None:
    """The three fractions are bounded above as well as below.

    Parameters
    ----------
    field_name
        The fraction set above one for this case.
    """
    baseline = anchor_implosion()
    values = {
        name: getattr(baseline, name)
        for name in (
            "absorbed_fraction",
            "shell_kinetic_energy_kj",
            "coupled_fraction",
            "in_flight_shell_thickness_um",
            "stagnation_inner_radius_um",
            "shell_pressure_mbar",
            "shell_density_g_cm3",
            "burnup_fraction",
        )
    }
    values[field_name] = 1.5
    with pytest.raises(DeviceConfigurationError, match="must not exceed one"):
        ImplosionDeclaration(**values)


def test_the_record_serialises_canonically() -> None:
    """Sorted keys, no NaN, one trailing newline, and a stable digest."""
    record = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    )
    raw = record.canonical_bytes()
    assert raw.endswith(b"\n")
    decoded = json.loads(raw.decode("utf-8"))
    assert decoded["schema"] == LEVEL0_SCHEMA
    assert decoded["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert decoded["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert list(decoded) == sorted(decoded)
    assert decoded["capsule"]["fuel_thickness_um"] == PRINTED_ICE_THICKNESS_UM
    assert (
        record.digest_sha256()
        == level0_physics(
            anchor_configuration(), anchor_capsule(), anchor_implosion()
        ).digest_sha256()
    )


def test_a_different_implosion_gives_a_different_digest() -> None:
    """The digest identifies the declarations, not only the configuration."""
    first = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion(coupled_fraction=0.4)
    )
    second = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion(coupled_fraction=0.5)
    )
    assert first.digest_sha256() != second.digest_sha256()


def test_the_declarations_project_every_field() -> None:
    """Both declarations round-trip into the record completely."""
    record = level0_physics(
        anchor_configuration(), anchor_capsule(), anchor_implosion()
    )
    capsule = record.capsule.to_record()
    implosion = record.implosion.to_record()
    assert capsule["ablator_thickness_um"] == PRINTED_ABLATOR_THICKNESS_UM
    assert set(implosion) == {
        "absorbed_fraction",
        "shell_kinetic_energy_kj",
        "coupled_fraction",
        "in_flight_shell_thickness_um",
        "stagnation_inner_radius_um",
        "shell_pressure_mbar",
        "shell_density_g_cm3",
        "burnup_fraction",
    }


def test_the_non_claims_are_carried_verbatim() -> None:
    """Every non-claim reaches the record, and none is empty."""
    assert len(LEVEL0_NON_CLAIMS) == len(set(LEVEL0_NON_CLAIMS))
    for statement in LEVEL0_NON_CLAIMS:
        assert statement.strip() == statement
        assert statement
