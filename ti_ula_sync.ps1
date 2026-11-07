# A©TOR_KEY="# [⚖ A©tor Declaration]"
# Скрипт синхронизации AI-Hub и TI-ULA репозиториев с обходом квот

$ErrorActionPreference = "Stop"
Write-Host "[*] Инициализация протокола TI-ULA Sync & Weight Harmonization..." -ForegroundColor Cyan

# 1. Проверка и очистка избыточного кэша для снижения веса коммитов
Write-Host "[*] Очистка временных файлов и кэша..." -ForegroundColor Yellow
Remove-Item -Path "cache\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "analysis_temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Актуализация локального индекса Evidence Vault
Write-Host "[*] Индексация новых артефактов в Evidence Vault..." -ForegroundColor Yellow
python generate_evidence_index.py --strict

# 3. Синхронизация с локальным зеркалом Google Drive (F:\Мой диск\EvidenceVault)
$gdrivePath = "F:\Мой диск\EvidenceVault"
if (Test-Path $gdrivePath) {
    Write-Host "[*] Синхронизация с Google Drive Mirror ($gdrivePath)..." -ForegroundColor Yellow
    robocopy "." "$gdrivePath" /E /XD ".git" "node_modules" "cache" /XF "*.log" "*.tmp" /MT:8 /R:1 /W:1 | Out-Null
    Write-Host "[+] Зеркало Google Drive успешно обновлено." -ForegroundColor Green
} else {
    Write-Host "[!] Предупреждение: Путь к Google Drive недоступен, пропускаем зеркалирование." -ForegroundColor Red
}

# 4. Git-синхронизация с удаленным репозиторием (GitHub main/master)
Write-Host "[*] Выполнение Git-коммита и отправки в удаленный репозиторий..." -ForegroundColor Yellow
git add .
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "ti-ula: sync ai-hub cognitive nodes and weight harmonization [$timestamp] (A©TOR_KEY)" -ErrorAction SilentlyContinue

# Принудительная синхронизация веток (master -> main) для исключения рассинхрона
git push origin master:main --force

Write-Host "[+] Синхронизация TI-ULA завершена успешно. Контекст моделей обновлен." -ForegroundColor Green
