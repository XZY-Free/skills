#!/usr/bin/env node
/*
  webdeck 截图自检脚本 —— 按投屏比例(1440×810)截指定页，自己看一眼排版崩没崩。
  代码对 ≠ 视觉对，所以做完/改完版式都该截一张看。

  用法：
    node shoot.mjs <url或本地文件路径> [页码,从1开始] [输出png路径]
  例：
    node shoot.mjs ./deck.html 3                  # 本地第3页 → /tmp/webdeck-shot.png
    node shoot.mjs http://host/培训 8 /tmp/p8.png  # 线上第8页（带中文路径会自动编码）

  注意：图片若用绝对路径引用(/xxx.jpg)，本地 file:// 看不到图，得截线上 URL。

  依赖 playwright。装在哪不一定，脚本会自己找：本地有就用本地，
  否则去 ~/.npm/_npx 缓存里找（NODE_PATH 对 ESM import 不生效，所以脚本自己解析）。
*/
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  // 本地没有 → 从 npx 缓存解析（createRequire 走 CommonJS，能吃 NODE_PATH 风格的目录）
  const base = execSync("ls -d ~/.npm/_npx/*/node_modules/playwright 2>/dev/null | head -1")
    .toString().trim();
  if (!base) { console.error('找不到 playwright，先 npx playwright install chromium'); process.exit(1); }
  const require = createRequire(base.replace(/playwright$/, '') );
  ({ chromium } = require('playwright'));
}

const arg = process.argv.slice(2);
const target = arg[0];
const pageNo = parseInt(arg[1] || '1', 10);
const out = arg[2] || '/tmp/webdeck-shot.png';

if (!target) { console.error('用法: node shoot.mjs <url或文件> [页码] [输出png]'); process.exit(1); }

// 本地路径转 file://，URL 原样（中文做 percent-encode）
let url;
if (/^https?:\/\//.test(target)) {
  url = encodeURI(target);
} else {
  const path = await import('node:path');
  url = 'file://' + encodeURI(path.resolve(target));
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 810 } });
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(400);

// 翻到目标页：从第1页按 → 翻 (pageNo-1) 次
for (let k = 0; k < pageNo - 1; k++) { await page.keyboard.press('ArrowRight'); await page.waitForTimeout(150); }
await page.waitForTimeout(700);   // 等入场动画落定

await page.screenshot({ path: out });
console.log('OK ->', out, '(第', pageNo, '页)');
await browser.close();
