<#
.SYNOPSIS
    Scales the NGINX deployment to a specified number of replicas.
.DESCRIPTION
    Updates replica count for deployment 'nginx', awaits rollout status,
    and displays updated Pod distribution across the cluster worker nodes.
#>

[CmdletBinding()]
param(
    [int]$Replicas = 6
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Scaling NGINX Deployment & Verification                  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`nScaling deployment 'nginx' to $Replicas replicas..." -ForegroundColor Yellow
kubectl scale deployment nginx --replicas=$Replicas

Write-Host "`nAwaiting rollout completion..." -ForegroundColor Yellow
kubectl rollout status deployment/nginx --timeout=120s

Write-Host "`nUpdated Deployment Status:" -ForegroundColor Cyan
kubectl get deployments nginx

Write-Host "`nUpdated Pods and Node Placement:" -ForegroundColor Cyan
kubectl get pods -l app=nginx -o wide

Write-Host "`nScale operation completed successfully." -ForegroundColor Green
