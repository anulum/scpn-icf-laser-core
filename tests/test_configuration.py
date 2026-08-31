# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device configuration container tests

"""Every branch of the device configuration container and its parsers.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from scpn_icf_laser_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import LaserDriver, TargetDeclaration

REGISTRY = RegistryBinding(version="1.0.0", digest_sha256="0" * 64)


def synthetic_configuration(
    identifier: str = "laser_icf_direct_drive",
    hohlraum: bool = False,
    ignitor_pulse: bool = False,
    pulse_duration_ns: float = 10.0,
) -> DeviceConfiguration:
    """Build a valid synthetic configuration with optional overrides."""
    return DeviceConfiguration(
        identifier=identifier,
        driver=LaserDriver(
            driver_energy_mj=1.0,
            pulse_duration_ns=pulse_duration_ns,
            wavelength_nm=351.0,
        ),
        target=TargetDeclaration(
            capsule_radius_um=1000.0,
            hohlraum=hohlraum,
            ignitor_pulse=ignitor_pulse,
        ),
        registry=REGISTRY,
    )


def test_registry_binding_rejects_bad_pins() -> None:
    """Malformed registry pins are rejected."""
    with pytest.raises(DeviceConfigurationError, match=r"registry\.version"):
        RegistryBinding(version="", digest_sha256="0" * 64)
    with pytest.raises(DeviceConfigurationError, match=r"registry\.digest_sha256"):
        RegistryBinding(version="1.0.0", digest_sha256="ZZ")


def test_all_owned_identifiers_construct() -> None:
    """Each owned identifier constructs with its class-consistent target."""
    direct = synthetic_configuration()
    indirect = synthetic_configuration("laser_icf_indirect_drive", hohlraum=True)
    fast = synthetic_configuration(
        "laser_icf_fast_or_shock_ignition", ignitor_pulse=True
    )
    assert direct.identifier == "laser_icf_direct_drive"
    assert indirect.target.hohlraum is True
    assert fast.target.ignitor_pulse is True


def test_unowned_identifier_is_rejected() -> None:
    """Identifiers outside this repository's ownership are rejected."""
    with pytest.raises(DeviceConfigurationError, match="not owned"):
        synthetic_configuration("ion_beam_icf")


def test_drive_scheme_class_invariants() -> None:
    """Hohlraum and ignitor flags must match the class exactly."""
    with pytest.raises(DeviceConfigurationError, match="requires the"):
        synthetic_configuration("laser_icf_indirect_drive", hohlraum=False)
    with pytest.raises(DeviceConfigurationError, match="forbids a hohlraum"):
        synthetic_configuration(hohlraum=True)
    with pytest.raises(DeviceConfigurationError, match="requires the separate"):
        synthetic_configuration("laser_icf_fast_or_shock_ignition", ignitor_pulse=False)
    with pytest.raises(DeviceConfigurationError, match="declares no"):
        synthetic_configuration(ignitor_pulse=True)


def test_consistency_report_clean_and_finding() -> None:
    """The report is empty below the LPI bound and precise above it."""
    assert synthetic_configuration().consistency_report() == ()
    hot = synthetic_configuration(pulse_duration_ns=1.0)
    findings = hot.consistency_report()
    assert len(findings) == 1
    assert "laser-plasma-instability" in findings[0].message
    indirect = synthetic_configuration(
        "laser_icf_indirect_drive", hohlraum=True, pulse_duration_ns=1.0
    )
    assert indirect.consistency_report() == ()


def test_canonical_round_trip_and_digest() -> None:
    """Canonical bytes round-trip losslessly and digest deterministically."""
    configuration = synthetic_configuration()
    data = configuration.canonical_bytes()
    assert data.endswith(b"\n")
    restored = configuration_from_bytes(data)
    assert restored == configuration
    expected = hashlib.sha256(data).hexdigest()
    assert configuration.digest_sha256() == expected


def test_from_record_round_trip_all_classes() -> None:
    """All owned configuration classes round-trip through records."""
    for configuration in (
        synthetic_configuration(),
        synthetic_configuration("laser_icf_indirect_drive", hohlraum=True),
        synthetic_configuration("laser_icf_fast_or_shock_ignition", ignitor_pulse=True),
    ):
        assert configuration_from_record(configuration.to_record()) == configuration


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (lambda _: "not-a-dict", "record: must be an object"),
        (lambda r: {**r, "extra": 1}, "unknown fields"),
        (lambda r: {**r, "driver": None}, "driver: must be an object"),
        (lambda r: {**r, "target": []}, "target: must be an object"),
        (lambda r: {**r, "registry": 7}, "registry: must be an object"),
        (lambda r: {**r, "identifier": 3}, "identifier: must be a string"),
    ],
)
def test_from_record_shape_violations(mutate: Any, fragment: str) -> None:
    """Each record-shape violation is rejected with a precise message."""
    record = synthetic_configuration().to_record()
    with pytest.raises(DeviceConfigurationError, match=fragment):
        configuration_from_record(mutate(record))


def test_from_record_field_type_violations() -> None:
    """Nested field-type violations name the offending field."""
    record = synthetic_configuration().to_record()
    record["driver"]["driver_energy_mj"] = "big"
    with pytest.raises(DeviceConfigurationError, match="driver_energy_mj: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["driver"]["driver_energy_mj"] = True
    with pytest.raises(DeviceConfigurationError, match="driver_energy_mj: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["target"]["hohlraum"] = "no"
    with pytest.raises(DeviceConfigurationError, match="hohlraum: must be"):
        configuration_from_record(record)
    record = synthetic_configuration().to_record()
    record["registry"]["version"] = None
    with pytest.raises(DeviceConfigurationError, match="version: must be a string"):
        configuration_from_record(record)


def test_from_bytes_rejects_invalid_documents() -> None:
    """Invalid UTF-8, invalid JSON, and non-finite literals are rejected."""
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"\xff\xfe")
    with pytest.raises(DeviceConfigurationError, match="invalid JSON document"):
        configuration_from_bytes(b"{not json")
    record = synthetic_configuration().to_record()
    text = json.dumps(record).replace("351.0", "NaN", 1)
    with pytest.raises(DeviceConfigurationError, match="non-finite JSON literal"):
        configuration_from_bytes(text.encode("utf-8"))


def test_integer_accepted_where_number_expected() -> None:
    """Integral JSON numbers are accepted for real-valued fields."""
    record = synthetic_configuration().to_record()
    record["driver"]["pulse_duration_ns"] = 10
    restored = configuration_from_record(record)
    assert restored.driver.pulse_duration_ns == 10.0
