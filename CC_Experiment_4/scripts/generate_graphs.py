import os
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 11

output_dir = r"C:\Users\sunay\OneDrive\Desktop\CC-Experiment-01-Hypervisor-Analysis\CC_Experiment_4\graphs"
os.makedirs(output_dir, exist_ok=True)

# 1. Pod Distribution (6 vs 12 Replicas)
fig, ax = plt.subplots(figsize=(8, 5))
nodes = ['kind-worker', 'kind-worker2']
pods_6 = [3, 3]
pods_12 = [6, 6]

x = np.arange(len(nodes))
width = 0.35

rects1 = ax.bar(x - width/2, pods_6, width, label='6 Replicas (Initial)', color='#0288d1')
rects2 = ax.bar(x + width/2, pods_12, width, label='12 Replicas (Scaled)', color='#388e3c')

ax.set_ylabel('Scheduled Pods', fontweight='bold')
ax.set_title('Workload Distribution Across Worker Nodes: 6 vs. 12 Replicas', fontweight='bold', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(nodes, fontweight='bold')
ax.legend(loc='upper left', frameon=True)
ax.set_ylim(0, 8)

for r in rects1 + rects2:
    h = r.get_height()
    ax.annotate(f'{h} Pods\n(50%)',
                xy=(r.get_x() + r.get_width() / 2, h),
                xytext=(0, 4), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "01_pod_distribution_6_vs_12.png"), dpi=200)
plt.close()

# 2. CPU Allocation Scaling
fig, ax = plt.subplots(figsize=(8, 5))
stages = ['6 Replicas (Requests)', '6 Replicas (Limits)', '12 Replicas (Requests)', '12 Replicas (Limits)']
worker1_cpu = [400, 600, 700, 1200]
worker2_cpu = [400, 600, 700, 1200]

x = np.arange(len(stages))
width = 0.35

rects1 = ax.bar(x - width/2, worker1_cpu, width, label='kind-worker', color='#1976d2')
rects2 = ax.bar(x + width/2, worker2_cpu, width, label='kind-worker2', color='#ff9800')

ax.set_ylabel('Allocated CPU (millicores / m)', fontweight='bold')
ax.set_title('Allocated CPU Commitments (Requests vs Limits) Before and After Scaling', fontweight='bold', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=9.5)
ax.legend(loc='upper left', frameon=True)
ax.set_ylim(0, 1500)

for r in rects1 + rects2:
    h = r.get_height()
    ax.annotate(f'{h}m',
                xy=(r.get_x() + r.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold', fontsize=9.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "02_cpu_allocation_scaling.png"), dpi=200)
plt.close()

# 3. Memory Allocation Scaling
fig, ax = plt.subplots(figsize=(8, 5))
stages = ['6 Replicas (Requests)', '6 Replicas (Limits)', '12 Replicas (Requests)', '12 Replicas (Limits)']
worker1_mem = [242, 384, 434, 768]
worker2_mem = [242, 384, 434, 768]

x = np.arange(len(stages))
width = 0.35

rects1 = ax.bar(x - width/2, worker1_mem, width, label='kind-worker', color='#512da8')
rects2 = ax.bar(x + width/2, worker2_mem, width, label='kind-worker2', color='#00796b')

ax.set_ylabel('Allocated Memory (MiB)', fontweight='bold')
ax.set_title('Allocated Memory Commitments (Requests vs Limits) Before and After Scaling', fontweight='bold', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=9.5)
ax.legend(loc='upper left', frameon=True)
ax.set_ylim(0, 1000)

for r in rects1 + rects2:
    h = r.get_height()
    ax.annotate(f'{h}Mi',
                xy=(r.get_x() + r.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold', fontsize=9.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "03_memory_allocation_scaling.png"), dpi=200)
plt.close()

# 4. Service Endpoint Distribution
fig, ax = plt.subplots(figsize=(7, 7))
labels = ['kind-worker\n(6 Endpoints: 10.244.1.x)', 'kind-worker2\n(6 Endpoints: 10.244.2.x)']
sizes = [6, 6]
colors = ['#1e88e5', '#43a047']

wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90,
                                  colors=colors, textprops=dict(color="black", fontweight="bold"),
                                  wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))

ax.set_title('NodePort 30080 Service Backend Endpoints Distribution\n(Total: 12 Endpoints in nginx-service-gbk48)',
             fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "04_service_endpoint_distribution.png"), dpi=200)
plt.close()

# 5. Multi-Panel Experiment Dashboard
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Subplot 1: Pod Scheduling Ratio
axs[0, 0].pie([6, 6], labels=['kind-worker (6)', 'kind-worker2 (6)'], autopct='%1.0f%%',
              colors=['#1976d2', '#388e3c'], startangle=90)
axs[0, 0].set_title('Final Workload Balance (12 Pods)', fontweight='bold')

# Subplot 2: CPU Growth
axs[0, 1].plot(['Initial (6 Pods)', 'Scaled (12 Pods)'], [400, 700], marker='o', lw=3, color='#e65100', label='CPU Requests (m)')
axs[0, 1].plot(['Initial (6 Pods)', 'Scaled (12 Pods)'], [600, 1200], marker='s', lw=3, color='#c62828', label='CPU Limits (m)')
axs[0, 1].set_ylabel('CPU (m)', fontweight='bold')
axs[0, 1].set_title('Per-Worker CPU Commitment Growth', fontweight='bold')
axs[0, 1].legend()

# Subplot 3: Memory Growth
axs[1, 0].plot(['Initial (6 Pods)', 'Scaled (12 Pods)'], [242, 434], marker='o', lw=3, color='#303f9f', label='Memory Requests (MiB)')
axs[1, 0].plot(['Initial (6 Pods)', 'Scaled (12 Pods)'], [384, 768], marker='s', lw=3, color='#6a1b9a', label='Memory Limits (MiB)')
axs[1, 0].set_ylabel('Memory (MiB)', fontweight='bold')
axs[1, 0].set_title('Per-Worker Memory Commitment Growth', fontweight='bold')
axs[1, 0].legend()

# Subplot 4: Service Endpoints
axs[1, 1].barh(['Registered Pods', 'Target Replicas'], [12, 12], color=['#00897b', '#00acc1'])
axs[1, 1].set_xlim(0, 15)
axs[1, 1].set_xlabel('Count', fontweight='bold')
axs[1, 1].set_title('Service Load Balancing Convergence (100%)', fontweight='bold')
for i, v in enumerate([12, 12]):
    axs[1, 1].text(v + 0.3, i, str(v), va='center', fontweight='bold')

plt.suptitle('Kubernetes Experiment 4: Comprehensive Analytical Dashboard', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "05_experiment_summary_dashboard.png"), dpi=200)
plt.close()

print("Experiment 4 graphs generated successfully!")
