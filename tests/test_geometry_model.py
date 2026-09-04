# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — tier-G1 device model tests

"""Tests of the tessellated device model.

Reproducing a printed value is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

import dataclasses
import json
import math

import pytest

from geometry_fixtures import (
    ANCHOR_CAPSULE_RADIUS_M,
    ANCHOR_CASE_RADIUS_M,
    ANCHOR_CAVITY_RADIUS_M,
    ANCHOR_FUEL_OUTER_RADIUS_M,
    ANCHOR_RINGS,
    ANCHOR_SEGMENTS,
    PRINTED_ABLATOR_THICKNESS_UM,
    PRINTED_CASE_TO_CAPSULE_RADIUS_RATIO,
    PRINTED_HOHLRAUM_AREA_RATIO_RANGE,
    PRINTED_ICE_THICKNESS_UM,
    anchor_capsule,
    anchor_configuration,
    anchor_hohlraum,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError, DeviceGeometryError
from scpn_icf_laser_core.geometry import MICROMETRE_M
from scpn_icf_laser_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_HOHLRAUM_WALL,
    BODY_NAMES_BY_IDENTIFIER,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    ROLE_ABLATOR,
    ROLE_ENCLOSURE,
    ROLE_FUEL,
    DeviceModel3D,
    build_device_model,
    capsule_radii_m,
    require_containment,
)
from scpn_icf_laser_core.physics.level0 import CapsuleDeclaration

DIRECT_IDENTIFIERS = ("laser_icf_direct_drive", "laser_icf_fast_or_shock_ignition")

#: Largest relative departure admitted when a printed micrometre
#: thickness is recovered from two metre-scale radii. Measured: the ice
#: thickness comes back exactly, the ablator thickness at 2.1e-15, which
#: is nine unit-in-last-place steps of a value near 37.
THICKNESS_RECOVERY_TOLERANCE = 1.0e-14


def direct_model() -> DeviceModel3D:
    """Build the directly driven anchor model.

    Returns
    -------
    DeviceModel3D
        The three capsule bodies at the anchor resolutions.
    """
    return build_device_model(
        anchor_configuration(), anchor_capsule(), ANCHOR_SEGMENTS, ANCHOR_RINGS
    )


def indirect_model() -> DeviceModel3D:
    """Build the indirectly driven anchor model.

    Returns
    -------
    DeviceModel3D
        The three capsule bodies and the enclosure around them.
    """
    return build_device_model(
        anchor_configuration(identifier="laser_icf_indirect_drive"),
        anchor_capsule(),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
        anchor_hohlraum(),
    )


def pole_radius_m(model: DeviceModel3D, name: str) -> float:
    """Return the outermost pole height of one body of a model.

    Parameters
    ----------
    model
        The built model.
    name
        Body name to read.

    Returns
    -------
    float
        The largest ``z`` over that body's vertices. Every spherical
        body here is centred on the origin and its profile places a
        vertex at exactly ``+radius``, so this is the body's outer
        radius rather than an approximation of it.
    """
    body = next(mesh for mesh in model.meshes if mesh.name == name)
    return max(z for _, _, z in body.vertices)


@pytest.mark.parametrize("identifier", DIRECT_IDENTIFIERS)
def test_a_directly_driven_target_is_three_concentric_bodies(identifier: str) -> None:
    """No enclosure is drawn where the drive reaches the capsule directly.

    The ignitor pulse of the fast-or-shock-ignition class is light, not
    hardware, so that class draws the same three bodies as plain direct
    drive.
    """
    model = build_device_model(
        anchor_configuration(identifier=identifier),
        anchor_capsule(),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
    )
    assert tuple(mesh.name for mesh in model.meshes) == (
        BODY_ABLATOR_SHELL,
        BODY_FUEL_ICE_SHELL,
        BODY_FUEL_VAPOUR_CORE,
    )
    assert model.hohlraum_digest_sha256 is None


def test_an_indirectly_driven_target_adds_the_enclosure() -> None:
    """The fourth body exists for exactly one identifier."""
    model = indirect_model()
    assert tuple(mesh.name for mesh in model.meshes) == (
        BODY_ABLATOR_SHELL,
        BODY_FUEL_ICE_SHELL,
        BODY_FUEL_VAPOUR_CORE,
        BODY_HOHLRAUM_WALL,
    )
    assert model.hohlraum_digest_sha256 == anchor_hohlraum().digest_sha256()


def test_the_vapour_is_drawn_although_it_is_a_gas() -> None:
    """The cavity carries a body because the review declares what is in it.

    The beam-target family draws nothing inside its bore because nothing
    is declared to be there. Here the fuel vapour has a printed density
    and belongs to the fuel inventory, so it is a body with a positive
    volume rather than an absence.
    """
    body = next(
        mesh for mesh in direct_model().meshes if mesh.name == BODY_FUEL_VAPOUR_CORE
    )
    assert body.role == ROLE_FUEL
    assert body.signed_volume_m3() > 0.0


def test_the_printed_capsule_radius_is_recovered_from_the_built_body() -> None:
    """The outer radius is read off the body, not off the configuration.

    The sphere profile places a vertex at exactly the centre plus the
    radius, and the capsule is centred on the origin, so this is an
    equality rather than a comparison within a tolerance.
    """
    assert pole_radius_m(direct_model(), BODY_ABLATOR_SHELL) == ANCHOR_CAPSULE_RADIUS_M


def test_the_three_capsule_radii_are_recovered_from_the_built_bodies() -> None:
    """Each layer's outer surface is where the declaration says it is."""
    model = direct_model()
    assert pole_radius_m(model, BODY_ABLATOR_SHELL) == ANCHOR_CAPSULE_RADIUS_M
    assert pole_radius_m(model, BODY_FUEL_ICE_SHELL) == ANCHOR_FUEL_OUTER_RADIUS_M
    assert pole_radius_m(model, BODY_FUEL_VAPOUR_CORE) == ANCHOR_CAVITY_RADIUS_M


def test_the_printed_layer_thicknesses_are_recovered_from_the_built_bodies() -> None:
    """The printed thicknesses come back out of the geometry.

    Measured, and the two behave differently: the ice thickness returns
    exactly 160, and the ablator thickness returns 36.99999999999992.
    The layer arithmetic is exact in micrometres — 1700, 1663 and 1503
    are all integers — and the rounding is introduced by the conversion
    to metres, where 1.7e-3 and 1.663e-3 are not representable and their
    difference no longer lands on 3.7e-5. The equality was measured
    before it was written, and it does not hold, so this is a bound and
    not an equality.
    """
    model = direct_model()
    ablator = (
        pole_radius_m(model, BODY_ABLATOR_SHELL)
        - pole_radius_m(model, BODY_FUEL_ICE_SHELL)
    ) / MICROMETRE_M
    ice = (
        pole_radius_m(model, BODY_FUEL_ICE_SHELL)
        - pole_radius_m(model, BODY_FUEL_VAPOUR_CORE)
    ) / MICROMETRE_M
    assert abs(ablator - PRINTED_ABLATOR_THICKNESS_UM) <= (
        THICKNESS_RECOVERY_TOLERANCE * PRINTED_ABLATOR_THICKNESS_UM
    )
    assert ice == PRINTED_ICE_THICKNESS_UM


def test_the_printed_case_to_capsule_ratio_is_recovered_from_the_built_bodies() -> None:
    """The enclosure stands at the printed ratio, measured from the solids.

    The case radius is the smallest distance from the axis to any vertex
    of the enclosure, and the capsule radius is the ablator's pole. Both
    are exact in binary and their quotient is exactly four, so this is
    an equality.
    """
    model = indirect_model()
    wall = next(mesh for mesh in model.meshes if mesh.name == BODY_HOHLRAUM_WALL)
    case_radius = min(math.hypot(x, y) for x, y, _ in wall.vertices)
    assert case_radius == ANCHOR_CASE_RADIUS_M
    ratio = case_radius / pole_radius_m(model, BODY_ABLATOR_SHELL)
    assert ratio == PRINTED_CASE_TO_CAPSULE_RADIUS_RATIO


def test_the_enclosure_area_lands_inside_the_printed_band() -> None:
    """The built enclosure is as large compared to the capsule as printed.

    Both areas are read from the bodies actually built, and both are
    polyhedral rather than ideal. The capsule's outer area comes out of
    the three recorded body areas by an identity: each shell records the
    sum of its two surfaces, so the ablator's area less the ice shell's
    plus the vapour core's leaves exactly the outermost surface. The
    enclosure's interior area is its inner perimeter times its built
    length, which is the lateral wall alone and therefore a lower bound
    on the enclosing surface the printed statement describes.

    Measured: 20.5, inside the printed 15 to 25.
    """
    model = indirect_model()
    areas = {mesh.name: mesh.surface_area_m2() for mesh in model.meshes}
    capsule_outer_area = (
        areas[BODY_ABLATOR_SHELL]
        - areas[BODY_FUEL_ICE_SHELL]
        + areas[BODY_FUEL_VAPOUR_CORE]
    )
    wall = next(mesh for mesh in model.meshes if mesh.name == BODY_HOHLRAUM_WALL)
    case_radius = min(math.hypot(x, y) for x, y, _ in wall.vertices)
    low, high = wall.bounding_box()
    length = high[2] - low[2]
    chord = 2.0 * case_radius * math.sin(math.pi / model.segments)
    interior_area = model.segments * chord * length
    ratio = interior_area / capsule_outer_area
    lowest, highest = PRINTED_HOHLRAUM_AREA_RATIO_RANGE
    assert lowest <= ratio <= highest


def test_swapping_the_anchor_resolutions_is_refused_by_the_segment_rule() -> None:
    """At the anchor counts the swap happens to be caught, and only there.

    Segments must be a multiple of eight and the anchor ring count is
    not one, so handing the ring count to the segments is refused. That
    is a property of these two particular numbers, not a guard against
    the mistake: the next test builds the same swap from two counts that
    are both legal and nothing objects.
    """
    with pytest.raises(DeviceGeometryError, match="multiple of 8"):
        build_device_model(
            anchor_configuration(), anchor_capsule(), ANCHOR_RINGS, ANCHOR_SEGMENTS
        )


def test_the_rings_and_the_segments_are_not_interchangeable() -> None:
    """Swapping two legal resolutions builds a different body, unnoticed.

    The rings sample the profile and the segments sample the
    revolution. Where both counts are legal, nothing in either would
    object to being handed the other and no gate downstream would
    notice, so the difference is asserted here.
    """
    upright = build_device_model(anchor_configuration(), anchor_capsule(), 8, 16)
    swapped = build_device_model(anchor_configuration(), anchor_capsule(), 16, 8)
    assert swapped.digest_sha256() != upright.digest_sha256()


def test_a_finer_profile_encloses_more_volume() -> None:
    """More rings inscribe more of the surface they approximate."""
    coarse = build_device_model(
        anchor_configuration(), anchor_capsule(), ANCHOR_SEGMENTS, 16
    )
    fine = direct_model()
    coarse_volume = coarse.meshes[2].signed_volume_m3()
    fine_volume = fine.meshes[2].signed_volume_m3()
    assert fine_volume > coarse_volume


def test_the_capsule_radii_are_converted_in_one_place() -> None:
    """The single conversion returns the three radii the bodies are built at."""
    assert capsule_radii_m(anchor_configuration(), anchor_capsule()) == (
        ANCHOR_CAPSULE_RADIUS_M,
        ANCHOR_FUEL_OUTER_RADIUS_M,
        ANCHOR_CAVITY_RADIUS_M,
    )


def test_a_layering_that_does_not_fit_is_refused_by_the_physics_relation() -> None:
    """The geometry cannot draw a capsule the level-0 record would refuse."""
    with pytest.raises(DeviceConfigurationError, match="no cavity"):
        build_device_model(
            anchor_configuration(),
            CapsuleDeclaration(
                ablator_thickness_um=900.0,
                fuel_thickness_um=900.0,
                fuel_density_g_cm3=0.25,
            ),
            ANCHOR_SEGMENTS,
            ANCHOR_RINGS,
        )


def test_an_indirect_drive_model_without_an_enclosure_is_refused() -> None:
    """Indirect drive is defined by the enclosure the drive radiates from."""
    with pytest.raises(DeviceGeometryError, match="hohlraum: required"):
        build_device_model(
            anchor_configuration(identifier="laser_icf_indirect_drive"),
            anchor_capsule(),
            ANCHOR_SEGMENTS,
            ANCHOR_RINGS,
        )


@pytest.mark.parametrize("identifier", DIRECT_IDENTIFIERS)
def test_a_directly_driven_model_with_an_enclosure_is_refused(identifier: str) -> None:
    """A case around a directly driven capsule would block its own drive."""
    with pytest.raises(DeviceGeometryError, match="must be absent"):
        build_device_model(
            anchor_configuration(identifier=identifier),
            anchor_capsule(),
            ANCHOR_SEGMENTS,
            ANCHOR_RINGS,
            anchor_hohlraum(),
        )


def test_a_case_no_wider_than_the_capsule_is_refused() -> None:
    """A case the capsule fills leaves no volume for the radiation field."""
    envelope = dataclasses.replace(
        anchor_hohlraum(), case_radius_m=ANCHOR_CAPSULE_RADIUS_M
    )
    with pytest.raises(DeviceGeometryError, match="case_radius_m"):
        require_containment(ANCHOR_CAPSULE_RADIUS_M, envelope)


def test_a_case_no_longer_than_the_capsule_diameter_is_refused() -> None:
    """A case shorter than the capsule cannot contain it."""
    envelope = dataclasses.replace(
        anchor_hohlraum(), length_m=2.0 * ANCHOR_CAPSULE_RADIUS_M
    )
    with pytest.raises(DeviceGeometryError, match="length_m"):
        require_containment(ANCHOR_CAPSULE_RADIUS_M, envelope)


def test_a_case_that_contains_the_capsule_is_admitted() -> None:
    """The anchor enclosure contains the anchor capsule.

    The check returns nothing and refuses by raising, so the assertion
    here is that it does not raise.
    """
    require_containment(ANCHOR_CAPSULE_RADIUS_M, anchor_hohlraum())


@pytest.mark.parametrize(("segments", "rings"), [(7, 64), (8, 1)])
def test_an_invalid_resolution_is_refused_under_the_device_error(
    segments: int, rings: int
) -> None:
    """The library's refusal arrives as this package's error type."""
    with pytest.raises(DeviceGeometryError):
        build_device_model(anchor_configuration(), anchor_capsule(), segments, rings)


def test_an_unknown_identifier_is_refused() -> None:
    """A model can only be built for a body set this family owns."""
    model = direct_model()
    with pytest.raises(DeviceGeometryError, match="identifier"):
        dataclasses.replace(model, identifier="laser_icf_unknown")


def test_a_body_set_in_the_wrong_order_is_refused() -> None:
    """The order is part of the contract, not an accident of construction."""
    model = direct_model()
    with pytest.raises(DeviceGeometryError, match="in order"):
        dataclasses.replace(model, meshes=tuple(reversed(model.meshes)))


def test_the_record_states_its_schema_units_and_non_claims() -> None:
    """The record carries what a consumer needs to read it correctly."""
    record = direct_model().to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == dict(MODEL_UNITS)
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert record["rings"] == ANCHOR_RINGS
    assert record["segments"] == ANCHOR_SEGMENTS


def test_every_body_reports_its_identity_and_its_measures() -> None:
    """Each body entry carries its name, role, material and measures."""
    record = indirect_model().to_record()
    roles = {body["name"]: body["role"] for body in record["bodies"]}
    assert roles == {
        BODY_ABLATOR_SHELL: ROLE_ABLATOR,
        BODY_FUEL_ICE_SHELL: ROLE_FUEL,
        BODY_FUEL_VAPOUR_CORE: ROLE_FUEL,
        BODY_HOHLRAUM_WALL: ROLE_ENCLOSURE,
    }
    for body in record["bodies"]:
        assert body["volume_m3"] > 0.0
        assert body["surface_area_m2"] > 0.0
        assert body["vertex_count"] > 0
        assert body["face_count"] > 0


def test_the_canonical_bytes_are_sorted_minimal_and_newline_terminated() -> None:
    """The model serialises the way every other record here does."""
    model = direct_model()
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_model() -> None:
    """The same design digests the same; a different capsule does not."""
    assert direct_model().digest_sha256() == direct_model().digest_sha256()
    thicker = build_device_model(
        anchor_configuration(),
        CapsuleDeclaration(
            ablator_thickness_um=40.0,
            fuel_thickness_um=160.0,
            fuel_density_g_cm3=0.25,
        ),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
    )
    assert thicker.digest_sha256() != direct_model().digest_sha256()
    assert thicker.capsule_digest_sha256 != direct_model().capsule_digest_sha256


def test_every_owned_configuration_has_a_body_set() -> None:
    """The map covers exactly the configurations this repository owns."""
    from scpn_icf_laser_core import OWNED_CONFIGURATIONS

    assert sorted(BODY_NAMES_BY_IDENTIFIER) == sorted(OWNED_CONFIGURATIONS)
