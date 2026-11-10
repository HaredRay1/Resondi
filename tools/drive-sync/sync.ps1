# Resondi -> Google Drive mirror.
# Keeps G:\My Drive\Resondi (Drive folder id 1JFf8zYd9qZHy_0uyAqefTuhzLzthJQOI)
# identical to this project folder. The PC is master: changes made only in Drive
# are overwritten, and files deleted here go to Drive's trash (30-day recovery).
# Runs forever: robocopy /MON re-syncs about a minute after any change.
# Started at logon by the scheduled task "Resondi Drive Sync" (see install.ps1).

$Source = 'C:\Users\Hared\Downloads\Resondi'
$Dest   = 'G:\My Drive\Resondi'
$LogDir = Join-Path $env:LOCALAPPDATA 'ResondiSync'
$Log    = Join-Path $LogDir 'sync.log'

New-Item -ItemType Directory -Force $LogDir | Out-Null

# Drive for desktop mounts G: a little after logon; wait for it (up to 30 min).
$waited = 0
while (-not (Test-Path $Dest)) {
    if ($waited -ge 1800) { Add-Content $Log "$(Get-Date -f s) G: not available after 30 min; giving up."; exit 1 }
    Start-Sleep -Seconds 15; $waited += 15
}

# Keep the log from growing without bound.
if ((Test-Path $Log) -and (Get-Item $Log).Length -gt 5MB) { Move-Item $Log "$Log.old" -Force }

Add-Content $Log "$(Get-Date -f s) starting mirror $Source -> $Dest"

$rcArgs = @(
    $Source, $Dest,
    '/MIR',               # copy everything, propagate deletions
    '/FFT',               # 2-second timestamp tolerance (Drive's virtual disk)
    '/COPY:DAT', '/DCOPY:T',
    '/XJ',                # skip junctions
    '/XD', '.git', 'node_modules', '__pycache__', '.claude',
           "$Source\model-rebuild\export",   # 6,902 ICBHI clips, regenerable; kept off Drive
           "$Source\model-rebuild\history-run1", "$Source\model-rebuild\work",
           "$Source\model-rebuild\work-exp", # experiment caches (~1 GB audio windows), regenerable
           "$Source\model-rebuild\work-3s",  # training caches, regenerable; kept off Drive
    '/XF', 'desktop.ini', '~$*', '*.tmp',
    '/R:2', '/W:5',
    '/MON:1', '/MOT:1',   # re-run after >=1 change, at most once a minute
    '/NP', '/NDL', "/UNILOG+:$Log"
)
& robocopy.exe @rcArgs
Add-Content $Log "$(Get-Date -f s) robocopy exited with code $LASTEXITCODE"
