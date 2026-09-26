param(
    [Parameter(Mandatory=$true)]
    [string]$FileName,
    [string]$RepoPath = "C:\Evidence"
)

# 0. Авторизация (Локальный ключ A©t0r)
$SecureTrigger = Read-Host -Prompt "Введите секретное слово для подписи" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureTrigger)
$TriggerWord = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
if ($TriggerWord -cne "База Данных") { Write-Host "[ DENIED ]" -ForegroundColor Red; return }

# 1. Прямая загрузка ядра EvidenceVault
$ModuleFile = "$HOME\Documents\PowerShell\Modules\EvidenceVault\EvidenceVault.psm1"
if (Test-Path $ModuleFile) { Import-Module $ModuleFile -Force } else {
    Write-Host "[!] Ошибка: Ядро не найдено в $ModuleFile" -ForegroundColor Red; return
}

# 2. Конвейер TI-ULA (Облако + Резолвинг)
Write-Host "[*] Синхронизация бинарного потока..." -ForegroundColor Yellow
Update-EvidenceRegistry
Sync-EvidenceVault
Resolve-CloudLinks

# 3. Извлечение хэша
$TargetFile = Join-Path $RepoPath $FileName
if (-not (Test-Path $TargetFile)) { Write-Host "[ ERROR ] Файл $FileName не найден!" -ForegroundColor Red; return }
$sha = (Get-FileHash -Path $TargetFile -Algorithm SHA256).Hash.ToUpper()

# 4. Формирование Markdown по вашему эталону
$MdFileName = "$($FileName -replace '\.pdf$','').md"
$Markdown = @"
---
layout: default
title: "Evidence Node: $FileName"
date: $(Get-Date -Format "yyyy-MM-dd")
author: "A©tor Maceret Alexei ©"
categories: [evidence, ti-ula, hash-standard]
---

# 📜 ТЕХНОЛОГИЧЕСКИЙ МАНИФЕСТ A©t0r ©

**Автор:** A©tor Maceret Alexei ©  
**Статус:** Юридически значимый архив (Apostille Mirror)  
**Протокол:** TI-ULA (Hash-as-a-Link)

---

## 📂 ФИКСАЦИЯ ДОКАЗАТЕЛЬСТВ
- **Файл:** $FileName
- **SHA-256:** `$sha`

**Инструкция по извлечению подлинника:**
```powershell
Get-CloudFileByHash "$sha"
` ``

---

### 🚀 Использование
1. Установите модуль EvidenceVault.
2. Запустите скрипт одной строкой:
```powershell
.\Publish-EvidenceNode.ps1 -FileName "$FileName"
` ``

---
**Semnat:** **A©tor Maceret Alexei ©**
"@
$Markdown = $Markdown -replace '` ``', '```'

# 5. Деплой в GitHub (Все ветки)
Set-Content -Path (Join-Path $RepoPath $MdFileName) -Value $Markdown -Encoding UTF8
git add .
git commit -m "[A©t0r ©] SIGNED: New Evidence Node $sha" -q
$CurrentBranch = git branch --show-current
git push origin `$CurrentBranch

Write-Host "`n[ SUCCESS ] УЗЕЛ $sha ЗАФИКСИРОВАН И ОПУБЛИКОВАН!" -ForegroundColor Cyan
