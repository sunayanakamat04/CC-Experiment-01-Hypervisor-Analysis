<#
.SYNOPSIS
    Deploys NGINX to the Kubernetes cluster and scales to 3 replicas.
.DESCRIPTION
    Creates a Kubernetes deployment named 'nginx' using the official nginx image,
    scales it to 3 replicas, waits for rollout, and outputs Pod placement across worker nodes.
#>

[CmdletBinding()]
param(
    [string]$Image = "nginx",
    [int]$InitialReplicas = 3
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " NGINX Workload Deployment (Kubernetes on Windows)       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Create Deployment
Write-Host "`n[1/3] Creating NGINX deployment..." -ForegroundColor Yellow
$existing = kubectl get deployment nginx --ignore-not-found 2>&1
if ($existing) {
    Write-Host "Deployment 'nginx' already exists." -ForegroundColor Cyan
} else {
    kubectl create deployment nginx --image=$Image
}

# 2. Scale to 3 replicas
Write-Host "`n[2/3] Scaling deployment 'nginx' to $InitialReplicas replicas..." -ForegroundColor Yellow
kubectl scale deployment nginx --replicas=$InitialReplicas

# 3. Wait for rollout and show status
Write-Host "`n[3/3] Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl rollout status deployment/nginx --timeout=120s

Write-Host "`nDeployment Status:" -ForegroundColor Cyan
kubectl get deployments nginx

Write-Host "`nPod Status and Worker Node Placement:" -ForegroundColor Cyan
kubectl get pods -l app=nginx -o wide
