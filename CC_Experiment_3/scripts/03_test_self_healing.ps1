<#
.SYNOPSIS
    Tests controller-driven self-healing by deleting one active Pod.
#>
$pod = (kubectl get pods -l app=nginx -o jsonpath="{.items[0].metadata.name}")
if (-not $pod) {
    Write-Error "No active NGINX pods found."
    exit 1
}

Write-Host "Triggering self-healing test by deleting pod: $pod" -ForegroundColor Yellow
kubectl delete pod $pod

Write-Host "Observing rapid reconciliation..." -ForegroundColor Cyan
kubectl get pods
Start-Sleep -Seconds 8
Write-Host "`nFinal steady state:" -ForegroundColor Green
kubectl get pods
kubectl get deployment nginx
