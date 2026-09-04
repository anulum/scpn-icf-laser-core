# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — tier-G1 device model

"""Tier-G1 tessellated model of a laser-ICF target.

The capsule is three concentric bodies about the origin: the ablator
shell, the solid fuel layer inside it, and the vapour the fuel layer
encloses. The vapour carries a body although it is a gas, because the
review this family anchors on prints its density and it is part of the
fuel inventory; the beam-target family draws no body for its bore for the
opposite reason, that nothing is declared to be there at all.

**The body set follows the identifier.** An indirect-drive target sits
inside a radiation enclosure and a direct-drive target does not, so the
hohlraum wall is a fourth body for exactly one of the three owned
configurations, and is refused for the other two rather than ignored.
That mirrors the configuration model, which already refuses a hohlraum
flag on a direct-drive identifier: the two refusals say the same thing
about the same machine, one about the declaration and one about the
solid.

Every dimension of the capsule is read from the configuration and the
level-0 capsule declaration and never redeclared here; see the envelope
module for why. The conversion from the micrometres those objects carry
to the metres every body is built in happens in exactly one function,
:func:`capsule_radii_m`.

The capsule bodies are spheres and spherical shells; the hohlraum wall
is an annular tube. All four are shapes the shared kernel library
already builds, so this tier adds no primitive.

**The bodies are inscribed polyhedra of revolution, not ideal spheres.**
A consumer comparing a volume here to ``4/3 pi r^3`` would be comparing
two different solids; the profile volume of the body actually built is
the reference, and the library states the same rule in its own design
record. Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    require_rings,
    require_segments,
    sphere_solid,
    spherical_shell,
)

from scpn_icf_laser_core.configuration import DeviceConfiguration
from scpn_icf_laser_core.errors import DeviceGeometryError
from scpn_icf_laser_core.geometry.device import HohlraumEnvelope
from scpn_icf_laser_core.physics.level0 import (
    CapsuleDeclaration,
    initial_inner_radius_um,
)

MODEL_SCHEMA: Final = "scpn.laser-icf-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the hohlraum axis; the capsule is centred on the origin",
    "origin": "the centre of the capsule",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a declared configuration and capsule",
    (
        "every body is an inscribed polyhedron of revolution, never an ideal "
        "sphere; the profile volume of the body built is its own reference"
    ),
    (
        "the capsule is three uniform concentric layers; no fill tube, no "
        "mounting stalk, no surface roughness and no layer non-uniformity is "
        "modelled, and those are the quantities an implosion is sensitive to"
    ),
    (
        "the hohlraum wall is one plain tube whose open ends stand for the "
        "laser entrance holes; no window, no cooling ring, no diagnostic "
        "aperture and no support is modelled"
    ),
    (
        "no body describes the target during a shot: these are the "
        "dimensions before the drive begins, and an implosion changes all "
        "of them"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field, dose or activation quantity is carried",
    "no value describes or validates any real machine or shot",
)

#: One micrometre in metres. The configuration and the level-0 capsule
#: declaration both carry micrometres; every body is built in metres, and
#: this is the only place the two meet.
MICROMETRE_M: Final = 1.0e-6

ROLE_ABLATOR: Final = "ablator"
ROLE_FUEL: Final = "fuel"
ROLE_ENCLOSURE: Final = "enclosure"
MATERIAL_PLASTIC_ABLATOR: Final = "plastic_ablator"
MATERIAL_SOLID_FUEL: Final = "solid_fuel_ice"
MATERIAL_FUEL_VAPOUR: Final = "fuel_vapour"
MATERIAL_HIGH_Z_CASE: Final = "high_z_case"

BODY_ABLATOR_SHELL: Final = "ablator_shell"
BODY_FUEL_ICE_SHELL: Final = "fuel_ice_shell"
BODY_FUEL_VAPOUR_CORE: Final = "fuel_vapour_core"
BODY_HOHLRAUM_WALL: Final = "hohlraum_wall"

CAPSULE_BODY_NAMES: Final = (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
)
BODY_NAMES_BY_IDENTIFIER: Final = {
    "laser_icf_direct_drive": CAPSULE_BODY_NAMES,
    "laser_icf_fast_or_shock_ignition": CAPSULE_BODY_NAMES,
    "laser_icf_indirect_drive": (*CAPSULE_BODY_NAMES, BODY_HOHLRAUM_WALL),
}
"""The body set of each owned configuration. Only an indirect-drive
target sits inside a radiation enclosure; the ignitor pulse of the
fast-or-shock-ignition class is light, not hardware, so that class draws
the same three bodies as direct drive."""


def _declaration_digest(record: dict[str, Any]) -> str:
    """Identify a declaration by the canonical bytes of its record.

    Parameters
    ----------
    record
        The declaration's JSON-serialisable record.

    Returns
    -------
    str
        SHA-256 of the canonical bytes as lowercase hex. The bytes are
        formed the way every other record in this repository is formed:
        sorted keys, minimal separators, one trailing newline, and no
        NaN or infinity anywhere.
    """
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()


def capsule_radii_m(
    configuration: DeviceConfiguration, capsule: CapsuleDeclaration
) -> tuple[float, float, float]:
    """Return the three capsule radii in metres, outermost first.

    Parameters
    ----------
    configuration
        Validated laser-ICF configuration carrying the outer radius.
    capsule
        Declared layering carrying the two thicknesses.

    Returns
    -------
    (outer, fuel_outer, cavity)
        The capsule's outer radius, the outer radius of the fuel layer,
        and the radius of the vapour cavity, all in metres.

    Raises
    ------
    DeviceConfigurationError
        If the two declared layers do not fit inside the capsule. The
        refusal comes from the level-0 record's own relation rather than
        from a copy of it, so the geometry cannot admit a layering the
        physics would have refused.
    """
    cavity_um = initial_inner_radius_um(configuration, capsule)
    outer_um = configuration.target.capsule_radius_um
    fuel_outer_um = outer_um - capsule.ablator_thickness_um
    return (
        outer_um * MICROMETRE_M,
        fuel_outer_um * MICROMETRE_M,
        cavity_um * MICROMETRE_M,
    )


def require_enclosure(
    configuration: DeviceConfiguration, hohlraum: HohlraumEnvelope | None
) -> HohlraumEnvelope | None:
    """Refuse an enclosure that does not match the configuration.

    Parameters
    ----------
    configuration
        Validated device configuration.
    hohlraum
        Declared enclosure, or ``None``.

    Returns
    -------
    HohlraumEnvelope or None
        The envelope, unchanged, once it matches the identifier.

    Raises
    ------
    DeviceGeometryError
        If an indirect-drive target is given no enclosure, or a
        directly driven one is given an enclosure. Both directions are
        refused: indirect drive is defined by the enclosure the drive
        radiates from, and a case around a directly driven capsule
        would block the drive it is supposed to receive.
    """
    wanted = BODY_HOHLRAUM_WALL in BODY_NAMES_BY_IDENTIFIER[configuration.identifier]
    if wanted and hohlraum is None:
        raise DeviceGeometryError(
            f"hohlraum: required for {configuration.identifier!r}, whose drive "
            f"is the radiation the enclosure emits"
        )
    if not wanted and hohlraum is not None:
        raise DeviceGeometryError(
            f"hohlraum: must be absent for {configuration.identifier!r}, whose "
            f"capsule is irradiated directly"
        )
    return hohlraum


def require_containment(capsule_radius_m: float, hohlraum: HohlraumEnvelope) -> None:
    """Refuse an enclosure the capsule does not fit inside.

    Parameters
    ----------
    capsule_radius_m
        Outer radius of the capsule, in metres.
    hohlraum
        Validated enclosure envelope.

    Raises
    ------
    DeviceGeometryError
        If the case radius does not exceed the capsule radius, or the
        case is not longer than the capsule's diameter. Equality is
        refused in both directions rather than admitted: a case that
        touches the capsule leaves no volume for the radiation field
        that defines the drive, and the printed guidance this family
        anchors on says the enclosure is large compared to the capsule,
        never equal to it.
    """
    if hohlraum.case_radius_m <= capsule_radius_m:
        raise DeviceGeometryError(
            "case_radius_m: must exceed the capsule's outer radius or the "
            f"capsule fills the case ({hohlraum.case_radius_m!r} <= "
            f"{capsule_radius_m!r})"
        )
    if hohlraum.length_m <= 2.0 * capsule_radius_m:
        raise DeviceGeometryError(
            "length_m: must exceed the capsule's diameter or the capsule does "
            f"not fit inside the case ({hohlraum.length_m!r} <= "
            f"{2.0 * capsule_radius_m!r})"
        )


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and capsule.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    capsule_digest_sha256
        Digest of the declared capsule layering.
    hohlraum_digest_sha256
        Digest of the enclosure envelope, or ``None`` for a directly
        driven target, which has none.
    segments
        Circumferential segment count every body was tessellated at.
    rings
        Polar step count the spherical bodies were sampled at.
    meshes
        The bodies, in the fixed order for that identifier.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the body names or their order
        differ from the set that identifier owns.
    """

    identifier: str
    configuration_digest_sha256: str
    capsule_digest_sha256: str
    hohlraum_digest_sha256: str | None
    segments: int
    rings: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the body names or their
            order differ from the set that identifier owns.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        names = tuple(mesh.name for mesh in self.meshes)
        if names != expected:
            raise DeviceGeometryError(
                f"meshes: bodies of {self.identifier!r} must be exactly "
                f"{expected!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule_digest_sha256": self.capsule_digest_sha256,
            "hohlraum_digest_sha256": self.hohlraum_digest_sha256,
            "segments": self.segments,
            "rings": self.rings,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_device_model(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    segments: int,
    rings: int,
    hohlraum: HohlraumEnvelope | None = None,
) -> DeviceModel3D:
    """Tessellate the bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated laser-ICF configuration; its identifier selects the
        body set and its capsule radius sets the outermost body.
    capsule
        Declared capsule layering.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.
    rings
        Polar steps from pole to pole for the spherical bodies; at least
        the library's minimum. It is independent of ``segments``: this
        one sets the profile, the other sets what the revolution keeps
        of it.
    hohlraum
        Enclosure envelope, required for ``laser_icf_indirect_drive``
        and refused for the two directly driven identifiers.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If a count is invalid, the enclosure does not match the
        configuration, or the capsule does not fit inside it; the
        library's refusals are re-raised under the device error type
        with their messages.
    DeviceConfigurationError
        If the declared layering does not fit inside the capsule.
    """
    try:
        require_segments(segments)
        require_rings(rings)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    enclosure = require_enclosure(configuration, hohlraum)
    outer, fuel_outer, cavity = capsule_radii_m(configuration, capsule)
    bodies = [
        (
            BODY_ABLATOR_SHELL,
            ROLE_ABLATOR,
            MATERIAL_PLASTIC_ABLATOR,
            spherical_shell(fuel_outer, outer, 0.0, segments, rings),
        ),
        (
            BODY_FUEL_ICE_SHELL,
            ROLE_FUEL,
            MATERIAL_SOLID_FUEL,
            spherical_shell(cavity, fuel_outer, 0.0, segments, rings),
        ),
        (
            BODY_FUEL_VAPOUR_CORE,
            ROLE_FUEL,
            MATERIAL_FUEL_VAPOUR,
            sphere_solid(cavity, 0.0, segments, rings),
        ),
    ]
    if enclosure is not None:
        require_containment(outer, enclosure)
        half_length = enclosure.length_m / 2.0
        bodies.append(
            (
                BODY_HOHLRAUM_WALL,
                ROLE_ENCLOSURE,
                MATERIAL_HIGH_Z_CASE,
                annular_tube(
                    enclosure.case_radius_m,
                    enclosure.outer_radius_m,
                    -half_length,
                    half_length,
                    segments,
                ),
            )
        )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule_digest_sha256=_declaration_digest(capsule.to_record()),
        hohlraum_digest_sha256=(
            None if enclosure is None else enclosure.digest_sha256()
        ),
        segments=segments,
        rings=rings,
        meshes=meshes,
    )
