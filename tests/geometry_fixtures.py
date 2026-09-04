# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — device geometry anchors and builders

"""Anchors and builders shared by the two geometry tiers' tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

**The capsule's anchors are not restated here.** Its outer radius and
its two layer thicknesses are printed by the review the level-0 record
already anchors on, and they live in :mod:`physics_fixtures`. This
module imports them, because a second copy would be a second place for
them to drift and the whole point of the geometry package is that the
capsule has one home.

The enclosure's anchors are new, and they come from a different
document with a weaker standing. The work this repository cites for
indirect drive, J. D. Lindl, *Phys. Plasmas* **2** (1995) 3933, is
behind a subscription and is not on file. What is on file is its public
precursor, the 1994 Teller Medal lecture (UCRL-JC-115197), filed and
labelled as a **related substitute, never the cited work**. Two of its
printed statements are dimensionless, which is exactly the granularity
this repository's own configuration and geometry carry:

- a case-to-capsule radius ratio of 4 to 1, printed in the assumptions
  box of its Fig. 10;
- hohlraum areas "typically 15-25 times that of the initial capsule
  area", printed on its fourth page.

Both were read off the rendered pages rather than off the text layer.
That is not ceremony: the text layer of the other filed source in this
repository drops the exponent of one of its equations, and the same
extraction habit is what caught it.

Everything else about the enclosure is declared, and every declared
constant here says so in its own name.
"""

from __future__ import annotations

from typing import Final

from physics_fixtures import (
    PRINTED_ABLATOR_THICKNESS_UM,
    PRINTED_ICE_THICKNESS_UM,
    PRINTED_TARGET_RADIUS_UM,
    anchor_capsule,
    anchor_configuration,
)
from scpn_icf_laser_core.geometry import (
    MICROMETRE_M,
    HohlraumEnvelope,
)

# --- Lindl 1994 (UCRL-JC-115197), the related public precursor ---
PRINTED_CASE_TO_CAPSULE_RADIUS_RATIO: Final = 4.0
PRINTED_HOHLRAUM_AREA_RATIO_RANGE: Final = (15.0, 25.0)

# --- Declared; the precursor prints no absolute hohlraum dimension ---
# The case radius follows the printed ratio, so the ratio is recoverable
# from the built bodies rather than merely stored beside them. The length
# is chosen so that the interior wall area of the body actually built
# lands inside the printed band; the wall thickness is a plain
# declaration and no source is claimed for it.
DECLARED_CASE_LENGTH_UM: Final = 17000.0
DECLARED_CASE_WALL_THICKNESS_UM: Final = 30.0

# --- Tessellation resolutions the tests build at ---
# Independent knobs: the segments set what the revolution keeps of the
# profile, the rings set the profile itself.
ANCHOR_SEGMENTS: Final = 8
ANCHOR_RINGS: Final = 32

# --- Derived from the anchors above, never typed ---
ANCHOR_CAPSULE_RADIUS_M: Final = PRINTED_TARGET_RADIUS_UM * MICROMETRE_M
ANCHOR_FUEL_OUTER_RADIUS_M: Final = (
    PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM
) * MICROMETRE_M
ANCHOR_CAVITY_RADIUS_M: Final = (
    PRINTED_TARGET_RADIUS_UM - PRINTED_ABLATOR_THICKNESS_UM - PRINTED_ICE_THICKNESS_UM
) * MICROMETRE_M
ANCHOR_CASE_RADIUS_M: Final = (
    PRINTED_TARGET_RADIUS_UM * PRINTED_CASE_TO_CAPSULE_RADIUS_RATIO * MICROMETRE_M
)

__all__ = [
    "ANCHOR_CAPSULE_RADIUS_M",
    "ANCHOR_CASE_RADIUS_M",
    "ANCHOR_CAVITY_RADIUS_M",
    "ANCHOR_FUEL_OUTER_RADIUS_M",
    "ANCHOR_RINGS",
    "ANCHOR_SEGMENTS",
    "DECLARED_CASE_LENGTH_UM",
    "DECLARED_CASE_WALL_THICKNESS_UM",
    "PRINTED_ABLATOR_THICKNESS_UM",
    "PRINTED_CASE_TO_CAPSULE_RADIUS_RATIO",
    "PRINTED_HOHLRAUM_AREA_RATIO_RANGE",
    "PRINTED_ICE_THICKNESS_UM",
    "PRINTED_TARGET_RADIUS_UM",
    "anchor_capsule",
    "anchor_configuration",
    "anchor_hohlraum",
]


def anchor_hohlraum() -> HohlraumEnvelope:
    """Build the enclosure the indirect-drive anchors are evaluated on.

    Returns
    -------
    HohlraumEnvelope
        A case whose radius is the printed ratio times the capsule's
        printed radius, of declared length and declared wall thickness.
    """
    return HohlraumEnvelope(
        case_radius_m=ANCHOR_CASE_RADIUS_M,
        wall_thickness_m=DECLARED_CASE_WALL_THICKNESS_UM * MICROMETRE_M,
        length_m=DECLARED_CASE_LENGTH_UM * MICROMETRE_M,
    )
