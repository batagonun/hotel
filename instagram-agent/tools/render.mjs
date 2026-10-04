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
      <rect width="${W}" height="620" fill="url(#band)"/>
      <path d="M540 620 L540 1350" stroke="#fbf3e4" stroke-width="2" opacity=".5"/>
      ${Array.from({ length: 30 }, (_, i) => `<line x1="${30 + (i * 67) % 480}" y1="${720 + (i * 53) % 520}" x2="${15 + (i * 67) % 480}" y2="${770 + (i * 53) % 520}" stroke="#9fb1c7" stroke-width="3" opacity=".55"/>`).join('')}
      <ellipse cx="230" cy="690" rx="200" ry="70" fill="#1a1f28"/><ellipse cx="360" cy="660" rx="150" ry="60" fill="#1a1f28"/>
      <circle cx="830" cy="760" r="110" fill="#fff0c8"/>
      ${Array.from({ length: 12 }, (_, i) => { const a = i * 30 * Math.PI / 180; return `<line x1="${830 + 140 * Math.cos(a)}" y1="${760 + 140 * Math.sin(a)}" x2="${830 + 185 * Math.cos(a)}" y2="${760 + 185 * Math.sin(a)}" stroke="#fff0c8" stroke-width="8" stroke-linecap="round"/>`; }).join('')}
      <path d="M0 1180 Q 540 1120 1080 1180 L1080 1350 L0 1350Z" fill="#1b1f27" opacity=".85"/>
      <rect x="532" y="1000" width="16" height="170" fill="#1b1f27"/>
      <circle cx="540" cy="980" r="70" fill="#1b1f27"/>`
  }
};

function page(post) {
  const s = scenes[post.scene];
  const ar = post.lang === 'ar';
  const headFont = ar ? "'Amiri'" : "'Cormorant'";
  const headSize = ar ? (post.scene === 'dunes' ? 64 : 92) : 74;
  return `<!doctype html><html lang="${post.lang}" dir="${ar ? 'rtl' : 'ltr'}"><head><meta charset="utf-8"><style>
  @font-face{font-family:'Amiri';src:url('${fontDir}/Amiri-Bold.ttf');font-weight:700}
  @font-face{font-family:'Cairo';src:url('${fontDir}/Cairo-Regular.ttf');font-weight:400}
  @font-face{font-family:'Cairo';src:url('${fontDir}/Cairo-Bold.ttf');font-weight:700}
  @font-face{font-family:'Cormorant';src:url('${fontDir}/Cormorant-Italic.ttf');font-style:italic;font-weight:500}
  @font-face{font-family:'Cormorant';src:url('${fontDir}/Cormorant-SemiBold.ttf');font-weight:600}
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:${W}px;height:${H}px;overflow:hidden;position:relative;color:${s.ink}}
  svg{position:absolute;inset:0}
  .txt{position:absolute;left:90px;right:90px;top:120px;text-align:center}
  .tag{font:700 30px 'Cairo',sans-serif;letter-spacing:${ar ? 0 : 6}px;color:${s.accent};margin-bottom:38px}
  .tag:after{content:'';display:block;width:70px;height:3px;background:${s.accent};margin:22px auto 0}
  h1{font-family:${headFont};font-weight:${ar ? 700 : 500};font-style:${ar ? 'normal' : 'italic'};font-size:${headSize}px;line-height:${ar ? 1.55 : 1.18}}
  .sub{margin-top:34px;font:${ar ? 400 : 600} ${ar ? 34 : 28}px ${ar ? "'Cairo'" : "'Cormorant'"},serif;letter-spacing:${ar ? 0 : 5}px;opacity:.88}
  .handle{direction:ltr;position:absolute;bottom:44px;left:0;right:0;text-align:center;font:600 26px 'Cormorant',serif;letter-spacing:4px;color:${s.ink};opacity:.75}
  </style></head><body>
  <svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">${s.svg}</svg>
  <div class="txt"><div class="tag">${post.tag}</div><h1>${post.headline}</h1><div class="sub">${post.sub}</div></div>
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
