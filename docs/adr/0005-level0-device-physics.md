<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Laser Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics as ignition condition and implosion figures

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), whose `LaserDriver` and `TargetDeclaration` already carry the
driver energy, the pulse duration, the wavelength and the capsule's
outer radius.

## Context

A laser-ICF implosion is a radiation-hydrodynamics problem. Nothing in
this repository computes one, and a level-0 record that pretended to
would be worthless. What a filed review does supply is the algebra
around such a calculation: the condition a hot spot must satisfy to
ignite, stated four equivalent ways with every coefficient printed, and
the definitions a one-dimensional design is quoted by.

The review — R. S. Craxton et al., *Phys. Plasmas* **22** (2015) 110501,
already collected in this repository's internal papers ledger — also
prints one worked design completely enough that its own statements can
be checked against its own equations. That turned out to matter.

## Decision

1. The capability `level0_device_physics` is implemented in three
   modules split by responsibility — the ignition condition, the
   implosion definitions, and the fuel inventory with its yield and gain
   — and a fourth composing them into a record.

2. **All four forms of the ignition condition are carried, because they
   constrain each other.** Equation 3-8's coefficient of 40 micrometres
   is not independent: it is equation 3-6's reference radius scaled by
   the ratio of the two printed pressures, and a test recovers it as the
   same IEEE double. The three coefficients then close on the energy
   relation `f_k E_k = 2 pi P R^3` to a fixed 0.53 %, at every energy
   over three decades — the rounding of the printed numbers, asserted
   as the measured offset rather than as an equality.

3. **The capsule layering and the implosion outcome are declared
   inputs**, in two separate objects: what the capsule was before the
   shot, and what the implosion did. Both come out of calculations this
   repository does not perform.

4. **Definitions carry their conditions.** The in-flight aspect ratio is
   read where the ablation front reaches two thirds of the initial inner
   radius, and that fraction lives in the module rather than in the
   caller. The convergence ratio is defined with alpha-particle
   deposition switched off, which no code can enforce and which is
   therefore stated in the docstring and in the record's non-claims. The
   hydrodynamic efficiency divides by **absorbed** energy, not incident.

5. **Two of the review's own numbers are not reproduced by its own
   relations, and both are recorded as tests rather than smoothed
   away.** Its worked example of equation 3-7 states a required pressure
   "exceeding 120 to 180 Gbar", where the equation at the stated inputs
   gives 112 to 125 Gbar. And its one-dimensional gain of 48 is not
   recovered from its printed geometry at its printed burnup fraction
   with solid fuel at standard density: that reconstruction gives about
   57, some 18 % high, because a quoted burnup fraction applies to the
   fuel that assembles and burns and part of the printed inventory is
   not in that state. **Neither number is used as an anchor.** Adjusting
   an input until they met would have been the easy move and would have
   made the record a fabrication.

6. Equation 3-6's coefficient is likewise carried as printed. Computed
   from equation 3-5's own floors it is 115 Gbar; the review prints 100.
   The implementation follows the printed value and a test carries the
   arithmetic, so the rounding is recorded where a reader will find it.

7. The capsule's initial inner radius is **built**, not declared: the
   outer radius the configuration carries, less the two declared
   thicknesses. A layering that does not fit is refused, because it
   describes a different capsule from the one the configuration
   declares.

8. No kernel-library pin. Every relation is arithmetic and elementary
   functions.

## Consequences

- The manifest gains the capability `level0_device_physics` at
  `computational_prototype`, pointing at
  `VALIDATION.md#level-0-device-physics`; the implemented capability
  count becomes three, and the derived inventory and studio descriptor
  are regenerated from the manifest.
- The package root re-exports the record and the principal relations.
- The record reports the gain its declared inputs imply, which for the
  review's design is the reconstruction near 57 rather than the printed
  48. A reader who wants the printed figure must supply the burning fuel
  mass, which this repository cannot compute.
- **What this ADR does not decide.** The family's tier-G1 and tier-G2
  device models are not landed here. Unlike the gridded electrostatic
  families, nothing blocks them: a capsule and its shells are solids of
  revolution the shared library can already express.
