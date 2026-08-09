# collect_master_text.ps1
$ReportPath = "H:\ACTOR_DEV_ENV\master_forensic_data\OCR_AUDIT_REPORT.json"
$OutputDir = "H:\ACTOR_DEV_ENV\master_forensic_data"
$OutputFile = Join-Path $OutputDir "MASTER_FORENSIC_TEXT_V1.txt"
$Report = Get-Content $ReportPath | ConvertFrom-Json

# Исключаем страницы по списку и порогу точности
$ExcludedPages = @(3, 5, 8)

$MasterText = ""

Write-Host "[SOCKET] Начинаю сборку Мастер-текста..." -ForegroundColor Cyan

foreach ($Entry in $Report) {
    if ($ExcludedPages -contains $Entry.page) {
        Write-Host "Пропуск страницы $($Entry.page) (в списке исключений)" -ForegroundColor Yellow
        continue
    }
    
    if ($Entry.accuracy -lt 70) {
        Write-Host "Пропуск страницы $($Entry.page) (точность $($Entry.accuracy)%)" -ForegroundColor Yellow
        continue
    }

    # Читаем текст страницы
    $PageJsonPath = Join-Path "H:\ACTOR_DEV_ENV" ("page_" + $Entry.page + ".json")
    if (Test-Path $PageJsonPath) {
        $PageData = Get-Content $PageJsonPath -Raw | ConvertFrom-Json
        $MasterText += "`n`n--- СТРАНИЦА $($Entry.page) ---`n`n"
        $MasterText += $PageData.raw_text
        Write-Host "Добавлена страница $($Entry.page)" -ForegroundColor Green
    }
}

$MasterText | Out-File -FilePath $OutputFile -Encoding utf8
Write-Host "Мастер-текст успешно собран в $OutputFile" -ForegroundColor Cyan
