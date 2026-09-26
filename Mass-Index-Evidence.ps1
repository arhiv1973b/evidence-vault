param(
    [string]$SourcePath = "H:\Загрузки",
    [string]$DestPath = "C:\Evidence"
)

# 0. Авторизация A©t0r
$SecureTrigger = Read-Host -Prompt "Введите секретное слово для массовой подписи (База Данных)" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureTrigger)
$TriggerWord = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
if ($TriggerWord -cne "База Данных") { Write-Host "[ DENIED ]" -ForegroundColor Red; return }

# 1. Поиск файлов
$Files = Get-ChildItem -Path $SourcePath -Filter *.pdf
if ($Files.Count -eq 0) {
    Write-Host "[!] В папке $SourcePath PDF-файлы не найдены." -ForegroundColor Yellow
    return
}

Write-Host "`n[*] Найдено файлов для индексации: $($Files.Count)" -ForegroundColor Cyan

# 2. Цикл обработки
foreach ($File in $Files) {
    Write-Host "`n>>> ОБРАБОТКА: $($File.Name) <<<" -ForegroundColor Yellow
    
    # Перенос в рабочую папку (если его там нет)
    $FinalTarget = Join-Path $DestPath $File.Name
    if (-not (Test-Path $FinalTarget)) {
        Copy-Item $File.FullName $DestPath
        Write-Host "[ + ] Файл скопирован в рабочий контур." -ForegroundColor DarkGray
    }

    # Запуск вашего автономного скрипта публикации
    & "C:\Evidence\Publish-EvidenceNode.ps1" -FileName $File.Name
}

# 3. Финальный глобальный пуш
Write-Host "`n[*] Финализация: Глобальная синхронизация с GitHub..." -ForegroundColor Cyan
git push origin master

Write-Host "`n[ TOTAL SUCCESS ] Все файлы проиндексированы и запечатаны в Erga Omnes!" -ForegroundColor Green
