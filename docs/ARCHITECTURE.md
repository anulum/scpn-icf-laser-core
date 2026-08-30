<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-ICF-LASER-CORE` is the device-family owner for laser-driven inertial
confinement fusion systems in the SCPN Reactor Systems Research Group
portfolio. The repository is `architecture_only`: every section below
describes boundaries and contracts, not implemented capability. The
capability and claim inventories are empty; both derived artefacts are
generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — inertial confinement of a
   spherically imploded capsule (`inertial` registry family) with laser
   energy as the driver. The three owned configurations span the family's
   drive-scheme space on shared physics: `laser_icf_direct_drive`
   (capsule ablation directly by beam illumination, symmetry set by beam
   geometry and imprint), `laser_icf_indirect_drive` (capsule driven by
   the X-ray bath of a laser-heated hohlraum, symmetry set by hohlraum
   radiation transport), and `laser_icf_fast_or_shock_ignition` (staged
   separation of compression and ignition — a short-pulse relativistic
   igniter or a late strong shock). All three share implosion
   hydrodynamics, hot-spot formation, hydrodynamic-instability budgets
   (Rayleigh–Taylor/Richtmyer–Meshkov), laser-plasma-interaction
   constraints, and shot-cycle lifecycle; the coupling path is the
   configuration parameter. Beam-driven ICF (ion/electron drivers),
   projectile impact, and magnetised liner implosion fail this sharing
   test and are excluded.
2. **Primary driver and energy delivery** — multi-beam high-energy laser
   systems with pulse shaping, frequency conversion, beam smoothing, and
   power balance; short-pulse petawatt-class systems as the fast-ignition
   stage where configured.
3. **Plant and shot lifecycle** — discrete shot-cycle lifecycle: target
   and capsule metrology acceptance, target insertion and alignment
   (including cryogenic layering where declared), laser charge, shot,
   implosion and burn window, and post-shot data acquisition with chamber
   recovery. Device-level hazard semantics cover optics damage, target
   misalignment, and pulse-shape non-conformance.
4. **Diagnostic, reference-frame, and clock model** — target-chamber
   coordinate conventions, drive-symmetry and implosion diagnostics
   (backscatter, velocity, shape), burn diagnostics (neutron yield,
   ion-temperature proxies, bang time as timing anchor), and
   picosecond-to-nanosecond shot-relative clock identities.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-ICF-LASER-CORE (device truth: drive-scheme policy, shot-cycle
                     lifecycle, symmetry/burn diagnostics, safety
                     envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
