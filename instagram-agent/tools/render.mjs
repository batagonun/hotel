// Renders each post of a batch to a 1080x1350 PNG with headless Chromium (free, open source).
// Usage: node tools/render.mjs posts/<batch>.json out/<batch>
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const { chromium } = pw;
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const [batchFile, outDir] = process.argv.slice(2);
const batch = JSON.parse(fs.readFileSync(path.resolve(root, batchFile), 'utf8'));
fs.mkdirSync(path.resolve(root, outDir), { recursive: true });
const fontDir = 'file://' + path.join(root, 'fonts');

const W = 1080, H = 1350;

// Each scene: background SVG + text colours + where the text sits.
const scenes = {
  dawn: {
    ink: '#fff8ef', accent: '#f6c36b', pos: 'top',
    svg: `
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#14213d"/><stop offset=".45" stop-color="#7a3b52"/>
          <stop offset=".72" stop-color="#e07a4f"/><stop offset="1" stop-color="#f6c36b"/>
        </linearGradient>
        <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#d8794e"/><stop offset="1" stop-color="#1c2541"/>
        </linearGradient>
        <radialGradient id="sun"><stop offset="0" stop-color="#fff3c4"/><stop offset=".6" stop-color="#ffd27a"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>
      </defs>
      <rect width="${W}" height="${H}" fill="url(#sky)"/>
      <circle cx="540" cy="1000" r="260" fill="url(#sun)" opacity=".9"/>
      <circle cx="540" cy="1000" r="120" fill="#fff1c9"/>
      <rect y="1000" width="${W}" height="350" fill="url(#water)"/>
      ${Array.from({ length: 9 }, (_, i) => `<rect x="${540 - (150 - i * 14)}" y="${1018 + i * 30}" width="${300 - i * 28}" height="5" rx="2.5" fill="#ffe1a1" opacity="${0.75 - i * 0.07}"/>`).join('')}
      <path d="M0 1000 L180 985 L330 996 L470 978 L600 992 L760 975 L900 990 L1080 980 L1080 1004 L0 1004Z" fill="#1c2541" opacity=".85"/>
      <rect y="1326" width="${W}" height="8" fill="#ce1126"/><rect y="1334" width="${W}" height="8" fill="#ffffff"/><rect y="1342" width="${W}" height="8" fill="#000"/>`
  },
  listen: {
    ink: '#2b2622', accent: '#b4532e', pos: 'top',
    svg: `
      <rect width="${W}" height="${H}" fill="#f3ebe0"/>
      <g style="mix-blend-mode:multiply">
        <circle cx="430" cy="900" r="250" fill="#e3a07c" opacity=".85"/>
        <circle cx="650" cy="900" r="250" fill="#8fb8b3" opacity=".85"/>
      </g>
      ${[0, 1, 2].map(i => `<path d="M ${300 - i * 50} ${780 - i * 40} q -${70 + i * 30} 120 0 ${240 + i * 80}" stroke="#b4532e" stroke-width="7" fill="none" stroke-linecap="round" opacity="${0.6 - i * 0.15}"/>`).join('')}
      ${[0, 1, 2].map(i => `<path d="M ${780 + i * 50} ${780 - i * 40} q ${70 + i * 30} 120 0 ${240 + i * 80}" stroke="#2a6f73" stroke-width="7" fill="none" stroke-linecap="round" opacity="${0.6 - i * 0.15}"/>`).join('')}`
  },
  walk: {
    ink: '#1f3a2e', accent: '#3f7d5b', pos: 'top',
    svg: `
      <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f1e6"/><stop offset=".55" stop-color="#dfe8d4"/><stop offset="1" stop-color="#8fae8a"/></linearGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#g)"/>
      <circle cx="820" cy="700" r="70" fill="#f3d08a" opacity=".8"/>
      <path d="M0 860 Q 270 800 540 850 T 1080 830 L1080 1350 L0 1350Z" fill="#b7cba9"/>
      <path d="M0 960 Q 300 900 600 960 T 1080 940 L1080 1350 L0 1350Z" fill="#9fbb93"/>
      <path d="M520 1350 C 560 1200, 380 1120, 520 1020 S 600 900, 560 860 L 580 860 C 640 910, 600 1000, 560 1030 C 470 1110, 700 1200, 700 1350Z" fill="#efe6cf"/>
      ${[[160, 900, 1], [260, 930, .8], [880, 900, 1.1], [980, 940, .8], [90, 990, 1.2]].map(([x, y, s]) => `
        <rect x="${x - 6 * s}" y="${y - 10}" width="${12 * s}" height="${60 * s}" fill="#5b4a3a"/>
        <ellipse cx="${x}" cy="${y - 50 * s}" rx="${55 * s}" ry="${80 * s}" fill="#4f7d5c"/>`).join('')}`
  },
  shadow: {
    ink: '#efe6d2', accent: '#c9a96e', pos: 'top',
    svg: `
      <defs>
        <linearGradient id="n" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d111c"/><stop offset=".7" stop-color="#1b2436"/><stop offset="1" stop-color="#2a3349"/></linearGradient>
        <linearGradient id="sh" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#05070c" stop-opacity=".95"/><stop offset="1" stop-color="#05070c" stop-opacity="0"/></linearGradient>
      </defs>
      <rect width="${W}" height="${H}" fill="url(#n)"/>
      ${Array.from({ length: 40 }, (_, i) => `<circle cx="${(i * 263) % W}" cy="${(i * 137) % 640}" r="${(i % 3) + 1}" fill="#efe6d2" opacity="${0.25 + (i % 4) * 0.15}"/>`).join('')}
      <circle cx="930" cy="160" r="46" fill="#efe6d2" opacity=".9"/><circle cx="950" cy="148" r="44" fill="#0f1420"/>
      <rect y="1080" width="${W}" height="270" fill="#232c40"/>
      <path d="M760 1110 L 20 1060 L 0 1200 L 760 1150Z" fill="url(#sh)"/>
      <ellipse cx="800" cy="1128" rx="46" ry="30" fill="#8a8f9c"/><ellipse cx="790" cy="1118" rx="30" ry="14" fill="#b4b8c2" opacity=".6"/>`
  },
  dunes: {
    ink: '#fff5e6', accent: '#f2c27b', pos: 'top',
    svg: `
      <defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f1433"/><stop offset=".5" stop-color="#6b2f4a"/><stop offset=".8" stop-color="#c8603f"/><stop offset="1" stop-color="#eba45e"/></linearGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#s)"/>
      ${Array.from({ length: 50 }, (_, i) => `<circle cx="${(i * 197) % W}" cy="${(i * 89) % 560}" r="${(i % 3) * .8 + .8}" fill="#fff" opacity="${0.2 + (i % 5) * 0.12}"/>`).join('')}
      <circle cx="300" cy="1010" r="80" fill="#ffd79a" opacity=".85"/>
      <path d="M0 1040 Q 250 960 520 1030 T 1080 1000 L1080 1350 L0 1350Z" fill="#a8523a"/>
      <path d="M0 1130 Q 380 1040 700 1120 T 1080 1090 L1080 1350 L0 1350Z" fill="#7d3a2e"/>
      <path d="M0 1230 Q 300 1170 620 1230 T 1080 1210 L1080 1350 L0 1350Z" fill="#4e2422"/>`
  },
  cups: {
    ink: '#4a2626', accent: '#b5574b', pos: 'top',
    svg: `
      <rect width="${W}" height="${H}" fill="#f6e5dd"/>
      <ellipse cx="540" cy="1215" rx="420" ry="40" fill="#e8cfc4"/>
      ${[[370, '#b5574b'], [710, '#7b8f7a']].map(([x, c]) => `
        <path d="M${x - 110} 1000 L${x + 110} 1000 L${x + 90} 1200 Q ${x} 1225 ${x - 90} 1200Z" fill="${c}"/>
        <path d="M${x + 104} 1040 q 70 10 60 70 q -8 50 -74 50" stroke="${c}" stroke-width="18" fill="none"/>
        <ellipse cx="${x}" cy="1000" rx="110" ry="20" fill="#3e2a22"/>`).join('')}
      <path d="M370 970 C 330 900, 420 860, 380 790 S 420 690, 540 760" stroke="#b5574b" stroke-width="9" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M710 970 C 750 900, 660 860, 700 790 S 660 690, 540 760" stroke="#7b8f7a" stroke-width="9" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M540 735 c -30 -40 -90 -10 -60 35 l 60 55 l 60 -55 c 30 -45 -30 -75 -60 -35z" fill="#b5574b" opacity=".85"/>`
  },
  table: {
    ink: '#fff6ea', accent: '#f1c27d', pos: 'top',
    svg: `
      <rect width="${W}" height="${H}" fill="#6e4b32"/>
      ${Array.from({ length: 14 }, (_, i) => `<rect y="${i * 100}" width="${W}" height="2" fill="#5a3c27" opacity=".6"/>`).join('')}
      <circle cx="540" cy="975" r="295" fill="#efe3cf"/>
      <circle cx="540" cy="975" r="295" fill="none" stroke="#c96e4a" stroke-width="12" stroke-dasharray="4 16"/>
      <circle cx="540" cy="975" r="80" fill="#d5a24a"/><circle cx="540" cy="975" r="60" fill="#e8c06d"/>
      ${[0, 60, 120, 180, 240, 300].map(a => {
        const r = 200, x = 540 + r * Math.cos(a * Math.PI / 180), y = 975 + r * Math.sin(a * Math.PI / 180);
        return `<circle cx="${x}" cy="${y}" r="54" fill="#ffffff"/><circle cx="${x}" cy="${y}" r="37" fill="#f3ead9"/>
          <circle cx="${x + 10}" cy="${y - 6}" r="11" fill="#7aa15a"/><circle cx="${x - 11}" cy="${y + 8}" r="9" fill="#c94c3a"/>`;
      }).join('')}`
  },
  storm: {
    ink: '#fbf3e4', accent: '#f2c879', pos: 'top',
    svg: `
      <defs>
        <linearGradient id="l" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#232a35"/><stop offset="1" stop-color="#3d4656"/></linearGradient>
        <linearGradient id="r" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3c77e"/><stop offset="1" stop-color="#d77d4f"/></linearGradient>
      </defs>
      <rect width="${W}" height="${H}" fill="url(#l)"/>
      <path d="M1080 0 L1080 1350 L540 1350 L540 0Z" fill="url(#r)"/>
      <defs><linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141821" stop-opacity=".92"/><stop offset=".8" stop-color="#141821" stop-opacity=".75"/><stop offset="1" stop-color="#141821" stop-opacity="0"/></linearGradient></defs>
      <rect width="${W}" height="780" fill="url(#band)"/>
      <path d="M540 780 L540 1350" stroke="#fbf3e4" stroke-width="2" opacity=".5"/>
      ${Array.from({ length: 30 }, (_, i) => `<line x1="${30 + (i * 67) % 480}" y1="${880 + (i * 53) % 330}" x2="${15 + (i * 67) % 480}" y2="${930 + (i * 53) % 330}" stroke="#9fb1c7" stroke-width="3" opacity=".55"/>`).join('')}
      <ellipse cx="230" cy="830" rx="200" ry="70" fill="#1a1f28"/><ellipse cx="360" cy="800" rx="150" ry="60" fill="#1a1f28"/>
      <circle cx="830" cy="900" r="95" fill="#fff0c8"/>
      ${Array.from({ length: 12 }, (_, i) => { const a = i * 30 * Math.PI / 180; return `<line x1="${830 + 120 * Math.cos(a)}" y1="${900 + 120 * Math.sin(a)}" x2="${830 + 160 * Math.cos(a)}" y2="${900 + 160 * Math.sin(a)}" stroke="#fff0c8" stroke-width="8" stroke-linecap="round"/>`; }).join('')}
      <path d="M0 1180 Q 540 1120 1080 1180 L1080 1350 L0 1350Z" fill="#1b1f27" opacity=".85"/>
      <rect x="532" y="1000" width="16" height="170" fill="#1b1f27"/>
      <circle cx="540" cy="980" r="70" fill="#1b1f27"/>`
  },
  flag: {
    ink: '#fff8ef', accent: '#f6c36b', pos: 'top',
    svg: `
      <defs><linearGradient id="fs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2b4f"/><stop offset=".55" stop-color="#5d4a6e"/><stop offset=".85" stop-color="#d9875a"/><stop offset="1" stop-color="#f1b46c"/></linearGradient>
      <linearGradient id="sand" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e2b77e"/><stop offset="1" stop-color="#a8743f"/></linearGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#fs)"/>
      <circle cx="250" cy="1010" r="90" fill="#ffd994" opacity=".75"/>
      <rect y="1150" width="${W}" height="200" fill="#2a3d5c"/>
      ${Array.from({ length: 6 }, (_, i) => `<rect x="${60 + i * 70}" y="${1180 + i * 22}" width="${200 - i * 20}" height="4" fill="#f1b46c" opacity="${.5 - i * .06}"/>`).join('')}
      <path d="M420 1160 L640 980 L1080 965 L1080 1160Z" fill="url(#sand)"/>
      <path d="M420 1160 L640 980 L700 980 L520 1160Z" fill="#f0cf9c" opacity=".55"/>
      <rect x="742" y="700" width="9" height="290" fill="#2b2b2b"/>
      <path d="M751 710 C 820 685, 880 740, 960 715 L 960 765 C 880 790, 820 735, 751 760Z" fill="#ce1126"/>
      <path d="M751 760 C 820 735, 880 790, 960 765 L 960 815 C 880 840, 820 785, 751 810Z" fill="#ffffff"/>
      <path d="M751 810 C 820 785, 880 840, 960 815 L 960 865 C 880 890, 820 835, 751 860Z" fill="#111"/>
      <circle cx="855" cy="788" r="11" fill="#c09300"/>`
  },
  boats: {
    ink: '#fff8ef', accent: '#f6c36b', pos: 'top',
    svg: `
      <defs><linearGradient id="bs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1a33"/><stop offset=".6" stop-color="#3b3f63"/><stop offset="1" stop-color="#c77b55"/></linearGradient>
      <linearGradient id="bw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d6a8a"/><stop offset="1" stop-color="#15263f"/></linearGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#bs)"/>
      <path d="M0 860 L1080 860 L1080 800 Q 900 760 760 790 Q 600 820 420 780 Q 220 740 0 790Z" fill="#d6a66c"/>
      <path d="M0 860 L1080 860 L1080 830 Q 700 800 0 840Z" fill="#b98550"/>
      <rect y="860" width="${W}" height="490" fill="url(#bw)"/>
      ${[[180, 960, 1], [560, 1040, 1.15], [860, 980, .95], [360, 1170, 1.3]].map(([x, y, k]) => `
        <path d="M${x - 110 * k} ${y} Q ${x} ${y + 40 * k} ${x + 110 * k} ${y} L ${x + 95 * k} ${y + 28 * k} Q ${x} ${y + 55 * k} ${x - 95 * k} ${y + 28 * k}Z" fill="#1b1f27"/>
        ${[-60, -20, 20, 60].map(o => `<circle cx="${x + o * k}" cy="${y - 22 * k}" r="${11 * k}" fill="#1b1f27"/><rect x="${x + o * k - 9 * k}" y="${y - 14 * k}" width="${18 * k}" height="${18 * k}" fill="#1b1f27"/>`).join('')}
        <path d="M${x - 120 * k} ${y + 30 * k} q 60 14 120 0 t 120 0" stroke="#9cc3dd" stroke-width="3" fill="none" opacity=".5"/>`).join('')}
      <path d="M120 900 Q 260 700 520 800" stroke="#cfe6f5" stroke-width="7" fill="none" opacity=".7" stroke-linecap="round"/>
      <path d="M940 900 Q 840 700 640 800" stroke="#cfe6f5" stroke-width="7" fill="none" opacity=".7" stroke-linecap="round"/>`
  },
  memorial: {
    ink: '#f3ead8', accent: '#d9b56a', pos: 'top',
    svg: `
      <defs><linearGradient id="ms" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0f1a"/><stop offset=".75" stop-color="#18223a"/><stop offset="1" stop-color="#2c3550"/></linearGradient>
      <radialGradient id="glow" cx=".5" cy=".85" r=".5"><stop offset="0" stop-color="#d9b56a" stop-opacity=".45"/><stop offset="1" stop-color="#d9b56a" stop-opacity="0"/></radialGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#ms)"/>
      ${Array.from({ length: 90 }, (_, i) => `<circle cx="${(i * 233) % W}" cy="${(i * 97) % 900}" r="${(i % 3) * .7 + .7}" fill="#f3ead8" opacity="${0.15 + (i % 5) * 0.12}"/>`).join('')}
      <rect width="${W}" height="${H}" fill="url(#glow)"/>
      ${Array.from({ length: 10 }, (_, i) => { const x0 = 300 + i * 48; const top = 760 + Math.abs(4.5 - i) * 85; return `<path d="M${x0} 1210 L${x0 + 30} 1210 L${540 + (i - 4.5) * 8 + 4} ${top} L${540 + (i - 4.5) * 8 - 4} ${top}Z" fill="#e9e1cf" opacity="${0.55 + (i % 2) * 0.2}"/>`; }).join('')}
      <rect y="1210" width="${W}" height="140" fill="#141a2a"/>
      <rect x="230" y="1205" width="620" height="12" fill="#3a425a"/>`
  },
  card: {
    ink: '#2b2622', accent: '#b4532e', pos: 'top',
    svg: `
      <rect width="${W}" height="${H}" fill="#f3ebe0"/>
      <g style="mix-blend-mode:multiply" opacity=".55">
        <circle cx="430" cy="1210" r="210" fill="#e3a07c"/>
        <circle cx="650" cy="1210" r="210" fill="#8fb8b3"/>
      </g>
      <rect x="60" y="60" width="${W - 120}" height="${H - 120}" fill="none" stroke="#d9cbb8" stroke-width="3" rx="18"/>`
  }
};

function page(post) {
  const s = scenes[post.scene];
  const ar = post.lang === 'ar';
  const headFont = ar ? "'Amiri'" : "'Cormorant'";
  const headSize = post.size || (ar ? (post.scene === 'dunes' ? 64 : 92) : 74);
  return `<!doctype html><html lang="${post.lang}" dir="${ar ? 'rtl' : 'ltr'}"><head><meta charset="utf-8"><style>
  @font-face{font-family:'Amiri';src:url('${fontDir}/Amiri-Bold.ttf');font-weight:700}
  @font-face{font-family:'Cairo';src:url('${fontDir}/Cairo-Regular.ttf');font-weight:400}
  @font-face{font-family:'Cairo';src:url('${fontDir}/Cairo-Bold.ttf');font-weight:700}
  @font-face{font-family:'Cormorant';src:url('${fontDir}/Cormorant-Italic.ttf');font-style:italic;font-weight:500}
  @font-face{font-family:'Cormorant';src:url('${fontDir}/Cormorant-SemiBold.ttf');font-weight:600}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:${W}px;height:${H}px;overflow:hidden;position:relative;color:${s.ink}}
  svg{position:absolute;inset:0}
  .txt{position:absolute;left:90px;right:90px;top:${post.scene === 'card' ? 230 : 120}px;text-align:center}
  .tag{font:700 30px 'Cairo',sans-serif;letter-spacing:${ar ? 0 : 6}px;color:${s.accent};margin-bottom:38px}
  .tag:after{content:'';display:block;width:70px;height:3px;background:${s.accent};margin:22px auto 0}
  h1{font-family:${headFont};font-weight:${ar ? 700 : 500};font-style:${ar ? 'normal' : 'italic'};font-size:${headSize}px;line-height:${ar ? 1.55 : 1.18}}
  .sub{margin-top:34px;font:${ar ? 400 : 600} ${ar ? (post.scene === 'card' ? 40 : post.sub.length > 50 ? 28 : 34) : 28}px ${ar ? "'Cairo'" : "'Cormorant'"},serif;letter-spacing:${ar ? 0 : 5}px;opacity:.88}
  .num{display:block;font:700 170px 'Amiri',serif;color:${s.accent};line-height:1;margin-bottom:10px}
  .swipe{position:fixed;left:0;right:0;bottom:100px;text-align:center;font:700 32px 'Cairo',sans-serif;color:${s.accent}}
  .arnote{margin-top:30px;direction:rtl;font:700 40px 'Amiri',serif;color:${s.accent}}
  .handle{direction:ltr;position:absolute;bottom:44px;left:0;right:0;text-align:center;font:600 26px 'Cormorant',serif;letter-spacing:4px;color:${s.ink};opacity:.75}
  </style></head><body>
  <svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">${s.svg}</svg>
  <div class="txt"><div class="tag">${post.tag}</div><h1>${post.headline}</h1><div class="sub">${post.sub}</div>${post.ar_note ? `<div class="arnote">${post.ar_note}</div>` : ''}${post.swipe ? `<div class="swipe">${post.swipe}</div>` : ''}</div>
  <div class="handle">@batagonun</div>
  </body></html>`;
}

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const pg = await browser.newPage({ viewport: { width: W, height: H } });
for (const post of batch.posts) {
  const tmp = path.resolve(root, outDir, '_render.html');
  fs.writeFileSync(tmp, page(post));
  await pg.goto('file://' + tmp, { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const out = path.resolve(root, outDir, `${post.id}.png`);
  await pg.screenshot({ path: out });
  console.log('rendered', out);
}
fs.rmSync(path.resolve(root, outDir, '_render.html'), { force: true });
await browser.close();
