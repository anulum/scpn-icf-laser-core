<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Laser Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (lengths in µm, densities in g/cm³,
pressures in Gbar and Mbar, energies in kJ and MJ):

| Module | Kernels | Operations |
|---|---|---|
| `physics/ignition.py` | ignition floors (Eq. 3-5), DT pressure, pressure for a radius (Eq. 3-6), pressure floor (Eq. 3-7), radius ceiling (Eq. 3-8), hot-spot energy `2 pi P R^3` | `* /`, `sqrt`, `pi`, **`pow`** (cube) |
| `physics/implosion.py` | DT adiabat `P / (2.2 rho^(5/3))`, IFAR, convergence ratio, absorbed energy, hydrodynamic efficiency | `* / -`, **`pow`** (real power 5/3) |
| `physics/yield_and_gain.py` | D-T specific energy, spherical shell mass `4/3 pi (R^3 - r^3) rho`, yield, gain | `* / -`, `pi`, **`pow`** (cubes) |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. The square root is correctly rounded by IEEE-754; `pow` (the
cubes and the real power 5/3) is the platform's, which the standard does
not require to be correctly rounded. A native backend that must agree bit
for bit would have to use one deterministic power on both sides. The
constants and their editions are documented in the physics modules and
bound by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-icf-laser-core.level0-physics-benchmark.v1`, generated 2026-10-31T04:11:34.192275+00:00, at commit
`32b935deb5db` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 2.56 (other sessions were active on the host);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (hot-spot, adiabat, aspect-ratio, shell-mass and yield closed forms per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.503 | 1.562 | 2.145 | 1.512 | 665253 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 31.980 | 36.092 | 37.361 | 31.943 | 31269 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
