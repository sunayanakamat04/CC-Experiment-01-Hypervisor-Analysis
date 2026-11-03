<#
.SYNOPSIS
    Step 6, 7, 8, 9, 10: Scale to 12 replicas, expose NodePort service, and test load balancing.
#>
param(
    [string]$ServiceManifest = "$PSScriptRoot\..\service.yaml"
)

Write-Host "Scaling deployment to 12 replicas..." -ForegroundColor Cyan
kubectl scale deployment resource-demo --replicas=12
kubectl rollout status deployment/resource-demo --timeout=90s

Write-Host "`nPod Distribution (12 Replicas):" -ForegroundColor Green
kubectl get pods -o wide

Write-Host "`nDeploying NodePort Service..." -ForegroundColor Cyan
kubectl apply -f (Resolve-Path $ServiceManifest).Path
kubectl get services
kubectl get endpoints nginx-service
kubectl get endpointslices

Write-Host "`nTesting Application Access on Port 30080:" -ForegroundColor Cyan
docker exec kind-control-plane curl -s -I http://172.20.0.3:30080

Write-Host "`nPost-Scaling Node Allocation:" -ForegroundColor Green
kubectl describe nodes | Select-String -Pattern "Name:", "Non-terminated Pods:", "  cpu ", "  memory " -Context 0, 4
