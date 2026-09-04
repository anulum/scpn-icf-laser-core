# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device geometry declaration tests

"""Tests of the radiation-enclosure envelope."""

from __future__ import annotations

import json
from typing import Any

import pytest

from geometry_fixtures import (
    DECLARED_CASE_LENGTH_UM,
    DECLARED_CASE_WALL_THICKNESS_UM,
    anchor_hohlraum,
)
from scpn_icf_laser_core.errors import DeviceGeometryError
from scpn_icf_laser_core.geometry import MICROMETRE_M
from scpn_icf_laser_core.geometry.device import (
    HOHLRAUM_FIELDS,
    HohlraumEnvelope,
    hohlraum_from_record,
)


def test_the_envelope_declares_exactly_three_lengths() -> None:
    """The enclosure is the only hardware this package's geometry declares.

    Everything else a laser-ICF model needs is already declared
    elsewhere: the capsule's outer radius in the configuration and its
    two layer thicknesses in the level-0 capsule declaration. If this
    tuple ever grows, something has acquired a second home.
    """
    assert HOHLRAUM_FIELDS == (
        "case_radius_m",
        "wall_thickness_m",
        "length_m",
    )


def test_the_outer_radius_is_the_bore_plus_the_wall() -> None:
    """The outer radius is derived, never declared."""
    envelope = anchor_hohlraum()
    assert envelope.outer_radius_m == (
        envelope.case_radius_m + DECLARED_CASE_WALL_THICKNESS_UM * MICROMETRE_M
    )


@pytest.mark.parametrize("field_name", HOHLRAUM_FIELDS)
def test_every_declared_length_must_be_strictly_positive(field_name: str) -> None:
    """A zero length is refused by the field that carries it."""
    values = dict(anchor_hohlraum().to_record())
    values[field_name] = 0.0
    with pytest.raises(DeviceGeometryError, match=field_name):
        HohlraumEnvelope(**values)


@pytest.mark.parametrize("field_name", HOHLRAUM_FIELDS)
def test_every_declared_length_must_be_finite(field_name: str) -> None:
    """A non-finite length is refused rather than clamped."""
    values = dict(anchor_hohlraum().to_record())
    values[field_name] = float("nan")
    with pytest.raises(DeviceGeometryError, match="must be finite"):
        HohlraumEnvelope(**values)


def test_the_record_carries_every_declared_field_and_nothing_else() -> None:
    """The projection is exactly the declaration."""
    assert set(anchor_hohlraum().to_record()) == set(HOHLRAUM_FIELDS)


def test_the_canonical_bytes_are_sorted_minimal_and_newline_terminated() -> None:
    """The serialisation is the group's canonical form."""
    data = anchor_hohlraum().canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_envelope() -> None:
    """The same declaration digests the same, a different one does not."""
    envelope = anchor_hohlraum()
    assert envelope.digest_sha256() == anchor_hohlraum().digest_sha256()
    longer = HohlraumEnvelope(
        case_radius_m=envelope.case_radius_m,
        wall_thickness_m=envelope.wall_thickness_m,
        length_m=envelope.length_m * 2.0,
    )
    assert longer.digest_sha256() != envelope.digest_sha256()


def test_a_record_round_trips_through_the_parser() -> None:
    """What the envelope writes, the parser reads back unchanged."""
    envelope = anchor_hohlraum()
    assert hohlraum_from_record(envelope.to_record()) == envelope


def test_the_parser_refuses_an_unknown_field() -> None:
    """An unknown member is refused rather than ignored."""
    record: dict[str, Any] = dict(anchor_hohlraum().to_record())
    record["case_material"] = "gold"
    with pytest.raises(DeviceGeometryError, match="unknown fields"):
        hohlraum_from_record(record)


@pytest.mark.parametrize("field_name", HOHLRAUM_FIELDS)
def test_the_parser_refuses_a_missing_field(field_name: str) -> None:
    """Every declared field is required; none defaults."""
    record: dict[str, Any] = dict(anchor_hohlraum().to_record())
    del record[field_name]
    with pytest.raises(DeviceGeometryError, match=f"{field_name}: required"):
        hohlraum_from_record(record)


@pytest.mark.parametrize("value", ["17e-3", None, [17.0]])
def test_the_parser_refuses_a_value_that_is_not_a_real_number(value: object) -> None:
    """A length that is not a number is refused, naming the field."""
    record: dict[str, Any] = dict(anchor_hohlraum().to_record())
    record["length_m"] = value
    with pytest.raises(DeviceGeometryError, match="must be a real number"):
        hohlraum_from_record(record)


def test_the_parser_refuses_a_boolean_where_a_length_belongs() -> None:
    """A flag standing where a length belongs is a mistake, not a one.

    Python calls ``bool`` a subclass of ``int``, so a plain numeric
    check would admit ``True`` as a one-metre case. It is refused by
    name.
    """
    record: dict[str, Any] = dict(anchor_hohlraum().to_record())
    record["length_m"] = True
    with pytest.raises(DeviceGeometryError, match="must be a real number"):
        hohlraum_from_record(record)


def test_the_parser_admits_an_integer_length() -> None:
    """An integer is a real number and is read as one."""
    record: dict[str, Any] = dict(anchor_hohlraum().to_record())
    record["length_m"] = 1
    assert hohlraum_from_record(record).length_m == 1.0


def test_the_declared_length_is_the_one_the_fixtures_state() -> None:
    """The anchor's case is the declared length, in metres."""
    assert anchor_hohlraum().length_m == DECLARED_CASE_LENGTH_UM * MICROMETRE_M
