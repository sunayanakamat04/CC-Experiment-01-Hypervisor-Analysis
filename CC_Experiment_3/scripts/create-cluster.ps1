<#
.SYNOPSIS
    Automates prerequisite validation and 3-node Kubernetes cluster creation using kind on Windows.
.DESCRIPTION
    Validates Docker Desktop, kind, and kubectl installations, checks configuration file existence,
    and spins up a 3-node Kubernetes cluster (1 control-plane and 2 worker nodes).
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "$PSScriptRoot\..\kind-config.yaml",
    [string]$ClusterName = "kind"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Kubernetes Cluster Initialization (kind on Windows)     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Docker Desktop daemon is active
Write-Host "`n[1/4] Checking Docker daemon status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker Desktop is not running. Please launch Docker Desktop and try again."
        exit 1
    }
    Write-Host "Docker is running." -ForegroundColor Green
} catch {
    Write-Error "Docker CLI is not accessible: $_"
    exit 1
}

# 2. Verify kind and kubectl tools
Write-Host "`n[2/4] Verifying kind and kubectl CLI tools..." -ForegroundColor Yellow
if (-not (Get-Command kind -ErrorAction SilentlyContinue)) {
    Write-Error "kind is not installed or not in PATH."
    exit 1
}
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "kubectl is not installed or not in PATH."
    exit 1
}
Write-Host "kind and kubectl binaries detected." -ForegroundColor Green

# 3. Verify configuration file
Write-Host "`n[3/4] Resolving cluster configuration..." -ForegroundColor Yellow
if (-not (Test-Path $ConfigFile)) {
    Write-Error "Configuration file not found at: $ConfigFile"
    exit 1
}
$resolvedConfig = (Resolve-Path $ConfigFile).Path
Write-Host "Using configuration: $resolvedConfig" -ForegroundColor Green

# 4. Create cluster
Write-Host "`n[4/4] Creating cluster '$ClusterName'..." -ForegroundColor Yellow
kind create cluster --name $ClusterName --config $resolvedConfig

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nCluster '$ClusterName' successfully created!" -ForegroundColor Green
    Write-Host "`nCluster Information:" -ForegroundColor Cyan
    kubectl cluster-info --context "kind-$ClusterName"
    Write-Host "`nNode Status:" -ForegroundColor Cyan
    kubectl get nodes -o wide
} else {
    Write-Error "Failed to create kind cluster."
    exit $LASTEXITCODE
}
