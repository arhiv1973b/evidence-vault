# A©t0r Autonomous Audit Log Parser
# Project: CASE-MACHERET-1997-2026
# Purpose: Extract evidence links between IDNP 2000001159655, 2000001159555, and FinComBank blockade.

$logPath = "H:\ACTOR_DEV_ENV\apostille-mirror\AUDIT_DETECTION_LOG_20260611.json"
$outputPath = "H:\ACTOR_DEV_ENV\apostille-mirror\extracted_targets.json"

if (-not (Test-Path $logPath)) {
    Write-Error "A©t0r Critical: Log file not found at $logPath"
    exit
}

Write-Host "Reading and parsing $logPath..." -ForegroundColor Cyan
# Using ConvertFrom-Json on the whole file if memory allows, or line-by-line if it's a JSON array of objects.
# Given the size, we'll try to load it.
$logData = Get-Content $logPath -Raw | ConvertFrom-Json

$extracted = @()
$uniqueHashes = @{}

Write-Host "Filtering entries for IDNP fraud and FinComBank blockade..." -ForegroundColor Cyan

foreach ($entry in $logData) {
    # Extract Target Document from the HTML 'Line' field
    if ($entry.Line -match 'Target Document:</strong> (.*)</p>') {
        $encodedName = $Matches[1]
        $decodedName = [System.Web.HttpUtility]::UrlDecode($encodedName)
        
        # Determine if this entry is relevant to the 655/555 fraud or FinComBank
        $isRelevant = $false
        if ($entry.Line -match "2000001159655" -or $entry.Line -match "2000001159555" -or $entry.Line -match "FinComBank") {
            $isRelevant = $true
        }

        if ($isRelevant) {
            # Extract Hash from Path (assuming the path contains the hash projection filename)
            $hash = "UNKNOWN"
            if ($entry.Path -match '([a-f0-9]{64})\.html$') {
                $hash = $Matches[1]
            }

            if (-not $uniqueHashes.ContainsKey($hash)) {
                $uniqueHashes[$hash] = $true
                $extracted += [PSCustomObject]@{
                    Filename = $decodedName
                    Hash = $hash
                    Timestamp = $entry.Timestamp # If available, otherwise we use log context
                    Context = "IDNP_FRAUD_FINCOMBANK_BLOCKADE"
                }
            }
        }
    }
}

Write-Host "Extraction complete. Found $($extracted.Count) unique relevant documents." -ForegroundColor Green
$extracted | ConvertTo-Json -Depth 4 | Out-File $outputPath -Encoding UTF8
Write-Host "Results saved to $outputPath" -ForegroundColor Cyan
