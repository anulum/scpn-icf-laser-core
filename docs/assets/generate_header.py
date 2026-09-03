# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Laser Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the direct-drive sphere under its symmetric beam
set, the three owned drive schemes with their hard class invariants,
and the laser-plasma-instability intensity gate. The right-hand text
panel states only facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the direct-drive target under converging beams
  (used by ``README.md``).
- ``repo_header_drive_schemes.png`` — direct, indirect and fast/shock
  ignition side by side.
- ``repo_header_lpi_bound.png`` — the shaped pulse under the
  documented laser-plasma-instability bound.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GOLD = "#ffcc55"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configurations", "direct · indirect · fast/shock"),
    ("Hohlraum Invariant", "separates indirect (Lindl, PoP 1995)"),
    ("Ignitor Invariant", "defines fast/shock (Tabak, PoP 1994)"),
    ("LPI Bound", "direct intensity flagged (Craxton 2015)"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "ICF LASER",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _target_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
    levels: int = 30,
) -> None:
    """Draw a glowing spherical target."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 140)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 140)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=levels,
        cmap=_glow_cmap(),
        alpha=0.95,
    )


def generate_direct_drive() -> None:
    """Generate ``repo_header.png``: the direct-drive sphere."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    _target_glow(ax, 0.0, 0.0, 0.42, 1.15)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    ax.plot(
        0.42 * np.cos(theta),
        0.42 * np.sin(theta),
        color=CYAN,
        lw=1.9,
        alpha=0.95,
    )
    ax.plot(
        0.62 * np.cos(theta),
        0.62 * np.sin(theta),
        color=PROBE,
        lw=0.7,
        alpha=0.45,
    )

    beam_count = 12
    for index in range(beam_count):
        angle = 2.0 * np.pi * index / beam_count + np.pi / beam_count
        outer = (2.75 * np.cos(angle), 1.38 * np.sin(angle))
        inner = (0.72 * np.cos(angle), 0.72 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={
                "arrowstyle": "-|>",
                "color": GOLD,
                "lw": 1.6,
                "alpha": 0.8,
                "mutation_scale": 10,
            },
        )
    ax.text(
        -2.75,
        1.3,
        "symmetric beam set",
        color=GOLD,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    ax.annotate(
        "",
        xy=(0.30, 0.30),
        xytext=(0.58, 0.58),
        arrowprops={"arrowstyle": "->", "color": "white", "lw": 1.1, "alpha": 0.7},
    )
    ax.text(
        0.66,
        0.66,
        "ablation drive",
        color="white",
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.8,
    )
    ax.text(
        0,
        -0.78,
        "spherical implosion",
        color=PROBE,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        0,
        -1.36,
        "laser_icf_direct_drive · uniform illumination, declared symmetry",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Light Becomes Pressure")
    _save(fig, plt, "repo_header.png")


def generate_drive_schemes() -> None:
    """Generate ``repo_header_drive_schemes.png``: the three schemes."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    centre = 1.8
    _target_glow(ax, centre, 0.35, 0.30, 0.85)
    ax.plot(
        centre + 0.30 * np.cos(theta),
        0.35 + 0.30 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    for index in range(8):
        angle = 2.0 * np.pi * index / 8 + np.pi / 8
        outer = (centre + 1.35 * np.cos(angle), 0.35 + 1.35 * np.sin(angle))
        inner = (centre + 0.52 * np.cos(angle), 0.35 + 0.52 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={
                "arrowstyle": "-|>",
                "color": GOLD,
                "lw": 1.2,
                "alpha": 0.8,
                "mutation_scale": 8,
            },
        )
    ax.text(
        centre,
        2.15,
        "direct drive",
        color="#99bbdd",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        -2.0,
        "beams on capsule",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    centre = 5.0
    ax.add_patch(
        plt.Rectangle(
            (centre - 0.55, -0.75),
            1.1,
            2.2,
            fill=False,
            ec=GOLD,
            lw=1.8,
            alpha=0.9,
        )
    )
    _target_glow(ax, centre, 0.35, 0.22, 0.5)
    ax.plot(
        centre + 0.22 * np.cos(theta),
        0.35 + 0.22 * np.sin(theta),
        color=CYAN,
        lw=1.4,
        alpha=0.95,
    )
    for sign in (+1, -1):
        for offset in (-0.25, 0.25):
            ax.annotate(
                "",
                xy=(centre + offset * 0.7, 0.35 + sign * 0.95),
                xytext=(centre + offset, 0.35 + sign * 1.9),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": GOLD,
                    "lw": 1.2,
                    "alpha": 0.8,
                    "mutation_scale": 8,
                },
            )
    ax.text(
        centre,
        2.15,
        "indirect drive",
        color="#99bbdd",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        -2.0,
        "hohlraum X-ray bath · Lindl 1995",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    centre = 8.2
    _target_glow(ax, centre, 0.35, 0.26, 0.7)
    ax.plot(
        centre + 0.26 * np.cos(theta),
        0.35 + 0.26 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    for index in range(6):
        angle = 2.0 * np.pi * index / 6 + np.pi / 6
        outer = (centre + 1.1 * np.cos(angle), 0.35 + 1.1 * np.sin(angle))
        inner = (centre + 0.45 * np.cos(angle), 0.35 + 0.45 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={
                "arrowstyle": "-|>",
                "color": GOLD,
                "lw": 0.9,
                "alpha": 0.55,
                "mutation_scale": 7,
            },
        )
    ax.annotate(
        "",
        xy=(centre - 0.28, 0.35),
        xytext=(centre - 1.5, 0.35),
        arrowprops={
            "arrowstyle": "-|>",
            "color": MAGENTA,
            "lw": 2.4,
            "alpha": 0.95,
            "mutation_scale": 13,
        },
    )
    ax.text(
        centre - 0.9,
        0.72,
        "ignitor pulse",
        color=MAGENTA,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        2.15,
        "fast / shock ignition",
        color="#99bbdd",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        -2.0,
        "staged drive · Tabak 1994",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    for divider_x in (3.4, 6.6):
        ax.plot(
            [divider_x, divider_x],
            [-1.7, 1.9],
            color=STEEL,
            lw=0.8,
            alpha=0.4,
        )
    ax.text(
        5.0,
        -2.85,
        "three identifiers, hard class invariants",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Three Drive Schemes, One Owner")
    _save(fig, plt, "repo_header_drive_schemes.png")


def generate_lpi_bound() -> None:
    """Generate ``repo_header_lpi_bound.png``: the intensity gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "pulse time",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.85,
        "on-target intensity",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    y_bound = 7.3
    ax.plot(
        [1.0, 9.0],
        [y_bound, y_bound],
        color=RED,
        lw=1.8,
        alpha=0.9,
        ls=(0, (6, 3)),
    )
    ax.text(
        8.9,
        y_bound + 0.3,
        "documented LPI bound",
        color=RED,
        fontsize=8.5,
        fontfamily="monospace",
        ha="right",
        alpha=0.95,
    )
    ax.fill_between([1.0, 9.0], y_bound, 9.0, color=RED, alpha=0.06)
    ax.text(
        5.0,
        8.35,
        "flagged for direct drive",
        color="#ff8899",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    time = np.linspace(0.0, 1.0, 400)
    pulse = (
        1.9
        + 0.7 * (time > 0.15)
        + 0.9 * (time > 0.45)
        + 2.4 * np.exp(-(((time - 0.83) / 0.09) ** 2))
    )
    px = 1.0 + 8.0 * time
    ax.plot(px, pulse, color=CYAN, lw=2.4, alpha=0.95)
    ax.fill_between(px, pulse, 1.7, color=CYAN, alpha=0.06)
    ax.text(
        2.4,
        3.0,
        "foot",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        7.65,
        5.7,
        "main drive",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        0.75,
        "declared pulse checked against the documented bound · "
        "Craxton et al., PoP 22 (2015) 110501",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Intensity Under A Documented Bound")
    _save(fig, plt, "repo_header_lpi_bound.png")


if __name__ == "__main__":
    generate_direct_drive()
    generate_drive_schemes()
    generate_lpi_bound()
