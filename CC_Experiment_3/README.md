# Kubernetes Multi-Node Cluster Orchestration, Workload Scaling, and Fault Recovery on Windows

## 1. Executive Summary

This report documents the design, local provisioning, workload deployment, horizontal scaling, and fault tolerance validation of a multi-node Kubernetes cluster hosted on Windows 11. Utilizing **kind (Kubernetes in Docker)**, **Docker Desktop**, and **WSL 2**, the experiment simulates a distributed enterprise Kubernetes environment entirely within local system memory and containers.

The experiment progresses through six core phases:
1. Toolchain preparation (WSL 2, Docker Engine, kubectl, and kind).
2. Runtime health and API client verification.
3. Declarative topology configuration defining one control-plane node and two dedicated worker nodes.
4. Infrastructure orchestration, cluster bootstrap, and system component inspection.
5. Containerized application deployment (NGINX) with multi-node scheduling across worker nodes.
6. Elastic scaling to six Pods followed by intentional Pod failure injection to validate Kubernetes controller-driven self-healing.

---

## 2. Objective and Scope

The primary objective of this experiment is to gain practical and architectural mastery over container orchestration on Windows systems using industry-standard cloud-native tools.

### Core Objectives

- **Local Infrastructure Orchestration**: Construct a three-node Kubernetes cluster where each node runs as an isolated container using Docker Desktop and WSL 2.
- **Declarative Configuration**: Author and interpret a multi-node cluster manifest (`kind-config.yaml`) using the `kind.x-k8s.io/v1alpha4` API.
- **Workload Management**: Deploy a containerized web server (NGINX) via Kubernetes Deployments, avoiding single-point-of-failure architectures.
- **Worker Node Placement**: Evaluate the Kubernetes Scheduler (`kube-scheduler`) as it distributes Pod replicas across heterogeneous worker nodes.
- **Dynamic Horizontal Scaling**: Adjust replica targets on-the-fly and analyze the scheduling throughput of new Pods.
- **Resilience and Automated Self-Healing**: Induce synthetic workload failures by deleting active Pods, observing how the Kubernetes ReplicaSet controller detects drift and automatically restores the desired state.

---

## 3. System and Environment Specifications

The experiment was conducted on a Windows 11 host operating system leveraging virtualization extensions and Linux containerization runtimes.

| Component | Technical Specification | Role in Architecture |
|:---|:---|:---|
| **Host Operating System** | Windows 11 Pro / Home (64-bit, x86_64) | Host management platform |
| **Virtualization Backend** | WSL 2 (Windows Subsystem for Linux) | High-performance Linux kernel layer for container execution |
| **Container Engine** | Docker Desktop v4.85.0 (Engine v29.6.2, containerd v2.2.5) | Host daemon managing node containers and networking |
| **Cluster Bootstrapper** | kind (Kubernetes in Docker) v0.33 | Multi-node cluster lifecycle orchestrator |
| **Cluster Version** | Kubernetes v1.37.0 | Target container orchestration system |
| **CLI Management** | kubectl v1.37 | Administrative client querying `kube-apiserver` |
| **Workload Image** | NGINX (`nginx:latest`) | Stateless HTTP web service |
| **Shell Environment** | Windows PowerShell | Native administrative scripting terminal |

---

## 4. Architectural Design: The Three-Node Topology

In production environments, Kubernetes strictly demarcates the responsibility between the administrative control plane and compute worker nodes. Through `kind`, each Kubernetes node is abstracted as a container running an isolated `systemd` daemon, `containerd` container runtime, and Kubernetes node agents.

```text
+-----------------------------------------------------------------------------------------+
|                                    WINDOWS 11 HOST                                      |
|                                                                                         |
|   Windows PowerShell (kubectl / kind client)                                            |
|        │                                                                                |
|        ▼ (HTTPS REST API / Port Forwarded Context)                                      |
|   +─────────────────────────────────────────────────────────────────────────────────+   |
|   │                       DOCKER DESKTOP ENGINE (WSL 2 BACKEND)                     │   |
|   │                                                                                 │   |
|   │   +─────────────────────────────────────────────────────────────────────────+   │   |
|   │   │                     kind-control-plane (Container)                      │   │   |
|   │   │  * kube-apiserver         * etcd (Cluster State Store)                  │   │   |
|   │   │  * kube-scheduler         * kube-controller-manager                     │   │   |
|   │   +────────────────────┬────────────────────────────────────┬───────────────+   │   |
|   │                        │                                    │                   │   |
|   │                        ▼ (Pod Placement)                    ▼ (Pod Placement)   │   |
|   │   +─────────────────────────────────────+  +────────────────────────────────+   │   |
|   │   │       kind-worker (Container)       │  │    kind-worker2 (Container)    │   │   |
|   │   │  * kubelet         * kube-proxy     │  │  * kubelet        * kube-proxy │   │   |
|   │   │  * containerd                       │  │  * containerd                  │   │   |
|   │   │                                     │  │                                │   │   |
|   │   │  [ NGINX Pod ]   [ NGINX Pod ]      │  │  [ NGINX Pod ]  [ NGINX Pod ]  │   │   |
|   │   +─────────────────────────────────────+  +────────────────────────────────+   │   |
|   +───┴─────────────────────────────────────────────────────────────────────────┴───+   |
+-----------------------------------------------------------------------------------------+
```

### Component Responsibilities

1. **Control-Plane Node (`kind-control-plane`)**:
   - **`kube-apiserver`**: Acts as the central administrative gateway, validating and configuring data for Pods, Services, and Deployments.
   - **`etcd`**: Provides consistent, highly available key-value storage for the entire cluster configuration and running state.
   - **`kube-scheduler`**: Assigns unassigned Pods to healthy worker nodes based on resource availability and balancing algorithms.
   - **`kube-controller-manager`**: Executes controllers (such as the Node and ReplicaSet controllers) that maintain cluster state.
2. **Worker Nodes (`kind-worker` and `kind-worker2`)**:
   - **`kubelet`**: The node-level agent that communicates with the API server, ensuring scheduled Pod containers are running and healthy.
   - **`kube-proxy`**: Manages host-level networking and packet filtering for Kubernetes Services.
   - **`containerd`**: The low-level OCI-compliant container runtime executing the application images.

---

## 5. Experimental Methodology and Execution

The experimental procedure follows a structured, step-by-step methodology executed through Windows PowerShell.

```text
Phase 1: Toolchain Setup ──> Phase 2: Runtime Checks ──> Phase 3: Manifest Configuration
                                                                    │
Phase 6: Scaling & Healing <── Phase 5: Workload Deployment <── Phase 4: Cluster Provisioning
```

### Phase 1: Toolchain Installation and Environment Setup

The prerequisite toolchain requires WSL 2, Docker Desktop, kubectl, and kind.

1. **WSL 2 Installation**:
   Enabled the Linux virtualization subsystem required for Docker's native Linux engine:
   ```powershell
   wsl --install
   ```
2. **Docker Desktop Configuration**:
   Installed Docker Desktop for Windows, explicitly activating the **WSL 2 based engine** option. Virtualization flags (Intel VT-x / AMD-V) were verified enabled in system BIOS.
3. **Command-Line Tools Installation**:
   Installed `kubectl` and `kind` using the Windows Package Manager (`winget`):
   ```powershell
   winget install -e --id Kubernetes.kubectl
   winget install -e --id Kubernetes.kind
   ```
4. **Shell Environment Refresh**:
   PowerShell was restarted to register the newly added binary paths in the system `PATH` variable:
   ```powershell
   exit
   ```

---

### Phase 2: Toolchain Validation and Runtime Verification

Prior to cluster creation, each component was verified to confirm proper daemon communication and binary accessibility:

1. **Docker Engine Verification**:
   ```powershell
   docker version
   ```
   *Observation:* Confirmed active communication between the Windows client and the WSL 2 server daemon (Engine version 29.6.2, API version 1.55).
2. **Container Execution Sanity Check**:
   ```powershell
   docker run hello-world
   ```
   *Observation:* The test container was pulled from Docker Hub, executed, and printed confirmation output, establishing that the container runtime was operational.
3. **CLI Version Checks**:
   ```powershell
   kubectl version --client
   kind version
   ```
   *Observation:* Confirmed `kubectl` client version v1.37.x and `kind` binary version v0.33.0.

---

### Phase 3: Declarative Multi-Node Topology Definition

By default, `kind` instantiates a single-node cluster where the control plane also runs user workloads. To create a multi-node architecture matching enterprise environments, a declarative configuration was authored.

1. **Workspace Directory Initialization**:
   ```powershell
   mkdir k8s-lab
   cd k8s-lab
   ```
2. **Authoring `kind-config.yaml`**:
   ```powershell
   notepad kind-config.yaml
   ```
   The configuration defines one control plane and two dedicated worker nodes:
   ```yaml
   kind: Cluster
   apiVersion: kind.x-k8s.io/v1alpha4
   nodes:
     - role: control-plane
     - role: worker
     - role: worker
   ```
3. **File Verification**:
   ```powershell
   Get-ChildItem
   ```
   *Observation:* Confirmed `kind-config.yaml` exists in the local workspace directory.

---

### Phase 4: Cluster Orchestration and Infrastructure Inspection

1. **Cluster Creation**:
   Provisioned the cluster using the declarative configuration:
   ```powershell
   kind create cluster --config kind-config.yaml
   ```
   *Lifecycle Events:*
   - Pulled the base node image (`kindest/node:v1.37.0`).
   - Prepared three node containers.
   - Wrote cluster configurations and booted `kube-apiserver`, `etcd`, `kube-scheduler`, and `kube-controller-manager`.
   - Installed the kindnet Container Network Interface (CNI) and local StorageClass.
   - Joined worker nodes to the control plane and set the active kubeconfig context to `kind-kind`.

2. **Cluster Health and API Verification**:
   ```powershell
   kubectl cluster-info --context kind-kind
   ```
   *Observation:* Confirmed that the Kubernetes control plane was active at `https://127.0.0.1:<port>` with CoreDNS registered.

3. **Node Status Inspection**:
   ```powershell
   kubectl get nodes
   ```
   *Recorded Output:*
   ```text
   NAME                 STATUS   ROLES           AGE   VERSION
   kind-control-plane   Ready    control-plane   51s   v1.37.0
   kind-worker          Ready    <none>          34s   v1.37.0
   kind-worker2         Ready    <none>          35s   v1.37.0
   ```
   All three nodes achieved the `Ready` status within approximately 50 seconds.

4. **Underlying Docker Container Inspection**:
   ```powershell
   docker ps
   ```
   *Observation:* Three distinct containers (`kind-control-plane`, `kind-worker`, `kind-worker2`) were observed running in the Docker daemon, listening on local bridged interfaces.

5. **Kubernetes System Pod Inspection**:
   ```powershell
   kubectl get pods -n kube-system -o wide
   ```
   *Observation:* Validated that core control-plane microservices (`etcd`, `kube-apiserver`, `kube-scheduler`, `kube-controller-manager`) were running as static Pods on `kind-control-plane`, while `kube-proxy` and `kindnet` were running as DaemonSets across all three nodes.

---

### Phase 5: Workload Deployment and Worker Node Scheduling

1. **NGINX Workload Provisioning**:
   Created a Deployment resource named `web` running NGINX with an initial replica count of three:
   ```powershell
   kubectl create deployment web --image=nginx --replicas=3
   ```
2. **Deployment Rollout Status**:
   ```powershell
   kubectl get deployments
   ```
   *Recorded Output:*
   ```text
   NAME   READY   UP-TO-DATE   AVAILABLE   AGE
   web    3/3     3            3           45s
   ```
3. **Pod Scheduling and Distribution Analysis**:
   ```powershell
   kubectl get pods -o wide
   ```
   *Recorded Pod Distribution:*
   ```text
   NAME                     READY   STATUS    AGE   IP           NODE
   web-69b9cdbbdd-5zrwl     1/1     Running   2m    10.244.1.2   kind-worker
   web-69b9cdbbdd-qfjgv     1/1     Running   2m    10.244.2.2   kind-worker2
   web-69b9cdbbdd-x5ssp     1/1     Running   2m    10.244.1.3   kind-worker
   ```
   *Analysis:* The `kube-scheduler` evenly distributed the workload across the two available worker nodes (`kind-worker` received two Pods, `kind-worker2` received one Pod), while completely isolating the control plane from application traffic.
4. **Pod Inspection**:
   ```powershell
   kubectl describe pod web-69b9cdbbdd-5zrwl
   ```
   *Observation:* Inspected container lifecycle events, confirming image pull, container instantiation, and successful scheduling binding by `default-scheduler`.

---

### Phase 6: Dynamic Horizontal Scaling and Self-Healing Verification

1. **Scaling Deployment to Six Replicas**:
   Increased the replica count to double the application capacity:
   ```powershell
   kubectl scale deployment web --replicas=6
   ```
2. **Post-Scale Distribution Verification**:
   ```powershell
   kubectl get pods -o wide
   ```
   *Recorded Output:*
   ```text
   NAME                     READY   STATUS    AGE   IP           NODE
   web-69b9cdbbdd-5zrwl     1/1     Running   5m    10.244.1.2   kind-worker
   web-69b9cdbbdd-g5tft     1/1     Running   26s   10.244.2.3   kind-worker2
   web-69b9cdbbdd-qfjgv     1/1     Running   5m    10.244.2.2   kind-worker2
   web-69b9cdbbdd-r7zrh     1/1     Running   26s   10.244.1.4   kind-worker
   web-69b9cdbbdd-rqjd5     1/1     Running   26s   10.244.2.4   kind-worker2
   web-69b9cdbbdd-x5ssp     1/1     Running   5m    10.244.1.3   kind-worker
   ```
   *Analysis:* The three additional Pods (`g5tft`, `r7zrh`, `rqjd5`) were provisioned in under 30 seconds. The scheduler maintained balance across worker nodes, placing 3 Pods on `kind-worker` and 3 Pods on `kind-worker2`.

3. **Fault Injection and Self-Healing Test**:
   To test the cluster's autonomic fault recovery, an active Pod was deliberately destroyed:
   ```powershell
   kubectl delete pod web-69b9cdbbdd-5zrwl
   ```
4. **Automated Reconciliation Observation**:
   ```powershell
   kubectl get pods
   ```
   *Recorded Behavior:*
   - The targeted Pod immediately entered the `Terminating` state.
   - The ReplicaSet controller detected an instantaneous variance between desired replicas ($R=6$) and ready replicas ($R=5$).
   - A replacement Pod was immediately provisioned with a new hash identifier, transitioning to `Running` in seconds.
   - The deployment returned to `6/6 AVAILABLE` state automatically without administrative intervention.

---

## 6. Screenshot Evidence and Operational Milestones

The following eight figures capture the verified milestone states during lab execution:

### Figure 1: Host Container Runtime and Tooling Verification
![Docker Verification](screenshots/01_docker_engine_and_hello_world_verification.jpeg)
*Verification of Docker Desktop v4.85.0 and Engine v29.6.2 running on Windows via WSL 2, followed by successful execution of the test container.*

---

### Figure 2: Declarative Multi-Node Manifest Authoring
![Cluster Configuration](screenshots/02_kind_multi_node_cluster_configuration.jpeg)
*The `kind-config.yaml` file opened in Notepad, defining the one control-plane and two worker nodes topology.*

---

### Figure 3: Cluster Provisioning and Node Synchronization
![Cluster Creation](screenshots/03_kind_cluster_creation_and_node_readiness.jpeg)
*Automated cluster orchestration showing image verification (`kindest/node:v1.37.0`), node joining, and three nodes (`kind-control-plane`, `kind-worker`, `kind-worker2`) reporting `Ready`.*

---

### Figure 4: Application Deployment and Replica Creation
![Deployment Creation](screenshots/04_nginx_deployment_creation_and_replica_scale_up.jpeg)
*Deployment instantiation via `kubectl create deployment` and scaling to 3 replicas with initial `ContainerCreating` state.*

---

### Figure 5: Multi-Pod Steady-State Execution
![Three Pods Running](screenshots/05_three_nginx_pods_running.jpeg)
*`kubectl get pods` status output showing all three Pods running in `1/1 Running` state with zero restarts.*

---

### Figure 6: Infrastructure Node Health Audit
![Node Health](screenshots/06_three_node_cluster_status_verification.jpeg)
*Cluster node inspection verifying persistent readiness of the control plane and both compute worker nodes.*

---

### Figure 7: Horizontal Elasticity to Six Replicas
![Scaling to 6](screenshots/07_scaling_nginx_deployment_to_six_replicas.jpeg)
*Dynamic scale-out to 6 replicas, showing rapid provisioning and distribution across the worker cluster.*

---

### Figure 8: Full Lifecycle Audit and Deployment Availability
![Full Lifecycle Verification](screenshots/08_deployment_scale_and_full_verification.jpeg)
*Terminal record documenting the full progression from initial deployment to 6/6 available replicas.*

---

## 7. Technical Analysis: Reconciliation and Self-Healing

The self-healing observed during the lab is governed by the Kubernetes reconciliation loop:

$$\text{Reconciliation Loop}: \quad \text{Current State} \xrightarrow{\Delta = \text{Desired} - \text{Actual}} \text{Target State}$$

```text
+─────────────────────────────────────────────────────────────────────────────+
|                     Kubernetes Reconciliation Mechanism                     |
|                                                                             |
|   1. Desired State: Replicas = 6 (Stored in etcd)                           |
|   2. Actual State:  Replicas = 5 (After Pod termination event)              |
|   3. Controller detects delta: Δ = -1 Pod                                   |
|   4. ReplicaSet invokes kube-apiserver: CreatePodRequest                    |
|   5. kube-scheduler selects least-loaded worker node                        |
|   6. Target kubelet invokes containerd: Pull & Start container              |
|   7. State restored: Replicas = 6                                           |
+─────────────────────────────────────────────────────────────────────────────+
```

Because workloads are managed declaratively via Deployments rather than bare Pods, Kubernetes guarantees high availability by treating individual Pod instances as ephemeral and automatically replaceable.

---

## 8. Diagnostic and Troubleshooting Reference

The table below outlines common operational issues and verified corrective actions:

| Diagnostic Symptom | Root Cause | Corrective Action |
|:---|:---|:---|
| `Cannot connect to the Docker daemon` | Docker Desktop service is stopped or initializing | Open Docker Desktop from the Start menu and wait until the status displays `Engine running`. |
| `kubectl or kind is not recognized` | Binary directory is missing from host `PATH` | Restart PowerShell or re-verify installation via `winget install -e --id Kubernetes.kubectl`. |
| `WSL 2 or virtualization missing` | Hardware virtualization disabled in BIOS/UEFI | Enable Intel VT-x or AMD-V/SVM in system firmware settings and run `wsl --update`. |
| `Node stays NotReady` | Container networking initialization delay | Allow 60 seconds for CNI startup. If unresolved, run `kind delete cluster` and recreate. |
| `ImagePullBackOff` on application Pod | Internet connectivity interruption or image typo | Execute `kubectl describe pod <pod-name>` to inspect failure events from the image puller. |
| `error parsing kind-config.yaml` | Tab characters or invalid indentation in YAML | Replace all tab characters with 2 spaces and verify schema structure against the reference manifest. |
| `Commands hang or behave oddly` | Running commands inside unsupported shells | Execute commands using Windows PowerShell rather than Git Bash or third-party wrappers. |

---

## 9. Key Technical Takeaways

1. **Lightweight Multi-Node Prototyping**: `kind` enables realistic multi-node Kubernetes cluster emulation on a single developer laptop without the computational overhead of full virtual machines.
2. **Workload Isolation by Design**: Worker nodes host application workloads while the control plane remains dedicated to API processing, scheduling, and state coordination.
3. **Declarative State Management**: Systems defined by desired state (manifests) provide automated resilience compared to manually maintained imperatively started containers.
4. **Autonomous Fault Recovery**: The Kubernetes control plane continuously monitors cluster conditions and replaces failed resources to maintain zero application downtime.

---

## 10. Command Quick Reference

| Lab Phase | Executed Command | Operational Purpose |
|:---|:---|:---|
| **Phase 1** | `wsl --install` | Installs WSL 2 Linux kernel subsystem |
| **Phase 1** | `winget install -e --id Kubernetes.kubectl` | Installs the Kubernetes CLI client |
| **Phase 1** | `winget install -e --id Kubernetes.kind` | Installs the kind cluster provisioning tool |
| **Phase 2** | `docker version` | Inspects Docker client and server daemon status |
| **Phase 2** | `docker run hello-world` | Executes baseline container validation |
| **Phase 2** | `kubectl version --client` | Inspects local kubectl client version |
| **Phase 2** | `kind version` | Inspects installed kind version |
| **Phase 3** | `mkdir k8s-lab; cd k8s-lab` | Initializes local workspace directory |
| **Phase 3** | `notepad kind-config.yaml` | Authors the 3-node cluster topology manifest |
| **Phase 3** | `Get-ChildItem` | Validates presence of the configuration file |
| **Phase 4** | `kind create cluster --config kind-config.yaml` | Orchestrates the multi-node Kubernetes cluster |
| **Phase 4** | `kubectl cluster-info --context kind-kind` | Validates API server and CoreDNS connectivity |
| **Phase 4** | `kubectl get nodes` | Checks health and readiness of all 3 cluster nodes |
| **Phase 4** | `docker ps` | Inspects underlying Docker node containers |
| **Phase 4** | `kubectl get pods -n kube-system -o wide` | Audits system control plane Pods |
| **Phase 5** | `kubectl create deployment web --image=nginx --replicas=3` | Deploys 3 NGINX Pod replicas |
| **Phase 5** | `kubectl get deployments` | Inspects desired vs ready deployment state |
| **Phase 5** | `kubectl get pods -o wide` | Evaluates Pod placement across worker nodes |
| **Phase 5** | `kubectl describe pod <pod-name>` | Inspects granular lifecycle events of a Pod |
| **Phase 6** | `kubectl scale deployment web --replicas=6` | Scales application workload to 6 replicas |
| **Phase 6** | `kubectl delete pod <pod-name>` | Injects fault by terminating an active Pod |
| **Phase 6** | `kubectl get pods` | Verifies automated replica reconciliation |
