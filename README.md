TYPE-1 VS TYPE-2 HYPERVISOR PERFORMANCE ANALYSIS



Experiment Overview



This experiment performs a performance analysis and comparison of virtual machines running on a Type-1 hypervisor and a Type-2 hypervisor.



The hypervisors used in this experiment are:



Type-1 Hypervisor: Proxmox VE

Type-2 Hypervisor: VMware Workstation



The same virtual machine configuration and CPU benchmark were used for both hypervisors to maintain consistency during performance analysis.





STANDARD VIRTUAL MACHINE CONFIGURATION



Guest Operating System: Ubuntu 22.04

CPU Allocation: 2 vCPU

Memory Allocation: 2 GB RAM

Disk Allocation: 20 GB

Benchmark Tool: Sysbench



CPU Benchmark Command:



sysbench cpu --cpu-max-prime=20000 run



The same resource configuration was used for both hypervisors for performance comparison.





TYPE-1 HYPERVISOR – PROXMOX VE



Hypervisor: Proxmox VE

Hypervisor Type: Type-1

Guest Operating System: Ubuntu

CPU Allocation: 2 vCPU

Memory Allocation: 2 GB

Disk Allocation: 20 GB





PROXMOX VE PERFORMANCE RESULTS



Total Execution Time: 10.0006 seconds

Total Events: 16903

Events per Second: 1689.43

Minimum Latency: 0.57 ms

Average Latency: 0.59 ms

Maximum Latency: 1.09 ms





TYPE-2 HYPERVISOR – VMWARE WORKSTATION



Hypervisor: VMware Workstation

Hypervisor Type: Type-2

Guest Operating System: Ubuntu 22.04

CPU Allocation: 2 vCPU

Memory Allocation: 2 GB

Disk Allocation: 20 GB

Network Configuration: NAT





VMWARE WORKSTATION PERFORMANCE RESULTS



Total Execution Time: 10.0006 seconds

Total Events: 7879

Events per Second: 787.70

Minimum Latency: 1.16 ms

Average Latency: 1.27 ms

Maximum Latency: 24.60 ms





PERFORMANCE COMPARISON



Parameter                    Type-1 Proxmox VE        Type-2 VMware Workstation



Total Execution Time         10.0006 s               10.0006 s

Total Events                 16903                   7879

Events per Second            1689.43                 787.70

Average Latency              0.59 ms                 1.27 ms





OBSERVATION



Both hypervisors were tested using the same CPU benchmark command and the same virtual machine resource configuration.



The recorded execution time for both benchmark runs was approximately 10 seconds. The number of events, events per second, and latency values obtained during the experiments were different for the two hypervisors.





SCREENSHOT EVIDENCE



Type-1 Hypervisor – Proxmox VE



The Proxmox VE implementation screenshots are available in:



screenshots/type1-proxmox/



The screenshots include:



01-proxmox-dashboard.png

02-proxmox-vm-configuration.png

03-proxmox-vm-running.png

04-proxmox-ubuntu-console.png

05-proxmox-system-configuration.png

06-proxmox-sysbench-result.png

07-proxmox-resource-monitoring.png





Type-2 Hypervisor – VMware Workstation



The VMware Workstation implementation screenshots are available in:



screenshots/type2-vmware/



The screenshots include:



01-vmware-vm-configuration.png

02-vmware-vm-running.png

03-vmware-system-configuration.png

04-vmware-sysbench-result.png





FINAL PERFORMANCE COMPARISON



The final performance comparison screenshot is available in:



screenshots/comparison/01-hypervisor-performance-comparison.png





DETAILED RESULTS



The detailed performance analysis is available in:



results/performance-analysis.md





REPOSITORY STRUCTURE



CC-Experiment-01-Hypervisor-Analysis/



screenshots/

&#x20;   type1-proxmox/

&#x20;       01-proxmox-dashboard.png

&#x20;       02-proxmox-vm-configuration.png

&#x20;       03-proxmox-vm-running.png

&#x20;       04-proxmox-ubuntu-console.png

&#x20;       05-proxmox-system-configuration.png

&#x20;       06-proxmox-sysbench-result.png

&#x20;       07-proxmox-resource-monitoring.png



&#x20;   type2-vmware/

&#x20;       01-vmware-vm-configuration.png

&#x20;       02-vmware-vm-running.png

&#x20;       03-vmware-system-configuration.png

&#x20;       04-vmware-sysbench-result.png



&#x20;   comparison/

&#x20;       01-hypervisor-performance-comparison.png



results/

&#x20;   performance-analysis.md



README.md

