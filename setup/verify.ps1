# 日常升級研究室：剪輯環境驗證
# 用法：powershell -ExecutionPolicy Bypass -File setup\verify.ps1 [-Video 你的影片.mp4]
# 不給影片時，會自動產生一段 20 秒的測試影片（只測得到流程，測不到中文辨識品質）。

param([string]$Video = "")

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $root ".venv\Scripts\python.exe"
$work = Join-Path $env:TEMP "dsr-verify"
New-Item -ItemType Directory -Force -Path $work | Out-Null

if (-not $Video) {
    $Video = Join-Path $work "test.mp4"
    ffmpeg -loglevel error -y -f lavfi -i "testsrc=d=20:s=1280x720" `
        -f lavfi -i "sine=f=440:d=8" -f lavfi -i "anullsrc=r=44100:cl=mono:d=4" -f lavfi -i "sine=f=440:d=8" `
        -filter_complex "[1][2][3]concat=n=3:v=0:a=1[a]" -map 0:v -map "[a]" -shortest `
        -c:v libx264 -c:a aac $Video
}

Write-Host "== 1/2 去空白測試（ffmpeg-skill）==" -ForegroundColor Yellow
$cut = Join-Path $work "cut.mp4"
$sw = [Diagnostics.Stopwatch]::StartNew()
& $python (Join-Path $root ".claude\skills\ffmpeg-skill\scripts\silence.py") $Video -o $cut
Write-Host ("去空白花了 {0:N0} 秒" -f $sw.Elapsed.TotalSeconds)

Write-Host "== 2/2 字幕測試（faster-whisper medium，CPU）==" -ForegroundColor Yellow
& $python (Join-Path $root "tools\transcribe.py") $Video --out (Join-Path $work "test.srt")

Write-Host ""
Write-Host "驗證完成，輸出在 $work" -ForegroundColor Green
Write-Host "請把上面兩行「花了幾秒」的結果回報給雲端的 Claude。"
