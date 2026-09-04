<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-ICF-LASER-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`LaserDriver`,
  `TargetDeclaration`, `DeviceConfiguration`) rejecting non-finite
  values, non-positive extents, and the hard drive-scheme class
  invariants: hohlraum required for indirect drive and forbidden for
  direct drive (Lindl, Phys. Plasmas 2 (1995) 3933), and the ignitor
  pulse exactly for fast/shock ignition (Tabak et al., Phys. Plasmas 1
  (1994) 1626) — every rejection branch is tested.
- The sphere-averaged on-target intensity `I = E / (tau 4 pi R^2)` as a
  documented derived quantity, with an advisory finding for direct-drive
  intensities above the documented laser-plasma-instability bound
  `1e15 W/cm^2` (Craxton et al., Phys. Plasmas 22 (2015) 110501),
  reported and never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not implosion, symmetry, or
  yield results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, unresolvable event-timing bounds,
  and incomplete candidate coverage — every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: beam-timing train, trajectory radiography, asymmetry mode set, shot-outcome set, synthetic oscillator, each bound to its clock domain.
- Documented advisory band and timing checks with their sources stated
  in the code: implosion-asymmetry bands of 1 MHz–10 GHz and tens-of-ps beam timing (Lindl 1995); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_icf_laser_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; a `timing_marker` in `"s"` exactly for
  event-relative channels and forbidden otherwise; numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The hot-spot ignition condition in the four equivalent forms a filed
  review prints: the floors on hot-spot areal density and ion
  temperature; the pressure floor that falls with hot-spot radius; the
  pressure floor in terms of the shell kinetic energy coupled into the
  hot spot; and the energy relation `f_k E_k = 2 pi P_hs R_hs^3` that
  carries one into the other.
- The definitions a one-dimensional design is quoted by — the DT shell
  adiabat, the in-flight aspect ratio with the evaluation point the
  review fixes, the convergence ratio, and the hydrodynamic efficiency
  against absorbed rather than incident energy.
- The fuel inventory of a declared capsule layering, the yield at a
  declared burnup fraction, and the target gain against incident energy.
- A composed record that builds the capsule's initial inner radius from
  the configuration's outer radius and the declared thicknesses, and
  refuses a layering that does not fit inside it.
- Every declared quantity validated where it is declared as well as
  inside the relation that consumes it, so a record can never be built
  from a set the relations would have refused one at a time.
- Canonical serialisation (sorted keys, NaN/infinity rejected) and
  SHA-256 digest identity of the record.

Anchors — printed values reproduced, and nothing further:

- The 40-micrometre coefficient of the radius ceiling, recovered exactly
  — as the same IEEE double — from the two printed pressure
  coefficients and the printed reference radius.
- Each of the two pressure relations reproducing its own coefficient at
  its own reference point.
- The design's initial inner radius and its aspect-ratio evaluation
  point, both exact from three printed lengths, the second despite two
  thirds not being exact in binary.
- The absorbed energy of the design, 95 % of 1.5 MJ, exact at 1425 kJ.
- The printed hydrodynamic efficiency and absorbed fraction reproducing
  the printed shell kinetic energy to the one significant figure it is
  stated with.

Measured, rather than assumed:

- The three printed ignition coefficients close on the energy relation
  0.53 % high, by the same relative amount at every energy from 1 kJ to
  1 MJ. That is the rounding of the printed coefficients; the test
  asserts the measured offset, not an equality.
- The pressure coefficient computed from the review's own ignition
  floors is 115 Gbar where it prints 100 Gbar. The implementation
  carries the printed value; a test carries the arithmetic.

Not reproduced — recorded as tests so they stay visible:

- The review's worked example of its own energy-form pressure floor
  states "120 to 180 Gbar"; the equation at the stated inputs gives 112
  to 125 Gbar. The upper figure is not produced by any coupled fraction
  in the stated range.
- The review's one-dimensional gain of 48 is not recovered from its
  printed geometry at its printed burnup fraction with solid fuel at
  standard density; that reconstruction gives about 57. The gap is
  physical, not arithmetic: a quoted burnup fraction applies to the fuel
  that assembles and burns. **Neither figure is used as an anchor**, and
  nothing was adjusted to make them meet.

Bounded claims — what is NOT claimed:

- No radiation hydrodynamics, transport, laser-plasma-interaction or
  burn calculation is performed anywhere in this package.
- The capsule layering, the in-flight shell state and the burnup
  fraction are declared inputs.
- The ignition floors are necessary algebraic conditions on a design,
  never a prediction that a design ignites.
- The convergence ratio's definition carries a condition on how its
  input is computed — alpha-particle deposition switched off — that no
  code here can enforce.
- The solid-fuel density used in the fuel-inventory tests is a standard
  value the filed review does not print, and the fixtures say so.
- No value describes, approximates or validates any real machine or
  shot; an anchor reproduces a number a filed source prints and nothing
  further.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`; consumer contract:
`docs/DEVICE_3D_MODEL_CONTRACT.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The body set of each owned configuration, in its fixed order: three
  concentric capsule bodies for the two directly driven identifiers, and
  those three plus the radiation enclosure for the indirect-drive one.
- The enclosure required for `laser_icf_indirect_drive` and refused for
  the two directly driven identifiers, both directions refusing rather
  than defaulting.
- An enclosure the capsule does not fit inside refused in the direction
  it is wrong, naming the field and both values: a case no wider than
  the capsule, and a case no longer than the capsule's diameter.
- A layering that leaves no cavity refused by the level-0 relation
  itself, so this tier cannot draw a capsule the physics record would
  have rejected.
- The single conversion from the micrometres the configuration and the
  capsule declaration carry to the metres the bodies are built in.
- Canonical serialisation and SHA-256 digest identity of the model
  record, including the digests of the configuration, the capsule
  declaration and the enclosure it was built from.

Anchors — printed values reproduced, and nothing further:

- The capsule's printed outer radius, and the outer radius of each
  layer, read off the built bodies as exact equalities. The sphere
  profile places a vertex at exactly the centre plus the radius, and the
  capsule is centred on the origin.
- The printed case-to-capsule radius ratio of 4 to 1, recovered exactly
  from the built solids: the smallest distance from the axis to any
  vertex of the enclosure, over the ablator shell's pole.
- The printed hohlraum area band of 15 to 25 times the initial capsule
  area, measured at 20.5 from the bodies actually built. The capsule's
  outer area comes out of the three recorded body areas by an identity,
  each shell recording the sum of its two surfaces; the enclosure's
  interior area is its inner perimeter times its built length, which is
  the lateral wall alone and therefore a lower bound on the enclosing
  surface the printed statement describes.

Measured, rather than assumed:

- The printed ablator thickness does **not** return exactly from the
  built bodies. The layer arithmetic is exact in micrometres — 1700,
  1663 and 1503 are integers — and the conversion to metres introduces
  the rounding, so the recovered value is 36.99999999999992, or 2.1e-15
  relative. The test carries a measured bound and states why. The fuel
  thickness, on the same arithmetic, returns exactly 160.
- Swapping the two resolutions builds a different body and no gate
  downstream would notice, so a test asserts the difference.

Boundaries:

- The enclosure's anchors come from a **related public precursor** of
  the cited indirect-drive work, filed and labelled as a substitute
  because the cited work is behind a subscription.
- The enclosure's wall thickness is declared; no source is claimed for
  it.
- Every body is an inscribed polyhedron of revolution. Comparing any
  volume here to `4/3 pi r^3` compares two different solids.

## Device CAD model

Evidence record of the `device_cad_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`). The tier is behind the
optional `cad` extra; two CI jobs install it.

What is exercised, all under the same coverage gate:

- The same body set and the same order as tier G1, for both drive
  classes.
- The library's fail-closed evidence on every body: the back-end's
  volume and area against the analytic closed forms, the faceted volume
  against the declared chord-deficit bound, and the faceted volume
  against the tier-G1 mesh of the same body.
- The assembly manifest, the normalised STEP bytes and their digest, and
  the pinned back-end versions.
- Refusals: an unknown identifier, a manifest of the wrong schema, a
  manifest counting the wrong number of bodies, a body set in the wrong
  order, and an invalid deflection arriving as this package's own error
  type.

Measured, and recorded because it does not transfer from the
metre-scale families:

- **The ring count has a ceiling set by the back-end.** Up to 32 rings
  the revolved solid's volume agrees with the analytic frustum stack to
  7e-15 relative; at 48 rings it disagrees by 3.5e-5, at 64 by 1.5e-5
  and at 128 by 6.5e-5, thousands of times the library's 1e-9 measure
  tolerance and not converging. The boundary is where the shortest
  generating segment falls below about 5e-6 m. Cylindrical bodies are
  unaffected. Nothing was loosened: the evidence kernel refused the
  first build, and a test asserts that refusal at 48 rings.
- **The angular deflection does not bind at this scale.** Between 0.5
  and 0.1 radians every body's deficit is identical to four significant
  figures.
- **The linear deflection buys a bound, not accuracy.** 2e-7 m is the
  tightest bound the bodies clear — the vapour core sits at 0.57 of its
  bound — and at 1e-7 m the vapour core exceeds its bound by fifteen per
  cent, which a test asserts. At 1e-8 m the back-end refuses outright.
- The deficit bound of each body uses that body's **outer** radius,
  which is the tightest bound a body of revolution admits; a sphere's
  circles run to zero at the poles and would make the bound unbounded.

Boundaries:

- Determinism of the STEP bytes is claimed within one pinned back-end
  environment only, never across back-end versions.
- No body is an engineering model and no fabrication tolerance is
  carried.
