# 🛡️ ФОРЕНЗИК-АУДИТ ТРАНЗАКЦИЙ: CASE-MACHERET-1997-2026
param (
    [string]$CsvPath = "C:\Users\arhiv\apostille-mirror-work\financial_logs\statement.csv",
    [string]$OutPath = "C:\Users\arhiv\apostille-mirror-work\financial_logs\AUDIT_REPORT.json"
)

Write-Host "Иницианизация проверки финансового шлюза..." -ForegroundColor Cyan

if (-Not (Test-Path $CsvPath)) {
    Write-Host "Файл выписки $CsvPath не найден. Поместите CSV файл в директорию." -ForegroundColor Red
    exit
}

$transactions = Import-Csv -Path $CsvPath -Delimiter "," # Настройте разделитель под формат вашего банка
$auditResults = @()
$sabotageFlags = 0

foreach ($tx in $transactions) {
    $amount = [decimal]$tx.Amount
    $description = $tx.Description.ToLower()
    $date = $tx.Date

    # Проверка на саботаж (скрытые комиссии, штрафы, списания, маркеры 555)
    if ($amount -lt 0 -and ($description -match "comision|penalitate|incaso|amenda|555")) {
        Write-Host "🚨 ОБНАРУЖЕНА АНОМАЛИЯ/САБОТАЖ: $date | $description | $amount" -ForegroundColor Red
        $sabotageFlags++
        $auditResults += [pscustomobject]@{
            Date = $date
            Type = "SABOTAGE_FLAG"
            Details = $description
            Amount = $amount
        }
    }
    # Проверка на успешный донат/поступление
    elseif ($amount -gt 0) {
        Write-Host "✅ ПОСТУПЛЕНИЕ СРЕДСТВ: $date | $amount MDL" -ForegroundColor Green
        $auditResults += [pscustomobject]@{
            Date = $date
            Type = "SUPPORT_RECEIVED"
            Details = "Incoming transaction verified"
            Amount = $amount
        }
    }
}

$finalReport = @{
    AuditDate = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    IntegrityStatus = if ($sabotageFlags -gt 0) { "COMPROMISED - SABOTAGE DETECTED" } else { "SECURE" }
    TotalSabotageEvents = $sabotageFlags
    Records = $auditResults
}

$finalReport | ConvertTo-Json -Depth 5 | Out-File -FilePath $OutPath -Encoding UTF8
Write-Host "Отчет об аудите сохранен: $OutPath" -ForegroundColor Cyan
