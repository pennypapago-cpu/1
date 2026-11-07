"""把影片或音訊轉成繁體中文 SRT 字幕。

用法：
    .venv\\Scripts\\python tools\\transcribe.py 影片.mp4 [--model medium] [--out 字幕.srt]

只用 CPU（int8），適合沒有 NVIDIA 顯示卡的筆電。
轉出來的字幕之後交給 AI 用腳本校正錯字。
"""
import argparse
import os
import time

from faster_whisper import WhisperModel

PROMPT = (
    "以下是繁體中文的 AI 工具教學影片，頻道名稱是日常升級研究室，"
    "會提到 ChatGPT、Claude、Gemini、NotebookLM、Codex、Copilot、Skill、Prompt。"
)


def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.src)[0] + ".srt"

    start = time.time()
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        a.src, language="zh", initial_prompt=PROMPT, vad_filter=True
    )
    with open(out, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n\n")
    took = time.time() - start
    print(f"完成：{out}")
    print(f"影片長度 {info.duration:.0f} 秒，花了 {took:.0f} 秒（{took / max(info.duration, 1):.2f} 倍時長）")


if __name__ == "__main__":
    main()
