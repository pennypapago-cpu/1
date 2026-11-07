// 把縮圖設定檔（JSON）渲染成 PNG。
// 用法：node tools/render_thumbnail.js 設定檔.json [輸出.png]
// 設定檔欄位：
//   format       "wide"（長片 1280x720，預設）或 "vertical"（Shorts 封面 1080x1920）
//   title        主標題。用 [[ ]] 包住要加黃色螢光筆的字，用 | 換行
//   badge        左上角工具名稱，例如 "ChatGPT"（可省略）
//   before       「以前」框的文字，用 | 換行
//   after        「現在」框的文字，用 | 換行
//   beforeLabel / afterLabel  可改成別的對比字（預設「以前」「現在」）
//   screenshot   右上角介面截圖的路徑，相對於設定檔（可省略，只用在橫式）
// 需要 playwright（雲端環境已內建；Windows 上執行 npm i playwright 後 npx playwright install chromium）。

const path = require("path");
const fs = require("fs");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

async function main() {
  const [specPath, outArg] = process.argv.slice(2);
  if (!specPath) {
    console.error("用法：node tools/render_thumbnail.js 設定檔.json [輸出.png]");
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  if (spec.screenshot) {
    spec.screenshot = pathToFileURL(path.resolve(path.dirname(specPath), spec.screenshot)).href;
  }
  const out = outArg || specPath.replace(/\.json$/i, ".png");
  const vertical = spec.format === "vertical";
  const size = vertical ? { width: 1080, height: 1920 } : { width: 1280, height: 720 };

  const template = path.join(__dirname, "..", "channel", "thumbnail", "template.html");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: size, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(template).href);
  await page.evaluate((s) => apply(s), spec);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out });
  await browser.close();
  console.log(`已輸出 ${out}（${size.width}x${size.height}）`);
}

main().catch((e) => { console.error(e); process.exit(1); });
