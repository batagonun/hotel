# Reel cover generator: python3 gen.py -> writes <name>.html per spec; render with tools/story_card.mjs
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
SPECS = json.load(open(os.path.join(H, 'specs.json')))
TPL = r'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Bold.ttf');font-weight:700}
@font-face{font-family:'Cairo';src:url('../../fonts/Cairo-Regular.ttf');font-weight:400}
@font-face{font-family:'Amiri';src:url('../../fonts/Amiri-Bold.ttf');font-weight:700}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#111}
.bg{position:absolute;inset:0;overflow:hidden}
.bg img{position:absolute;width:100%;height:100%;object-fit:cover;object-position:__POS__;filter:__FILTER__;transform:scale(__ZOOM__)}
.shade{position:absolute;inset:0;background:
 linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 34%,rgba(0,0,0,.62) 50%,rgba(0,0,0,.62) 66%,rgba(0,0,0,0) 80%,rgba(0,0,0,.6) 100%)}
.frame{position:absolute;inset:34px;border:3px solid rgba(255,213,74,.85)}
body>div{direction:rtl}
.tag{position:absolute;top:290px;left:0;right:0;text-align:center;font:700 44px Cairo;color:#ffd54a;letter-spacing:1px;text-shadow:0 3px 12px rgba(0,0,0,.9)}
.tag:before,.tag:after{content:'';display:inline-block;width:70px;height:3px;background:#ffd54a;vertical-align:middle;margin:0 22px}
.hook{position:absolute;left:60px;right:60px;top:__TOP__px;text-align:center;font:700 __SIZE__px/1.22 Cairo;color:#fff;
 text-shadow:0 6px 0 rgba(0,0,0,.55),0 0 30px rgba(0,0,0,.95),0 0 60px rgba(0,0,0,.7)}
.hook b{color:#ffd54a}
.sub{margin-top:34px;font:400 50px/1.4 __SUBFONT__;color:#fff}
.cta{position:absolute;bottom:300px;left:0;right:0;text-align:center;font:700 40px Cairo;color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.95)}
.cta span{color:#ffd54a}
.handle{position:absolute;bottom:90px;left:0;right:0;text-align:center;font:700 30px Cairo;color:rgba(255,255,255,.75);direction:ltr!important}
__EXTRA_CSS__
</style></head><body>
<div class="bg">__BG__</div><div class="shade"></div><div class="frame"></div>
<div class="tag">__TAG__</div>
<div class="hook">__HOOK__<div class="sub">__SUB__</div></div>
<div class="cta">__CTA__</div>
<div class="handle">@batagonun</div>
</body></html>'''
SHADOW_CSS = '''.cloth{position:absolute;inset:0;background:radial-gradient(ellipse 75% 55% at 50% 50%,#ffd99a,#f0a24a 55%,#8a3e10 95%)}
.bg img.sil{height:auto;object-fit:fill;transform:none;mix-blend-mode:multiply;filter:blur(1.2px) contrast(1.4)}'''
for name, s in SPECS.items():
    if s.get('bg_html'):
        bg, extra = s['bg_html'], SHADOW_CSS
    else:
        bg, extra = '<img src="%s">' % s['img'], ''
    out = TPL
    for k, v in {'__BG__': bg, '__EXTRA_CSS__': extra, '__TAG__': s['tag'], '__HOOK__': s['hook'],
                 '__SUB__': s.get('sub', ''), '__CTA__': s.get('cta', 'الحكاية كاملة <span>جوّه</span>'),
                 '__POS__': s.get('pos', 'center'), '__FILTER__': s.get('filter', 'brightness(1.05) contrast(1.08)'),
                 '__ZOOM__': str(s.get('zoom', 1)), '__TOP__': str(s.get('top', 760)), '__SIZE__': str(s.get('size', 132)),
                 '__SUBFONT__': s.get('subfont', 'Amiri')}.items():
        out = out.replace(k, v)
    open(os.path.join(H, name + '.html'), 'w').write(out)
    print(name)
