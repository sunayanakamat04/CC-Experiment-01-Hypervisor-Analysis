#!/usr/bin/env python3
"""
Generate every graph used in the report from the recorded measurements.

Inputs  (relative to the repo root):
    data/results.csv               idle vs. load summary (kubectl top + Dashboard)
    data/readings_under_load.csv   successive kubectl top readings

Outputs:
    graphs/*.png                   one file per graph + graphs/00_summary.png

Usage:
    pip install -r analysis/requirements.txt
    python analysis/plot_results.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "graphs"
OUT.mkdir(exist_ok=True)

# Resource settings from manifests/php-apache.yaml
CPU_REQUEST_M, CPU_LIMIT_M = 100, 500
MEM_REQUEST_MI, MEM_LIMIT_MI = 64, 128

# Palette
C_TOP = "#D98E04"     # kubectl top
C_DASH = "#1F9D6B"    # Dashboard
C_LIMIT = "#D93A40"
C_REQ = "#6B7280"
C_NODE_CPU = "#7C5CE0"
C_NODE_MEM = "#0E7490"
C_LOADGEN = "#9CA3AF"

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.axisbelow": True,
    "figure.facecolor": "white",
})

results = pd.read_csv(DATA / "results.csv")
readings = pd.read_csv(DATA / "readings_under_load.csv")


def val(stage, source, col):
    row = results[(results.stage == stage) & (results.source == source)]
    return float(row[col].iloc[0])


def grouped_bars(ax, top_vals, dash_vals, fmt="{:g}"):
    labels = ["Idle", "Under load"]
    x = range(len(labels))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], top_vals, w, color=C_TOP, label="kubectl top")
    b2 = ax.bar([i + w / 2 for i in x], dash_vals, w, color=C_DASH, label="Dashboard")
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(fmt.format(b.get_height()), (b.get_x() + b.get_width() / 2, b.get_height()),
                        ha="center", va="bottom", fontsize=10, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)


# ---------------------------------------------------------------- graph 1
def g_pod_cpu(ax):
    grouped_bars(
        ax,
        [val("idle", "kubectl_top", "pod_cpu_m"), val("load", "kubectl_top", "pod_cpu_m")],
        [val("idle", "dashboard", "pod_cpu_m"), val("load", "dashboard", "pod_cpu_m")],
    )
    ax.axhline(CPU_LIMIT_M, color=C_LIMIT, ls="--", lw=1.4)
    ax.axhline(CPU_REQUEST_M, color=C_REQ, ls=":", lw=1.4)
    ax.set_xlim(-0.7, 1.6)
    ax.text(-0.68, CPU_LIMIT_M + 10, f"limit {CPU_LIMIT_M}m", color=C_LIMIT, fontsize=10)
    ax.text(-0.68, CPU_REQUEST_M + 10, f"request {CPU_REQUEST_M}m", color=C_REQ, fontsize=10)
    ax.set_ylim(0, 680)
    ax.set_ylabel("CPU (millicores)")
    ax.set_title("Pod CPU: idle vs under load (php-apache)")
    ax.legend(loc="upper left", ncol=2, frameon=False)


# ---------------------------------------------------------------- graph 2
def g_pod_mem(ax):
    grouped_bars(
        ax,
        [val("idle", "kubectl_top", "pod_mem_mi"), val("load", "kubectl_top", "pod_mem_mi")],
        [val("idle", "dashboard", "pod_mem_mi"), val("load", "dashboard", "pod_mem_mi")],
    )
    ax.axhline(MEM_LIMIT_MI, color=C_LIMIT, ls="--", lw=1.4)
    ax.axhline(MEM_REQUEST_MI, color=C_REQ, ls=":", lw=1.4)
    ax.set_xlim(-0.7, 1.6)
    ax.text(-0.68, MEM_LIMIT_MI + 3, f"limit {MEM_LIMIT_MI}Mi", color=C_LIMIT, fontsize=10)
    ax.text(-0.68, MEM_REQUEST_MI + 3, f"request {MEM_REQUEST_MI}Mi", color=C_REQ, fontsize=10)
    ax.set_ylim(0, 175)
    ax.set_ylabel("Memory (MiB)")
    ax.set_title("Pod memory: idle vs under load (php-apache)")
    ax.legend(loc="upper left", ncol=2, frameon=False)


# ---------------------------------------------------------------- graph 3
def g_node(ax):
    labels = ["Idle", "Under load"]
    cpu = [val("idle", "kubectl_top", "node_cpu_pct"), val("load", "kubectl_top", "node_cpu_pct")]
    mem = [val("idle", "kubectl_top", "node_mem_pct"), val("load", "kubectl_top", "node_mem_pct")]
    x = range(2)
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], cpu, w, color=C_NODE_CPU, label="Node CPU %")
    b2 = ax.bar([i + w / 2 for i in x], mem, w, color=C_NODE_MEM, label="Node memory %")
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(f"{b.get_height():g}%", (b.get_x() + b.get_width() / 2, b.get_height()),
                        ha="center", va="bottom", fontsize=10, xytext=(0, 3), textcoords="offset points")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Utilisation (%)")
    ax.set_title("Node utilisation barely changes (minikube node)")
    ax.legend(loc="upper left", frameon=False)


# ---------------------------------------------------------------- graph 4
def g_plateau(ax):
    x = readings["label"]
    ax.plot(x, readings["pod_cpu_m"], marker="o", lw=2.2, color=C_TOP, label="php-apache (kubectl top)")
    ax.plot(x, readings["loadgen_cpu_m"], marker="s", lw=1.8, color=C_LOADGEN, label="load-generator (kubectl top)")
    ax.axhline(CPU_LIMIT_M, color=C_LIMIT, ls="--", lw=1.4)
    ax.text(0.02, CPU_LIMIT_M + 10, f"CPU limit {CPU_LIMIT_M}m", color=C_LIMIT, fontsize=10)
    for xi, yi in zip(x, readings["pod_cpu_m"]):
        ax.annotate(f"{yi:g}m", (xi, yi), ha="center", va="bottom", fontsize=10, xytext=(0, 6), textcoords="offset points")
    ax.set_ylim(0, 600)
    ax.set_ylabel("CPU (millicores)")
    ax.set_title("Pod CPU rises, then plateaus at the limit")
    ax.legend(loc="center right", frameon=False)
    ax.text(0.5, -0.22, "Successive manual readings, not evenly spaced in time",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555")


# ---------------------------------------------------------------- graph 5
def g_req_limit(ax):
    names = ["Usage, idle", "CPU request", "CPU limit", "Usage, under load"]
    vals = [val("idle", "kubectl_top", "pod_cpu_m"), CPU_REQUEST_M, CPU_LIMIT_M, val("load", "kubectl_top", "pod_cpu_m")]
    colors = [C_DASH, C_REQ, C_LIMIT, C_TOP]
    bars = ax.barh(names, vals, color=colors, height=0.55)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:g}m", (v, b.get_y() + b.get_height() / 2), va="center", xytext=(6, 0), textcoords="offset points")
    ax.invert_yaxis()
    ax.set_xlim(0, 600)
    ax.set_xlabel("CPU (millicores)")
    ax.set_title("Observed CPU vs configured request and limit")
    ax.grid(axis="y", visible=False)


# ---------------------------------------------------------------- graph 6
def g_agreement(ax):
    items = [
        ("CPU idle", abs(val("idle", "dashboard", "pod_cpu_m") - val("idle", "kubectl_top", "pod_cpu_m")), "m"),
        ("CPU load", abs(val("load", "dashboard", "pod_cpu_m") - val("load", "kubectl_top", "pod_cpu_m")), "m"),
        ("Memory idle", abs(val("idle", "dashboard", "pod_mem_mi") - val("idle", "kubectl_top", "pod_mem_mi")), "Mi"),
        ("Memory load", abs(val("load", "dashboard", "pod_mem_mi") - val("load", "kubectl_top", "pod_mem_mi")), "Mi"),
    ]
    names = [i[0] for i in items]
    vals = [i[1] for i in items]
    colors = [C_TOP if "CPU" in n else C_DASH for n in names]
    bars = ax.bar(names, vals, color=colors, width=0.55)
    for b, (n, v, u) in zip(bars, items):
        ax.annotate(f"{v:.2f}{u}", (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom",
                    xytext=(0, 3), textcoords="offset points", fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_ylabel("|Dashboard - kubectl top|  (m or Mi)")
    ax.set_title("Dashboard vs kubectl top: absolute difference")
    ax.text(0.5, -0.2, "Differences come from sampling time; CPU under load is identical (501m)",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555")


GRAPHS = [
    ("01_pod_cpu_idle_vs_load.png", g_pod_cpu),
    ("02_pod_memory_idle_vs_load.png", g_pod_mem),
    ("03_node_utilisation.png", g_node),
    ("04_pod_cpu_plateau.png", g_plateau),
    ("05_cpu_usage_vs_request_limit.png", g_req_limit),
    ("06_tool_agreement.png", g_agreement),
]

for fname, fn in GRAPHS:
    fig, ax = plt.subplots(figsize=(8, 5))
    fn(ax)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=200)
    plt.close(fig)
    print("wrote", OUT / fname)

# Combined overview sheet
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for ax, (_, fn) in zip(axes.flat, GRAPHS):
    fn(ax)
fig.suptitle("Cluster monitoring with Metrics Server and Dashboard - summary of results", fontsize=16, y=0.995)
fig.tight_layout()
fig.savefig(OUT / "00_summary.png", dpi=150)
plt.close(fig)
print("wrote", OUT / "00_summary.png")
