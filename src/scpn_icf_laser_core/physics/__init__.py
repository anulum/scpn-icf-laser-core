# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — level-0 device physics package

"""Level-0 device physics of the laser-ICF device family.

The published closed forms of a filed review, evaluated on a declared
capsule and a declared implosion: the hot-spot ignition condition in the
four equivalent forms that review prints, the definitions an imploding
shell is quoted by — adiabat, in-flight aspect ratio, convergence ratio,
hydrodynamic efficiency — and the fuel inventory, yield and target gain
that follow from the capsule's layering.

Nothing here simulates an implosion. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_icf_laser_core.physics.ignition import (
    HOT_SPOT_ENERGY_SCALE_KJ,
    HOT_SPOT_PRESSURE_AT_REFERENCE_GBAR,
    HOT_SPOT_PRESSURE_COEFFICIENT_GBAR,
    IGNITION_AREAL_DENSITY_G_CM2,
    IGNITION_ION_TEMPERATURE_KEV,
    REFERENCE_HOT_SPOT_RADIUS_UM,
    dt_pressure_gbar,
    hot_spot_energy_kj,
    hot_spot_pressure_floor_gbar,
    hot_spot_pressure_for_radius_gbar,
    hot_spot_radius_ceiling_um,
    ignition_condition_met,
)
from scpn_icf_laser_core.physics.implosion import (
    DT_ADIABAT_COEFFICIENT,
    IFAR_EVALUATION_RADIUS_FRACTION,
    absorbed_energy_kj,
    convergence_ratio,
    dt_adiabat,
    hydrodynamic_efficiency,
    ifar_evaluation_radius_um,
    in_flight_aspect_ratio,
    require_fraction,
)
from scpn_icf_laser_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CapsuleDeclaration,
    ImplosionDeclaration,
    Level0Physics,
    OperatingPoint,
    initial_inner_radius_um,
    level0_physics,
)
from scpn_icf_laser_core.physics.yield_and_gain import (
    DT_FUSION_ENERGY_MEV,
    dt_specific_energy_j_per_g,
    fusion_yield_mj,
    spherical_shell_mass_mg,
    target_gain,
)

__all__ = [
    "DT_ADIABAT_COEFFICIENT",
    "DT_FUSION_ENERGY_MEV",
    "HOT_SPOT_ENERGY_SCALE_KJ",
    "HOT_SPOT_PRESSURE_AT_REFERENCE_GBAR",
    "HOT_SPOT_PRESSURE_COEFFICIENT_GBAR",
    "IFAR_EVALUATION_RADIUS_FRACTION",
    "IGNITION_AREAL_DENSITY_G_CM2",
    "IGNITION_ION_TEMPERATURE_KEV",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "REFERENCE_HOT_SPOT_RADIUS_UM",
    "CapsuleDeclaration",
    "ImplosionDeclaration",
    "Level0Physics",
    "OperatingPoint",
    "absorbed_energy_kj",
    "convergence_ratio",
    "dt_adiabat",
    "dt_pressure_gbar",
    "dt_specific_energy_j_per_g",
    "fusion_yield_mj",
    "hot_spot_energy_kj",
    "hot_spot_pressure_floor_gbar",
    "hot_spot_pressure_for_radius_gbar",
    "hot_spot_radius_ceiling_um",
    "hydrodynamic_efficiency",
    "ifar_evaluation_radius_um",
    "ignition_condition_met",
    "in_flight_aspect_ratio",
    "initial_inner_radius_um",
    "level0_physics",
    "require_fraction",
    "spherical_shell_mass_mg",
    "target_gain",
]
