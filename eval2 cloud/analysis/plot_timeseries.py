#!/usr/bin/env python3
"""
Plot a time series recorded with scripts/collect-metrics.(ps1|sh).

Input : data/timeseries.csv   (or pass a path as the first argument)
Output: graphs/timeseries_pod_cpu.png, timeseries_pod_memory.png, timeseries_node.png

Usage:
    python analysis/plot_timeseries.py [path/to/timeseries.csv]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "timeseries.csv"
out = ROOT / "graphs"
out.mkdir(exist_ok=True)

df = pd.read_csv(src, parse_dates=["timestamp"])
if df.empty:
    sys.exit(f"{src} has no rows - run the collector while the cluster is up.")

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25})


def finish(ax, title, ylabel, path):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Time")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.legend(frameon=False)
    ax.figure.autofmt_xdate()
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=200)
    plt.close(ax.figure)
    print("wrote", path)


pods = df[df.scope == "pod"]
for col, title, ylabel, name in [
    ("cpu_millicores", "Pod CPU over time", "CPU (millicores)", "timeseries_pod_cpu.png"),
    ("memory_mib", "Pod memory over time", "Memory (MiB)", "timeseries_pod_memory.png"),
]:
    fig, ax = plt.subplots(figsize=(9, 5))
    for pod, g in pods.groupby("name"):
        ax.plot(g["timestamp"], g[col], marker="o", ms=3, label=pod)
    finish(ax, title, ylabel, out / name)

nodes = df[df.scope == "node"]
if not nodes.empty:
    fig, ax = plt.subplots(figsize=(9, 5))
    for node, g in nodes.groupby("name"):
        ax.plot(g["timestamp"], g["cpu_percent"], marker="o", ms=3, label=f"{node} CPU %")
        ax.plot(g["timestamp"], g["memory_percent"], marker="s", ms=3, label=f"{node} memory %")
    finish(ax, "Node utilisation over time", "Utilisation (%)", out / "timeseries_node.png")
