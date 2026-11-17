#!/usr/bin/env bash
# Bring up the monitoring lab: minikube + Metrics Server + Dashboard addon + php-apache.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Starting minikube"
minikube start

echo "==> Enabling Metrics Server and Dashboard addons"
minikube addons enable metrics-server
minikube addons enable dashboard

echo "==> Deploying php-apache"
kubectl apply -f "$ROOT/manifests/php-apache.yaml"
kubectl rollout status deployment/php-apache --timeout=300s
kubectl rollout status deployment/metrics-server -n kube-system --timeout=300s

echo "==> Waiting for Metrics Server to return data (can take 1-2 minutes)"
for _ in $(seq 1 40); do
  if kubectl top nodes >/dev/null 2>&1; then break; fi
  sleep 5
done

kubectl get nodes
kubectl get pods -A
kubectl top nodes || echo "Metrics not available yet - wait a bit and retry."
kubectl top pods  || true
echo
echo "Done. Open the Dashboard with: ./scripts/open-dashboard.sh"
