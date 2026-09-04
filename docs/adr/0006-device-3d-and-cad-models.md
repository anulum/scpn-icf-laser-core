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

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), which owns the capsule's outer radius, and ADR 0005 (level-0
device physics), which owns its layering.

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

**The ring count has a ceiling, and it is the back-end's.** Up to and
including 32 rings the revolved solid's volume agrees with the analytic
frustum stack to 7e-15 relative. At 48 rings it disagrees by 3.5e-5, at
64 by 1.5e-5 and at 128 by 6.5e-5 — thousands of times the library's
1e-9 measure tolerance, and not converging. The boundary is where the
shortest generating segment of the profile falls below about 5e-6 m.
The cylindrical bodies are unaffected at every count.

Nothing was loosened. The evidence kernel refused the first build,
naming the body and the bound; the ring count came down to 32, where the
solids are exact again. A test asserts the refusal at 48 rings so that
the ceiling is a recorded measurement rather than a remembered one.

**The angular deflection does not bind.** Between 0.5 and 0.1 radians
every body's deficit is identical to four significant figures.

**The linear deflection buys a bound, not accuracy.** The deficit is set
by the ring count; the deflection sets what the deficit is measured
against. At 1e-8 m the back-end refuses outright with a numeric error.

The choice is 2e-7 m, which is the tightest bound the bodies actually
clear: the worst of them, the vapour core, sits at 0.57 of its bound,
and one step down at 1e-7 m it exceeds its bound by fifteen per cent. A
test asserts that failure too. This is not the widest available margin,
and it is not meant to be: a margin is only as good as the bound it is a
margin on.

**The radius handed to the deficit bound is each body's outer radius.**
A sphere's circles run from zero at the poles to the outer radius at the
equator, so there is no single smallest circle to name and the poles
would make the bound unbounded. The outer radius is the tightest bound
the body admits.

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
