#!/usr/bin/env bash
# Remove the lab workloads. Pass --delete-cluster to also delete the minikube cluster.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
kubectl delete pod load-generator --ignore-not-found
kubectl delete -f "$ROOT/manifests/php-apache.yaml" --ignore-not-found
kubectl delete -f "$ROOT/manifests/optional/hpa.yaml" --ignore-not-found 2>/dev/null
if [ "${1:-}" = "--delete-cluster" ]; then minikube delete; else echo "Cluster kept. Use --delete-cluster to remove it, or 'minikube stop' to pause it."; fi
