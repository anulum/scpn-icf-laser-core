# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — tier-G2 device model

"""Tier-G2 B-rep model of a laser-ICF target.

The same bodies as tier G1, and the same dependence of the body set on
the identifier, built as exact solids through the shared library's
``cad`` group instead of tessellated, checked fail-closed by the
library's evidence kernel against its analytic closed forms and against
its tier-G1 twin, and exported as normalised STEP bytes with a digest.

**This is the first family in the group whose bodies are millimetres
across, and everything below was measured here rather than taken from a
sibling. The scale does not merely shift the numbers; it puts a bound
on the ring count that no metre-scale family meets.**

The ring count is bounded from above by the back-end, and the shape of
that bound is not a simple ceiling. Scanning every count from thirty to
seventy-five on this family's own bodies gives three regimes:

- **thirty to thirty-nine** — every count exact, agreeing with the
  analytic frustum stack to 7e-15 relative;
- **forty to sixty-one** — a mixed band. Even counts refuse: forty
  reports 1.7e-4 on the fuel shell, against a 1e-9 tolerance. Odd
  counts stay exact, all of forty-one, forty-three and so on to
  sixty-one;
- **sixty-two and above** — every count refuses.

The cylindrical bodies are unaffected throughout.

**The parity is not a coincidence, and it is as far as measurement
goes.** An even ring count places exactly one profile sample on the
equator, at exactly ``(0, R)``; an odd count places none. The refusals
in the mixed band fall exactly on the even counts. That correlation is
measured. Whether the equatorial sample is what the revolve fails on is
**not** established here — the mechanism belongs to the back-end.

**Where the band starts moves with the body's radius.** The first
refusal is at 34 rings for a solid sphere of 1.0 mm, 40 at 1.503 mm, 42
at 1.8 mm, 46 at 2.34 mm, 50 at 3.0 mm and 58 at 5.0 mm; at 10 mm and
above nothing fails up to a hundred and twenty rings, which is why no
metre-scale family in this group meets the bound at all. **No single
length is constant where the band starts**: the shortest generating
segment there runs from 9.2e-5 m to 2.7e-4 m over those radii. So each
family must measure its own and may not inherit a sibling's.

Nothing was loosened to accommodate that. The evidence kernel refuses,
naming the body and the bound, which is what it is for. **The default
is the top of the first regime, not the highest count that happens to
pass.** Odd counts up to sixty-one do pass, and building there would
mean sitting one step from a refusal on the strength of a parity whose
cause is unknown. A test asserts the refusal at the first count above
the default.

At that count the deflections behave as follows. The angular
deflection does not bind: between 0.5 and 0.1 radians the volume
deficit of every body is identical to four significant figures and only
the facet count moves. The linear deflection does not set the deficit
either — it sets the **bound** the deficit is measured against, while
the ring count sets the deficit itself. At 1e-8 m the back-end refuses
outright with ``Standard_NumericError``.

So the linear deflection is chosen as the tightest bound that the
bodies actually clear, and 2e-7 m is that value: the worst body, the
vapour core, sits at 0.56 of its bound, and the next step down, 1e-7 m,
does not pass at all — the vapour core exceeds its bound by thirteen per
cent. This is not the widest margin available; a margin is only as good
as the bound it is a margin on.

**The radius handed to the deficit bound is the outer radius of each
body, and that is deliberate.** The bound ``2 d / r`` is written for a
circular profile of one radius; a sphere's circles run from zero at the
poles to the outer radius at the equator, so there is no single smallest
circle to name and the poles would make the bound unbounded. The outer
radius gives the **tightest** bound the body admits, and every body is
measured to clear it. Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    annular_tube_brep,
    assembly_evidence,
    backend_versions,
    facet_assembly,
    sphere_brep,
    spherical_shell_brep,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_icf_laser_core.configuration import DeviceConfiguration
from scpn_icf_laser_core.errors import DeviceGeometryError
from scpn_icf_laser_core.geometry.device import HohlraumEnvelope
from scpn_icf_laser_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_HOHLRAUM_WALL,
    BODY_NAMES_BY_IDENTIFIER,
    MATERIAL_FUEL_VAPOUR,
    MATERIAL_HIGH_Z_CASE,
    MATERIAL_PLASTIC_ABLATOR,
    MATERIAL_SOLID_FUEL,
    ROLE_ABLATOR,
    ROLE_ENCLOSURE,
    ROLE_FUEL,
    build_device_model,
    capsule_radii_m,
    require_containment,
    require_enclosure,
)
from scpn_icf_laser_core.physics.level0 import CapsuleDeclaration

CAD_MODEL_SCHEMA: Final = "scpn.laser-icf-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"
CAD_MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the hohlraum axis; the capsule is centred on the origin",
    "origin": "the centre of the capsule",
}
CAD_MODEL_NON_CLAIMS: Final = (
    "exact solids of revolution of a declared configuration and capsule",
    (
        "every body is a polyhedron of revolution, never an ideal sphere; the "
        "frustum stack of the profile built is its own analytic reference"
    ),
    (
        "the capsule is three uniform concentric layers; no fill tube, no "
        "mounting stalk, no surface roughness and no layer non-uniformity is "
        "modelled"
    ),
    (
        "the hohlraum wall is one plain tube whose open ends stand for the "
        "laser entrance holes; no window, cooling ring or aperture is modelled"
    ),
    (
        "determinism of the STEP bytes is claimed within one pinned back-end "
        "environment only, never across back-end versions"
    ),
    "no body is an engineering model and no fabrication tolerance is carried",
    "no value describes or validates any real machine or shot",
)

#: Reference tessellation the B-rep bodies are checked against.
DEFAULT_REFERENCE_MESH_SEGMENTS: Final = 8
#: Polar steps of the spherical profiles: the largest count below the
#: back-end's first refusal on this family's own bodies, which is the
#: top of the regime where every count is exact. Higher odd counts pass
#: and are still not used; see the module docstring. Where the refusals
#: begin is a function of the body's radius and was measured here rather
#: than inherited, so a sibling family's count says nothing about this
#: one's.
DEFAULT_SPHERE_RINGS: Final = 39
#: Mesher deflections, both set by measurement on this family's own
#: millimetre scale rather than copied from a metre-scale sibling.
DEFAULT_LINEAR_DEFLECTION_M: Final = 2.0e-7
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.1


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep device model of one configuration and capsule.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256, capsule_digest_sha256
        Digests of the inputs the model was built from.
    hohlraum_digest_sha256
        Digest of the enclosure envelope, or ``None`` where there is
        none.
    reference_mesh_segments, rings
        Tier-G1 reference the bodies were checked against, and the polar
        step count both tiers share.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.
    backend_versions
        Versions of the pinned back-ends that produced the solids.
    assembly_manifest
        The library's assembly manifest of the bodies.
    step_sha256
        Digest of the normalised STEP bytes.
    bodies
        Checked evidence of each body, in the fixed order.
    step_data
        The normalised STEP bytes themselves.
    faceted_meshes
        The faceted meshes the evidence was computed from.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the manifest schema, the body
        count or the body order is wrong.
    """

    identifier: str
    configuration_digest_sha256: str
    capsule_digest_sha256: str
    hohlraum_digest_sha256: str | None
    reference_mesh_segments: int
    rings: int
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes
    faceted_meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the manifest and the body set against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the manifest schema, the
            body count or the body order is wrong.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(expected):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(expected)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        names = tuple(body.name for body in self.bodies)
        if names != expected:
            raise DeviceGeometryError(
                f"bodies: of {self.identifier!r} must be exactly {expected!r} "
                f"in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(CAD_MODEL_UNITS),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule_digest_sha256": self.capsule_digest_sha256,
            "hohlraum_digest_sha256": self.hohlraum_digest_sha256,
            "reference_mesh_segments": self.reference_mesh_segments,
            "rings": self.rings,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
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


def build_device_cad(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    hohlraum: HohlraumEnvelope | None = None,
    segments: int = DEFAULT_REFERENCE_MESH_SEGMENTS,
    rings: int = DEFAULT_SPHERE_RINGS,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep device model of a validated design.

    Parameters
    ----------
    configuration
        Validated laser-ICF configuration.
    capsule
        Declared capsule layering.
    hohlraum
        Enclosure envelope, required for ``laser_icf_indirect_drive``
        and refused for the two directly driven identifiers.
    segments
        Segment count of the tier-G1 reference mesh of the comparison.
    rings
        Polar steps of the spherical profiles, shared by both tiers.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a count or a deflection is invalid, the enclosure does not
        match the configuration, the capsule does not fit inside it, or
        a body violates a declared evidence bound; the library's
        refusals are re-raised under the device error type with their
        messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    DeviceConfigurationError
        If the declared layering does not fit inside the capsule.
    """
    reference = build_device_model(configuration, capsule, segments, rings, hohlraum)
    enclosure = require_enclosure(configuration, hohlraum)
    outer, fuel_outer, cavity = capsule_radii_m(configuration, capsule)
    try:
        solids = [
            spherical_shell_brep(
                fuel_outer,
                outer,
                0.0,
                rings,
                BODY_ABLATOR_SHELL,
                ROLE_ABLATOR,
                MATERIAL_PLASTIC_ABLATOR,
            ),
            spherical_shell_brep(
                cavity,
                fuel_outer,
                0.0,
                rings,
                BODY_FUEL_ICE_SHELL,
                ROLE_FUEL,
                MATERIAL_SOLID_FUEL,
            ),
            sphere_brep(
                cavity,
                0.0,
                rings,
                BODY_FUEL_VAPOUR_CORE,
                ROLE_FUEL,
                MATERIAL_FUEL_VAPOUR,
            ),
        ]
        radii = [outer, fuel_outer, cavity]
        if enclosure is not None:
            require_containment(outer, enclosure)
            half_length = enclosure.length_m / 2.0
            solids.append(
                annular_tube_brep(
                    enclosure.case_radius_m,
                    enclosure.outer_radius_m,
                    -half_length,
                    half_length,
                    BODY_HOHLRAUM_WALL,
                    ROLE_ENCLOSURE,
                    MATERIAL_HIGH_Z_CASE,
                )
            )
            radii.append(enclosure.case_radius_m)
        brep = BrepAssembly(tuple(solids))
        faceted = facet_assembly(brep, linear_deflection_m, angular_deflection_rad)
        bodies = assembly_evidence(
            brep.bodies,
            tuple(radii),
            faceted,
            reference.meshes,
            linear_deflection_m,
            segments,
        )
    except (CadError, GeometryError) as exc:
        raise DeviceGeometryError(str(exc)) from exc
    manifest = brep.manifest()
    extras = {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "identifier": configuration.identifier,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "capsule_digest_sha256": reference.capsule_digest_sha256,
        "assembly_manifest_sha256": brep.manifest_sha256(),
        "units": dict(CAD_MODEL_UNITS),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }
    step_data = step_bytes(brep, extras)
    return DeviceModelCAD(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule_digest_sha256=reference.capsule_digest_sha256,
        hohlraum_digest_sha256=reference.hohlraum_digest_sha256,
        reference_mesh_segments=segments,
        rings=rings,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=manifest,
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
