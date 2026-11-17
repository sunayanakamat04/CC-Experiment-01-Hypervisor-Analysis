<#
.SYNOPSIS
  Bring up the monitoring lab: minikube + Metrics Server + Dashboard addon + php-apache.
.USAGE
  .\scripts\setup.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Starting minikube" -ForegroundColor Cyan
minikube start

Write-Host "==> Enabling Metrics Server and Dashboard addons" -ForegroundColor Cyan
minikube addons enable metrics-server
minikube addons enable dashboard

Write-Host "==> Deploying php-apache" -ForegroundColor Cyan
kubectl apply -f "$Root\manifests\php-apache.yaml"
kubectl rollout status deployment/php-apache --timeout=300s
kubectl rollout status deployment/metrics-server -n kube-system --timeout=300s

Write-Host "==> Waiting for Metrics Server to return data (can take 1-2 minutes)" -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    kubectl top nodes 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 5
}
if (-not $ready) { Write-Warning "Metrics not available yet - wait a bit and run 'kubectl top nodes' manually." }

kubectl get nodes
kubectl get pods -A
kubectl top nodes
kubectl top pods
Write-Host "`nDone. Open the Dashboard with:  .\scripts\open-dashboard.ps1" -ForegroundColor Green
