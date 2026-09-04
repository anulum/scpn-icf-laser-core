# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device geometry declarations

"""The one mechanical envelope a laser-ICF device carries that nothing else does.

This module is deliberately small, and its size is the design.

A laser-ICF target is a capsule, and every dimension of that capsule is
already declared somewhere in this package. The outer radius belongs to
:class:`~scpn_icf_laser_core.parameters.TargetDeclaration`, because the
configuration's own intensity estimate divides by it. The ablator and
fuel thicknesses belong to
:class:`~scpn_icf_laser_core.physics.level0.CapsuleDeclaration`, because
the level-0 record's fuel mass is computed from them. Declaring either
again here would put the same number in two homes, and the first time
they disagreed the model would draw a capsule the physics record does
not describe.

So the geometry tiers read the capsule from those two objects and this
module declares only what neither of them carries: the radiation
enclosure of an indirect-drive target. A hohlraum is not a property of
the capsule and not a term in any level-0 relation; it is hardware
around the target, and it exists for exactly one of the three owned
configurations.

Validation is fail-closed, serialisation is canonical, and the SHA-256
digest identifies the exact envelope. Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_laser_core.errors import DeviceConfigurationError, DeviceGeometryError
from scpn_icf_laser_core.parameters import require_positive

HOHLRAUM_FIELDS: Final = (
    "case_radius_m",
    "wall_thickness_m",
    "length_m",
)


def _positive(name: str, value: float) -> float:
    """Apply the package's positivity rule under the geometry error type.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except DeviceConfigurationError as exc:
        raise DeviceGeometryError(str(exc)) from exc


def _canonical_bytes(record: dict[str, float]) -> bytes:
    """Serialise a record canonically.

    Parameters
    ----------
    record
        Mapping of field names to values.

    Returns
    -------
    bytes
        UTF-8 JSON with sorted keys, minimal separators and a trailing
        newline; NaN and infinity are never emitted.
    """
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return (text + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class HohlraumEnvelope:
    """Validated envelope of the radiation enclosure of an indirect-drive target.

    Parameters
    ----------
    case_radius_m
        Inner radius of the case wall; strictly positive, and checked
        against the capsule's outer radius when a model is built.
    wall_thickness_m
        Radial thickness of the case wall; strictly positive.
    length_m
        Axial length of the case; strictly positive, and checked against
        the capsule when a model is built.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    case_radius_m: float
    wall_thickness_m: float
    length_m: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in HOHLRAUM_FIELDS:
            _positive(name, getattr(self, name))

    @property
    def outer_radius_m(self) -> float:
        """Outer radius of the case wall (inner radius plus wall thickness)."""
        return self.case_radius_m + self.wall_thickness_m

    def to_record(self) -> dict[str, float]:
        """Project the envelope to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in HOHLRAUM_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the envelope canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline.
        """
        return _canonical_bytes(self.to_record())

    def digest_sha256(self) -> str:
        """Identify the exact envelope.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded object.
    field
        Field name.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is absent or is not a real number. Booleans are
        refused although Python calls them integers: a flag standing
        where a length belongs is a mistake, not a zero or a one.
    """
    if field not in record:
        raise DeviceGeometryError(f"{field}: required")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeviceGeometryError(f"{field}: must be a real number, got {value!r}")
    return float(value)


def hohlraum_from_record(record: dict[str, Any]) -> HohlraumEnvelope:
    """Build a hohlraum envelope from a decoded record.

    Parameters
    ----------
    record
        Decoded object carrying exactly :data:`HOHLRAUM_FIELDS`.

    Returns
    -------
    HohlraumEnvelope
        The validated envelope.

    Raises
    ------
    DeviceGeometryError
        If a field is missing, of the wrong type, unknown, or violates a
        model invariant.
    """
    unknown = sorted(set(record) - set(HOHLRAUM_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"hohlraum: unknown fields {unknown!r}")
    return HohlraumEnvelope(**{name: _number(record, name) for name in HOHLRAUM_FIELDS})
