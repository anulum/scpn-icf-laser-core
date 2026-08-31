# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device configuration container

"""Device configuration container bound to the SPO reactor registry.

A :class:`DeviceConfiguration` composes a validated laser driver and
target declaration under exactly one of the three registry identifiers
this repository owns. The drive-scheme class invariants are hard: the
hohlraum separates indirect from direct drive (Lindl, PoP 2 (1995)
3933) and the ignitor pulse defines fast/shock ignition (Tabak et al.,
PoP 1 (1994) 1626). A direct-drive intensity above the documented
laser-plasma-instability bound is flagged (Craxton et al., PoP 22
(2015) 110501). Serialisation is canonical (sorted keys, no NaN or
infinity accepted anywhere) and the SHA-256 digest of those bytes
identifies the exact parameter set. The registry binding is a data pin
only — this package never imports SCPN Phase Orchestrator code.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import LaserDriver, TargetDeclaration

OWNED_CONFIGURATIONS: Final = (
    "laser_icf_direct_drive",
    "laser_icf_fast_or_shock_ignition",
    "laser_icf_indirect_drive",
)
DIRECT_DRIVE_LPI_BOUND_W_CM2: Final = 1.0e15
HEX_DIGEST: Final = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class RegistryBinding:
    """Pin to one SPO reactor registry release.

    Parameters
    ----------
    version
        Registry release version; non-empty.
    digest_sha256
        Registry digest as 64 lowercase hexadecimal characters.

    Raises
    ------
    DeviceConfigurationError
        If either pin component is malformed.
    """

    version: str
    digest_sha256: str

    def __post_init__(self) -> None:
        """Validate the registry pin.

        Raises
        ------
        DeviceConfigurationError
            If either pin component is malformed.
        """
        if not self.version:
            raise DeviceConfigurationError("registry.version: must be non-empty")
        if HEX_DIGEST.fullmatch(self.digest_sha256) is None:
            raise DeviceConfigurationError(
                "registry.digest_sha256: must be 64 lowercase hexadecimal "
                f"characters, got {self.digest_sha256!r}"
            )


@dataclass(frozen=True, slots=True)
class ConsistencyFinding:
    """One internal-consistency finding on a device configuration.

    Parameters
    ----------
    field
        Dotted field path the finding refers to.
    message
        Human-readable statement of the inconsistency.
    """

    field: str
    message: str


@dataclass(frozen=True, slots=True)
class DeviceConfiguration:
    """Validated laser-ICF device configuration.

    Parameters
    ----------
    identifier
        SPO registry configuration identifier; one of
        ``laser_icf_direct_drive``,
        ``laser_icf_fast_or_shock_ignition``, or
        ``laser_icf_indirect_drive``.
    driver
        Validated laser driver.
    target
        Validated target declaration.
    registry
        Pin to the SPO reactor registry release the identifier belongs
        to.

    Raises
    ------
    DeviceConfigurationError
        If the identifier is not owned by this repository or a
        drive-scheme class invariant is violated.
    """

    identifier: str
    driver: LaserDriver
    target: TargetDeclaration
    registry: RegistryBinding

    def __post_init__(self) -> None:
        """Validate identifier ownership and drive-scheme invariants.

        Raises
        ------
        DeviceConfigurationError
            If the identifier is not owned by this repository or a
            drive-scheme class invariant is violated.
        """
        if self.identifier not in OWNED_CONFIGURATIONS:
            raise DeviceConfigurationError(
                f"identifier: {self.identifier!r} is not owned by "
                f"SCPN-ICF-LASER-CORE; owned: {OWNED_CONFIGURATIONS!r}"
            )
        if self.identifier == "laser_icf_indirect_drive" and not self.target.hohlraum:
            raise DeviceConfigurationError(
                "target.hohlraum: laser_icf_indirect_drive requires the "
                "radiation enclosure that defines indirect drive"
            )
        if self.identifier == "laser_icf_direct_drive" and self.target.hohlraum:
            raise DeviceConfigurationError(
                "target.hohlraum: laser_icf_direct_drive forbids a hohlraum"
            )
        if (
            self.identifier == "laser_icf_fast_or_shock_ignition"
            and not self.target.ignitor_pulse
        ):
            raise DeviceConfigurationError(
                "target.ignitor_pulse: laser_icf_fast_or_shock_ignition "
                "requires the separate ignitor pulse that defines the class"
            )
        if (
            self.identifier != "laser_icf_fast_or_shock_ignition"
            and self.target.ignitor_pulse
        ):
            raise DeviceConfigurationError(
                f"target.ignitor_pulse: {self.identifier} declares no ignitor pulse"
            )

    def on_target_intensity_w_cm2(self) -> float:
        """Sphere-averaged on-target intensity of the configuration.

        Returns
        -------
        float
            ``I = E / (tau 4 pi R^2)`` in watts per square centimetre.
        """
        return self.target.on_target_intensity_w_cm2(self.driver)

    def consistency_report(self) -> tuple[ConsistencyFinding, ...]:
        """Report physics-consistency findings without failing.

        Returns
        -------
        tuple of ConsistencyFinding
            Advisory findings from the documented estimates; empty when
            a direct-drive intensity sits below the documented
            laser-plasma-instability bound. Findings are advisory
            instruments, not machine claims.
        """
        findings: list[ConsistencyFinding] = []
        if self.identifier == "laser_icf_direct_drive":
            intensity = self.on_target_intensity_w_cm2()
            if intensity > DIRECT_DRIVE_LPI_BOUND_W_CM2:
                findings.append(
                    ConsistencyFinding(
                        field="driver.driver_energy_mj",
                        message=(
                            f"on-target intensity {intensity:.3g} W/cm^2 "
                            "exceeds the documented direct-drive "
                            "laser-plasma-instability bound "
                            f"{DIRECT_DRIVE_LPI_BOUND_W_CM2:.0e} W/cm^2"
                        ),
                    )
                )
        return tuple(findings)

    def to_record(self) -> dict[str, Any]:
        """Project the configuration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Nested record with every declared parameter.
        """
        return {
            "identifier": self.identifier,
            "driver": {
                "driver_energy_mj": self.driver.driver_energy_mj,
                "pulse_duration_ns": self.driver.pulse_duration_ns,
                "wavelength_nm": self.driver.wavelength_nm,
            },
            "target": {
                "capsule_radius_um": self.target.capsule_radius_um,
                "hohlraum": self.target.hohlraum,
                "ignitor_pulse": self.target.ignitor_pulse,
            },
            "registry": {
                "version": self.registry.version,
                "digest_sha256": self.registry.digest_sha256,
            },
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the configuration canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact parameter set.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _require_mapping(record: dict[str, Any], field: str) -> dict[str, Any]:
    """Return one required mapping field of a record.

    Parameters
    ----------
    record
        Parent mapping under inspection.
    field
        Key that must hold a mapping.

    Returns
    -------
    dict[str, Any]
        The nested mapping.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a mapping.
    """
    value = record.get(field)
    if not isinstance(value, dict):
        raise DeviceConfigurationError(f"{field}: must be an object")
    return value


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a real number.

    Returns
    -------
    float
        The numeric value; booleans are rejected.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a real number.
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DeviceConfigurationError(f"{field}: must be a number, got {value!r}")
    return float(value)


def _boolean(record: dict[str, Any], field: str) -> bool:
    """Return one required boolean field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a boolean.

    Returns
    -------
    bool
        The boolean value.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a boolean.
    """
    value = record.get(field)
    if not isinstance(value, bool):
        raise DeviceConfigurationError(f"{field}: must be a boolean, got {value!r}")
    return value


def _string(record: dict[str, Any], field: str) -> str:
    """Return one required string field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a string.

    Returns
    -------
    str
        The string value.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a string.
    """
    value = record.get(field)
    if not isinstance(value, str):
        raise DeviceConfigurationError(f"{field}: must be a string, got {value!r}")
    return value


def configuration_from_record(record: Any) -> DeviceConfiguration:
    """Build a validated configuration from a decoded record.

    Parameters
    ----------
    record
        Decoded JSON object in the shape produced by
        :meth:`DeviceConfiguration.to_record`.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the record shape or any value violates the model.
    """
    if not isinstance(record, dict):
        raise DeviceConfigurationError("record: must be an object")
    known = {"identifier", "driver", "target", "registry"}
    unknown = sorted(set(record) - known)
    if unknown:
        raise DeviceConfigurationError(f"record: unknown fields {unknown!r}")
    driver = _require_mapping(record, "driver")
    target = _require_mapping(record, "target")
    registry = _require_mapping(record, "registry")
    return DeviceConfiguration(
        identifier=_string(record, "identifier"),
        driver=LaserDriver(
            driver_energy_mj=_number(driver, "driver_energy_mj"),
            pulse_duration_ns=_number(driver, "pulse_duration_ns"),
            wavelength_nm=_number(driver, "wavelength_nm"),
        ),
        target=TargetDeclaration(
            capsule_radius_um=_number(target, "capsule_radius_um"),
            hohlraum=_boolean(target, "hohlraum"),
            ignitor_pulse=_boolean(target, "ignitor_pulse"),
        ),
        registry=RegistryBinding(
            version=_string(registry, "version"),
            digest_sha256=_string(registry, "digest_sha256"),
        ),
    )


def configuration_from_bytes(data: bytes) -> DeviceConfiguration:
    """Build a validated configuration from canonical JSON bytes.

    Parameters
    ----------
    data
        UTF-8 JSON document; NaN and infinity literals are rejected.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the document is not valid strict JSON or violates the model.
    """

    def _reject_constant(literal: str) -> float:
        raise DeviceConfigurationError(
            f"record: non-finite JSON literal {literal!r} is rejected"
        )

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeviceConfigurationError(f"record: invalid JSON document: {exc}") from exc
    return configuration_from_record(record)
