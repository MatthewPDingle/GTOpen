# Start the GTOpen data generator at every sign-in and keep it running (Windows).
#   tools\datagen\autostart.cmd YOUR_GITHUB_LOGIN [datagen run options]
#   tools\datagen\autostart.cmd remove
# Creates the scheduled task "GTOpen generator" for the signed-in user: it runs
# tools\datagen\keep-running.cmd at sign-in and looks every 15 minutes that it is
# still there. The task is not elevated and has no time limit. It starts the
# generator now. Run it from an Administrator window if Windows refuses.
# See docs/contribute-compute.md, "Running unattended".
$ErrorActionPreference = 'Stop'
$name = 'GTOpen generator'
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if ($args.Count -lt 1) {
    Write-Host 'usage: tools\datagen\autostart.cmd YOUR_GITHUB_LOGIN [datagen run options]'
    Write-Host '       tools\datagen\autostart.cmd remove'
    exit 1
}
if ($args[0] -eq 'remove') {
    if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $name -Confirm:$false
        Write-Host "Removed the task `"$name`". A generator window that is open keeps running until you close it."
    } else {
        Write-Host "There is no task `"$name`"."
    }
    exit 0
}
foreach ($a in $args) {
    if ($a -notmatch '^[A-Za-z0-9_.\-]+$') {
        Write-Host "this argument cannot go into a scheduled task: $a"
        exit 1
    }
}
$script = Join-Path $PSScriptRoot 'keep-running.cmd'
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument ("/c `"`"$script`" $($args -join ' ')`"") -WorkingDirectory $repo
$atLogon = New-ScheduledTaskTrigger -AtLogOn -User $user
$every = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(15) -RepetitionInterval (New-TimeSpan -Minutes 15)
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger @($atLogon, $every) -Settings $settings `
    -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName $name
Write-Host "Done. The task `"$name`" starts the generator at every sign-in of $user and keeps it running."
Write-Host 'A generator window opens now. To undo: tools\datagen\autostart.cmd remove'
