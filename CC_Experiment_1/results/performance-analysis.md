# Hypervisor Performance Analysis

## 1. Experiment Overview

This experiment compares CPU performance for a virtual machine running under:

- Type-1 Hypervisor: Proxmox VE
- Type-2 Hypervisor: VMware Workstation

The CPU benchmark used for both virtual machines was:

```bash
sysbench cpu --cpu-max-prime=20000 run
```

The VMware virtual machine was configured with Ubuntu 22.04, 2 vCPU, 2 GB RAM, 20 GB disk, and NAT networking.

## 2. Type-1 Hypervisor — Proxmox VE

### Configuration

- Hypervisor: Proxmox VE
- Hypervisor Type: Type-1
- Guest Operating System: Ubuntu
- CPU Allocation: 2 vCPU
- Memory Allocation: 2 GB
- Disk Allocation: 20 GB

### Sysbench Result

| Metric | Result |
|---|---:|
| Total Execution Time | 10.0006 s |
| Total Events | 16903 |
| Events per Second | 1689.43 |
| Minimum Latency | 0.57 ms |
| Average Latency | 0.59 ms |
| Maximum Latency | 1.09 ms |

## 3. Type-2 Hypervisor — VMware Workstation

### Configuration

- Hypervisor: VMware Workstation
- Hypervisor Type: Type-2
- Guest Operating System: Ubuntu 22.04
- CPU Allocation: 2 vCPU
- Memory Allocation: 2 GB
- Disk Allocation: 20 GB
- Network: NAT

### Sysbench Result

| Metric | Result |
|---|---:|
| Total Execution Time | 10.0006 s |
| Total Events | 7879 |
| Events per Second | 787.70 |
| Minimum Latency | 1.16 ms |
| Average Latency | 1.27 ms |
| Maximum Latency | 24.60 ms |

## 4. Performance Comparison

| Parameter | Type-1 Proxmox VE | Type-2 VMware Workstation |
|---|---:|---:|
| Total Execution Time | 10.0006 s | 10.0006 s |
| Total Events | 16903 | 7879 |
| Events per Second | 1689.43 | 787.70 |
| Average Latency | 0.59 ms | 1.27 ms |

## 5. Observation

Both hypervisor experiments used the same Sysbench CPU benchmark command and a virtual machine configuration based on 2 vCPU and 2 GB memory. The recorded benchmark values above are the values obtained during the experiment.

The execution time recorded for both runs was approximately 10 seconds. The number of processed events, events per second, and latency values differed between the two runs.

## 6. Screenshots

### Type-1 — Proxmox VE

Stored under:

```text
screenshots/type1-proxmox/
```

### Type-2 — VMware Workstation

Stored under:

```text
screenshots/type2-vmware/
```

### Final Comparison

The final comparison table is stored as:

```text
screenshots/comparison/01-hypervisor-performance-comparison.png
```
