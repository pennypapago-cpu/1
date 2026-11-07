# 第二週：Windows 剪輯環境

目標：在頻道主的 Windows 筆電（i7-1260P、16 GB、Intel 內顯）裝好剪輯工具，並用對帳影片做第一次試點。

## 步驟一：把 repo 拿到電腦上（只做一次）

在 PowerShell 執行（還沒有 git 的話，先執行 `winget install --id Git.Git -e`，再重開 PowerShell）：

```
cd $HOME\Documents
git clone https://github.com/pennypapago-cpu/1 日常升級研究室
cd 日常升級研究室
```

之後每次開始工作前，先執行 `git pull`，拿到雲端團隊最新的腳本和雷達報告。

## 步驟二：安裝（約 10 到 20 分鐘，大部分時間在下載）

在 repo 資料夾打開 Claude Code，對它說：

> 照 docs/第二週-Windows剪輯環境.md 幫我安裝剪輯環境。

或自己在 PowerShell 執行：

```
powershell -ExecutionPolicy Bypass -File setup\windows-setup.ps1
```

會安裝：Git、Python 3.12、Node.js LTS、ffmpeg、faster-whisper，並下載 medium 語音模型（約 1.5 GB）。Python 套件裝在 repo 內的 `.venv`，不會影響電腦上的其他程式。

## 步驟三：驗證速度

先關掉瀏覽器等吃記憶體的程式，再執行：

```
powershell -ExecutionPolicy Bypass -File setup\verify.ps1 -Video "對帳影片的完整路徑.mp4"
```

會跑兩項：去空白、轉字幕。把顯示的秒數回報給雲端的 Claude，用來修正團隊共識裡的推估值（目前推估：10 分鐘影片轉字幕約 5 到 10 分鐘）。

## 步驟四：試點（對帳影片）

在 Claude Code 裡說：

> 用對帳影片做一次 AI 粗剪：去空白、上字幕、轉一支直式 Shorts。輸出到 output 資料夾，不要動原始檔。

然後比較 AI 版本和你自己剪的版本，記錄：

- 去空白有沒有誤剪（螢幕錄影比較容易誤剪）
- 字幕錯字數量
- 你修正花了幾分鐘

結果回報給雲端的 Claude，決定剪輯師接下來負責多少工作。

## 注意

- 這些腳本是在 Linux 雲端環境寫的，沒有在 Windows 上實際執行過。遇到錯誤時，把錯誤訊息貼給 Claude Code 處理即可。
- 影片檔已經列在 `.gitignore`，不會被推送到 GitHub。輸出請放在 `output/`（也已排除）。
