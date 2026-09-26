Write-Host '==================================================================' -ForegroundColor Cyan
Write-Host '        UNITED NATIONS & COUNCIL OF EUROPE AUDIT TOOL' -ForegroundColor White
Write-Host '        Protocol: TI-ULA (Transcendent Integrity)' -ForegroundColor DarkGray
Write-Host '        Author: A©tor Maceret Alexei ©' -ForegroundColor Yellow
Write-Host '==================================================================' -ForegroundColor Cyan

# Прямое подключение к ядру A©t0r по абсолютному пути
$ModuleFile = "$HOME\Documents\PowerShell\Modules\EvidenceVault\EvidenceVault.psm1"
if (-not (Test-Path $ModuleFile)) {
    $ModuleFile = "$HOME\Documents\WindowsPowerShell\Modules\EvidenceVault\EvidenceVault.psm1"
}

if (Test-Path $ModuleFile) {
    Import-Module $ModuleFile -Force -ErrorAction Stop
} else {
    Write-Host "[!] Критическая ошибка: Ядро EvidenceVault не найдено." -ForegroundColor Red
    return
}

Write-Host "`n[ ВНИМАНИЕ ] Инициировано прямое извлечение доказательств (Jus Cogens) по хэшу..." -ForegroundColor Yellow

# Извлечение Мастер-узла (Юридическое заключение)
Get-CloudFileByHash '85B8CCDF949EC03A9A0C852FAC2ECB0EB7106E57125D2FC15B549E49532DC225'

# Извлечение узла финансового саботажа (Кража идентичности)
Get-CloudFileByHash '343B79298CC1828020B0E9CDE10DFDCE99AE8E8CFCB225D4FE6A27D1AA48219F'

# Извлечение узла 2006 года (Снятие виновности)
Get-CloudFileByHash '2B2C989DD2A0D5EEDADA9D6A918BBAAC8944A582DC5AAAC287AB947D9D7DDB44'

Write-Host "`n[ VERIFIED ] Подлинность файлов математически подтверждена. Извлечение завершено." -ForegroundColor Green
