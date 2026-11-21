// Renders a 1080x1920 story card (HTML -> JPG) with headless Chromium. Usage: node tools/story_card.mjs <card.html> <out.jpg>
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'path';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const [html, out] = process.argv.slice(2);
const b = await pw.chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + path.resolve(html), { waitUntil: 'load' });
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: out, type: 'jpeg', quality: 92 });
await b.close(); console.log('story', out);
