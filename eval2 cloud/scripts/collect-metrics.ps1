<#
.SYNOPSIS
  Sample 'kubectl top' at a fixed interval and append timestamped rows to a CSV.
.USAGE
  .\scripts\collect-metrics.ps1                          # every 10 s for 5 min
  .\scripts\collect-metrics.ps1 -IntervalSeconds 15 -DurationSeconds 600
  Then:  python analysis\plot_timeseries.py
#>
param(
    [int]$IntervalSeconds = 10,
    [int]$DurationSeconds = 300,
    [string]$OutFile = (Join-Path (Split-Path -Parent $PSScriptRoot) "data\timeseries.csv")
)

function ConvertTo-Millicores([string]$v) {
    if ($v -match '^(\d+)m$') { return [int]$Matches[1] }
    return [int]([double]$v * 1000)
}
function ConvertTo-MiB([string]$v) {
    if ($v -match '^([\d\.]+)Ki$') { return [math]::Round([double]$Matches[1] / 1024, 2) }
    if ($v -match '^([\d\.]+)Mi$') { return [double]$Matches[1] }
    if ($v -match '^([\d\.]+)Gi$') { return [double]$Matches[1] * 1024 }
    return $v
}

"timestamp,scope,name,cpu_millicores,memory_mib,cpu_percent,memory_percent" | Out-File $OutFile -Encoding ascii
$end = (Get-Date).AddSeconds($DurationSeconds)
Write-Host "Sampling every $IntervalSeconds s for $DurationSeconds s -> $OutFile (Ctrl+C to stop early)"

while ((Get-Date) -lt $end) {
    $ts = (Get-Date).ToString("s")

    # kubectl top pods --no-headers  ->  NAME CPU MEM
    kubectl top pods --no-headers 2>$null | ForEach-Object {
        $p = @($_ -split '\s+' | Where-Object { $_ })
        if ($p.Count -ge 3) {
            "$ts,pod,$($p[0]),$(ConvertTo-Millicores $p[1]),$(ConvertTo-MiB $p[2]),," | Add-Content $OutFile -Encoding ascii
        }
    }

    # kubectl top nodes --no-headers ->  NAME CPU CPU% MEM MEM%
    kubectl top nodes --no-headers 2>$null | ForEach-Object {
        $p = @($_ -split '\s+' | Where-Object { $_ })
        if ($p.Count -ge 5) {
            "$ts,node,$($p[0]),$(ConvertTo-Millicores $p[1]),$(ConvertTo-MiB $p[3]),$($p[2].TrimEnd('%')),$($p[4].TrimEnd('%'))" | Add-Content $OutFile -Encoding ascii
        }
    }
    Start-Sleep -Seconds $IntervalSeconds
}
Write-Host "Done. Rows written to $OutFile" -ForegroundColor Green
