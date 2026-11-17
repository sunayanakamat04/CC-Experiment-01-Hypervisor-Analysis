#!/usr/bin/env bash
# Sample 'kubectl top' at a fixed interval and write timestamped rows to a CSV.
#   ./scripts/collect-metrics.sh [interval_seconds=10] [duration_seconds=300] [out_file]
# Then: python analysis/plot_timeseries.py
set -uo pipefail
INTERVAL="${1:-10}"
DURATION="${2:-300}"
OUT="${3:-$(cd "$(dirname "$0")/.." && pwd)/data/timeseries.csv}"

to_m() {   # 501m -> 501 ; 1 (cores) -> 1000
  case "$1" in
    *m) echo "${1%m}" ;;
    *)  awk -v v="$1" 'BEGIN{printf "%d", v*1000}' ;;
  esac
}
to_mi() {  # Ki/Mi/Gi -> MiB
  case "$1" in
    *Ki) awk -v v="${1%Ki}" 'BEGIN{printf "%.2f", v/1024}' ;;
    *Mi) echo "${1%Mi}" ;;
    *Gi) awk -v v="${1%Gi}" 'BEGIN{printf "%.0f", v*1024}' ;;
    *)   echo "$1" ;;
  esac
}

echo "timestamp,scope,name,cpu_millicores,memory_mib,cpu_percent,memory_percent" > "$OUT"
end=$(( $(date +%s) + DURATION ))
echo "Sampling every ${INTERVAL}s for ${DURATION}s -> $OUT (Ctrl+C to stop early)"

while [ "$(date +%s)" -lt "$end" ]; do
  ts=$(date +"%Y-%m-%dT%H:%M:%S")
  { kubectl top pods --no-headers 2>/dev/null || true; } | while read -r name cpu mem _; do
    [ -n "${name:-}" ] && echo "$ts,pod,$name,$(to_m "$cpu"),$(to_mi "$mem"),,"
  done >> "$OUT"
  { kubectl top nodes --no-headers 2>/dev/null || true; } | while read -r name cpu cpup mem memp _; do
    [ -n "${name:-}" ] && echo "$ts,node,$name,$(to_m "$cpu"),$(to_mi "$mem"),${cpup%\%},${memp%\%}"
  done >> "$OUT"
  sleep "$INTERVAL"
done
echo "Done. Rows written to $OUT"
