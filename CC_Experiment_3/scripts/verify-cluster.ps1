<#
.SYNOPSIS
    Verifies Kubernetes cluster health, nodes, system Pods, and underlying Docker containers.
.DESCRIPTION
    Runs status checks across the kind control plane, worker nodes, kube-system Pods, and Docker containers.
#>

[CmdletBinding()]
param(
    [string]$ClusterContext = "kind-kind"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Kubernetes Cluster Health & Architecture Verification    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Cluster info
Write-Host "`n[1/4] Cluster Context & Control Plane Info:" -ForegroundColor Yellow
kubectl cluster-info --context $ClusterContext

# 2. Kubernetes Nodes
Write-Host "`n[2/4] Kubernetes Cluster Nodes (Role & Status):" -ForegroundColor Yellow
kubectl get nodes -o wide --context $ClusterContext

# 3. Docker Node Containers
Write-Host "`n[3/4] Underlying Docker Containers Running Kind Nodes:" -ForegroundColor Yellow
docker ps --filter "name=kind-" --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 4. Kube-System Pods
Write-Host "`n[4/4] Kubernetes System Pods (CoreDNS, etcd, kube-proxy, etc.):" -ForegroundColor Yellow
kubectl get pods -n kube-system -o wide --context $ClusterContext

Write-Host "`nVerification complete." -ForegroundColor Green
