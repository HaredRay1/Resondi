# Render the 200-frame Resondi product video at 720p, then encode a 1080p MP4.
# Runs on its own (about 3 hours on this PC). Log: build\dev2\out\video.log
$root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $root
$log = "build\dev2\out\video.log"
"start $(Get-Date)" | Out-File $log -Encoding utf8
Get-ChildItem build\dev2\out\video -Filter "f_*.png" -ErrorAction SilentlyContinue | Remove-Item
$env:FRAMES = "1-200"; $env:STEP = "1"; $env:PCT = "67"
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b source-material\3d\Resondi_.blend --python build\dev2\render_spin_video.py 2>&1 |
    Select-String "Saved|rendered frames|Error|Traceback" | ForEach-Object { $_.Line } | Out-File $log -Append -Encoding utf8
$env:PYTHONIOENCODING = "utf-8"
& C:\Users\Hared\AppData\Local\Python\bin\python.exe build\dev2\encode_video.py 2>&1 | Select-String "wrote|Error" |
    ForEach-Object { $_.Line } | Out-File $log -Append -Encoding utf8
"done $(Get-Date)" | Out-File $log -Append -Encoding utf8
