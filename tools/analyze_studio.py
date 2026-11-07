"""分析 YouTube Studio 匯出的 CSV，產出週報需要的數字。

用法：
    python3 tools/analyze_studio.py 表格資料.csv --current-subs 1350 [--out reports/2026-11-14-數據.md]

CSV 怎麼匯出：YouTube Studio → 數據分析 → 右上角「進階模式」→ 選日期範圍 →
右上角下載圖示 → 「逗號分隔值 (.csv)」。下載的壓縮檔裡有一個「表格資料.csv」
（英文介面叫 Table data.csv），把它交給這支程式。
進階模式表格請確認有勾選這些欄位：觀看次數、觀看時間（小時）、訂閱人數、
曝光次數、曝光點閱率、平均觀看時長、長度。

只用 Python 標準函式庫，Windows 和雲端都能直接跑。
"""
import argparse
import csv
import datetime as dt
import io
import re
import sys

# 目標設定（來自 docs/團隊共識.md）
START_DATE = dt.date(2026, 11, 7)
START_SUBS = 1290
CHALLENGE = (10_000, dt.date(2027, 5, 7))
FLOOR = (4_000, dt.date(2027, 5, 7))
CHECKPOINT = dt.date(2027, 2, 7)
CHECKPOINT_MONTHLY = 1_000
WATCH_HOURS_TARGET = 4_000
SHORTS_MAX_SECONDS = 180  # Shorts 最長 3 分鐘；用長度判斷只是近似值

# 欄位名稱對照（中英文介面都可能出現；比對時忽略大小寫和空白）
COLUMNS = {
    "content": ["內容", "content"],
    "title": ["影片標題", "video title", "標題"],
    "published": ["影片發布時間", "影片發佈時間", "video publish time", "發布時間"],
    "duration": ["長度", "duration"],
    "views": ["觀看次數", "views"],
    "watch_hours": ["觀看時間 (小時)", "觀看時間（小時）", "watch time (hours)"],
    "subs": ["訂閱人數", "subscribers"],
    "impressions": ["曝光次數", "impressions"],
    "ctr": ["曝光點閱率 (%)", "曝光點閱率（%）", "impressions click-through rate (%)"],
    "avd": ["平均觀看時長", "average view duration"],
}


def norm(s):
    return re.sub(r"\s+", "", (s or "").lower()).replace("（", "(").replace("）", ")")


def num(v):
    v = (v or "").strip().replace(",", "").replace("%", "")
    if not v:
        return 0.0
    if ":" in v:  # 0:03:25 這種時長格式
        sec = 0
        for part in v.split(":"):
            sec = sec * 60 + float(part)
        return sec
    try:
        return float(v)
    except ValueError:
        return 0.0


def read_rows(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16", "cp950"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        sys.exit("CSV 是空的")
    header = {norm(h): h for h in rows[0].keys()}
    col = {}
    for key, names in COLUMNS.items():
        for n in names:
            if norm(n) in header:
                col[key] = header[norm(n)]
                break
    missing = [k for k in ("title", "views", "subs") if k not in col]
    if missing:
        sys.exit(f"找不到必要欄位：{missing}。CSV 的欄位是：{list(rows[0].keys())}")
    videos = []
    for r in rows:
        first = (r.get(col.get("content", ""), "") or r.get(col["title"], "")).strip()
        if first in ("總計", "Total", "合計"):
            continue
        g = lambda k: num(r.get(col[k])) if k in col else None
        title = r[col["title"]].strip()
        dur = g("duration")
        is_short = "#shorts" in title.lower() or (dur is not None and 0 < dur <= SHORTS_MAX_SECONDS)
        videos.append({
            "title": title, "published": r.get(col.get("published", ""), "").strip(),
            "type": "Shorts" if is_short else "長片", "duration": dur,
            "views": g("views") or 0, "watch_hours": g("watch_hours"),
            "subs": g("subs") or 0, "impressions": g("impressions"),
            "ctr": g("ctr"), "avd": g("avd"),
        })
    return videos, col


def per_k(subs, views):
    return subs / views * 1000 if views else 0.0


def fmt(x, d=0):
    return "—" if x is None else f"{x:,.{d}f}"


def report(videos, col, current_subs, today):
    out = []
    w = out.append
    w(f"# 數據週報 {today.isoformat()}\n")
    w("> 由 tools/analyze_studio.py 產生。Shorts／長片是用影片長度（3 分鐘以下）或標題含 #shorts 判斷，可能有少數誤判。\n")

    # 目標進度
    days = (today - START_DATE).days
    gained = current_subs - START_SUBS
    w("## 目標進度\n")
    w(f"- 目前訂閱：**{current_subs:,}**（起點 {START_SUBS:,}，{days} 天來 {gained:+,}）")
    for name, (target, deadline) in (("挑戰目標", CHALLENGE), ("保底目標", FLOOR)):
        left_days = max((deadline - today).days, 1)
        need = target - current_subs
        w(f"- {name} {target:,}（{deadline}）：還差 {max(need, 0):,}，需要每天 {max(need, 0) / left_days:.1f} 人")
    if days > 0:
        pace = gained / days
        w(f"- 目前實際速度：每天 {pace:.1f} 人，約每月 {pace * 30:.0f} 人")
        w(f"- 第 3 個月檢查點（{CHECKPOINT}）：每月要 {CHECKPOINT_MONTHLY:,} 人以上才繼續衝挑戰目標")
    w("")

    # 分類彙總
    w("## Shorts 和長片比較（這次匯出的期間）\n")
    w("| 類型 | 支數 | 觀看次數 | 觀看時數 | 新增訂閱 | 每千次觀看帶來訂閱 | 平均點閱率 |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for t in ("長片", "Shorts"):
        vs = [v for v in videos if v["type"] == t]
        if not vs:
            continue
        views = sum(v["views"] for v in vs)
        subs = sum(v["subs"] for v in vs)
        hours = sum(v["watch_hours"] or 0 for v in vs) if "watch_hours" in col else None
        ctrs = [v["ctr"] for v in vs if v["ctr"]]
        ctr = sum(ctrs) / len(ctrs) if ctrs else None
        w(f"| {t} | {len(vs)} | {fmt(views)} | {fmt(hours, 1)} | {fmt(subs)} | {per_k(subs, views):.2f} | {fmt(ctr, 1)}{'%' if ctr else ''} |")
    w("")
    if "watch_hours" in col:
        long_hours = sum(v["watch_hours"] or 0 for v in videos if v["type"] == "長片")
        w(f"長片觀看時數 {long_hours:,.1f} 小時，營利門檻 {WATCH_HOURS_TARGET:,} 小時"
          f"（{long_hours / WATCH_HOURS_TARGET:.0%}）。注意：門檻算的是最近 365 天，匯出期間要選「過去 365 天」這個數字才準。\n")

    # 排行
    ranked = sorted((v for v in videos if v["views"] >= 50), key=lambda v: per_k(v["subs"], v["views"]), reverse=True)
    w("## 每千次觀看帶來訂閱：前 5 名（觀看 50 次以上）\n")
    w("| 類型 | 標題 | 觀看 | 新增訂閱 | 每千次 | 點閱率 | 平均觀看時長(秒) |")
    w("|---|---|---:|---:|---:|---:|---:|")
    for v in ranked[:5]:
        w(f"| {v['type']} | {v['title']} | {fmt(v['views'])} | {fmt(v['subs'])} | {per_k(v['subs'], v['views']):.2f} | {fmt(v['ctr'], 1)} | {fmt(v['avd'])} |")
    if len(ranked) >= 10:  # 影片太少時前後名次會重疊，就不列後 5 名
        w("\n## 後 5 名\n")
        w("| 類型 | 標題 | 觀看 | 新增訂閱 | 每千次 | 點閱率 | 平均觀看時長(秒) |")
        w("|---|---|---:|---:|---:|---:|---:|")
        for v in ranked[-5:][::-1]:
            w(f"| {v['type']} | {v['title']} | {fmt(v['views'])} | {fmt(v['subs'])} | {per_k(v['subs'], v['views']):.2f} | {fmt(v['ctr'], 1)} | {fmt(v['avd'])} |")
    w("\n## 缺少的欄位\n")
    miss = [k for k in COLUMNS if k not in col]
    w("、".join(miss) if miss else "無")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--current-subs", type=int, required=True, help="Studio 首頁顯示的目前訂閱總數")
    ap.add_argument("--today", help="報告日期 YYYY-MM-DD，預設今天（台北時間）")
    ap.add_argument("--out")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else (dt.datetime.utcnow() + dt.timedelta(hours=8)).date()
    videos, col = read_rows(a.csv)
    text = report(videos, col, a.current_subs, today)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"已輸出 {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
