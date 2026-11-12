# Builds kinetic-typography poem scenes (window.frame(t)) from a short spec; render with tools/anim.mjs.
import json, sys, html
HEAD = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Amiri';src:url('../../fonts/Amiri-Bold.ttf');font-weight:700}
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Regular.ttf');font-weight:400}
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Bold.ttf');font-weight:700}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0d0b1a}
canvas{position:absolute;inset:0}
.seg{position:absolute;left:50px;right:50px;top:0;bottom:0;display:none;flex-direction:column;align-items:center;justify-content:center;direction:rtl;text-align:center;color:#f6efe3}
.talk{font:700 84px/1.5 'Cairo'}
.talk .y{color:#f2c75c}
.verse{font:700 104px/1.55 'Amiri'}
.verse span,.talk span{display:inline-block;margin:0 12px}
.gold{color:#f2c75c;text-shadow:0 0 40px rgba(242,199,92,.45)}
.note{font:400 50px/1.6 'Cairo';margin-top:50px;opacity:.92}
.note b{color:#f2c75c}
.src{position:absolute;bottom:120px;left:40px;right:40px;text-align:center;font:400 32px/1.5 'Cairo';color:#f6efe3;opacity:0;direction:rtl}
.handle{position:absolute;bottom:50px;left:0;right:0;text-align:center;font:600 30px 'Cairo';letter-spacing:4px;color:#f6efe3;opacity:.6;direction:ltr}
</style></head><body><canvas id="c" width="1080" height="1920"></canvas>
"""
TAIL = """<script>
const SEG=%s, HUE=%s, SRC_AT=%s;
const c=document.getElementById('c'),x=c.getContext('2d');
let seed=7;const rnd=()=>((seed=seed*16807%%2147483647)/2147483647);
const P=[...Array(70)].map(()=>({x:rnd()*1080,y:rnd()*1920,r:1+rnd()*3,s:10+rnd()*30,p:rnd()*6}));
const cl=v=>Math.max(0,Math.min(1,v)),ease=v=>1-Math.pow(1-cl(v),3);
window.frame=function(t){
 const g=x.createLinearGradient(0,0,1080,1920);
 g.addColorStop(0,'hsl('+(HUE[0]+Math.sin(t/4)*12)+',45%%,9%%)');g.addColorStop(1,'hsl('+(HUE[1]+Math.cos(t/5)*12)+',40%%,15%%)');
 x.fillStyle=g;x.fillRect(0,0,1080,1920);
 for(const p of P){const y=(p.y-t*p.s+9600)%%1920;x.globalAlpha=.22+.22*Math.sin(t*1.5+p.p);x.fillStyle='#f2c75c';x.beginPath();x.arc(p.x,y,p.r,0,7);x.fill()}
 x.globalAlpha=1;
 SEG.forEach((s,i)=>{const el=document.getElementById('s'+i);const on=t>=s[0]&&t<s[1];el.style.display=on?'flex':'none';if(!on)return;
  const out=cl((s[1]-t)/0.5);
  [...el.querySelectorAll('span')].forEach((w,j)=>{const k=ease((t-s[0]-0.15-j*s[2])/0.6);w.style.opacity=k*out;w.style.transform='translateY('+((1-k)*40)+'px)';w.style.filter='blur('+((1-k)*8)+'px)'});
  const n=el.querySelector('.note');if(n){const k=ease((t-s[3])/0.8);n.style.opacity=k*out;n.style.transform='translateY('+((1-k)*30)+'px)'}});
 document.getElementById('src').style.opacity=ease((t-SRC_AT)/0.8);
};
window.frame(0);
</script></body></html>"""
def words(line, cls=''):
    out=[]
    for w in line.split():
        g = w.startswith('*'); w = w.lstrip('*')
        out.append(f'<span class="{"gold" if g else cls}">{html.escape(w)}</span>')
    return ' '.join(out)
spec = json.load(open(sys.argv[1]))
body = []; segs = []
for i, s in enumerate(spec['segments']):
    kind = s['kind']
    lines = '<br>'.join(words(l) for l in s['lines'])
    note = f'<div class="note">{s["note"]}</div>' if s.get('note') else ''
    body.append(f'<div class="seg" id="s{i}"><div class="{kind}">{lines}</div>{note}</div>')
    segs.append([s['t0'], s['t1'], s.get('step', 0.4), s.get('note_at', s['t0'] + 2)])
body.append(f'<div class="src" id="src">{spec["src"]}</div><div class="handle">@batagonun</div>')
open(sys.argv[2], 'w').write(HEAD + '\n'.join(body) + TAIL % (json.dumps(segs), json.dumps(spec.get('hue', [250, 300])), spec['src_at']))
