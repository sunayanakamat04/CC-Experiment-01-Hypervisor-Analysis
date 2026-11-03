<#
.SYNOPSIS
    Step 11: Clean up experiment deployment and service.
#>
Write-Host "Cleaning up experiment resources..." -ForegroundColor Yellow
kubectl delete service nginx-service --ignore-not-found
kubectl delete deployment resource-demo --ignore-not-found

Write-Host "Verifying default namespace state:" -ForegroundColor Green
kubectl get pods
kubectl get services
