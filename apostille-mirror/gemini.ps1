param ([string]$Prompt)

$ErrorActionPreference = "Stop"
$logPath = ".\error_log.json"

function Write-A©t0rHeader {
    Write-Host "" -ForegroundColor Gray
    Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        A©t0r :: GEMINI CASCADE GATEWAY v1.1          ║" -ForegroundColor Cyan
    Write-Host "║        CASE-MACHERET-1997-2026 · Anti-Poison         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# ANTI_CONTEXT_POISONING_GUARD: Check for "completion spoofing" in prompt
$poisonPatterns = @("Фаза успешно завершена", "Результат выполнения:", "Что конкретно сделано:")
foreach ($p in $poisonPatterns) {
    if ($Prompt -match [regex]::Escape($p)) {
        Write-Host "[!] ANTI_CONTEXT_POISONING_TRIGGER: Обнаружена фраза-индикатор завершения в запросе." -ForegroundColor Yellow
    }
}

try {
    Write-A©t0rHeader
    
    # Директива: Генерация внешних запросов (API Gemini) только при триггере 'NEED_GEMINI'
    if ($Prompt -match "NEED_GEMINI") {
        # Логика отправки $Prompt на API Gemini
        # Приоритет: Среда -> Динамический поиск
        $apiKey = $env:GOOGLE_GENERATIVE_AI_API_KEY
        if (-not $apiKey) {
            $keyFile = Get-ChildItem -Path $HOME, '.', '..' -Filter 'GOOGLE_GENERATIVE_AI_API_KEY.txt' -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($null -ne $keyFile) { 
                $apiKey = Get-Content $keyFile.FullName -Raw | ForEach-Object { $_.Trim() } 
            }
        }
        
        if (-not $apiKey) {
            throw "Критическая ошибка: GOOGLE_GENERATIVE_AI_API_KEY не найден. [ANTI_POISON: Проверьте C:\Users\arhiv\База Данных.txt]"
        }

        # Загрузка конфигурации из gemini-api-config.json
        $configFile = Join-Path $PSScriptRoot "gemini-api-config.json"
        if (-not (Test-Path $configFile)) { throw "Файл конфигурации $configFile не найден." }
        $config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
        
        $systemInstruction = $config.request_template.system_instruction.parts[0].text
        
        $bodyObject = @{
            system_instruction = @{ parts = @(@{ text = $systemInstruction }) }
            contents = @(@{ role = "user"; parts = @(@{ text = $Prompt }) })
            generationConfig = $config.request_template.generationConfig
            safetySettings = $config.request_template.safetySettings
        }
        $bodyJson = $bodyObject | ConvertTo-Json -Depth 10
        
        $url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$apiKey"
        
        Write-Host "📡 [A©t0r] Эскалация запроса к Gemini API..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri $url -Method POST -Body ([System.Text.Encoding]::UTF8.GetBytes($bodyJson)) -ContentType 'application/json; charset=utf-8'
        $responseText = $response.candidates[0].content.parts[0].text
        
        Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "🤖 [Gemini API Response]" -ForegroundColor Cyan
        Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host $responseText
        Write-Host "─────────────────────────────────────────────────" -ForegroundColor DarkGray
        return $responseText
    } else {
        # Каскадная маршрутизация: вызов Docker-шлюза (qwen2.5:3b)
        Write-Host "🏠 [A©t0r] Локальный анализ (Docker/Qwen)..." -ForegroundColor Gray
        $dockerResponse = docker run --rm -v "${PSScriptRoot}:/app" gateway_agent python gateway_agent/proxy_logic.py $Prompt
        if ($LASTEXITCODE -ne 0) { throw "Docker execution failed with exit code $LASTEXITCODE. Response: $dockerResponse" }
        Write-Host $dockerResponse
        return $dockerResponse
    }
} catch {
    $errorDetails = @{
        timestamp = Get-Date -Format "o"
        message   = $_.Exception.Message
        command   = $Prompt
        stack     = $_.ScriptStackTrace
        identity  = "A©t0r"
    }
    $errorDetails | ConvertTo-Json | Set-Content $logPath
    Write-Host "ОШИБКА: Записана в $logPath. Инициатор: A©t0r." -ForegroundColor Red
}

