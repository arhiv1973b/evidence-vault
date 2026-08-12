$ErrorActionPreference = 'Stop'
$repo = 'H:\ACTOR_DEV_ENV\copilot-worktrees\apostille-mirror\arhiv1973b-studious-system'
$script = Join-Path $repo 'google_drive_mirror_bridge.py'
$logDir = Join-Path $repo 'logs'
$logFile = Join-Path $logDir 'google_drive_mirror_bridge.log'
$mirrorRoot = Join-Path $repo 'apostille-mirror\google-drive-mirror'

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$arguments = @(
    $script,
    '--source-root', 'F:\Мой диск',
    '--mirror-root', $mirrorRoot,
    '--watch',
    '--interval', '300'
)

Start-Process -FilePath 'python.exe' -ArgumentList $arguments -WorkingDirectory $repo -RedirectStandardOutput $logFile -RedirectStandardError $logFile -WindowStyle Hidden
Write-Host "Started detached Google Drive mirror bridge. Log: $logFile"
