# Kubernetes Lab on Windows

Build a three-node Kubernetes cluster on your own laptop, deploy an NGINX web app, then scale it and watch Kubernetes heal itself.

---

## Lab Overview

| Attribute | Specification |
|:---|:---|
| **Steps** | 6 parts, 27 steps |
| **Estimated Time** | About 60 min |
| **System** | Windows 10 / 11 (64-bit) |
| **Level** | Beginner |
| **Key Tools** | WSL 2, Docker Desktop, kubectl, kind v0.33, NGINX |

### Cluster Architecture

```text
+---------------------------------------------------------------------------------+
| Your Windows laptop                                                             |
|                                                                                 |
|  PowerShell                                                                     |
|  kubectl · kind                                                                 |
|         │                                                                       |
|         ▼                                                                       |
|  Docker Desktop (WSL 2)  [Each node is one container]                           |
|  +---------------------------------------------------------------------------+  |
|  | kind-control-plane                                                        |  |
|  | API server · scheduler · etcd · controller manager                        |  |
|  +---------------------------------------------------------------------------+  |
|  +-----------------------------------+   +-----------------------------------+  |
|  | kind-worker                       |   | kind-worker2                      |  |
|  | [Pod]  [Pod]  [Pod]               |   | [Pod]  [Pod]                      |  |
|  +-----------------------------------+   +-----------------------------------+  |
+---------------------------------------------------------------------------------+
```

### The Lab at a Glance

1. **Build**: A cluster with 1 control plane and 2 workers
2. **Deploy**: Three NGINX Pods and see where they run
3. **Scale and heal**: Go to six Pods and watch one come back

---

## Before You Begin

**Goal:** Build a local Kubernetes cluster with one control-plane node and two worker nodes, deploy NGINX, and test scaling and self-healing.

### Check Your Laptop

- Windows 10 or 11, 64-bit
- Internet access (about 2 GB to download)
- Administrator permission to install software
- 8 GB RAM at least (16 GB recommended)
- PowerShell (not Git Bash)

### How to Use This Manual

- Work through the steps in order. Copy one command at a time into PowerShell and press Enter.
- Read *What it does* before you run it.
- Compare your screen with *You should see* before moving on.
- Replace anything in `<angle brackets>` with a real name, without the brackets.

---

## Part 1 of 6: Install the Tools

You need four tools: WSL 2 (the Linux layer), Docker Desktop (runs the nodes), kubectl (talks to the cluster) and kind (creates the cluster).

### Step 1.1: Install WSL 2

Run PowerShell as Administrator:

```powershell
wsl --install
```

- **What it does:** Installs Windows Subsystem for Linux (WSL 2), which Docker Desktop runs on.
- **You should see:** Download and install progress, then a request to restart. Restart Windows when asked.

### Step 1.2: Install Docker Desktop

1. Download Docker Desktop for Windows from `docker.com/products/docker-desktop`.
2. Run the installer and keep **"Use WSL 2 instead of Hyper-V"** ticked.
3. Open Docker Desktop from the Start menu and accept the terms.

- **What it does:** Installs Docker, which will run each Kubernetes node as a container. This step uses the installer, not a PowerShell command.
- **You should see:** Docker Desktop's status shows Engine running.
- **Important:** If Docker Desktop says WSL 2 or virtualization is missing, finish the WSL setup and restart Windows. If needed, turn on CPU virtualization (Intel VT-x or AMD-V/SVM) in your BIOS/UEFI settings.

### Step 1.3: Install kubectl

Run in PowerShell:

```powershell
winget install -e --id Kubernetes.kubectl
```

- **What it does:** Installs kubectl, the command-line tool used to control Kubernetes.
- **You should see:** Successfully installed at the end. Type `Y` and press Enter if winget asks to accept source agreements.

### Step 1.4: Install kind

Run in PowerShell:

```powershell
winget install -e --id Kubernetes.kind
```

- **What it does:** Installs kind (Kubernetes IN Docker), which creates a Kubernetes cluster using Docker containers.
- **You should see:** Successfully installed at the end.

### Step 1.5: Reopen PowerShell

```powershell
exit
```

- **What it does:** Closes this PowerShell window. Open a new one so it can find the tools you just installed.

---

## Part 2 of 6: Check That the Tools Work

Open Docker Desktop and wait until the Engine is running. Then, in a new PowerShell window, run these commands one by one.

### Step 2.1: Check Docker

```powershell
docker version
```

- **What it does:** Shows the versions of Docker's client and server.
- **You should see:** Both a Client section and a Server section. If the Server part shows an error, Docker Desktop is not running yet.

### Step 2.2: Test a Container

```powershell
docker run hello-world
```

- **What it does:** Downloads and runs a tiny test container.
- **You should see:**
  ```text
  Hello from Docker!
  This message shows that your installation appears to be working correctly.
  ```

### Step 2.3: Check kubectl

```powershell
kubectl version --client
```

- **What it does:** Shows the installed kubectl version.
- **You should see:**
  ```text
  Client Version: v1.37.x
  Kustomize Version: v5.x.x
  ```

### Step 2.4: Check kind

```powershell
kind version
```

- **What it does:** Shows the installed kind version.
- **You should see:** A version line, such as:
  ```text
  kind v0.33.0 go1.26.x windows/amd64
  ```

---

## Part 3 of 6: Create the Cluster Configuration File

A short file tells kind to build one control-plane node and two worker nodes instead of a single node.

### Step 3.1: Create a Lab Folder

```powershell
mkdir k8s-lab
```

- **What it does:** Creates a folder to keep the lab files in. If it already exists, just continue.

### Step 3.2: Enter the Folder

```powershell
cd k8s-lab
```

- **What it does:** Moves PowerShell into the lab folder. Run all the following commands from here.
- **You should see:** The prompt now ends in `\k8s-lab>`.

### Step 3.3: Open the Configuration File

```powershell
notepad kind-config.yaml
```

- **What it does:** Opens Notepad with a new file called `kind-config.yaml`.
- **You should see:** A question asking whether to create a new file. Click Yes.

### Step 3.4: Paste the Configuration and Save

Paste the following content into Notepad exactly as shown:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

- **What it does:** Asks kind to create three nodes: one control-plane node and two worker nodes.
- **Note:** Use spaces, not tabs. Make sure the file is saved as `kind-config.yaml` and not `kind-config.yaml.txt`.

### Step 3.5: Check That the File Exists

```powershell
Get-ChildItem
```

- **What it does:** Lists the files in the current folder.
- **You should see:** `kind-config.yaml` in the Name column.

---

## Part 4 of 6: Build the Three-Node Kubernetes Cluster

One command builds the whole cluster. Then you check that all three nodes are healthy and look at what is running inside.

### Step 4.1: Create the Cluster

```powershell
kind create cluster --config kind-config.yaml
```

- **What it does:** Creates the cluster. The first run can take a few minutes while the Kubernetes node image downloads.
- **You should see:**
  ```text
  Creating cluster "kind" ...
  • Ensuring node image (kindest/node:v1.37.0)
  ✓ Ensuring node image (kindest/node:v1.37.0)
  • Preparing nodes
  ✓ Preparing nodes
  • Writing configuration
  ✓ Writing configuration
  • Starting control-plane
  ✓ Starting control-plane
  • Installing CNI
  ✓ Installing CNI
  • Installing StorageClass
  ✓ Installing StorageClass
  • Joining worker nodes
  ✓ Joining worker nodes
  Set kubectl context to "kind-kind"
  ```

### Step 4.2: Check the Cluster Connection

```powershell
kubectl cluster-info --context kind-kind
```

- **What it does:** Checks that kubectl can talk to the new cluster.
- **You should see:**
  ```text
  Kubernetes control plane is running at https://127.0.0.1:<port>
  CoreDNS is running at https://127.0.0.1:<port>/api/v1/...
  ```

### Step 4.3: Check Node Status

```powershell
kubectl get nodes
```

- **What it does:** Lists the control-plane node and the two worker nodes.
- **You should see:** Three nodes with STATUS `Ready`:
  ```text
  NAME                 STATUS   ROLES           AGE   VERSION
  kind-control-plane   Ready    control-plane   51s   v1.37.0
  kind-worker          Ready    <none>          34s   v1.37.0
  kind-worker2         Ready    <none>          35s   v1.37.0
  ```

### Step 4.4: Check the Docker Containers

```powershell
docker ps
```

- **What it does:** Shows the running Docker containers. Each one is a kind node.
- **You should see:** Three containers named `kind-control-plane`, `kind-worker`, and `kind-worker2` in the NAMES column.

### Step 4.5: Check the Kubernetes System Pods

```powershell
kubectl get pods -n kube-system -o wide
```

- **What it does:** Lists Kubernetes' own components, such as the API server and the scheduler.
- **You should see:** Pods such as `etcd`, `kube-apiserver`, `kube-scheduler`, and `kube-controller-manager` on `kind-control-plane`, and a `kube-proxy` Pod on every node.
- **What just happened?** The control-plane node is the cluster's brain: it stores the state and decides where work goes. The two workers are the muscles where your apps will run. All three are Docker containers on your laptop.

---

## Part 5 of 6: Deploy an NGINX Web Application

Now ask Kubernetes to run a real app: three copies of the NGINX web server, spread over the workers.

### Step 5.1: Create Three NGINX Replicas

```powershell
kubectl create deployment web --image=nginx --replicas=3
```

- **What it does:** Creates a Deployment named `web` and asks Kubernetes to run three copies (Pods) of the NGINX web server.
- **You should see:**
  ```text
  deployment.apps/web created
  ```

### Step 5.2: Check the Deployment

```powershell
kubectl get deployments
```

- **What it does:** Shows how many replicas you asked for and how many are ready.
- **You should see:** Wait until READY shows `3/3`:
  ```text
  NAME   READY   UP-TO-DATE   AVAILABLE   AGE
  web    3/3     3            3           45s
  ```

### Step 5.3: See Where the Pods Are Running

```powershell
kubectl get pods -o wide
```

- **What it does:** Lists the three Pods and the node each one was placed on.
- **You should see:** Under the NODE column, the Pods are spread over `kind-worker` and `kind-worker2`.

### Step 5.4: Inspect a Pod (Optional)

```powershell
kubectl describe pod <pod-name>
```

- **What it does:** Shows the details and history of one Pod. Replace `<pod-name>` with a real name copied from Step 5.3.
- **You should see:** Under Events at the bottom, a line confirming the Scheduler assigned the Pod to a worker node.

---

## Part 6 of 6: Scale the Pods and Test Self-Healing

Change how many copies you want, then delete one on purpose and watch Kubernetes put it back without being asked.

### Step 6.1: Scale from Three Pods to Six

```powershell
kubectl scale deployment web --replicas=6
```

- **What it does:** Changes the desired number of NGINX Pods from three to six.
- **You should see:**
  ```text
  deployment.apps/web scaled
  ```

### Step 6.2: Check the Six Pods

```powershell
kubectl get pods -o wide
```

- **What it does:** Shows all the Pods and the node each one was placed on.
- **You should see:** Six web Pods with STATUS `Running`, shared between the two workers.

### Step 6.3: Delete One Pod for the Test

```powershell
kubectl delete pod <pod-name>
```

- **What it does:** Deletes one Pod on purpose. Replace `<pod-name>` with a real web Pod name from Step 6.2.
- **You should see:** A line confirming that the Pod was deleted.

### Step 6.4: Confirm Self-Healing

```powershell
kubectl get pods
```

- **What it does:** Checks that Kubernetes created a replacement Pod to bring the Deployment back to six replicas.
- **You should see:** Six Pods again. The replacement has a new name and an AGE of only a few seconds.

---

## Lab Screenshots

The following actual screenshots document the completed lab steps:

### 1. Docker Verification (Steps 2.1 & 2.2)
![Docker Verification](screenshots/01_docker_engine_and_hello_world_verification.jpeg)
*Docker version check and running the hello-world container.*

### 2. Cluster Configuration File (Steps 3.3 & 3.4)
![Cluster Configuration](screenshots/02_kind_multi_node_cluster_configuration.jpeg)
*kind-config.yaml specifying 1 control-plane and 2 worker nodes.*

### 3. Cluster Creation & Node Status (Steps 4.1 – 4.3)
![Cluster Creation](screenshots/03_kind_cluster_creation_and_node_readiness.jpeg)
*kind cluster creation, cluster-info check, and three Ready nodes.*

### 4. Deploying NGINX & Scaling (Steps 5.1 & 5.2)
![Deploy NGINX](screenshots/04_nginx_deployment_creation_and_replica_scale_up.jpeg)
*Creating NGINX deployment and scaling to 3 replicas.*

### 5. Three Pods in Running State (Step 5.3)
![Three Pods Running](screenshots/05_three_nginx_pods_running.jpeg)
*Three NGINX Pods in 1/1 Running state.*

### 6. Node Health Verification (Step 4.3)
![Node Health](screenshots/06_three_node_cluster_status_verification.jpeg)
*Verifying control-plane and both worker nodes are Ready.*

### 7. Scaling to Six Pods (Steps 6.1 & 6.2)
![Scaling to 6](screenshots/07_scaling_nginx_deployment_to_six_replicas.jpeg)
*Scaling deployment to 6 replicas with all Pods Running.*

### 8. Full Session & Deployment Verification (Step 6.2)
![Full Lifecycle Verification](screenshots/08_deployment_scale_and_full_verification.jpeg)
*Full session verifying 6/6 available replicas.*

---

## What You Have Learned

- **Installed the tools:** WSL 2, Docker Desktop, kubectl and kind on Windows.
- **Built a cluster:** One control-plane node and two workers, all running as Docker containers.
- **Looked inside:** Saw the API server, scheduler, etcd and kube-proxy running as Pods.
- **Deployed an app:** Ran three NGINX Pods and saw which node each one was placed on.
- **Scaled and healed:** Went from 3 to 6 Pods and watched a deleted Pod come back by itself.

---

## If Something Goes Wrong

| What you see | What to do |
|:---|:---|
| Cannot connect to the Docker daemon or error during connect | Docker Desktop isn't running. Open it and wait for Engine running. |
| kubectl or kind is not recognized | Close every PowerShell window and open a new one (Step 1.5). |
| WSL 2 or virtualization missing | Run `wsl --install` as Administrator and restart. Turn on virtualization in BIOS/UEFI. |
| A node stays NotReady | Wait 1–2 minutes. Still stuck? Close other apps, run `kind delete cluster`, then repeat Step 4.1. |
| A Pod shows ImagePullBackOff | No internet or a typo in the image name. `kubectl describe pod <pod-name>` shows the exact error. |
| error parsing kind-config.yaml | The file has tabs or wrong spacing. Re-copy it exactly as shown in Step 3.4. |
| Commands hang or behave oddly in Git Bash | Use PowerShell instead. |

---

## Command Quick Reference

Every command from Steps 1–6, in the order you used them:

| Part | Command | What it does |
|:---|:---|:---|
| 1 | `wsl --install` | Install WSL 2 (as Administrator) |
| 1 | `winget install -e --id Kubernetes.kubectl` | Install kubectl |
| 1 | `winget install -e --id Kubernetes.kind` | Install kind |
| 2 | `docker version` | Check Docker client and server |
| 2 | `docker run hello-world` | Test that containers run |
| 2 | `kubectl version --client` | Check kubectl |
| 2 | `kind version` | Check kind |
| 3 | `mkdir k8s-lab` | Make the lab folder |
| 3 | `cd k8s-lab` | Go into the lab folder |
| 3 | `notepad kind-config.yaml` | Create the config file |
| 3 | `Get-ChildItem` | List files in the folder |
| 4 | `kind create cluster --config kind-config.yaml` | Build the 3-node cluster |
| 4 | `kubectl cluster-info --context kind-kind` | Check the connection |
| 4 | `kubectl get nodes` | List nodes and their status |
| 4 | `docker ps` | See the node containers |
| 4 | `kubectl get pods -n kube-system -o wide` | See the system Pods |
| 5 | `kubectl create deployment web --image=nginx --replicas=3` | Run 3 NGINX Pods |
| 5 | `kubectl get deployments` | Check desired vs ready replicas |
| 5 | `kubectl get pods -o wide` | See Pods and their nodes |
| 5 | `kubectl describe pod <pod-name>` | Details and events of one Pod |
| 6 | `kubectl scale deployment web --replicas=6` | Scale to 6 Pods |
| 6 | `kubectl delete pod <pod-name>` | Delete one Pod |
| 6 | `kubectl get pods` | Check the replacement Pod |
