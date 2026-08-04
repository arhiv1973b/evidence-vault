param(
    [string]$Model = "",
    [string]$Prompt = "",
    [switch]$List,
    [switch]$Install,
    [switch]$Interactive
)

function Write-Color($text, $color="White") { Write-Host $text -ForegroundColor $color }

function Write-Header {
    Write-Host ""
    Write-Color "╔══════════════════════════════════════════════════════╗" Cyan
    Write-Color "║     A©tor AI SWITCHER v2.0 — Коммутатор моделей     ║" Cyan
    Write-Color "║        CASE-MACHERET-1997-2026 · Active Mode         ║" Cyan
    Write-Color "╚══════════════════════════════════════════════════════╝" Cyan
    Write-Host ""
}

$MODELS = [ordered]@{
    "gemini-flash"   = @{ Provider="gemini";     EnvKey="GOOGLE_GENERATIVE_AI_API_KEY"; Name="Gemini 2.5 Flash";       ID="gemini-2.5-flash" }
    "gemini-pro"     = @{ Provider="gemini";     EnvKey="GOOGLE_GENERATIVE_AI_API_KEY"; Name="Gemini 2.5 Pro";         ID="gemini-2.5-pro" }
    "gemini-3-flash" = @{ Provider="gemini";     EnvKey="GOOGLE_GENERATIVE_AI_API_KEY"; Name="Gemini 3 Flash Preview"; ID="gemini-3-flash-preview" }
    #    "claude-sonnet"  = @{ Provider="anthropic";  EnvKey="ANTHROPIC_API_KEY";            Name="Claude Sonnet 4.6";      ID="claude-3-5-sonnet-20241022" }
    #    "claude-haiku"   = @{ Provider="anthropic";  EnvKey="ANTHROPIC_API_KEY";            Name="Claude Haiku 4.5";       ID="claude-3-5-haiku-20241022" }
    "gpt-4o"         = @{ Provider="openai";     EnvKey="OPENAI_API_KEY";               Name="GPT-4o";                 ID="gpt-4o" }
    "gpt-4o-mini"    = @{ Provider="openai";     EnvKey="OPENAI_API_KEY";               Name="GPT-4o Mini";            ID="gpt-4o-mini" }
    "grok"           = @{ Provider="grok";       EnvKey="GROK_API_KEY";                 Name="Grok (xAI)";             ID="grok-3-mini" }
    "llama-groq"     = @{ Provider="groq";       EnvKey="GROQ_API_KEY";                 Name="Llama 3.3 70B (Groq)";  ID="llama-3.3-70b-versatile" }
    "or-deepseek"    = @{ Provider="openrouter"; EnvKey="OPENROUTER_API_KEY";           Name="DeepSeek R1";            ID="deepseek/deepseek-r1" }
    "or-claude"      = @{ Provider="openrouter"; EnvKey="OPENROUTER_API_KEY";           Name="Claude via OpenRouter";  ID="anthropic/claude-sonnet-4-5" }
}

function Get-KeyStatus {
    $s = @{}
    foreach ($a in $MODELS.Keys) {
        $v = [System.Environment]::GetEnvironmentVariable($MODELS[$a].EnvKey)
        $s[$a] = ($null -ne $v -and $v -ne "")
    }
    return $s
}

function Show-Models {
    Write-Header
    $status = Get-KeyStatus
    foreach ($a in $MODELS.Keys) {
        $ok   = $status[$a]
        $icon = if ($ok) { "✅" } else { "❌" }
        $col  = if ($ok) { "Green" } else { "Red" }
        Write-Color ("  {0} [{1,-14}] {2}" -f $icon, $a, $MODELS[$a].Name) $col
    }
    Write-Host ""
    Write-Color "  Использование: actor-ai -Model gemini-flash -Prompt `"Вопрос`"" Cyan
    Write-Color "  Интерактив:    actor-ai -Interactive" Cyan
    Write-Host ""
}

function Invoke-AI {
    param([string]$Alias, [string]$UserPrompt)
    if (-not $MODELS.Contains($Alias)) { Write-Color "❌ Модель '$Alias' не найдена." Red; return }

    $cfg      = $MODELS[$Alias]
    $apiKey   = [System.Environment]::GetEnvironmentVariable($cfg.EnvKey)
    if (-not $apiKey) { Write-Color "❌ Ключ $($cfg.EnvKey) не найден." Red; return }

    Write-Color "`n  🤖 [$($cfg.Name)] обрабатывает запрос..." Yellow

    $headers = @{ "Content-Type" = "application/json" }
    $uri = ""; $body = ""

    switch ($cfg.Provider) {
        "gemini" {
            $uri = "https://generativelanguage.googleapis.com/v1beta/models/$($cfg.ID):generateContent?key=$apiKey"
            $body = @{ contents = @(@{ parts = @(@{ text = $UserPrompt }) }) } | ConvertTo-Json -Depth 5
        }
        "anthropic" {
            $uri = "https://api.anthropic.com/v1/messages"
            $headers["x-api-key"] = $apiKey
            $headers["anthropic-version"] = "2023-06-01"
            $body = @{ model=$cfg.ID; max_tokens=1024; messages=@(@{ role="user"; content=$UserPrompt }) } | ConvertTo-Json -Depth 5
        }
        "openai" {
            $uri = "https://api.openai.com/v1/chat/completions"
            $headers["Authorization"] = "Bearer $apiKey"
            $body = @{ model=$cfg.ID; messages=@(@{ role="user"; content=$UserPrompt }) } | ConvertTo-Json -Depth 5
        }
        "grok" {
            $uri = "https://api.x.ai/v1/chat/completions"
            $headers["Authorization"] = "Bearer $apiKey"
            $body = @{ model=$cfg.ID; messages=@(@{ role="user"; content=$UserPrompt }) } | ConvertTo-Json -Depth 5
        }
        "groq" {
            $uri = "https://api.groq.com/openai/v1/chat/completions"
            $headers["Authorization"] = "Bearer $apiKey"
            $body = @{ model=$cfg.ID; messages=@(@{ role="user"; content=$UserPrompt }) } | ConvertTo-Json -Depth 5
        }
        "openrouter" {
            $uri = "https://openrouter.ai/api/v1/chat/completions"
            $headers["Authorization"] = "Bearer $apiKey"
            $headers["HTTP-Referer"] = "https://arhiv1973b.github.io/apostille-mirror/"
            $body = @{ model=$cfg.ID; messages=@(@{ role="user"; content=$UserPrompt }) } | ConvertTo-Json -Depth 5
        }
    }

    try {
        $resp = Invoke-RestMethod -Uri $uri -Method POST -Headers $headers -Body $body -TimeoutSec 60
        $text = switch ($cfg.Provider) {
            "anthropic" { $resp.content[0].text }
            "gemini"    { $resp.candidates[0].content.parts[0].text }
            default     { $resp.choices[0].message.content }
        }
        Write-Color "─────────────────────────────────────────────────" DarkGray
        Write-Color "  [$($cfg.Name)]" Cyan
        Write-Color "─────────────────────────────────────────────────" DarkGray
        Write-Host $text
        Write-Color "─────────────────────────────────────────────────" DarkGray
        Write-Host ""
        return $text
    } catch {
        Write-Color "❌ Ошибка: $($_.Exception.Message)" Red
    }
}

function Start-Interactive {
    Write-Header
    $status  = Get-KeyStatus
    $active  = $MODELS.Keys | Where-Object { $status[$_] }
    $current = $active | Select-Object -First 1
    Write-Color "  Активных моделей: $($active.Count) | Текущая: $current" Green
    Write-Color "  Команды: /list /switch <alias> /exit" DarkGray
    Write-Host ""
    while ($true) {
        Write-Host -NoNewline "  A©tor [$current]> " -ForegroundColor Yellow
        $inp = Read-Host
        if ($inp -eq "/exit") { break }
        elseif ($inp -eq "/list") { Show-Models }
        elseif ($inp -match "^/switch\s+(\S+)") {
            $t = $matches[1]
            if ($MODELS.Contains($t) -and $status[$t]) { $current = $t; Write-Color "  ✅ → $($MODELS[$current].Name)" Green }
            else { Write-Color "  ❌ Модель недоступна." Red }
        }
        elseif ($inp.Trim() -ne "") { Invoke-AI -Alias $current -UserPrompt $inp }
    }
}

Write-Header
if ($List)                              { Show-Models }
elseif ($Install)                       { Write-Color "pip install google-generativeai openai anthropic" Yellow }
elseif ($Interactive)                   { Start-Interactive }
elseif ($Model -ne "" -and $Prompt -ne "") { Invoke-AI -Alias $Model -UserPrompt $Prompt }
else                                    { Show-Models }
