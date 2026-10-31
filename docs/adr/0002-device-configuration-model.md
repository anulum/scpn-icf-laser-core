<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the three
laser-ICF registry configurations this repository owns
(`laser_icf_direct_drive`, `laser_icf_fast_or_shock_ignition`,
`laser_icf_indirect_drive`). The claim boundary and repository-level
`evidence_maturity` semantics follow the family pilot.

## Decision

1. The package `scpn_icf_laser_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   laser driver (energy, pulse duration, wavelength) and the target
   declaration (capsule radius, hohlraum flag, ignitor-pulse flag).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard drive-scheme class invariants: `laser_icf_indirect_drive`
   requires a hohlraum and `laser_icf_direct_drive` forbids one — the
   presence of the radiation enclosure is what separates the schemes;
   `laser_icf_fast_or_shock_ignition` requires the separate ignitor
   pulse that defines it, and the other two classes forbid it. The
   filed review R. S. Craxton et al., Phys. Plasmas 22 (2015) 110501,
   describes indirect drive through a hohlraum (PDF p. 8), fast
   ignition as separate compression and ignition phases (Sec. XIV,
   PDF p. 261) and shock ignition as an added high-intensity spike
   (Sec. XV, PDF p. 285).
4. Derived quantity: the sphere-averaged on-target intensity
   ``I = E / (tau 4 pi R^2)``. Advisory finding, reported by
   `consistency_report()` and never clamped: a direct-drive intensity
   above a declared ``10^15 W/cm^2`` bound. Craxton et al. state no
   single bound; they print an ignition design at 8 x 10^14 W/cm^2
   (Sec. III A, PDF p. 20) and stimulated Raman backscatter rising from
   about 8 % at 0.9 x 10^15 to about 36 % at 8 x 10^15 W/cm^2
   (PDF p. 296).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (drive/symmetry/burn diagnostic semantics with the
  bang-time anchor, safety envelope) build on these types; maturity
  advances per capability only with the evidence the family standard
  requires.

## Amendment 2026-10-31

The class invariants were credited to J. D. Lindl, Phys. Plasmas 2
(1995) 3933, and M. Tabak et al., Phys. Plasmas 1 (1994) 1626, neither
of which is on file; they are now bound to pages of the filed Craxton et
al. (2015) review. The text also said that laser-plasma instabilities
"dominate" above 10^15 W/cm^2 and credited that to Craxton et al.; the
review prints no such single bound, so the bound is named declared and
the printed values beside it are quoted. No invariant, value or check
changed.
