<#
.SYNOPSIS
    Step 3, 4, 5: Deploy resource-demo with requests/limits, analyze scheduling, and audit allocations.
#>
param(
    [string]$Manifest = "$PSScriptRoot\..\deployment.yaml"
)

Write-Host "Deploying resource-demo (6 replicas)..." -ForegroundColor Cyan
kubectl apply -f (Resolve-Path $Manifest).Path

Write-Host "Waiting for rollout..." -ForegroundColor Cyan
kubectl rollout status deployment/resource-demo --timeout=90s

Write-Host "`nPod Distribution (6 Replicas):" -ForegroundColor Green
kubectl get pods -o wide

Write-Host "`nScheduling Events:" -ForegroundColor Green
kubectl get events --sort-by=.metadata.creationTimestamp | Select-Object -Last 10

Write-Host "`nNode Allocation Analysis:" -ForegroundColor Green
kubectl describe nodes | Select-String -Pattern "Name:", "Non-terminated Pods:", "  cpu ", "  memory " -Context 0, 4
