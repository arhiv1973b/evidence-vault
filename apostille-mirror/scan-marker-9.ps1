# A©t0r Forensic Scanner: Detect Compromised Card Marker "9"
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$scanDirectory = "$projectPath" # Scoping to the full project for maximum detection
$outputFile = "$projectPath\leaky_algorithm_matches.json"

# Регулярное выражение: ищет маскированные карты, где последняя из 4 видимых цифр — это '9'.
# Поддерживает форматы: **** **** **** 1239, ******XXXXXX1239, ************1239, и т.д.
$cardPattern = '(?:\*|x|X){4,15}[-\s]?\d{3}9\b'

Write-Host "A©t0r: Инициализация поиска маркера '9' в транзакциях..." -ForegroundColor Cyan

$matchesFound = @()
$filesToScan = Get-ChildItem -Path $scanDirectory -File -Recurse -Include *.json, *.jsonl, *.csv, *.txt, *.md, *.html -Exclude leaky_algorithm_matches.json

foreach ($file in $filesToScan) {
    $lineNumber = 1
    try {
        foreach ($line in Get-Content $file.FullName -ErrorAction SilentlyContinue) {
            if ($line -match $cardPattern) {
                $matchedCard = $matches[0]
                
                # Структурируем находку для реестра доказательств
                $matchesFound += [PSCustomObject]@{
                    Timestamp      = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                    SourceFile     = $file.FullName.Replace($projectPath, "")
                    LineNumber     = $lineNumber
                    MatchedMask    = $matchedCard
                    RawContext     = $line.Trim() -replace '(?s)\s+', ' '
                    MarkerSuspect  = $true
                }
            }
            $lineNumber++
        }
    } catch {
        # Skip files that cannot be read
    }
}

$totalMatches = $matchesFound.Count

if ($totalMatches -gt 0) {
    Write-Host "Обнаружено совпадений: $totalMatches" -ForegroundColor Red
    $matchesFound | ConvertTo-Json -Depth 3 | Set-Content $outputFile
    Write-Host "Детализированный лог сохранен в: $outputFile" -ForegroundColor Yellow
} else {
    Write-Host "Совпадений с терминальным маркером '9' в указанной директории не найдено." -ForegroundColor Green
}
