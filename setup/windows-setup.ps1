# 日常升級研究室：Windows 剪輯環境安裝腳本
# 用法：在 repo 根目錄開 PowerShell，執行
#   powershell -ExecutionPolicy Bypass -File setup\windows-setup.ps1
# 可以重複執行，已經裝好的會跳過。

$ErrorActionPreference = "Stop"

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

function Install-IfMissing($command, $wingetId) {
    if (Get-Command $command -ErrorAction SilentlyContinue) {
        Write-Host "[略過] $command 已安裝" -ForegroundColor DarkGray
    } else {
        Write-Host "[安裝] $wingetId ..." -ForegroundColor Cyan
        winget install --id $wingetId -e --accept-source-agreements --accept-package-agreements
        Refresh-Path
    }
}

Write-Host "== 1/4 安裝基本工具 ==" -ForegroundColor Yellow
Install-IfMissing "git"    "Git.Git"
Install-IfMissing "py"     "Python.Python.3.12"
Install-IfMissing "node"   "OpenJS.NodeJS.LTS"
Install-IfMissing "ffmpeg" "Gyan.FFmpeg"

Write-Host "== 2/4 建立 Python 虛擬環境並安裝 faster-whisper ==" -ForegroundColor Yellow
$venv = Join-Path $PSScriptRoot "..\.venv"
if (-not (Test-Path $venv)) { py -3.12 -m venv $venv }
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --upgrade pip --quiet
& $python -m pip install faster-whisper --quiet

Write-Host "== 3/4 下載語音模型（medium，約 1.5 GB，只需下載一次）==" -ForegroundColor Yellow
& $python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8'); print('模型就緒')"

Write-Host "== 4/4 檢查版本 ==" -ForegroundColor Yellow
git --version
& $python --version
node --version
ffmpeg -hide_banner -version | Select-Object -First 1

Write-Host ""
Write-Host "安裝完成。下一步：執行 setup\verify.ps1 做速度測試。" -ForegroundColor Green
