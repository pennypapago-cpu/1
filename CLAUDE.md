# 日常升級研究室：AI 經營團隊

這個 repo 是 YouTube 頻道「日常升級研究室」的 AI 團隊共用資料夾。頻道主一人經營，AI 只產出草稿，上傳、發佈、回覆留言都由頻道主親手處理。

- 目標、角色、分工與建置順序：`docs/團隊共識.md`
- 頻道語氣與格式：`channel/風格檔.md`（產出任何內容前必讀）
- Agent 定義：`.claude/agents/`
- 剪輯技能：`.claude/skills/`（來源與授權見 `.claude/skills/SOURCES.md`）

## 資料夾

- `radar/`：新聞雷達每日報告（`YYYY-MM-DD.md`）
- `shorts/`：Shorts 腳本草稿
- `scripts/`：長片腳本草稿
- `packaging/`：標題與縮圖（每支影片一個資料夾）
- `channel/`：風格檔、縮圖版型（`channel/thumbnail/`）與頻道資料
- `tools/`：縮圖渲染（`render_thumbnail.js`）、字幕轉寫（`transcribe.py`）

## 原則

- 一律使用繁體中文、台灣用語。
- 事實要有來源；推估或未驗證的內容要明確標示。
- 日期一律用台北時間。
- 不要把原始影片檔放進 repo，影片留在頻道主的電腦上。
