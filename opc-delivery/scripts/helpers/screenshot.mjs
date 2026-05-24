#!/usr/bin/env node
// Capture route screenshots for MasterGo D2C verification.

import fs from 'node:fs'
import path from 'node:path'

function arg(name, fallback) {
  const idx = process.argv.indexOf(`--${name}`)
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback
}

const base = arg('base', 'http://localhost:3000')
const routes = arg('routes', '/').split(',').map((route) => route.trim()).filter(Boolean)
const outDir = arg('out', 'screenshots')
const width = Number(arg('width', '1440'))
const height = Number(arg('height', '900'))

let chromium
try {
  ;({ chromium } = await import('playwright'))
} catch {
  console.error('Playwright is not installed. Run: pnpm add -D playwright && npx playwright install chromium')
  process.exit(2)
}

fs.mkdirSync(outDir, { recursive: true })
const browser = await chromium.launch()
const context = await browser.newContext({ viewport: { width, height } })

for (const route of routes) {
  const page = await context.newPage()
  const url = new URL(route, base).toString()
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.waitForTimeout(500)
  const safe = route === '/' ? 'root' : route.replace(/^\/+/, '').replace(/[^A-Za-z0-9_-]+/g, '_')
  const target = path.join(outDir, `${safe}.png`)
  await page.screenshot({ path: target, fullPage: true })
  console.log(`${route} -> ${target}`)
  await page.close()
}

await browser.close()
