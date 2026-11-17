# Concepts and viva notes

Plain-language explanations of everything used in this experiment, followed by likely evaluation questions.

---

## 1. The experiment in one paragraph

A local Kubernetes cluster (minikube) was started, Metrics Server and the Dashboard were enabled so resource usage
could be seen, a sample app (`php-apache`) was deployed, usage was recorded at idle, load was generated with a
second pod, and usage was recorded again. The pod's CPU rose from 5m to 501m (its 500m limit) while the node
stayed at about 6% CPU, and `kubectl top` and the Dashboard showed the same numbers.

A restaurant analogy: the cluster is the kitchen, the app is the cook, the load is customers ordering, and
Metrics Server is the manager with a clipboard. `kubectl top` and the Dashboard are two ways of reading that same clipboard.

---

## 2. Concepts

**Kubernetes cluster / node.** A cluster is a set of machines (nodes) that run containers. minikube creates a
one-node cluster on your laptop.

**Pod.** The smallest deployable unit - a wrapper around one or more containers. `php-apache` and
`load-generator` are each one pod.

**Deployment.** Keeps a desired number of identical pods running and replaces them if they fail. `php-apache` is
a Deployment with 1 replica.

**Service.** A stable network name and address in front of pods. The load generator calls `http://php-apache`,
which the Service routes to the pod.

**Metrics Server.** A cluster add-on that collects current CPU and memory usage from each node's kubelet and serves
it through the Metrics API (`metrics.k8s.io`). It keeps no history and only tracks CPU and memory. `kubectl top`,
the Dashboard's usage figures, and the Horizontal Pod Autoscaler all rely on it.

**Kubernetes Dashboard.** A web UI for viewing and managing cluster resources. With Metrics Server running it
shows CPU and memory per pod and node.

**Millicores (m).** CPU units: 1000m = 1 core. 501m is about half a core.

**Mi (mebibyte).** Memory units. `kubectl top` reports the working-set memory of the container.

**Requests vs limits.**
- *Request*: the amount the scheduler reserves; used to decide where a pod can run.
- *Limit*: the maximum the container may use.
- Exceeding the **CPU limit** causes **throttling** (the container is slowed, usage plateaus at the limit).
- Exceeding the **memory limit** causes an **OOM kill** (the container is terminated and restarted).

**Load generator.** A `busybox` pod running `while true; do wget -q -O- http://php-apache; done`. It sends
requests back to back. The `OK!` it prints is the application's reply; the real work happens in the app pod.

---

## 3. How `kubectl top` and the Dashboard get their numbers

```
container -> kubelet (cAdvisor) -> Metrics Server -> Metrics API -> kubectl top
                                                              └──-> Dashboard
```

Because both read from the same source, their values match. Small differences appear when they sample at slightly
different moments, which is most noticeable at idle where values are tiny (5m vs 1.00m).

---

## 4. Likely evaluation questions

**What did you do?**
Set up a minikube cluster with Metrics Server and the Dashboard, deployed a CPU-intensive sample app, recorded pod and node
usage at idle, generated load, recorded usage again, and compared `kubectl top` with the Dashboard.

**Why do you need Metrics Server?**
Without it, `kubectl top` fails and the Dashboard has no CPU or memory data. It provides the resource metrics API.

**Where does Metrics Server get its data?**
From the kubelet on each node, which reads container statistics via cAdvisor.

**Does Metrics Server store history?**
No, only the latest values. Long-term history needs something like Prometheus.

**Why did you not write your own application?**
The lab asks to deploy "a sample application". `php-apache` is the standard Kubernetes example for resource and
autoscaling demos; it is CPU-bound by design, so load shows up clearly in the metrics.

**Why does a stream of `OK!` count as load?**
`OK!` is just the response. Each request makes the app run a CPU-heavy loop, which is why pod CPU went from 5m to 501m.

**Why did CPU stop increasing at about 500m?**
That is the container's CPU limit. Beyond it the container is throttled, so usage cannot rise further however much
more load is sent. Raising or removing the limit, or adding replicas, would allow more.

**Why did memory barely change?**
The app does not retain data between requests, so memory does not accumulate (8Mi to 13Mi, far below the 128Mi limit).

**Why did node usage barely change?**
The node has far more capacity than one half-core pod uses, so the node-level average stays low (about 6% CPU,
11% memory). Pod-level metrics are needed to see the saturation.

**Why are `kubectl top` and the Dashboard slightly different at times?**
They sample at slightly different moments and Metrics Server refreshes only periodically. Under load both showed 501m.

**What happens if a pod exceeds its CPU limit? Its memory limit?**
CPU: throttled. Memory: OOM-killed and restarted.

**Why is the CPU request (100m) a problem here?**
The app used about five times that. Requests drive scheduling, so a request far below real usage can lead to overcommitted
nodes. Monitoring data like this is used to right-size requests and limits.

**Why did the Helm install of the Dashboard fail?**
The upstream Dashboard project was archived and the chart repo URL returned 404. The Dashboard bundled with minikube
(`minikube dashboard`) was used instead.

**Why a single-node cluster? Would multi-node help?**
One node is enough because the goal is to observe usage change under load. A multi-node cluster would be useful for
studying scheduling and scaling across nodes, which is a different experiment.

**Is a GPU needed?**
No. Metrics Server reports only CPU and memory. GPU metrics need a separate exporter (for example NVIDIA DCGM).

**What would you do next?**
Add a Horizontal Pod Autoscaler (`manifests/optional/hpa.yaml`) so the cluster adds replicas when CPU is high, and add
Prometheus and Grafana for history and alerting.

**What are the limitations of your results?**
Values were sampled manually in a single run on a single node, the Dashboard's node page was not captured, and the
load was a single sequential loop. See the README's limitations section.
