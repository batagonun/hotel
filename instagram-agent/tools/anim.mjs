// Renders an animated HTML scene frame by frame (free, no AI): the page exposes window.frame(t) that draws
// the scene at time t (seconds). Frames are screenshotted and piped into ffmpeg.
// Usage: node tools/anim.mjs <scene.html> <seconds> <out.mp4|out_dir/> [fps=25] [--alpha]
//   out.mp4  -> opaque H.264 video (with a soft synthesized pad, same as story.py)
//   out_dir/ -> transparent PNG frames f00000.png… for overlaying on real footage
import { createRequire } from 'node:module';
import { execSync, spawn } from 'node:child_process';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const { chromium } = pw;
import fs from 'fs';
import path from 'path';

const [html, secs, out, fpsArg] = process.argv.slice(2);
const fps = parseInt(fpsArg || '25', 10);
const alpha = process.argv.includes('--alpha');
const n = Math.round(parseFloat(secs) * fps);

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
const size = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]);
await page.setViewportSize({ width: size[0], height: Math.min(size[1], 1920) });

let ff;
if (out.endsWith('/')) fs.mkdirSync(out, { recursive: true });
else {
  const d = (n / fps).toFixed(2);
  const audio = `aevalsrc='0.06*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.04*sin(2*PI*330*t)+0.03*sin(2*PI*440*t)':s=44100:d=${d},lowpass=f=1200,afade=t=in:d=1,afade=t=out:st=${(d - 1.2).toFixed(2)}:d=1.2`;
  ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-f', 'lavfi', '-i', audio, '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
}
for (let i = 0; i < n; i++) {
  await page.evaluate(t => window.frame(t), i / fps);
  if (ff) {
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  } else {
    await page.screenshot({ path: path.join(out, `f${String(i).padStart(5, '0')}.png`), omitBackground: alpha });
  }
}
await browser.close();
if (ff) { ff.stdin.end(); await new Promise(r => ff.on('close', r)); }
console.log('anim', out, n, 'frames');
