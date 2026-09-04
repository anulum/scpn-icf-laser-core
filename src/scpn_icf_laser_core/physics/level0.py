# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — level-0 physics record

"""Level-0 physics record of one validated laser-ICF configuration.

The configuration carries the driver and the capsule's outer radius. It
does not carry the capsule's layering, the state of the shell in flight,
or how much of the fuel burns, and none of those can be computed here —
they come out of the radiation-hydrodynamics calculations this
repository does not perform. They are therefore declared, in two
objects that keep the two kinds of declaration apart: what the capsule
is made of before the shot, and what the implosion did.

The record then evaluates the definitions of
:mod:`~scpn_icf_laser_core.physics.implosion`, the ignition floors of
:mod:`~scpn_icf_laser_core.physics.ignition`, and the yield and gain of
:mod:`~scpn_icf_laser_core.physics.yield_and_gain` on that pair, and
reports whether the declared hot spot clears the floors its own coupled
energy sets.

One cross-check is structural rather than declared: the capsule's
initial inner radius is the outer radius less the two declared
thicknesses, so a layering that does not fit inside the capsule the
configuration declares is refused rather than reported.

Design record: ADR 0005.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_laser_core.configuration import DeviceConfiguration
from scpn_icf_laser_core.errors import DeviceConfigurationError
from scpn_icf_laser_core.parameters import require_positive
from scpn_icf_laser_core.physics.ignition import (
    hot_spot_pressure_floor_gbar,
    hot_spot_radius_ceiling_um,
)
from scpn_icf_laser_core.physics.implosion import (
    absorbed_energy_kj,
    convergence_ratio,
    dt_adiabat,
    hydrodynamic_efficiency,
    ifar_evaluation_radius_um,
    in_flight_aspect_ratio,
    require_fraction,
)
from scpn_icf_laser_core.physics.yield_and_gain import (
    fusion_yield_mj,
    spherical_shell_mass_mg,
    target_gain,
)

LEVEL0_SCHEMA: Final = "scpn.icf-laser-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published implosion definitions and "
        "ignition floors on a declared capsule and a declared implosion"
    ),
    (
        "no radiation hydrodynamics, no transport, no laser-plasma "
        "interaction and no burn calculation is performed anywhere here"
    ),
    (
        "the capsule layering, the in-flight shell state and the burnup "
        "fraction are declared inputs; they come out of calculations this "
        "repository does not perform and could not check"
    ),
    (
        "the ignition floors are necessary algebraic conditions on a design, "
        "never a prediction that a design ignites"
    ),
    (
        "the convergence ratio is defined with alpha-particle deposition "
        "turned off, a condition on how its input is computed that no code "
        "here can enforce"
    ),
    (
        "no value describes or validates any real machine or shot; an anchor "
        "reproduces a number a filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class CapsuleDeclaration:
    """Declared layering of a capsule, before the shot.

    Parameters
    ----------
    ablator_thickness_um
        Thickness of the outer ablator in micrometres; strictly
        positive.
    fuel_thickness_um
        Thickness of the fuel layer inside it, in micrometres; strictly
        positive.
    fuel_density_g_cm3
        Density of the solid fuel layer in grams per cubic centimetre;
        strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive.
    """

    ablator_thickness_um: float
    fuel_thickness_um: float
    fuel_density_g_cm3: float

    def __post_init__(self) -> None:
        """Validate the declared layering.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite or not strictly positive.
        """
        require_positive("ablator_thickness_um", self.ablator_thickness_um)
        require_positive("fuel_thickness_um", self.fuel_thickness_um)
        require_positive("fuel_density_g_cm3", self.fuel_density_g_cm3)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "ablator_thickness_um": self.ablator_thickness_um,
            "fuel_thickness_um": self.fuel_thickness_um,
            "fuel_density_g_cm3": self.fuel_density_g_cm3,
        }


@dataclass(frozen=True, slots=True)
class ImplosionDeclaration:
    """Declared outcome of one implosion.

    Parameters
    ----------
    absorbed_fraction
        Fraction of the incident laser energy absorbed, in ``(0, 1]``.
    shell_kinetic_energy_kj
        Kinetic energy of the imploding shell in kilojoules; strictly
        positive.
    coupled_fraction
        Fraction ``f_k`` of that kinetic energy converted into hot-spot
        internal energy at peak compression, in ``(0, 1]``.
    in_flight_shell_thickness_um
        Shell thickness where the in-flight aspect ratio is read;
        strictly positive.
    stagnation_inner_radius_um
        Inner radius at peak compression, computed with alpha-particle
        deposition turned off; strictly positive.
    shell_pressure_mbar
        In-flight shell pressure in megabar; strictly positive.
    shell_density_g_cm3
        In-flight shell density in grams per cubic centimetre; strictly
        positive.
    burnup_fraction
        Fraction of the fuel inventory consumed, in ``(0, 1]``.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite, not strictly positive, or, for the
        fractions, above one.
    """

    absorbed_fraction: float
    shell_kinetic_energy_kj: float
    coupled_fraction: float
    in_flight_shell_thickness_um: float
    stagnation_inner_radius_um: float
    shell_pressure_mbar: float
    shell_density_g_cm3: float
    burnup_fraction: float

    def __post_init__(self) -> None:
        """Validate the declared implosion.

        Raises
        ------
        DeviceConfigurationError
            If any value leaves its documented interval. Each is
            validated here as well as inside the relation that consumes
            it, so a record can never be built from a set the relations
            would have refused one at a time.
        """
        require_fraction("absorbed_fraction", self.absorbed_fraction)
        require_fraction("coupled_fraction", self.coupled_fraction)
        require_fraction("burnup_fraction", self.burnup_fraction)
        require_positive("shell_kinetic_energy_kj", self.shell_kinetic_energy_kj)
        require_positive(
            "in_flight_shell_thickness_um", self.in_flight_shell_thickness_um
        )
        require_positive("stagnation_inner_radius_um", self.stagnation_inner_radius_um)
        require_positive("shell_pressure_mbar", self.shell_pressure_mbar)
        require_positive("shell_density_g_cm3", self.shell_density_g_cm3)

    def coupled_energy_kj(self) -> float:
        """Return the kinetic energy coupled into the hot spot.

        Returns
        -------
        float
            The product ``f_k E_k`` in kilojoules.
        """
        return self.coupled_fraction * self.shell_kinetic_energy_kj

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "absorbed_fraction": self.absorbed_fraction,
            "shell_kinetic_energy_kj": self.shell_kinetic_energy_kj,
            "coupled_fraction": self.coupled_fraction,
            "in_flight_shell_thickness_um": self.in_flight_shell_thickness_um,
            "stagnation_inner_radius_um": self.stagnation_inner_radius_um,
            "shell_pressure_mbar": self.shell_pressure_mbar,
            "shell_density_g_cm3": self.shell_density_g_cm3,
            "burnup_fraction": self.burnup_fraction,
        }


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Composed level-0 operating point of one configuration.

    Parameters
    ----------
    on_target_intensity_w_cm2
        Sphere-averaged on-target intensity the configuration carries.
    initial_inner_radius_um
        Capsule radius less the two declared thicknesses.
    ifar_evaluation_radius_um
        Ablation-front radius the aspect ratio is read at.
    in_flight_aspect_ratio
        The aspect ratio at that point.
    convergence_ratio
        Initial inner radius over the stagnation inner radius.
    shell_adiabat
        Shell pressure over the Fermi-degenerate pressure at its
        density.
    absorbed_energy_kj
        Laser energy the target absorbed.
    hydrodynamic_efficiency
        Shell kinetic energy over absorbed energy.
    coupled_energy_kj
        Kinetic energy converted into hot-spot internal energy.
    hot_spot_pressure_floor_gbar
        Least hot-spot pressure that ignites at that coupled energy.
    hot_spot_radius_ceiling_um
        Largest hot spot that ignites at that coupled energy.
    fuel_mass_mg
        Mass of the declared fuel layer.
    fusion_yield_mj
        Energy released at the declared burnup fraction.
    target_gain
        Yield over incident laser energy.
    """

    on_target_intensity_w_cm2: float
    initial_inner_radius_um: float
    ifar_evaluation_radius_um: float
    in_flight_aspect_ratio: float
    convergence_ratio: float
    shell_adiabat: float
    absorbed_energy_kj: float
    hydrodynamic_efficiency: float
    coupled_energy_kj: float
    hot_spot_pressure_floor_gbar: float
    hot_spot_radius_ceiling_um: float
    fuel_mass_mg: float
    fusion_yield_mj: float
    target_gain: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "on_target_intensity_w_cm2": self.on_target_intensity_w_cm2,
            "initial_inner_radius_um": self.initial_inner_radius_um,
            "ifar_evaluation_radius_um": self.ifar_evaluation_radius_um,
            "in_flight_aspect_ratio": self.in_flight_aspect_ratio,
            "convergence_ratio": self.convergence_ratio,
            "shell_adiabat": self.shell_adiabat,
            "absorbed_energy_kj": self.absorbed_energy_kj,
            "hydrodynamic_efficiency": self.hydrodynamic_efficiency,
            "coupled_energy_kj": self.coupled_energy_kj,
            "hot_spot_pressure_floor_gbar": self.hot_spot_pressure_floor_gbar,
            "hot_spot_radius_ceiling_um": self.hot_spot_radius_ceiling_um,
            "fuel_mass_mg": self.fuel_mass_mg,
            "fusion_yield_mj": self.fusion_yield_mj,
            "target_gain": self.target_gain,
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    capsule
        The declared capsule layering.
    implosion
        The declared implosion.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    capsule: CapsuleDeclaration
    implosion: ImplosionDeclaration
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule": self.capsule.to_record(),
            "implosion": self.implosion.to_record(),
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

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
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def initial_inner_radius_um(
    configuration: DeviceConfiguration, capsule: CapsuleDeclaration
) -> float:
    """Return the capsule's initial inner radius.

    The outer radius the configuration declares, less the ablator and
    fuel thicknesses the capsule declares.

    Parameters
    ----------
    configuration
        Validated laser-ICF configuration.
    capsule
        Declared capsule layering.

    Returns
    -------
    float
        The initial inner radius in micrometres.

    Raises
    ------
    DeviceConfigurationError
        If the two declared layers do not fit inside the capsule. This
        is refused rather than reported: a layering that does not fit
        describes a different capsule from the one the configuration
        declares.
    """
    remaining = (
        configuration.target.capsule_radius_um
        - capsule.ablator_thickness_um
        - capsule.fuel_thickness_um
    )
    if remaining <= 0.0:
        raise DeviceConfigurationError(
            "capsule: an ablator of "
            f"{capsule.ablator_thickness_um!r} um and fuel of "
            f"{capsule.fuel_thickness_um!r} um leave no cavity inside a "
            f"capsule of radius {configuration.target.capsule_radius_um!r} um"
        )
    return remaining


def level0_physics(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    implosion: ImplosionDeclaration,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated laser-ICF configuration supplying the driver and the
        capsule's outer radius.
    capsule
        Declared capsule layering.
    implosion
        Declared implosion outcome.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared value leaves its documented interval or the
        layering does not fit the capsule; the refusals name the field.
    """
    inner = initial_inner_radius_um(configuration, capsule)
    evaluation_radius = ifar_evaluation_radius_um(inner)
    absorbed = absorbed_energy_kj(
        configuration.driver.driver_energy_mj, implosion.absorbed_fraction
    )
    coupled = implosion.coupled_energy_kj()
    fuel_outer = configuration.target.capsule_radius_um - capsule.ablator_thickness_um
    fuel_mass = spherical_shell_mass_mg(
        fuel_outer, capsule.fuel_thickness_um, capsule.fuel_density_g_cm3
    )
    released = fusion_yield_mj(fuel_mass, implosion.burnup_fraction)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule=capsule,
        implosion=implosion,
        operating_point=OperatingPoint(
            on_target_intensity_w_cm2=configuration.on_target_intensity_w_cm2(),
            initial_inner_radius_um=inner,
            ifar_evaluation_radius_um=evaluation_radius,
            in_flight_aspect_ratio=in_flight_aspect_ratio(
                evaluation_radius, implosion.in_flight_shell_thickness_um
            ),
            convergence_ratio=convergence_ratio(
                inner, implosion.stagnation_inner_radius_um
            ),
            shell_adiabat=dt_adiabat(
                implosion.shell_pressure_mbar, implosion.shell_density_g_cm3
            ),
            absorbed_energy_kj=absorbed,
            hydrodynamic_efficiency=hydrodynamic_efficiency(
                implosion.shell_kinetic_energy_kj, absorbed
            ),
            coupled_energy_kj=coupled,
            hot_spot_pressure_floor_gbar=hot_spot_pressure_floor_gbar(coupled),
            hot_spot_radius_ceiling_um=hot_spot_radius_ceiling_um(coupled),
            fuel_mass_mg=fuel_mass,
            fusion_yield_mj=released,
            target_gain=target_gain(released, configuration.driver.driver_energy_mj),
        ),
    )
