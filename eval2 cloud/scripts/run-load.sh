#!/usr/bin/env bash
# Start the load generator:  ./scripts/run-load.sh
# Stop it:                   ./scripts/run-load.sh stop
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ "${1:-}" = "stop" ]; then
  kubectl delete pod load-generator --ignore-not-found
  exit 0
fi
kubectl delete pod load-generator --ignore-not-found >/dev/null
kubectl apply -f "$ROOT/manifests/load-generator.yaml"
kubectl wait --for=condition=Ready pod/load-generator --timeout=180s
echo "Load generator running. Give Metrics Server ~1-2 minutes, then run: kubectl top pods"
