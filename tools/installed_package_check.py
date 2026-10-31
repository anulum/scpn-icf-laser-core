# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — installed-wheel contract check

"""Exercise the installed package from outside the source checkout.

The installed-wheel workflow builds the wheel, installs it into a clean
environment and runs this script with ``python -I`` from a directory
outside the checkout. The script fails closed unless the package was
imported from the environment rather than the checkout, ships its
``py.typed`` marker, reports matching installed metadata with the pinned
kernel dependency, and serves the public path from a canonical
configuration document and the declared capsule and implosion through
level-0 physics to the tessellated device model. In ``base`` mode
the optional CAD back-end must be absent and a CAD request must raise the
documented ``CadUnavailableError``; in ``cad`` mode one B-rep model must be
built and
carry its STEP digest.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import sys
from pathlib import Path
from typing import Final

DISTRIBUTION: Final = "scpn-icf-laser-core"
PACKAGE: Final = "scpn_icf_laser_core"
KERNEL_REQUIREMENT: Final = "scpn-reactor-kernels"
MODES: Final = ("base", "cad")

CONFIGURATION_DOCUMENT: Final = (
    b'{"driver":{"driver_energy_mj":1.5,"pulse_duration_ns":10.0,'
    b'"wavelength_nm":350.0},"identifier":"laser_icf_direct_drive",'
    b'"registry":{"digest_sha256":'
    b'"0000000000000000000000000000000000000000000000000000000000000000",'
    b'"version":"1.0.0"},"target":{"capsule_radius_um":1700.0,'
    b'"hohlraum":false,"ignitor_pulse":false}}\n'
)
"""The anchor configuration of the test suite, from the filed review.

Every declared value below is the same anchor the physics and geometry tests
use. They serve only as a regression anchor for the installed package;
nothing is asserted about the target the review describes.
"""

CAPSULE: Final[dict[str, float]] = {
    "ablator_thickness_um": 37.0,
    "fuel_thickness_um": 160.0,
    "fuel_density_g_cm3": 0.25,
}
"""Declared capsule layering of the anchor."""

IMPLOSION: Final[dict[str, float]] = {
    "absorbed_fraction": 0.95,
    "shell_kinetic_energy_kj": 100.0,
    "coupled_fraction": 0.4,
    "in_flight_shell_thickness_um": 41.23456790123457,
    "stagnation_inner_radius_um": 65.34782608695652,
    "shell_pressure_mbar": 100.0,
    "shell_density_g_cm3": 10.0,
    "burnup_fraction": 0.2,
}
"""Declared implosion outcome of the anchor."""

MODEL_SEGMENTS: Final = 8
MODEL_RINGS: Final = 39
"""Tessellation resolution of the checked tier-G1 model (the suite's own)."""


def layout_findings(package_dir: Path, checkout: Path) -> list[str]:
    """Check where the package was imported from and what it ships.

    Parameters
    ----------
    package_dir
        Directory of the imported package.
    checkout
        Source checkout the installed package must not come from.

    Returns
    -------
    list[str]
        Findings; empty when the package lies outside the checkout and
        carries its ``py.typed`` marker.
    """
    return failed(
        [
            (
                not package_dir.resolve().is_relative_to(checkout.resolve()),
                f"{PACKAGE} imported from the checkout: {package_dir}",
            ),
            (
                (package_dir / "py.typed").is_file(),
                f"{PACKAGE} ships no py.typed marker",
            ),
        ]
    )


def failed(checks: list[tuple[bool, str]]) -> list[str]:
    """Return the messages of the checks that did not hold.

    Parameters
    ----------
    checks
        Pairs of an outcome and the finding reported when it is false.

    Returns
    -------
    list[str]
        Findings in check order.
    """
    return [message for holds, message in checks if not holds]


def metadata_findings(
    version: str,
    distribution_name: str = DISTRIBUTION,
    required: str = KERNEL_REQUIREMENT,
) -> list[str]:
    """Check the installed distribution metadata.

    Parameters
    ----------
    version
        ``__version__`` of the imported package.
    distribution_name
        Installed distribution to read.
    required
        Requirement the distribution must declare.

    Returns
    -------
    list[str]
        Findings; empty when the distribution is installed with the same
        version and declares the required dependency.
    """
    try:
        distribution = importlib.metadata.distribution(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return [f"{distribution_name} is not installed"]
    requirements = distribution.requires or []
    return failed(
        [
            (
                distribution.version == version,
                f"installed version {distribution.version} != package {version}",
            ),
            (
                any(item.startswith(required) for item in requirements),
                f"{distribution_name} does not require {required}",
            ),
        ]
    )


def public_path_findings(mode: str) -> list[str]:
    """Serve the public path through the installed package.

    Parameters
    ----------
    mode
        ``base`` when the CAD back-end must be absent, ``cad`` when it must
        build a model.

    Returns
    -------
    list[str]
        Findings; empty when every promised capability of the mode works
        and the absent one fails as documented.
    """
    from scpn_reactor_kernels.errors import CadUnavailableError

    from scpn_icf_laser_core import configuration_from_bytes
    from scpn_icf_laser_core.geometry import build_device_cad, build_device_model
    from scpn_icf_laser_core.physics import (
        CapsuleDeclaration,
        ImplosionDeclaration,
        level0_physics,
    )

    configuration = configuration_from_bytes(CONFIGURATION_DOCUMENT)
    capsule = CapsuleDeclaration(**CAPSULE)
    implosion = ImplosionDeclaration(**IMPLOSION)
    record = level0_physics(configuration, capsule, implosion)
    model = build_device_model(configuration, capsule, MODEL_SEGMENTS, MODEL_RINGS)
    findings = failed(
        [
            (
                configuration.canonical_bytes() == CONFIGURATION_DOCUMENT,
                "configuration did not round-trip byte for byte",
            ),
            (
                record.canonical_bytes()
                == level0_physics(configuration, capsule, implosion).canonical_bytes(),
                "level-0 record is not deterministic",
            ),
            (
                model.canonical_bytes()
                == build_device_model(
                    configuration, capsule, MODEL_SEGMENTS, MODEL_RINGS
                ).canonical_bytes(),
                "tessellated model is not deterministic",
            ),
        ]
    )
    if mode == "base":
        try:
            build_device_cad(configuration, capsule)
        except CadUnavailableError:
            return findings
        return [*findings, "CAD back-end present in the base environment"]
    cad = build_device_cad(configuration, capsule)
    return findings + failed(
        [
            (len(cad.step_sha256) == 64, "CAD model carries no STEP digest"),
            (
                cad.configuration_digest_sha256 == configuration.digest_sha256(),
                "CAD model is bound to another configuration",
            ),
        ]
    )


def check_installed(mode: str, checkout: Path) -> list[str]:
    """Run every installed-package check for one environment.

    Parameters
    ----------
    mode
        One of :data:`MODES`.
    checkout
        Source checkout the package must not be imported from.

    Returns
    -------
    list[str]
        All findings; empty when the installed package meets its contract.
    """
    package = importlib.import_module(PACKAGE)
    package_dir = Path(package.__file__ or "").parent
    findings = layout_findings(package_dir, checkout)
    findings += metadata_findings(str(package.__version__))
    findings += public_path_findings(mode)
    return findings


def report(mode: str, findings: list[str]) -> int:
    """Print the outcome of one environment and return its exit status.

    Parameters
    ----------
    mode
        Environment mode that was checked.
    findings
        Findings of :func:`check_installed`.

    Returns
    -------
    int
        ``0`` without findings, else ``1``.
    """
    if findings:
        print(f"installed-package: FAIL {mode}", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1
    print(f"installed-package: PASS {mode}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the installed-package check from the command line.

    Parameters
    ----------
    argv
        Argument vector; ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the installed package meets its contract, else ``1``.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    args = parser.parse_args(argv)
    return report(args.mode, check_installed(args.mode, args.checkout))


if __name__ == "__main__":
    sys.exit(main())
