# A©t0r Forensic Aggregator v2.0: Высокоскоростной анализ распределения
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$scanDirectory = "$projectPath"
$outputCsv = "$projectPath\terminal_stats.csv"

# Улучшенный паттерн: захватывает блок видимых цифр в конце маски (от 1 до 4 цифр)
$cardPattern = '(?:\*|x|X){4,19}[-\s]?(\d{1,4})\b'

Write-Host "A©t0r: Запуск высокоскоростного сканирования через Select-String..." -ForegroundColor Cyan

# Инициализация счетчиков 0-9
$stats = @{}
for ($i = 0; $i -le 9; $i++) { $stats[$i.ToString()] = 0 }

# Сбор целевых файлов
$filesToScan = Get-ChildItem -Path $scanDirectory -File -Recurse -Include *.json, *.jsonl, *.csv, *.txt, *.md, *.html -Exclude leaky_algorithm_matches.json, terminal_stats.csv

foreach ($file in $filesToScan) {
    # Select-String работает напрямую с потоком файла, выполняя поиск на уровне ядра
    $matchesInFile = Select-String -LiteralPath $file.FullName -Pattern $cardPattern -AllMatches -ErrorAction SilentlyContinue
    
    foreach ($match in $matchesInFile) {
        foreach ($subMatch in $match.Matches) {
            # Извлекаем захваченную группу цифр
            $digitsBlock = $subMatch.Groups[1].Value
            # Берем строго самый последний символ (терминальную цифру)
            $lastDigit = $digitsBlock[-1].ToString()
            
            $stats[$lastDigit]++
        }
    }
}

# Формируем объект данных для вывода и экспорта
$reportData = $stats.GetEnumerator() | Sort-Object Name | ForEach-Object {
    [PSCustomObject]@{
        TerminalDigit = $_.Name
        OccurrenceCount = $_.Value
        ScanTimestamp   = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
}

# Экспорт результатов в CSV-таблицу
$reportData | Export-Csv -Path $outputCsv -NoTypeInformation -Encoding utf8
Write-Host "Результаты успешно экспортированы в: $outputCsv" -ForegroundColor Yellow

# Дублирование итогов в консоль для оперативного контроля
Write-Host "`n--- Сводный реестр распределения ---" -ForegroundColor Yellow
foreach ($row in $reportData) {
    if ($row.OccurrenceCount -gt 0) {
        Write-Host "Цифра [$($row.TerminalDigit)]: $($row.OccurrenceCount) совпадений" -ForegroundColor White
    } else {
        Write-Host "Цифра [$($row.TerminalDigit)]: 0" -ForegroundColor Gray
    }
}
