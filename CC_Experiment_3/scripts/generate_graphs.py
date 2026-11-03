import os
import matplotlib.pyplot as plt
import numpy as np

# Set clean aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 11

output_dir = r"C:\Users\sunay\OneDrive\Desktop\CC-Experiment-01-Hypervisor-Analysis\CC_Experiment_3\graphs"
os.makedirs(output_dir, exist_ok=True)

# 1. Cluster Topology Diagram
fig, ax = plt.subplots(figsize=(9, 5))
ax.axis('off')

# Boxes
cp_box = dict(boxstyle="round,pad=0.8", facecolor="#2b5c8f", edgecolor="#1a365d", lw=2)
w1_box = dict(boxstyle="round,pad=0.8", facecolor="#2e7d32", edgecolor="#1b5e20", lw=2)
w2_box = dict(boxstyle="round,pad=0.8", facecolor="#2e7d32", edgecolor="#1b5e20", lw=2)

ax.text(0.5, 0.8, "kind-control-plane (Container: 172.20.0.4)\nAPI Server | Scheduler | etcd | Controller Manager",
        ha="center", va="center", color="white", weight="bold", bbox=cp_box, fontsize=12)

ax.text(0.25, 0.3, "kind-worker (172.20.0.3)\nkubelet | kube-proxy | containerd\n3 Pods Allocated (50%)",
        ha="center", va="center", color="white", weight="bold", bbox=w1_box, fontsize=11)

ax.text(0.75, 0.3, "kind-worker2 (172.20.0.2)\nkubelet | kube-proxy | containerd\n3 Pods Allocated (50%)",
        ha="center", va="center", color="white", weight="bold", bbox=w2_box, fontsize=11)

# Connecting arrows
ax.annotate("", xy=(0.3, 0.45), xytext=(0.45, 0.68),
            arrowprops=dict(arrowstyle="->", lw=2.5, color="#1a365d"))
ax.annotate("", xy=(0.7, 0.45), xytext=(0.55, 0.68),
            arrowprops=dict(arrowstyle="->", lw=2.5, color="#1a365d"))

ax.text(0.5, 0.05, "Figure 1: Three-Node Kubernetes Physical Topology in Docker Desktop WSL 2",
        ha="center", fontsize=11, style="italic", color="#333333")

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "01_cluster_topology_architecture.png"), dpi=200)
plt.close()

# 2. Pod Distribution by Worker Node
fig, ax = plt.subplots(figsize=(8, 5))
stages = ['1 Replica\n(Initial)', '3 Replicas\n(Scaled)', '6 Replicas\n(Final)']
worker1_pods = [1, 2, 3]
worker2_pods = [0, 1, 3]

x = np.arange(len(stages))
width = 0.35

rects1 = ax.bar(x - width/2, worker1_pods, width, label='kind-worker', color='#1976d2')
rects2 = ax.bar(x + width/2, worker2_pods, width, label='kind-worker2', color='#388e3c')

ax.set_ylabel('Number of Scheduled Pods', fontweight='bold')
ax.set_title('Pod Placement and Worker Node Distribution (1 -> 3 -> 6 Replicas)', fontweight='bold', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(stages)
ax.legend(loc='upper left', frameon=True)
ax.set_ylim(0, 4)

for r in rects1 + rects2:
    h = r.get_height()
    ax.annotate(f'{h}',
                xy=(r.get_x() + r.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "02_pod_distribution_by_node.png"), dpi=200)
plt.close()

# 3. Scaling Timeline & Replicas
fig, ax = plt.subplots(figsize=(8, 5))
time_points = [0, 1, 2, 3, 4, 5, 6, 7]
desired = [1, 1, 3, 3, 3, 6, 6, 6]
ready =   [0, 1, 1, 2, 3, 3, 5, 6]

ax.step(time_points, desired, where='post', label='Desired Replicas (Deployment)', color='#d32f2f', lw=2.5, linestyle='--')
ax.plot(time_points, ready, marker='o', label='Ready Replicas (Pods Running)', color='#0288d1', lw=2.5)

ax.set_xlabel('Timeline Progression (Arbitrary Event Steps)', fontweight='bold')
ax.set_ylabel('Replica Count', fontweight='bold')
ax.set_title('Dynamic Workload Elasticity: Target vs. Actual Replicas', fontweight='bold', fontsize=13)
ax.set_ylim(0, 7)
ax.legend(loc='upper left', frameon=True)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "03_scaling_timeline_pod_states.png"), dpi=200)
plt.close()

# 4. Self-Healing State Convergence Flow
fig, ax = plt.subplots(figsize=(8, 5))
t = [0, 1, 2, 3, 4, 5, 6, 7, 8]
running_pods = [6, 5, 5, 5, 5, 5, 5, 5, 6]
terminating =  [0, 1, 1, 1, 1, 0, 0, 0, 0]
creating =     [0, 0, 1, 1, 1, 1, 1, 1, 0]

ax.plot(t, running_pods, marker='s', label='Active Running Pods', color='#2e7d32', lw=2.5)
ax.plot(t, terminating, marker='x', label='Terminating Pod', color='#c62828', lw=2, linestyle=':')
ax.plot(t, creating, marker='^', label='Replacement (ContainerCreating)', color='#f57c00', lw=2, linestyle='-.')

ax.axvline(1, color='red', linestyle='--', alpha=0.6, label='Manual Pod Deletion Event')
ax.axvline(8, color='green', linestyle='--', alpha=0.6, label='100% Desired State Restored')

ax.set_xlabel('Time Elapsed (seconds)', fontweight='bold')
ax.set_ylabel('Pod Instance Count', fontweight='bold')
ax.set_title('Autonomic Self-Healing: Pod Failure & Automatic Recovery', fontweight='bold', fontsize=13)
ax.set_ylim(-0.5, 7)
ax.legend(loc='center right', frameon=True)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "04_self_healing_reconciliation_flow.png"), dpi=200)
plt.close()

print("Experiment 3 graphs generated successfully!")
