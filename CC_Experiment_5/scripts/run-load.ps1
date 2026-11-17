<#
.SYNOPSIS
  Start the load generator (loops HTTP requests against the php-apache Service).
.USAGE
  .\scripts\run-load.ps1          # start load in the background
  .\scripts\run-load.ps1 -Stop    # stop it
#>
param([switch]$Stop)
$Root = Split-Path -Parent $PSScriptRoot

if ($Stop) {
    kubectl delete pod load-generator --ignore-not-found
    return
}
kubectl delete pod load-generator --ignore-not-found | Out-Null
kubectl apply -f "$Root\manifests\load-generator.yaml"
kubectl wait --for=condition=Ready pod/load-generator --timeout=180s
Write-Host "Load generator running. Give Metrics Server ~1-2 minutes, then run: kubectl top pods" -ForegroundColor Green
