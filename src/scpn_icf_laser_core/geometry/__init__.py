# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device geometry package

"""The enclosure declaration and the two geometry tiers of the laser-ICF family.

A capsule is three concentric bodies, and an indirect-drive target adds
the radiation enclosure around them. The capsule's own dimensions are
read from the configuration and the level-0 capsule declaration rather
than redeclared, so this package declares only the enclosure.
Design record: ADR 0006.
"""

from __future__ import annotations

from scpn_icf_laser_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DEFAULT_SPHERE_RINGS,
    DeviceModelCAD,
    build_device_cad,
)
from scpn_icf_laser_core.geometry.device import (
    HOHLRAUM_FIELDS,
    HohlraumEnvelope,
    hohlraum_from_record,
)
from scpn_icf_laser_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_HOHLRAUM_WALL,
    BODY_NAMES_BY_IDENTIFIER,
    CAPSULE_BODY_NAMES,
    MATERIAL_FUEL_VAPOUR,
    MATERIAL_HIGH_Z_CASE,
    MATERIAL_PLASTIC_ABLATOR,
    MATERIAL_SOLID_FUEL,
    MICROMETRE_M,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    ROLE_ABLATOR,
    ROLE_ENCLOSURE,
    ROLE_FUEL,
    DeviceModel3D,
    build_device_model,
    capsule_radii_m,
    require_containment,
    require_enclosure,
)

__all__ = [
    "BODY_ABLATOR_SHELL",
    "BODY_FUEL_ICE_SHELL",
    "BODY_FUEL_VAPOUR_CORE",
    "BODY_HOHLRAUM_WALL",
    "BODY_NAMES_BY_IDENTIFIER",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS",
    "CAPSULE_BODY_NAMES",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "DEFAULT_SPHERE_RINGS",
    "HOHLRAUM_FIELDS",
    "MATERIAL_FUEL_VAPOUR",
    "MATERIAL_HIGH_Z_CASE",
    "MATERIAL_PLASTIC_ABLATOR",
    "MATERIAL_SOLID_FUEL",
    "MICROMETRE_M",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
    "ROLE_ABLATOR",
    "ROLE_ENCLOSURE",
    "ROLE_FUEL",
    "DeviceModel3D",
    "DeviceModelCAD",
    "HohlraumEnvelope",
    "build_device_cad",
    "build_device_model",
    "capsule_radii_m",
    "hohlraum_from_record",
    "require_containment",
    "require_enclosure",
]
