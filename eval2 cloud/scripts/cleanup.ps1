<#
.SYNOPSIS
  Remove the lab workloads. Add -DeleteCluster to also delete the minikube cluster.
#>
param([switch]$DeleteCluster)
$Root = Split-Path -Parent $PSScriptRoot
kubectl delete pod load-generator --ignore-not-found
kubectl delete -f "$Root\manifests\php-apache.yaml" --ignore-not-found
kubectl delete -f "$Root\manifests\optional\hpa.yaml" --ignore-not-found 2>$null
if ($DeleteCluster) { minikube delete } else { Write-Host "Cluster kept. Use -DeleteCluster to remove it, or 'minikube stop' to pause it." }
