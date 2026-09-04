# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — tier-G2 device model tests

"""Every branch of the tier-G2 model, and what its geometry is limited by.

The two passing builds are cached: each costs about five seconds, and
rebuilding one per test buys no evidence a single build does not already
carry. The three builds that are supposed to fail are not cached,
because what they assert is the failure.
"""

from __future__ import annotations

import dataclasses
import functools
import json

import pytest

from geometry_fixtures import (
    ANCHOR_RINGS,
    anchor_capsule,
    anchor_configuration,
    anchor_hohlraum,
)
from scpn_icf_laser_core.errors import DeviceGeometryError
from scpn_icf_laser_core.geometry import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_HOHLRAUM_WALL,
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DEFAULT_SPHERE_RINGS,
    DeviceModelCAD,
    build_device_cad,
)

#: Ring count measured to break the back-end's own volume measure at this
#: radius. Thirty-two is exact; forty-eight is not.
RINGS_ABOVE_THE_CEILING = 48
#: Linear deflection measured not to pass: one step below the default,
#: the vapour core exceeds its declared bound.
DEFLECTION_BELOW_WHAT_PASSES_M = 1.0e-7
#: The strongest guarantee any declared bound makes here. Measured: the
#: widest is the vapour core's at 0.0266 %.
BOUND_CEILING = 1.0e-3


@functools.cache
def direct_cad() -> DeviceModelCAD:
    """Build and cache the directly driven B-rep model.

    Returns
    -------
    DeviceModelCAD
        The three capsule bodies at the module defaults.
    """
    return build_device_cad(anchor_configuration(), anchor_capsule())


@functools.cache
def indirect_cad() -> DeviceModelCAD:
    """Build and cache the indirectly driven B-rep model.

    Returns
    -------
    DeviceModelCAD
        The three capsule bodies and the enclosure around them.
    """
    return build_device_cad(
        anchor_configuration(identifier="laser_icf_indirect_drive"),
        anchor_capsule(),
        anchor_hohlraum(),
    )


def test_the_body_set_follows_the_identifier_at_this_tier_too() -> None:
    """Both tiers draw the same bodies for the same configuration."""
    assert (
        tuple(body.name for body in direct_cad().bodies)
        == (BODY_NAMES_BY_IDENTIFIER["laser_icf_direct_drive"])
    )
    assert (
        tuple(body.name for body in indirect_cad().bodies)
        == (BODY_NAMES_BY_IDENTIFIER["laser_icf_indirect_drive"])
    )


def test_every_body_measures_as_its_analytic_form_says_it_should() -> None:
    """The back-end's volume and area agree with the closed forms.

    The evidence kernel refuses at construction if they do not, so a
    model existing is already the assertion. This states the margin
    rather than restating the refusal: measured, every relative error
    here is at the level of floating-point noise.
    """
    for body in indirect_cad().bodies:
        assert body.volume_relative_error < 1e-12
        assert body.surface_area_relative_error < 1e-12


def test_every_faceted_body_clears_its_declared_deficit_bound() -> None:
    """The faceting loses less volume than the declared bound allows.

    Measured at the module's deflections: the worst body is the vapour
    core, at 0.57 of its bound.
    """
    for body in indirect_cad().bodies:
        assert body.faceted_volume_relative_deficit <= (
            body.faceted_volume_deficit_bound
        )
        assert body.faceted_volume_deficit_bound < BOUND_CEILING


def test_every_faceted_body_agrees_with_its_tier_one_twin() -> None:
    """The B-rep and the tessellation describe the same solid."""
    for body in indirect_cad().bodies:
        assert body.mesh_volume_relative_difference <= (
            body.mesh_volume_difference_bound
        )


def test_the_ring_count_the_back_end_cannot_hold_is_refused() -> None:
    """Above the measured ceiling the solid is wrong and the build refuses.

    At this radius the revolve is exact to 7e-15 up to thirty-two rings
    and departs by 3.5e-5 at forty-eight, which is far above the
    library's measure tolerance. Nothing here was loosened to admit it:
    the evidence kernel refuses, naming the body and the bound, and this
    test is the record that the refusal is real rather than theoretical.
    """
    with pytest.raises(DeviceGeometryError, match="volume_relative_error"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            None,
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            RINGS_ABOVE_THE_CEILING,
        )


def test_the_next_tighter_deflection_does_not_pass() -> None:
    """The declared deflection is the tightest bound the bodies clear.

    One step below it the vapour core's deficit exceeds its own bound by
    about fifteen per cent. Recording that here is what makes the choice
    of deflection falsifiable rather than a preference.
    """
    with pytest.raises(DeviceGeometryError, match="faceted_volume_relative_deficit"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            None,
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            DEFAULT_SPHERE_RINGS,
            DEFLECTION_BELOW_WHAT_PASSES_M,
        )


def test_an_invalid_deflection_arrives_as_the_device_error() -> None:
    """The library's refusal is re-raised under this package's error type."""
    with pytest.raises(DeviceGeometryError, match="strictly positive"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            None,
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            DEFAULT_SPHERE_RINGS,
            0.0,
        )


def test_the_record_states_its_schema_units_and_non_claims() -> None:
    """The record carries what a consumer needs to read it correctly."""
    record = direct_cad().to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["units"] == dict(CAD_MODEL_UNITS)
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["rings"] == DEFAULT_SPHERE_RINGS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD


def test_the_record_carries_the_evidence_of_every_body() -> None:
    """Each body's checked evidence is in the record, in order."""
    record = indirect_cad().to_record()
    names = [body["name"] for body in record["bodies"]]
    assert names == list(BODY_NAMES_BY_IDENTIFIER["laser_icf_indirect_drive"])
    for body in record["bodies"]:
        assert body["analytic_volume_m3"] > 0.0
        assert body["faceted_volume_deficit_bound"] > 0.0


def test_the_two_tiers_agree_on_what_the_design_is() -> None:
    """Both tiers report the same digests for the same inputs."""
    model = indirect_cad()
    assert model.configuration_digest_sha256 == (
        anchor_configuration(identifier="laser_icf_indirect_drive").digest_sha256()
    )
    assert model.hohlraum_digest_sha256 == anchor_hohlraum().digest_sha256()
    assert model.rings == ANCHOR_RINGS


def test_a_directly_driven_model_reports_no_enclosure_digest() -> None:
    """There is no enclosure, so there is no digest of one."""
    assert direct_cad().hohlraum_digest_sha256 is None


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The model serialises the way every other record here does."""
    data = direct_cad().canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_model() -> None:
    """The record digests stably, and the two body sets differ."""
    assert direct_cad().digest_sha256() == direct_cad().digest_sha256()
    assert direct_cad().digest_sha256() != indirect_cad().digest_sha256()


def test_the_step_export_is_deterministic_within_this_environment() -> None:
    """The normalised STEP bytes carry a digest of themselves."""
    model = indirect_cad()
    assert model.step_data
    assert model.step_sha256 == indirect_cad().step_sha256
    assert model.backend_versions


def test_the_faceted_meshes_are_the_bodies_that_were_checked() -> None:
    """The meshes the evidence came from are kept, in the same order."""
    model = indirect_cad()
    assert [mesh.name for mesh in model.faceted_meshes] == [
        body.name for body in model.bodies
    ]
    for mesh in model.faceted_meshes:
        assert mesh.signed_volume_m3() > 0.0


def test_an_unknown_identifier_is_refused() -> None:
    """A model can only exist for a body set this family owns."""
    with pytest.raises(DeviceGeometryError, match="identifier"):
        dataclasses.replace(direct_cad(), identifier="laser_icf_unknown")


def test_a_manifest_of_the_wrong_schema_is_refused() -> None:
    """The assembly manifest must be the library's own."""
    model = direct_cad()
    manifest = dict(model.assembly_manifest)
    manifest["schema"] = "something.else.v1"
    with pytest.raises(DeviceGeometryError, match=r"assembly_manifest\.schema"):
        dataclasses.replace(model, assembly_manifest=manifest)


def test_a_manifest_counting_the_wrong_number_of_bodies_is_refused() -> None:
    """The manifest's body count must match the identifier's body set."""
    model = direct_cad()
    manifest = dict(model.assembly_manifest)
    manifest["body_count"] = 99
    with pytest.raises(DeviceGeometryError, match="body_count"):
        dataclasses.replace(model, assembly_manifest=manifest)


def test_a_body_set_in_the_wrong_order_is_refused() -> None:
    """The order is part of the contract at this tier too."""
    model = direct_cad()
    with pytest.raises(DeviceGeometryError, match="in order"):
        dataclasses.replace(model, bodies=tuple(reversed(model.bodies)))


def test_the_enclosure_is_the_widest_body_and_the_vapour_the_narrowest() -> None:
    """The bound each body gets follows its own radius, not one global value.

    Four bodies, four different bounds: the enclosure's is the loosest
    because it is the widest body, and the vapour core's is the tightest.
    A single copied deflection would have hidden that.
    """
    bounds = {
        body.name: body.faceted_volume_deficit_bound for body in indirect_cad().bodies
    }
    assert bounds[BODY_HOHLRAUM_WALL] < bounds[BODY_ABLATOR_SHELL]
    assert bounds[BODY_ABLATOR_SHELL] < bounds[BODY_FUEL_VAPOUR_CORE]
