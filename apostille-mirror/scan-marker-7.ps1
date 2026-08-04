# A©t0r Forensic Scanner: Detect Anomaly Marker "7"
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$scanDirectory = "$projectPath"
$outputFile = "$projectPath\anomaly_marker_7_matches.json"

# Регулярное выражение: ищет маскированные карты, заканчивающиеся на '7'
$cardPattern = '(?:\*|x|X){4,19}[-\s]?\d{0,3}7\b'

Write-Host "A©t0r: Поиск аномального маркера '7'..." -ForegroundColor Cyan

$matchesFound = @()
$filesToScan = Get-ChildItem -Path $scanDirectory -File -Recurse -Include *.json, *.jsonl, *.csv, *.txt, *.md, *.html -Exclude leaky_algorithm_matches.json, terminal_stats.csv, anomaly_marker_7_matches.json

foreach ($file in $filesToScan) {
    $lineNumber = 1
    try {
        # Using Select-String to find the specific pattern
        $results = Select-String -LiteralPath $file.FullName -Pattern $cardPattern -AllMatches -ErrorAction SilentlyContinue
        foreach ($res in $results) {
            foreach ($m in $res.Matches) {
                $matchesFound += [PSCustomObject]@{
                    Timestamp      = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                    SourceFile     = $file.FullName.Replace($projectPath, "")
                    LineNumber     = $res.LineNumber
                    MatchedMask    = $m.Value
                    RawContext     = $res.Line.Trim() -replace '(?s)\s+', ' '
                    MarkerSuspect  = $true
                }
            }
        }
    } catch { }
}

if ($matchesFound.Count -gt 0) {
    Write-Host "Обнаружено совпадений для '7': $($matchesFound.Count)" -ForegroundColor Red
    $matchesFound | ConvertTo-Json -Depth 3 | Set-Content $outputFile
} else {
    Write-Host "Совпадений для '7' не найдено." -ForegroundColor Green
}
