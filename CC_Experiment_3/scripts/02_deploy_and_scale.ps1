<#
.SYNOPSIS
    Deploys NGINX workload and scales to 3 and 6 replicas.
#>
Write-Host "Creating NGINX Deployment..." -ForegroundColor Cyan
kubectl create deployment nginx --image=nginx

Write-Host "Scaling to 3 replicas..." -ForegroundColor Cyan
kubectl scale deployment nginx --replicas=3
kubectl rollout status deployment/nginx --timeout=90s
kubectl get pods -o wide

Write-Host "`nScaling to 6 replicas..." -ForegroundColor Cyan
kubectl scale deployment nginx --replicas=6
kubectl rollout status deployment/nginx --timeout=90s
kubectl get pods -o wide
kubectl get deployment nginx
