param ([string]$Prompt = "Проверка связи. Контур активен.")

# Директива: Использование каскадного шлюза A©t0r (gemini.ps1)
# Это обеспечивает соблюдение Identity Protection и Cascade Routing (Local-First).

$gatewayPath = Join-Path $PSScriptRoot "gemini.ps1"

if (-not (Test-Path $gatewayPath)) {
    Write-Error "Критическая ошибка: Шлюз $gatewayPath не найден."
    exit 1
}

# Подготовка расширенного промпта для сохранения контекста аудита
$fullPrompt = @"
СИСТЕМНАЯ ИНСТРУКЦИЯ (Форензик-Контур A©tor v6.1):
Проведи аудит по делу CASE-MACHERET-1997-2026.
Принимай манифесты, логи, структуры реестров.
Цель: Фиксация целостности (INTEGRITY_LOCKED).

ЗАПРОС:
$Prompt
"@

try {
    # Вызов каскадного шлюза. 
    # Если требуется эскалация до внешнего API, промпт должен содержать NEED_GEMINI.
    $response = powershell -NoProfile -File $gatewayPath -Prompt $fullPrompt
    return $response
} catch {
    Write-Error "Сбой в контуре A©t0r при обработке запроса: $_"
}

