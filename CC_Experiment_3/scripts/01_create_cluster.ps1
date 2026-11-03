<#
.SYNOPSIS
    Automates multi-node Kubernetes cluster creation using kind on Windows.
#>
param(
    [string]$ConfigPath = "$PSScriptRoot\..\kind-config.yaml"
)

Write-Host "Verifying Docker Desktop..." -ForegroundColor Cyan
docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker Desktop is not active. Please launch Docker Desktop."
    exit 1
}

Write-Host "Creating 3-node cluster from $ConfigPath..." -ForegroundColor Cyan
kind create cluster --config (Resolve-Path $ConfigPath).Path

Write-Host "`nCluster Info:" -ForegroundColor Green
kubectl cluster-info --context kind-kind

Write-Host "`nNode Status:" -ForegroundColor Green
kubectl get nodes -o wide
