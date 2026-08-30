<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)  
**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The `inertial` registry family spans
laser, beam, and impact drivers; a boundary decision was needed on which
drive schemes share one repository.

## Decision

1. `SCPN-ICF-LASER-CORE` owns exactly three registry configurations:
   `laser_icf_direct_drive`, `laser_icf_indirect_drive`, and
   `laser_icf_fast_or_shock_ignition`. All three implode a capsule with
   laser energy and share implosion hydrodynamics, instability budgets,
   laser-plasma-interaction constraints, target metrology, shot-cycle
   lifecycle, and diagnostics; the coupling path (direct ablation, hohlraum
   X-ray bath, staged igniter or late shock) is the configuration
   parameter.
2. The repository owns device-level truth only: drive-scheme configuration
   policy, pulse-shaping and symmetry-control declarations, target and
   capsule metrology contracts, shot-cycle lifecycle semantics,
   symmetry/burn diagnostic and clock declarations, actuator-response
   model boundaries, the safety-envelope declaration, and the device-owned
   CONTROL adapter specification.
3. Solver mathematics — implosion hydrodynamics, radiation transport, burn
   physics — remains in `SCPN-FUSION-CORE` until an exact surface passes
   the family migration gate. No solver code is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One repository for all inertial configurations** (laser + beam +
  impact): rejected — the driver and energy-delivery surface differs
  fundamentally (laser optics and laser-plasma interaction versus
  accelerator transport versus hypervelocity launchers), which drags
  lifecycle, diagnostics, and hazard structure apart (surfaces 2–4).
- **Separate repositories per laser scheme** (direct, indirect, staged):
  rejected — all five boundary surfaces are substantially shared; the
  split would triplicate every contract for a coupling-path difference.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity per laser-ICF configuration
  and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
