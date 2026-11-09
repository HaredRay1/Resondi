# Registers (or re-registers) the scheduled task that runs sync.ps1 at logon,
# hidden, and starts it now. Run once:
#   powershell -ExecutionPolicy Bypass -File tools\drive-sync\install.ps1
# To stop syncing:  Unregister-ScheduledTask -TaskName 'Resondi Drive Sync' -Confirm:$false
#                   (and end any running robocopy.exe)

$TaskName = 'Resondi Drive Sync'
$Script   = Join-Path $PSScriptRoot 'sync.ps1'

$action   = New-ScheduledTaskAction -Execute 'powershell.exe' `
            -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Script`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew `
            -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
schtasks /Query /TN $TaskName /FO LIST | Select-String 'TaskName|Status'
