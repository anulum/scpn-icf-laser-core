<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — CHANGELOG
-->

# Changelog

## [Unreleased]

### Fixed

- Tier-G2 ring count raised from 32 to 39, the top of the regime where
  every count is exact on this family's bodies, with the tier-G1 anchor
  following it so both tiers share one resolution. The refusal test now
  asserts 40 rings, the back-end's first refusal and the step
  immediately above the default, instead of 48.
- Withdrawn from ADR 0006, `docs/DEVICE_3D_MODEL_CONTRACT.md` and
  `VALIDATION.md`: the statement that 32 rings is the ceiling, and the
  statement that the boundary sits where the shortest generating segment
  falls below about 5e-6 m. Neither was measured. No single length is
  constant where the refusals begin — the shortest generating segment
  there runs from 9.2e-5 m to 2.7e-4 m across radii — and where they
  begin is a function of the body's radius, the first refusal falling at
  34 rings for 1.0 mm and 58 for 5.0 mm.
- The ring-count behaviour restated from a scan of every count from 30
  to 75 rather than from its endpoints: counts to 39 are all exact, 40
  to 61 alternate with every even count refusing and every odd count
  exact, and 62 and above all refuse. An even count places exactly one
  profile sample on the equator and an odd count places none, which the
  record states as a measured correlation and not as a cause. The
  default stays at the top of the first regime. ADR 0006 carries a dated
  correction subsection recording both rounds of what was withdrawn.
- Measured percentages corrected where the ring count moved them: the
  vapour core sits at 0.56 of its deficit bound, and exceeds it by 13 %
  at the next tighter linear deflection.
- Withdrawn: the statement that 2e-7 m is the tightest linear deflection
  the bodies clear. It held only against the four-value ladder that was
  tested; 1.2e-7 m clears as well. The faceted volume deficit is now
  measured to be independent of the deflection — 1.502834e-4 across six
  values — so the threshold is exact at `deficit * r / 2` = 1.12938e-7 m,
  with 1.13e-7 m building and 1.12e-7 m refused. The declared 2e-7 m is
  restated as a margin over that threshold. Two new tests assert the
  independence and compute the threshold from the built model.

### Added

- Diagnostic-plan depth: per-channel signal inventories, frame
  transformations with a fixed kind-admissibility table and connectivity
  rule, and a clock topology partitioning the physical clocks into rooted
  domains with a star of relations to the reference root. Envelope
  `scpn.reactor-diagnostic-plan-envelope.v1` bumped to `1.2.0`; the
  fixture is regenerated from the public surface and re-pinned. All new
  members are declarations: no observation, phase, mapping, or control
  authority is created.
- Local gate parity with the wider ecosystem: the pre-commit chain now
  also runs REUSE licensing compliance and a typographical checker
  (`_typos.toml` carries the deliberate reactor vocabulary), and adds
  the upstream YAML, TOML, large-file and private-key guards. Licensing
  and spelling were previously verified only in hosted CI, so a broken
  REUSE annotation — including the aggregate annotation that covers the
  binary header images — could reach a push before being caught.
- Generated repository header artwork: `docs/assets/generate_header.py`
  renders three deterministic 1280x640 images from the repository's own
  domain surface (the direct-drive sphere used by the README, the three
  owned drive schemes, and the laser-plasma-instability gate).
- Modular hosted-workflow surface per the ecosystem workflow-modularity
  standard: `ci.yml` reduced to a coordinator with a stable fail-closed
  `gate` job, single-responsibility reusable workflows for static
  analysis/repository policy and for tests, a versioned machine-readable
  inventory (`.github/workflow-inventory.json`,
  `scpn.workflow-inventory.v1` `1.0.0`), and a fail-closed modularity
  guard (`tools/audit_workflows.py`) enforced locally (preflight gate,
  pre-commit hook) and in hosted CI. The duplicate documentation-links
  step was removed from the CI chain; `docs.yml` remains the single
  owner of documentation validation.

- Typed reference frames, clock synchronisation relations (synthetic
  bounds only; no correlation evidence claimed), and per-channel
  acquisition windows and element counts in the diagnostic model;
  hardened decoders (recursive exact-key, duplicate-member, and
  byte-canonical refusal in both codecs); envelope `1.1.0` adding
  `manifest_sha256` over the committed canonical `reactor-domain.json`
  (fixture regenerated; byte hash re-pinned in tests).

- Portable diagnostic-plan envelope
  (`src/scpn_icf_laser_core/plan_envelope.py`,
  `scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): a
  producer-owned, canonically serialised wrapper carrying project
  identity, exact owned configurations, capability and maturity,
  synthetic/review-only/non-actuating statements, both SPO registry
  pins, the inner plan's SHA-256, the producer revision, and fixed
  no-observation/no-control non-claims; strict parsers refuse unknown,
  duplicate, and non-finite members, and an immutable committed fixture
  exercises the exchange end to end.

- Diagnostic and clock semantics model
  (`src/scpn_icf_laser_core/observability.py`), the second implemented
  capability at `computational_prototype`: frozen clock, channel,
  deferral, and plan objects aligned fail-closed with the pinned SPO
  observability-profile catalogue (candidate applicability, carrier
  admissibility, exact class-fixed evidence vocabularies, clock-kind
  compatibility, Nyquist and event-timing bounds); cited advisory band
  and timing checks; canonical serialisation with SHA-256 digests and
  strict NaN-rejecting round-trip parsing (design record
  `docs/adr/0003-diagnostic-clock-semantics.md`).

- Device configuration model (`src/scpn_icf_laser_core/`), the first implemented
  capability at `computational_prototype`: validated frozen parameter
  objects with device-specific invariants and documented, cited
  consistency estimates; canonical serialisation with SHA-256 digests
  and strict NaN-rejecting round-trip parsing; a data-only pin to the
  SPO reactor registry; and the reactor-domain validator branch
  enforcing populated capability inventories with the ADR 0002
  evidence-maturity ceiling rule (design record
  `docs/adr/0002-device-configuration-model.md`).

- Architecture-only repository scaffold: governance, security, licensing,
  REUSE metadata, contribution and support policies, and citation metadata.
- Machine-readable domain manifest `reactor-domain.json` binding the project
  to SCPN Phase Orchestrator reactor registry `1.0.0`
  (configurations `laser_icf_direct_drive`,
  `laser_icf_fast_or_shock_ignition`, `laser_icf_indirect_drive`).
- Device-owned CONTROL adapter specification and threat model.
- Derived Studio portfolio descriptor (`not_federated`) and generated
  capability inventory (zero implemented capabilities).
- Validation tooling: domain-manifest validator, descriptor derivation and
  inventory generation with drift checks, and a fail-closed preflight
  orchestrator, each with statement- and branch-complete tests.
- Continuous-integration, code-scanning, security-audit, documentation,
  SBOM, pre-commit, and Scorecard workflow definitions (read-only
  permissions; no publication or deployment workflows).

### Changed

- Studio portfolio descriptor schema ratified at version 1.1.0 after
  downstream review, before any consumer adoption (1.0.0 superseded
  unconsumed): canonical JSON Schema published in-repository with a strict
  unknown-field policy, explicit source repository, nullable lifecycle
  evidence pointer, nullable versioned control-intent reference, ratified
  capability item shape, and a machine-protection object (independent
  final-veto owner with availability `not_assessed`) replacing the former
  boolean flag.
