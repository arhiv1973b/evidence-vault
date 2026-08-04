$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$suspectPattern = "\b0?69[- ]?292[- ]?927\b"

Write-Host "A©t0r: Инициализация точечного сканирования по маркеру суспекта [$suspectPattern]..." -ForegroundColor Cyan

$filesToScan = Get-ChildItem -LiteralPath $projectPath -File -Recurse -Include *.json, *.jsonl, *.csv, *.txt, *.md, *.html -Exclude leaky_algorithm_matches.json -ErrorAction SilentlyContinue

$foundMatches = @()

foreach ($file in $filesToScan) {
    $match = Select-String -LiteralPath $file.FullName -Pattern $suspectPattern -ErrorAction SilentlyContinue
    if ($match) {
        $foundMatches += $match
    }
}

if ($foundMatches.Count -gt 0) {
    Write-Host "`n[CRITICAL] Обнаружены прямые следы присутствия суспекта в логах! ($($foundMatches.Count) совп.)" -ForegroundColor Red
    foreach ($m in $foundMatches) {
        $shortPath = $m.Path.Replace($projectPath, "")
        Write-Host "-> Лог: $shortPath [Строка $($m.LineNumber)]: " -NoNewline -ForegroundColor Yellow
        Write-Host "$($m.Line.Trim())" -ForegroundColor White
    }
} else {
    Write-Host "`n[✓] Сканирование завершено. Прямых текстовых совпадений для 069292927 не обнаружено." -ForegroundColor Green
    Write-Host "Контур чист на уровне открытых текстовых манифестов." -ForegroundColor Gray
}
