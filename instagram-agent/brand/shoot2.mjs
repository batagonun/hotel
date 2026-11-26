// Renders the brand assets (profile pictures + Facebook cover) from brand.html to PNG.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const { chromium } = pw;
import path from 'node:path';
const dir = path.dirname(new URL(import.meta.url).pathname);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1700, height: 1200 } });
await p.goto('file://' + path.join(dir, 'brand2.html'));
await p.evaluate(() => document.fonts.ready);
for (const [id, f] of [['prof','profile.png'],['cover','fb-cover.png']])
  await p.locator('#' + id).screenshot({ path: path.join(dir, f) });
await b.close();
console.log('ok');
