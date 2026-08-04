# A©t0r State Injector для Restitution Target (JSONL Идемпотентный режим)
$projectPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
$registryFile = "$projectPath\ai_registry.json"
$targetHtml = "$projectPath\support.html"

if (-not (Test-Path $targetHtml)) {
    Write-Error "A©t0r Critical Error: support.html не найден по пути $targetHtml"
    exit
}

$currentCollected = 0.00

# Чтение и парсинг формата JSONL (выбираем последнюю валидную запись)
if (Test-Path $registryFile) {
    $lines = Get-Content $registryFile | Where-Object { $_.Trim() -ne "" }
    if ($lines) {
        $lastLine = $lines[-1]
        try {
            $registryData = ConvertFrom-Json $lastLine -ErrorAction Stop
            if ($null -ne $registryData.current_restitution_collected) {
                $currentCollected = $registryData.current_restitution_collected
            }
        } catch {
            Write-Warning "A©t0r Warning: Не удалось распарсить последнюю строку JSONL. Используется значение по умолчанию."
        }
    }
} else {
    Write-Warning "A©t0r Warning: Файл ai_registry.json отсутствует. Значение сброшено в 0.00."
}

# Принудительное форматирование в инвариантную культуру (с точкой вместо запятой для JS)
$currentCollectedJS = ($currentCollected -as [double]).ToString("F2", [System.Globalization.CultureInfo]::InvariantCulture)

# Чтение и обновление HTML кода на лету
$htmlContent = Get-Content $targetHtml -Raw

# Идемпотентный поиск паттерна переменной в JS блоке
if ($htmlContent -match 'let currentAmount = [0-9.]+;') {
    $htmlContent = $htmlContent -replace 'let currentAmount = [0-9.]+;', "let currentAmount = $currentCollectedJS;"
    $htmlContent | Set-Content $targetHtml -NoNewline
    Write-Host "A©t0r Success: Данные синхронизированы. Цель: 25.2M MDL. Текущий баланс: $currentCollectedJS MDL" -ForegroundColor Cyan
} else {
    Write-Error "A©t0r Critical: Точка инъекции 'let currentAmount = ...;' не найдена внутри support.html"
}
