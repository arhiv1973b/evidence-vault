# A©t0r Forensic Tool: Apple Ecosystem & Pay Token Identifier
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"

# Сигнатурные паттерны: учетные записи, платежные маркеры, идентификаторы среды
$applePatterns = @(
    '\b[A-Za-z0-9._%+-]+@(icloud|me|mac)\.com\b',       # Электронная почта / Apple ID
    'Apple[- ]?Pay',                                    # Платежная система
    '\b(DPAN|DAN|Tokenized|DeviceAccount)\b',           # Специфика токенизации карт в Wallet
    '\b(iPhone|iPad|iOS|Macintosh|Darwin)\b',           # Аппаратные маркеры и User-Agent
    'com\.apple\.[a-zA-Z0-9\.]+'                        # Системные идентификаторы / метаданные
)

$combinedPattern = $applePatterns -join '|'

Write-Host "A©t0r: Запуск инспекции связи с устройствами и сервисами Apple..." -ForegroundColor Cyan

$filesToScan = Get-ChildItem -LiteralPath $projectPath -File -Recurse -Include *.json, *.jsonl, *.csv, *.txt, *.md, *.html -Exclude leaky_algorithm_matches.json, terminal_stats.csv -ErrorAction SilentlyContinue

$appleMatches = @()

foreach ($file in $filesToScan) {
    # Поиск на уровне ядра Select-String с защитой путей через -LiteralPath
    $matchesInFile = Select-String -LiteralPath $file.FullName -Pattern $combinedPattern -AllMatches -ErrorAction SilentlyContinue
    
    foreach ($match in $matchesInFile) {
        foreach ($subMatch in $match.Matches) {
            $appleMatches += [PSCustomObject]@{
                Timestamp   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                SourceFile  = $file.FullName.Replace($projectPath, "")
                LineNumber  = $match.LineNumber
                MatchedSign = $subMatch.Value
                Context     = $match.Line.Trim() -replace '(?s)\s+', ' '
            }
        }
    }
}

$outputFile = "$projectPath\apple_device_links.json"

if ($appleMatches.Count -gt 0) {
    Write-Host "`n[CRITICAL] Обнаружены следы взаимодействия с экосистемой Apple! ($($appleMatches.Count) вхожд.)" -ForegroundColor Red
    $appleMatches | ConvertTo-Json -Depth 3 | Set-Content $outputFile
    
    # Краткий вывод структуры совпадений в консоль
    $appleMatches | Group-Object MatchedSign | Sort-Object Count -Descending | ForEach-Object {
        Write-Host "-> Сигнатура [$($_.Name)]: $($_.Count) совпадений" -ForegroundColor Yellow
    }
    Write-Host "`nПолный форензик-отчет сохранен в: $outputFile" -ForegroundColor Yellow
} else {
    Write-Host "`n[✓] Сканирование завершено. Прямых признаков присутствия Apple-идентификаторов не обнаружено." -ForegroundColor Green
    Write-Host "Контур чист от открытых аппаратных маркеров iOS/Wallet." -ForegroundColor Gray
}
