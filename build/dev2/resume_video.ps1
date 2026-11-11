# Resume the Resondi product video: render only the frames still missing, then encode the MP4.
# Safe to re-run after an interruption. Log: build\dev2\out\video.log
$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root
$log = "build\dev2\out\video.log"
$have = @(Get-ChildItem build\dev2\out\video -Filter "f_*.png" -ErrorAction SilentlyContinue |
    ForEach-Object { [int]($_.BaseName -replace 'f_', '') })
$missing = 1..200 | Where-Object { $have -notcontains $_ }
"resume $(Get-Date): $($missing.Count) frames missing" | Out-File $log -Append -Encoding utf8
if ($missing.Count -gt 0) {
    $env:FRAMES = "$($missing[0])-200"; $env:STEP = "1"; $env:PCT = "67"
    & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b source-material\3d\Resondi_.blend --python build\dev2\render_spin_video.py 2>&1 |
        Select-String "Saved|rendered frames|Error|Traceback" | ForEach-Object { $_.Line } | Out-File $log -Append -Encoding utf8
}
$env:PYTHONIOENCODING = "utf-8"
& C:\Users\Hared\AppData\Local\Python\bin\python.exe build\dev2\encode_video.py 2>&1 | Select-String "wrote|Error" |
    ForEach-Object { $_.Line } | Out-File $log -Append -Encoding utf8
"done $(Get-Date)" | Out-File $log -Append -Encoding utf8
