# A©t0r Forensic Timeline Aggregator
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$timelineFile = "$projectPath\FORENSIC_TIMELINE_20260611.json"

$events = @()

# 1. Извлечение событий из реестра (ai_registry.json - формат JSONL)
if (Test-Path "$projectPath\ai_registry.json") {
    Get-Content "$projectPath\ai_registry.json" | ForEach-Object {
        try {
            $data = $_ | ConvertFrom-Json
            if ($null -ne $data.timestamp) {
                $events += [PSCustomObject]@{
                    Timestamp = $data.timestamp
                    Type      = "REGISTRY_EVENT"
                    Detail    = "Balance: $($data.current_restitution_collected) MDL"
                    Source    = "ai_registry.json"
                }
            }
        } catch {}
    }
}

# 2. Извлечение маркеров Apple (apple_device_links.json)
if (Test-Path "$projectPath\apple_device_links.json") {
    $data = Get-Content "$projectPath\apple_device_links.json" | ConvertFrom-Json
    foreach ($item in $data) {
        $events += [PSCustomObject]@{
            Timestamp = $item.Timestamp
            Type      = "APPLE_SESSION"
            Detail    = "Signature: $($item.MatchedSign) in $($item.SourceFile)"
            Source    = "apple_device_links.json"
        }
    }
}

# 3. Извлечение аномалий (Marker 7 и 9)
$anomalyFiles = @("leaky_algorithm_matches.json", "anomaly_marker_7_matches.json")
foreach ($file in $anomalyFiles) {
    if (Test-Path "$projectPath\$file") {
        $data = Get-Content "$projectPath\$file" | ConvertFrom-Json
        foreach ($item in $data) {
            $events += [PSCustomObject]@{
                Timestamp = $item.Timestamp
                Type      = "MARKER_ANOMALY"
                Detail    = "Match: $($item.MatchedMask) in $($item.SourceFile)"
                Source    = $file
            }
        }
    }
}

# Сортировка по времени и экспорт
if ($events.Count -gt 0) {
    $events | Sort-Object Timestamp | ConvertTo-Json -Depth 3 | Set-Content $timelineFile
    Write-Host "A©t0r Success: Сводная хронология сформирована и сохранена в: $timelineFile" -ForegroundColor Cyan
    Write-Host "Всего событий в цепочке: $($events.Count)" -ForegroundColor Yellow
} else {
    Write-Warning "A©t0r Warning: Событий для формирования хронологии не обнаружено."
}
