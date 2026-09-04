<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Laser Core — device model contract
-->

# Device model contract

What a consumer of this repository's geometry receives, and what it may
not conclude from it.

## The one thing to read first

Every body here is an **inscribed polyhedron of revolution**, not a
sphere. Its own profile — the frustum stack the body was built from — is
its analytic reference. Comparing a volume in these records to
`4/3 π r³`, or an area to `4 π r²`, compares two different solids and
will show a deficit that is a property of the comparison, not of the
model.

## The two tiers

| Tier | Schema | Built by |
|---|---|---|
| G1, tessellated | `scpn.laser-icf-3d-model.v1` | `build_device_model` |
| G2, B-rep | `scpn.laser-icf-cad-model.v1` | `build_device_cad` |

Both schemas are at version `1.0.0`. Tier G2 requires the optional
`cad` extra; every other capability of this package works without it.

## Units and frame

| | |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the hohlraum axis |
| origin | the centre of the capsule |

The configuration and the level-0 capsule declaration carry
**micrometres**. The conversion happens once, in `capsule_radii_m`, and
nowhere else.

## The bodies depend on the configuration

| Identifier | Bodies, in order |
|---|---|
| `laser_icf_direct_drive` | `ablator_shell`, `fuel_ice_shell`, `fuel_vapour_core` |
| `laser_icf_fast_or_shock_ignition` | `ablator_shell`, `fuel_ice_shell`, `fuel_vapour_core` |
| `laser_icf_indirect_drive` | the three above, then `hohlraum_wall` |

| Body | Role | Material token | Shape |
|---|---|---|---|
| `ablator_shell` | `ablator` | `plastic_ablator` | spherical shell |
| `fuel_ice_shell` | `fuel` | `solid_fuel_ice` | spherical shell |
| `fuel_vapour_core` | `fuel` | `fuel_vapour` | sphere |
| `hohlraum_wall` | `enclosure` | `high_z_case` | annular tube |

The order is part of the contract and is validated at construction.

An enclosure is **required** for `laser_icf_indirect_drive` and
**refused** for the two directly driven identifiers. Both directions
refuse rather than default.

## Where each dimension comes from

| Dimension | Home |
|---|---|
| capsule outer radius | `TargetDeclaration.capsule_radius_um` |
| ablator thickness | `CapsuleDeclaration.ablator_thickness_um` |
| fuel thickness | `CapsuleDeclaration.fuel_thickness_um` |
| case radius, wall thickness, case length | `HohlraumEnvelope` |

Nothing in that table appears twice. The geometry package declares only
the last row.

A layering that does not fit inside the capsule is refused by the
level-0 relation itself, so this tier cannot draw a capsule the physics
record would have rejected. A case no wider than the capsule, or no
longer than its diameter, is refused here.

## Resolutions

`segments` sets what the revolution keeps of the profile; `rings` sets
the profile. They are independent, and passing one where the other
belongs builds a valid body of the wrong shape that no gate downstream
would notice.

Defaults for tier G2: 8 reference segments, 32 rings, a linear
deflection of 2e-7 m and an angular deflection of 0.1 rad.

## Exports and identity

Both tiers serialise canonically — sorted keys, minimal separators, one
trailing newline, no NaN or infinity — and carry the SHA-256 of those
bytes. Tier G2 additionally carries normalised STEP bytes and their
digest, the library's assembly manifest, and the back-end versions that
produced the solids.

Each record names the digests of the inputs it was built from: the
configuration, the capsule declaration, and the enclosure where there is
one.

## Declared limits

- **32 rings is a ceiling at this scale, not a preference.** Above it
  the back-end's own volume measure departs from the analytic form by
  more than four orders of magnitude beyond the library's tolerance. The
  evidence kernel refuses.
- **2e-7 m is the tightest linear deflection the bodies clear.** One
  step tighter, the vapour core exceeds its declared bound.
- The faceting deficit bound of each body is `2 d / r` at that body's
  **outer** radius, which is the tightest bound a body of revolution
  admits.
- Determinism of the STEP bytes is claimed **within one pinned back-end
  environment**, never across back-end versions.

## Non-claims

- No dimension describes the target during a shot. These are the
  dimensions before the drive begins, and an implosion changes all of
  them.
- The capsule is three uniform concentric layers. No fill tube, no
  mounting stalk, no surface roughness and no layer non-uniformity is
  modelled — and those are precisely the quantities an implosion is
  sensitive to.
- The enclosure is one plain tube whose open ends stand for the laser
  entrance holes. No window, cooling ring, diagnostic aperture or
  support is modelled.
- No body is an engineering model, and no material property, load,
  field, dose, activation quantity or fabrication tolerance is carried.
- No value here describes or validates any real machine or shot.
  Reproducing a printed value is an anchor, never a claim about that
  machine.
