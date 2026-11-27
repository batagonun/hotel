#!/usr/bin/env python3
"""Builds one w49b reel from a JSON spec: HTML scene -> tools/anim.mjs -> (optional Gemini voice) -> mp4.

Usage: python3 reels/w49b/build.py reels/w49b/<id>.json [--html-only] [--no-voice]
Layer types: verse (lines of [text, rhyme]), cards, quiz. Every layer has dur, bg (image or .mp4), credit.
A layer may carry "say": text read by tools/tts.py (fusha/masri from spec "voice_topic").
"""
import json, os, subprocess, sys, html, wave, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # instagram-agent
HERE = os.path.dirname(os.path.abspath(__file__))
spec_path = sys.argv[1]
S = json.load(open(spec_path, encoding='utf-8'))
rid = S['id']
media = os.path.join(ROOT, 'media', 'w49b')
work = os.path.join(media, 'work', rid); os.makedirs(work, exist_ok=True)
outdir = os.path.join(ROOT, 'out', 'w49b'); os.makedirs(outdir, exist_ok=True)
ACC = S.get('accent', '#ffd54a')


def wav_dur(p):
    with contextlib.closing(wave.open(p)) as w:
        return w.getnframes() / float(w.getframerate())


# ---- voice segments -------------------------------------------------------
voiced = 'voice_topic' in S and '--no-voice' not in sys.argv and '--html-only' not in sys.argv
if voiced:
    for i, L in enumerate(S['layers']):
        if not L.get('say'):
            continue
        txt = os.path.join(work, f'say{i}.txt'); wav = os.path.join(work, f'say{i}.wav')
        regen = not (os.path.exists(wav) and os.path.exists(txt) and open(txt, encoding='utf-8').read() == L['say'])
        if regen:
            open(txt, 'w', encoding='utf-8').write(L['say'])
            env = dict(os.environ, GEMINI_API_KEY='dummy')
            subprocess.run(['python3', '-I', os.path.join(ROOT, 'tools', 'tts.py'), txt, wav, '--topic', S['voice_topic']]
                           + (['--voice', S['voice']] if S.get('voice') else []), check=True, env=env)
        L['_vd'] = wav_dur(wav)
        L['dur'] = max(L['dur'], round(L['_vd'] + 1.0, 2))

# ---- schedule ---------------------------------------------------------------
t = 0; sched = []
for L in S['layers']:
    sched.append([round(t, 2), round(t + L['dur'], 2)]); t += L['dur']
TOTAL = round(t, 2)


def esc(s):
    return s  # specs are trusted, hand-written HTML fragments


def bg_html(i, L):
    bg = L['bg']; blur = ' blurred' if L.get('blur') else ''
    if bg.endswith('.mp4'):
        return f'<video class="photo vid{blur}" id="p{i}" src="{bg}" muted preload="auto"></video>'
    pos = L.get('pos', 'center')
    if L.get('fit') == 'portrait':
        return (f'<div class="photo blurred" style="background-image:url(\'{bg}\')"></div>'
                f'<div class="portrait{" wide" if L.get("wide") else ""}" id="p{i}" style="background-image:url(\'{bg}\');background-position:{pos};background-size:{L.get("psize", "cover")}"></div>')
    return f'<div class="photo{blur}" id="p{i}" style="background-image:url(\'{bg}\');background-position:{pos}"></div>'


parts = []
for i, L in enumerate(S['layers']):
    h = [f'<div class="L" id="L{i}">', bg_html(i, L), '<div class="tint"></div><div class="glow"></div>']
    if L['type'] == 'verse':
        h.append(f'<div class="band" id="b{i}">')
        for ln in L['lines']:
            txt, rh = (ln + [''])[:2]
            h.append(f'<div class="v">{esc(txt)}<span class="rh">{esc(rh)}</span></div>')
        h.append('</div>')
        if L.get('who'):
            h.append(f'<div class="who" id="w{i}">{esc(L["who"])}</div>')
    elif L['type'] == 'cards':
        for j, c in enumerate(L['cards']):
            st = f'top:{c.get("top", 500 + j * 300)}px'
            if c.get('size'): st += f';font-size:{c["size"]}px'
            if c.get('color'): st += f';color:{c["color"]}'
            h.append(f'<div class="card" id="c{i}_{j}" style="{st}">{esc(c["t"])}</div>')
    elif L['type'] == 'quiz':
        h.append(f'<div class="qt" id="q{i}">{esc(L["q"])}</div>')
        for j, a in enumerate(L['a']):
            h.append(f'<div class="btn" id="a{i}_{j}" style="top:{900 + j * 230}px">{esc(a)}</div>')
        h.append(f'<div class="bar"><i id="bar{i}"></i></div>')
    if L.get('credit'):
        h.append(f'<div class="credit">{esc(L["credit"])}</div>')
    h.append('</div>')
    parts.append('\n'.join(h))

js_layers = json.dumps([{'type': L['type'], 'n': len(L.get('cards', L.get('lines', L.get('a', [])))),
                         'at': [c.get('at', 0.2 + j * 1.2) for j, c in enumerate(L.get('cards', []))],
                         'kb': 'portrait' if L.get('fit') == 'portrait' else L.get('kb', 'in'), 'vid': L['bg'].endswith('.mp4'), 'vs': L.get('vstart', 0)}
                        for L in S['layers']])

page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Amiri';src:url('../../fonts/Amiri-Bold.ttf');font-weight:700}}
@font-face{{font-family:'Cairo';src:url('../../fonts/Cairo-Regular.ttf');font-weight:400}}
@font-face{{font-family:'Cairo';src:url('../../fonts/Cairo-Bold.ttf');font-weight:700}}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0b0b10}}
body>div{{direction:rtl}}
.L{{position:absolute;inset:0;opacity:0;display:none;overflow:hidden}}
.photo{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background-size:cover;background-position:center;transform:scale(1.2);filter:{S.get('filter', 'sepia(.25) brightness(.95) contrast(1.08)')}}}
.photo.blurred{{filter:brightness(.55) blur(12px)}}
.portrait{{position:absolute;left:250px;right:250px;top:300px;height:700px;background-size:cover;border:5px solid {ACC};border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,.7);filter:{S.get('filter', 'sepia(.25) brightness(.95) contrast(1.08)')}}}
.portrait.wide{{left:50px;right:50px;top:380px;height:600px}}
.tint{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.45),rgba(0,0,0,0) 30%,rgba(0,0,0,0) 62%,rgba(0,0,0,.6))}}
.glow{{position:absolute;inset:0;background:radial-gradient(ellipse 80% 34% at 50% 48%,rgba(0,0,0,.45),rgba(0,0,0,0))}}
.T{{text-shadow:0 0 3px #000,0 0 8px #000,0 3px 10px rgba(0,0,0,.95),0 6px 30px rgba(0,0,0,.9)}}
.band{{position:absolute;left:0;right:0;top:{S.get('verse_top', 700)}px;padding:40px 30px;text-align:center}}
.v{{font:700 {S.get('verse_size', 92)}px/1.75 'Amiri';color:#fff;white-space:nowrap}}
.v .rh{{color:{ACC}}}
.who{{position:absolute;left:0;right:0;top:{S.get('verse_top', 700) + 420}px;text-align:center;font:700 44px 'Cairo';color:{ACC}}}
.series{{position:absolute;top:110px;left:0;right:0;text-align:center;z-index:9}}
.series span{{font:700 38px 'Cairo';color:#111;background:{ACC};padding:8px 30px;border-radius:40px}}
.qt{{position:absolute;top:470px;left:60px;right:60px;text-align:center;font:700 92px/1.4 'Cairo';color:#fff}}
.btn{{position:absolute;left:140px;right:140px;height:170px;border-radius:30px;border:4px solid #fff;color:#fff;font:700 66px/170px 'Cairo';text-align:center;box-shadow:0 0 20px rgba(0,0,0,.6),inset 0 0 20px rgba(0,0,0,.4)}}
.bar{{position:absolute;top:1480px;left:200px;right:200px;height:14px;border-radius:7px;background:rgba(255,255,255,.2);overflow:hidden;box-shadow:0 0 12px #000}}
.bar i{{display:block;height:100%;width:0;background:{ACC}}}
.card{{position:absolute;left:50px;right:50px;padding:20px;color:#fff;text-align:center;font:700 64px/1.5 'Cairo'}}
.card b{{color:{ACC}}}
.src{{position:absolute;bottom:115px;left:50px;right:50px;text-align:center;font:400 27px/1.5 'Cairo';color:#eee;z-index:9;opacity:0}}
.handle{{position:absolute;bottom:50px;left:0;right:0;text-align:center;font:700 28px 'Cairo';color:#fff;opacity:.7;direction:ltr;letter-spacing:4px;z-index:9}}
.credit{{position:absolute;bottom:62px;right:36px;font:400 20px 'Cairo';color:rgba(255,255,255,.7);z-index:9}}
.band,.who,.qt,.btn,.card,.src,.credit{{text-shadow:0 0 3px #000,0 0 8px #000,0 3px 10px rgba(0,0,0,.95),0 6px 30px rgba(0,0,0,.9)}}
</style></head><body>
<div style="position:absolute;top:-500px;font:700 40px Amiri">ا</div><div style="position:absolute;top:-500px;font:700 40px Cairo">ا</div><div style="position:absolute;top:-500px;font:400 40px Cairo">ا</div>
{chr(10).join(parts)}
<div class="series"><span>{S['series']}</span></div>
<div class="src" id="src">{S['src']}</div>
<div class="handle">@batagonun</div>
<script>
const S={json.dumps(sched)},Ls={js_layers},TOTAL={TOTAL};
const cl=v=>Math.max(0,Math.min(1,v)),ease=v=>1-Math.pow(1-cl(v),3);
const $=id=>document.getElementById(id);
function pop(id,lt,a,dy){{const e=$(id);if(!e)return;const k=ease((lt-a)/0.6);e.style.opacity=k;e.style.transform='translateY('+((1-k)*(dy===undefined?40:dy))+'px)'}}
function lines(id,lt,a){{[...$(id).children].forEach((c,j)=>{{const k=ease((lt-a-j*1.2)/0.9);c.style.opacity=k;c.style.filter='blur('+((1-k)*10)+'px)'}})}}
window.frame=async function(t){{
 const waits=[];
 S.forEach((s,i)=>{{const L=$('L'+i);const fi=i==0?1:cl((t-s[0])/0.4),fo=i==S.length-1?1:cl((s[1]-t)/0.4);L.style.opacity=Math.min(fi,fo);const on=(t>=s[0]-.01&&t<s[1]+.01);L.style.display=on?'block':'none';
  if(!on)return; const lt=t-s[0],D=s[1]-s[0],P=Ls[i],p=$('p'+i);
  const sc=P.kb=='portrait'?1+lt*0.006:(P.kb=='out'?1.3-lt*0.012:1.2+lt*0.015); p.style.transform='scale('+sc+')';
  if(P.vid){{const want=P.vs+lt; if(Math.abs(p.currentTime-want)>0.02){{waits.push(new Promise(r=>{{p.addEventListener('seeked',r,{{once:true}});p.currentTime=want}}))}}}}
  if(P.type=='verse'){{pop('b'+i,lt,0.1,0);lines('b'+i,lt,0.3);pop('w'+i,lt,0.3+P.n*1.2)}}
  else if(P.type=='cards'){{P.at.forEach((a,j)=>pop('c'+i+'_'+j,lt,a))}}
  else if(P.type=='quiz'){{pop('q'+i,lt,0.1);for(let j=0;j<P.n;j++)pop('a'+i+'_'+j,lt,0.9+j*0.6);$('bar'+i).style.width=(cl((lt-1.8)/(D-2.2))*100)+'%'}}
 }});
 $('src').style.opacity=ease((t-(TOTAL-3.2))/0.8);
 if(waits.length) await Promise.all(waits);
}};
window.frame(0);
</script></body></html>'''

scene = os.path.join(HERE, f'{rid}.html')
open(scene, 'w', encoding='utf-8').write(page)
print('scene', scene, 'total', TOTAL)
if '--html-only' in sys.argv:
    sys.exit(0)

music = os.path.join(media, 'music', S['music'])
raw = os.path.join(work, 'raw.mp4')
if '--mix-only' not in sys.argv: subprocess.run(['node', os.path.join(ROOT, 'tools', 'anim.mjs'), scene, str(TOTAL), raw, '25', f'--music={music}@{S.get("music_offset", 0)}'], check=True)
final = os.path.join(outdir, f'{rid}.mp4')
if voiced:
    ins, flt, k = ['-i', raw], [], 1
    for i, L in enumerate(S['layers']):
        if L.get('say'):
            ins += ['-i', os.path.join(work, f'say{i}.wav')]
            d = int((sched[i][0] + 0.35) * 1000)
            flt.append(f'[{k}:a]aresample=44100,adelay={d}|{d},volume=1.5[v{k}]'); k += 1
    vlabels = ''.join(f'[v{j}]' for j in range(1, k))
    flt.append(f'{vlabels}amix=inputs={k - 1}:normalize=0,asplit=2[voice][voice2]')
    flt.append('[0:a]volume=0.45[mus]')
    flt.append('[mus][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck]')
    flt.append('[duck][voice2]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[a]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[a]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', str(TOTAL), '-movflags', '+faststart', final], check=True)
else:
    os.replace(raw, final)
print('reel', final, TOTAL)
