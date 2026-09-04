# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device capability package

"""Device capability models of the SCPN laser-ICF device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics``, ``level0_device_physics``,
``device_3d_model`` and ``device_cad_model`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, the published closed-form ignition condition
and implosion definitions evaluated on a declared capsule and implosion,
the tessellated and B-rep models of the capsule and its radiation
enclosure on the shared kernel library, documented consistency
estimates, canonical serialisation with SHA-256 digests, and data-only
pins to the SPO registries. No claim about any real machine or
diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_laser_core.configuration import (
    DIRECT_DRIVE_LPI_BOUND_W_CM2,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_icf_laser_core.errors import (
    DeviceConfigurationError,
    DeviceGeometryError,
    DiagnosticPlanError,
)
from scpn_icf_laser_core.geometry import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_HOHLRAUM_WALL,
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    DeviceModel3D,
    DeviceModelCAD,
    HohlraumEnvelope,
    build_device_cad,
    build_device_model,
    hohlraum_from_record,
)
from scpn_icf_laser_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_icf_laser_core.parameters import LaserDriver, TargetDeclaration
from scpn_icf_laser_core.physics import (
    DT_ADIABAT_COEFFICIENT,
    DT_FUSION_ENERGY_MEV,
    IGNITION_AREAL_DENSITY_G_CM2,
    IGNITION_ION_TEMPERATURE_KEV,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CapsuleDeclaration,
    ImplosionDeclaration,
    Level0Physics,
    OperatingPoint,
    convergence_ratio,
    dt_adiabat,
    fusion_yield_mj,
    hot_spot_pressure_floor_gbar,
    hot_spot_radius_ceiling_um,
    hydrodynamic_efficiency,
    ignition_condition_met,
    in_flight_aspect_ratio,
    level0_physics,
    target_gain,
)
from scpn_icf_laser_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BODY_ABLATOR_SHELL",
    "BODY_FUEL_ICE_SHELL",
    "BODY_FUEL_VAPOUR_CORE",
    "BODY_HOHLRAUM_WALL",
    "BODY_NAMES_BY_IDENTIFIER",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CATALOGUE_BINDING",
    "DIRECT_DRIVE_LPI_BOUND_W_CM2",
    "DT_ADIABAT_COEFFICIENT",
    "DT_FUSION_ENERGY_MEV",
    "IGNITION_AREAL_DENSITY_G_CM2",
    "IGNITION_ION_TEMPERATURE_KEV",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "CandidateProfile",
    "CapsuleDeclaration",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FrameKind",
    "HohlraumEnvelope",
    "ImplosionDeclaration",
    "LaserDriver",
    "Level0Physics",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "TargetDeclaration",
    "__version__",
    "build_device_cad",
    "build_device_model",
    "configuration_from_bytes",
    "configuration_from_record",
    "convergence_ratio",
    "dt_adiabat",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "fusion_yield_mj",
    "hohlraum_from_record",
    "hot_spot_pressure_floor_gbar",
    "hot_spot_radius_ceiling_um",
    "hydrodynamic_efficiency",
    "ignition_condition_met",
    "in_flight_aspect_ratio",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "target_gain",
    "verify_envelope",
]
