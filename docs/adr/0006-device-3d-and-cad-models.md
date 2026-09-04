<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Laser Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models of a capsule and its enclosure

Status: accepted (2026-09-04), amended the same day — see "Correction,
2026-09-04" below, which withdraws the ring-count ceiling and the
boundary mechanism the first version stated. Builds on ADR 0002 (device
configuration model), which owns the capsule's outer radius, and ADR
0005 (level-0 device physics), which owns its layering.

## Context

A laser-ICF target is small, layered and spherical, and every one of
those three facts changed a decision here.

**Small.** The bodies are millimetres across. Every other family in this
group models metres, and two things that hold at metre scale do not hold
at this one. They are recorded under their own heading below, because a
reader who assumes the sibling families' numbers transfer will build a
model that fails its own evidence gate — which is exactly what happened
on the first build here.

**Layered.** The capsule is an ablator, a fuel layer and the vapour the
fuel layer encloses. All three are concentric about one point, and the
dimensions that define them already exist in this repository: the outer
radius in the configuration, because the configuration's intensity
estimate divides by it, and the two thicknesses in the level-0 capsule
declaration, because the fuel mass is computed from them.

**Spherical.** The shared kernel library gained spherical bodies and the
spherical shell in the increment this landing pins. Nothing here needs a
primitive the library does not have.

## Decision

**One geometry declaration, and it is not the capsule.** The geometry
package declares only the radiation enclosure of an indirect-drive
target, because that is the one piece of hardware neither the
configuration nor the level-0 record carries. The capsule's three radii
are computed from the two objects that already own them, by a single
function, in a single conversion from micrometres to metres. Declaring
the capsule again here would have given every one of its dimensions a
second home.

**The body set follows the identifier.** Direct drive and the
fast-or-shock-ignition class draw three bodies; indirect drive draws
four. The enclosure is required for the indirect-drive identifier and
refused for the other two, both directions refusals rather than
defaults. The configuration model already refuses a hohlraum flag on a
direct-drive identifier; this is the same statement about the same
machine, made about the solid instead of the declaration.

The ignitor pulse of the fast-or-shock-ignition class adds no body. It
is light, not hardware.

**The vapour is drawn, although it is a gas.** The beam-target family
draws nothing inside its beam pipe, and the fusion-fission family draws
nothing in its vacuum zone, both for the same reason: nothing is
declared to be there. Here the review prints the vapour's density and
the vapour belongs to the fuel inventory, so it is a body.

**The enclosure's open ends are its laser entrance holes.** The wall is
one plain annular tube. No hole is cut, because a cut is a boolean
operation this tier does not perform and a hole drawn as a hole would
claim a dimension no filed source prints.

## What the sources print, and what is declared

The capsule's anchors come from the review this repository already
anchors its physics on: an outer radius of 1700 µm, a 37 µm plastic
ablator and a 160 µm layer of solid fuel. All three are recovered from
the built bodies rather than read back out of the declaration.

The enclosure's anchors come from a **related public precursor** of the
cited indirect-drive work, filed and labelled as a substitute because
the cited work itself is behind a subscription. It prints no absolute
hohlraum dimension, but it prints two dimensionless ones: a
case-to-capsule radius ratio of 4 to 1, and hohlraum areas typically 15
to 25 times the initial capsule area. The case radius follows the
printed ratio, so the ratio is recoverable from the built solids — it
comes back exactly four — and the enclosure's length is chosen so that
the interior wall area of the body actually built lands inside the
printed band, measured at 20.5.

The wall thickness is declared and no source is claimed for it.

## What the millimetre scale changed, measured

**The ring count is bounded by the back-end, and the bound is not a
simple ceiling.** Scanning every count from 30 to 75 on this family's
own bodies gives three regimes:

| ring counts | behaviour |
|---|---|
| 30 to 39 | every count exact, to 7e-15 relative |
| 40 to 61 | mixed: every even count refuses, every odd count is exact |
| 62 and above | every count refuses |

The first refusal is at 40 rings, where the fuel shell and the vapour
core both depart — the shell by 1.7e-4 against a 1e-9 tolerance. The
cylindrical bodies are unaffected throughout.

**The parity is measured; its cause is not claimed.** An even ring count
places exactly one profile sample on the equator, at exactly `(0, R)`,
and an odd count places none. The refusals inside the mixed band fall
exactly on the even counts. That correlation is measured. Whether the
equatorial sample is what the revolve fails on is **not** established
here; the mechanism belongs to the back-end.

**Where the band starts moves with the body's radius**, measured on
solid spheres:

| radius | first refusal |
|---|---|
| 1.000 mm | 34 |
| 1.503 mm (this family's cavity) | 40 |
| 1.800 mm | 42 |
| 2.340 mm | 46 |
| 3.000 mm | 50 |
| 5.000 mm | 58 |
| 10 mm and above | none up to 120 |

That last row is why no metre-scale family in this group meets the bound
at all, and the rows above it are why **each family must measure its own
and may not inherit a sibling's.**

**No single length is constant where the band starts.** The shortest
generating segment there runs from 9.2e-5 m at 1.0 mm to 2.7e-4 m at
5.0 mm, a factor of three over the same radii, so it is not the quantity
that sets it.

**The default is the top of the first regime, not the highest count that
passes.** Odd counts to 61 do pass. Building there would mean sitting
one step from a refusal on the strength of a parity whose cause is
unknown, and buying a finer profile with a margin of zero. Nothing was
loosened: the evidence kernel refuses, naming the body and the bound,
and a test asserts the refusal at 40 — the step immediately above the
default, because a number far above it passes the same test while
locating nothing.

**The angular deflection does not bind.** Between 0.5 and 0.1 radians
every body's deficit is identical to four significant figures.

**The linear deflection does not change the model at all.** Measured
across 5e-7, 2e-7, 1.5e-7, 1.2e-7, 1.15e-7 and 1.13e-7 metres, the
vapour core's faceted volume deficit is 1.502834e-4 at every one of
them, to seven significant figures. Only the declared bound `2 d / r`
moves. At 1e-8 m the back-end refuses outright with a numeric error.

**So the threshold is exact rather than a rung on a ladder.** The bound
is violated when `2 d / r` falls below the deficit, so the smallest
deflection the worst body clears is `deficit · r / 2` = **1.12938e-7 m**.
Measured either side: 1.13e-7 m builds at 0.9995 of its bound, and
1.12e-7 m is refused.

The choice of 2e-7 m sits above that threshold deliberately, leaving the
vapour core at 0.56 of its bound — a stated margin against back-end
drift, and **not** the tightest bound the bodies clear, which is what
this record claimed while it was sampling a four-value ladder instead of
computing the threshold. Two tests carry it now: one builds at two
deflections and asserts the deficits are equal while the bounds differ
by their ratio, and one computes the threshold from the built model.

**The radius handed to the deficit bound is each body's outer radius.**
A sphere's circles run from zero at the poles to the outer radius at the
equator, so there is no single smallest circle to name and the poles
would make the bound unbounded. The outer radius is the tightest bound
the body admits.

### Correction, 2026-09-04

The version of this section accepted earlier the same day said the
ceiling was 32 rings and that the boundary sat "where the shortest
generating segment of the profile falls below about 5e-6 m". Both
statements are withdrawn.

Neither was measured. The sweep behind them tested 32, 48, 64 and 128
and never tested 33 through 47, so it located a failure and reported it
as a boundary; and the segment length was inferred rather than measured,
which the table above falsifies. The ring counts 33 to 39 were available
the whole time and are exact.

The consequence was a real one and not merely a wording defect: the
family shipped at 32 rings, seven steps below the resolution its own
back-end supports, and the consumer contract told a reader that 32 was a
hard ceiling. The measurement above replaces both, and the test now
asserts the step immediately above the default so the same gap cannot
reopen.

**A third statement in this section was corrected the same afternoon.**
It said 2e-7 m was "the tightest bound the bodies actually clear". That
is true only against the ladder of four values it tested; 1.2e-7 m
clears as well, and the exact threshold is 1.12938e-7 m. The section
above now computes the threshold instead of sampling for it. Three
rounds of correction on one section, all of the same kind: a shape
inferred from a few points and written in the register of a
measurement.

**The correction was itself refined an hour later, and that is recorded
too.** Its first form said 39 was "the largest count the bodies are
exact at". It is not: 41, 43 and every other odd count to 61 are exact
as well. Scanning the whole range instead of the endpoints turned up the
parity structure and the third regime above 61, which is what the
section above now states. The number 39 did not move — it is the top of
the first regime either way — but the reason for it did, from "the
back-end cannot go higher" to "higher is erratic and its margin is
zero". Two rounds of correction on one finding is the cost of having
reported an endpoint sweep as a boundary in the first place.

Incident record:
`.coordination/incidents/INCIDENT_2026-09-04T1315_ring_ceiling_reported_without_measuring_the_boundary.md`.

## Consequences

- Two capabilities are declared, `device_3d_model` and
  `device_cad_model`, both at `computational_prototype` maturity.
- This repository gains its first dependency: the shared kernel library,
  pinned by commit, with the CAD back-end as an optional extra naming
  the same commit. Three workflows gain an install step and one of them
  also installs the system library the mesher links against.
- The manifest gains a `kernel_library` pin. The manifest validator does
  not inspect that field — a fleet-wide finding this repository joins
  rather than resolves, because resolving it changes the shared standard
  and that is an owner-authorised change. A repository contract test
  holds the pin, the dependency and the workflows to one commit in the
  meantime.
- A consumer must not compare any volume here to `4/3 π r³`. Every body
  is an inscribed polyhedron of revolution, and its own profile is its
  reference. The library states the same rule in its ADR 0013.
- The two resolutions are independent and neither gate would catch them
  being swapped, so a test asserts that swapping them builds a different
  body.
