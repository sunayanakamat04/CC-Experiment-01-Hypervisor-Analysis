<#
.SYNOPSIS
    Step 1 & Step 2: Verify cluster nodes and analyze initial metrics.
#>
Write-Host "Verifying cluster nodes..." -ForegroundColor Cyan
kubectl get nodes -o wide

Write-Host "`nChecking node metrics..." -ForegroundColor Cyan
kubectl top nodes

Write-Host "`nChecking Metrics Server status..." -ForegroundColor Cyan
kubectl get deployment metrics-server -n kube-system
