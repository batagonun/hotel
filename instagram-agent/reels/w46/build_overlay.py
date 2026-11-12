# Builds a transparent text overlay scene (window.frame(t)) for real-footage reels; render with
# `node tools/anim.mjs <html> <secs> <dir>/ 25 --alpha`, then composite with compose_video.sh.
import json, sys, html
HEAD = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Regular.ttf');font-weight:400}
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Bold.ttf');font-weight:700}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;direction:rtl}
.shade{position:absolute;left:0;right:0;top:0;height:1150px;background:linear-gradient(180deg,rgba(0,0,0,.8),rgba(0,0,0,.6) 65%,rgba(0,0,0,0))}
.shadeb{position:absolute;left:0;right:0;bottom:0;height:440px;background:linear-gradient(0deg,rgba(0,0,0,.72),rgba(0,0,0,0))}
.cap{position:absolute;top:230px;left:60px;right:60px;text-align:center;color:#fff;font:700 88px/1.45 'Cairo';text-shadow:0 4px 24px rgba(0,0,0,.6);display:none}
.cap span{display:inline-block;margin:0 10px}
.cap .y{color:#ffd166}
.sub{position:absolute;left:70px;right:70px;text-align:center;color:#fff;font:400 62px/1.5 'Cairo';text-shadow:0 3px 16px rgba(0,0,0,.75);display:none}
.sub b{color:#ffd166}
.pill{display:inline-block;background:#ffd166;color:#1d1a16;border-radius:40px;padding:4px 34px;font:700 46px 'Cairo';margin-bottom:22px}
.src{position:absolute;bottom:120px;left:50px;right:50px;text-align:center;color:#fff;font:400 31px/1.5 'Cairo';opacity:0}
.h{position:absolute;bottom:50px;left:0;right:0;text-align:center;color:#fff;font:600 30px 'Cairo';letter-spacing:4px;opacity:.7;direction:ltr}
</style></head><body><div class="shade"></div><div class="shadeb"></div>
"""
TAIL = """<script>
const C=%s,S=%s,SRC_AT=%s;
const cl=v=>Math.max(0,Math.min(1,v)),ease=v=>1-Math.pow(1-cl(v),3);
function show(el,a,y=0,s=1){el.style.opacity=a;el.style.transform='translateY('+y+'px) scale('+s+')'}
window.frame=function(t){
 C.forEach((c,i)=>{const el=document.getElementById('c'+i);const on=t>=c[0]&&t<c[1];el.style.display=on?'block':'none';if(!on)return;
  const out=cl((c[1]-t)/0.4);[...el.querySelectorAll('span')].forEach((w,j)=>{const k=ease((t-c[0]-0.15-j*c[2])/0.45);show(w,k*out,(1-k)*30,0.85+0.15*k)});
  const p=el.querySelector('.pill');if(p)show(p,ease((t-c[0])/0.5)*out)});
 S.forEach((s,i)=>{const el=document.getElementById('x'+i);const on=t>=s[0]&&t<s[1];el.style.display=on?'block':'none';if(on){const k=ease((t-s[0])/0.6);show(el,k*cl((s[1]-t)/0.4),(1-k)*20)}});
 document.getElementById('src').style.opacity=ease((t-SRC_AT)/0.8);
};
window.frame(0);
</script></body></html>"""
def words(line):
    return ' '.join(f'<span class="{"y" if w.startswith("*") else ""}">{html.escape(w.lstrip("*"))}</span>' for w in line.split())
spec = json.load(open(sys.argv[1])); body = []; C = []; S = []
for i, c in enumerate(spec['caps']):
    pill = f'<div class="pill">{c["pill"]}</div><br>' if c.get('pill') else ''
    st = f' style="font-size:{c["size"]}px"' if c.get('size') else ''
    body.append(f'<div class="cap" id="c{i}"{st}>{pill}' + '<br>'.join(words(l) for l in c['lines']) + '</div>')
    C.append([c['t0'], c['t1'], c.get('step', 0.28)])
for i, s in enumerate(spec['subs']):
    body.append(f'<div class="sub" id="x{i}" style="top:{s.get("top", 640)}px">{s["html"]}</div>')
    S.append([s['t0'], s['t1']])
body.append(f'<div class="src" id="src">{spec["src"]}</div><div class="h">@batagonun</div>')
open(sys.argv[2], 'w').write(HEAD + '\n'.join(body) + TAIL % (json.dumps(C), json.dumps(S), spec['src_at']))
