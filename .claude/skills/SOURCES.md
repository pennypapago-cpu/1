# 影片剪輯技能來源

這些 skill 是從 GitHub 複製進來的第三方專案（2026-11-07），不是自己寫的。更新時請重新從原始 repo 下載，並再檢查一次程式碼。

| 資料夾 | 來源 | 版本 (commit) | 授權 |
|---|---|---|---|
| `ffmpeg-skill/` | https://github.com/kajisho5/ffmpeg-skill | 9bdb444 (v3.2.0) | MIT |
| `remotion-*/` | https://github.com/remotion-dev/skills | a2824c6 | Remotion 授權：個人與 3 人以下公司免費，詳見 `remotion-license` |
| `explainer-*/`、`motion-broll/`、`object-separation/`、`sound-effects/` | https://github.com/Barty-Bart/motion-graphics | 3d83d98 | MIT（見 `LICENSE.motion-graphics`），音效檔各自授權見 `sound-effects/LICENSES.md` |

ffmpeg-skill 只放了 npm 套件實際發布的檔案，沒有放 tests、docs 網站和圖檔。

## 執行需求（在你自己的電腦上）

- ffmpeg：去空白、字幕、裁切、輸出都靠它。
- 語音轉文字引擎（去口誤、自動字幕需要）：例如 faster-whisper 或 whisper.cpp。
- Node.js：Remotion 和 motion-broll 需要，第一次使用時 skill 會引導安裝套件。
- `sound-effects` 會在執行時從 mixkit、freesound 等網站下載額外音效。
