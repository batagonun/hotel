# UNESCO carousel (29 Nov): photo on top, ivory "paper" panel at the bottom with dark text (high legibility),
# a tatreez-style stitched strip on the panel edge. Different template from the w48 "abyat" carousel.
import os
here = os.path.dirname(os.path.abspath(__file__))
F = '../../../fonts/'
CSS = f"""
@font-face{{font-family:'Amiri';src:url('{F}Amiri-Bold.ttf');font-weight:700}}
@font-face{{font-family:'Cairo';src:url('{F}Cairo-Regular.ttf');font-weight:400}}
@font-face{{font-family:'Cairo';src:url('{F}Cairo-Bold.ttf');font-weight:700}}
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;direction:rtl;text-align:right;background:#14110e}}
.ph{{position:absolute;inset:0 0 auto 0;height:760px;background-size:cover;background-position:center}}
.ph::after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,0) 35%)}}
.top{{position:absolute;top:44px;right:56px;left:56px;display:flex;justify-content:space-between;align-items:center;z-index:2}}
.series{{font:700 30px 'Cairo';color:#fff;background:rgba(20,17,14,.72);padding:6px 22px;border-radius:40px}}
.num{{font:700 30px 'Cairo';color:#fff;background:#b3261e;padding:6px 20px;border-radius:40px;direction:ltr}}
.panel{{position:absolute;left:0;right:0;bottom:0;height:640px;background:#f7efe0;color:#1d1a16}}
.stitch{{position:absolute;left:0;right:0;top:-18px;height:18px;
 background:repeating-linear-gradient(45deg,#b3261e 0 9px,transparent 9px 18px),repeating-linear-gradient(-45deg,#1f6b3a 0 9px,#f7efe0 9px 18px)}}
.yr{{position:absolute;top:48px;right:64px;font:700 30px 'Cairo';color:#fff;background:#1f6b3a;padding:4px 22px;border-radius:8px}}
.t{{position:absolute;top:110px;right:64px;left:64px;font:700 76px/1.35 'Cairo';color:#1d1a16}}
.d{{position:absolute;top:240px;right:64px;left:64px;font:400 42px/1.65 'Cairo';color:#2b2620}}
.d b{{color:#b3261e}}
.s{{position:absolute;bottom:70px;right:64px;left:64px;font:400 25px/1.5 'Cairo';color:#6b6155}}
.h{{position:absolute;bottom:26px;left:64px;font:700 24px 'Cairo';color:#8a7f72;direction:ltr;letter-spacing:3px}}
.ai{{position:absolute;top:712px;left:20px;font:400 20px 'Cairo';color:rgba(255,255,255,.75);z-index:2}}
"""
SRC = "📚 المصدر: اليونسكو، قوائم التراث الثقافي غير المادي · <span dir=\"ltr\">ich.unesco.org</span>"
def page(name, img, body, num, extra_css=''):
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{extra_css}</style></head><body>
<div class="ph" style="background-image:url('../../../media/{img}')"></div>
<div class="top"><div class="series">فلسطين في اليونسكو</div><div class="num">{num}</div></div>
<div class="ai">صورة مولّدة بالذكاء الاصطناعي</div>
<div class="panel"><div class="stitch"></div>{body}<div class="h">@batagonun</div></div></body></html>"""
    open(os.path.join(here, name + '.html'), 'w').write(html)

COVER_CSS = """
.cv{position:absolute;inset:0;background:url('../../../media/w48b/ai-tatreez.png') center/cover;filter:brightness(.42) saturate(.9)}
.cvg{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,8,6,.2),rgba(10,8,6,.85) 75%)}
.k{position:absolute;top:120px;right:0;left:0;text-align:center;font:700 34px 'Cairo';color:#fff}
.k span{background:#b3261e;padding:8px 28px;border-radius:40px}
.big{position:absolute;top:330px;right:60px;left:60px;text-align:center;font:700 112px/1.3 'Cairo';color:#fff;text-shadow:0 4px 24px rgba(0,0,0,.9)}
.n9{display:inline-block;background:#f7efe0;color:#1d1a16;padding:0 30px;border-radius:14px}
.sub2{position:absolute;top:820px;right:60px;left:60px;text-align:center;font:400 44px/1.6 'Cairo';color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.95)}
.sw{position:absolute;bottom:150px;right:0;left:0;text-align:center;font:700 40px 'Cairo';color:#fff}
.strip{position:absolute;left:0;right:0;bottom:0;height:22px;background:repeating-linear-gradient(45deg,#b3261e 0 11px,#1f6b3a 11px 22px)}
.ai2{position:absolute;bottom:40px;left:30px;font:400 20px 'Cairo';color:rgba(255,255,255,.7)}
.h2{position:absolute;bottom:40px;right:40px;font:700 24px 'Cairo';color:rgba(255,255,255,.8);direction:ltr;letter-spacing:3px}
"""
open(os.path.join(here, 's0.html'), 'w').write(f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{COVER_CSS}</style></head><body>
<div class="cv"></div><div class="cvg"></div>
<div class="k"><span>29 نوفمبر · اليوم الدولي للتضامن مع الشعب الفلسطيني</span></div>
<div class="big">فلسطين سجّلت<br><span class="n9">9</span> حاجات<br>في اليونسكو</div>
<div class="sub2">تراث إنساني للعالم كله… تعرف كام واحدة فيهم؟</div>
<div class="sw">اسحب ←</div>
<div class="ai2">الخلفية مولّدة بالذكاء الاصطناعي</div><div class="h2">@batagonun</div><div class="strip"></div></body></html>""")

page('s1', 'w48c/ai-hikaye.jpg', f"""<div class="yr">2008</div><div class="t">الحكاية الفلسطينية</div>
<div class="d">حواديت شعبية بتحكيها <b>الستات</b>.<br>وحسب اليونسكو: تقريبًا كل ست فلسطينية فوق السبعين <b>حكّاءة</b>.</div>
<div class="s">{SRC}</div>""", '1/5')
page('s2', 'w48b/ai-tatreez.png', f"""<div class="yr">2021</div><div class="t">التطريز الفلسطيني</div>
<div class="d">التوب عليه طيور وشجر وورد.<br>والألوان والرسمة بتقول الست <b>من أنهي بلد</b>، و<b>متجوزة ولا لأ</b>.</div>
<div class="s">{SRC}</div>""", '2/5')
page('s3', 'w48c/ai-dabkeh.jpg', f"""<div class="yr">2023</div><div class="t">الدبكة</div>
<div class="d">رقصة جماعية على <b>آلات النفخ</b> والغُنا الشعبي.<br>بتترقص في الأفراح والأعياد، وكمان في <b>حفلات التخرج</b>.</div>
<div class="s">{SRC}</div>""", '3/5')
page('s4', 'w48c/ai-soap.jpg', f"""<div class="yr">2024</div><div class="t">الصابون النابلسي</div>
<div class="d"><b>3 مكونات بس</b>: زيت زيتون ومية وقلوي.<br>بيتعمل بعد موسم الزيتون، وعليه <b>ختم العيلة</b>، ويتخزّن <b>سنة كاملة</b>.</div>
<div class="s">{SRC}</div>""", '4/5')
LIST_CSS = """.ls{position:absolute;top:175px;right:64px;left:64px;font:400 38px/1.6 'Cairo';color:#2b2620;margin:0;padding:0;list-style:none}
.ls li b{display:inline-block;min-width:110px;color:#fff;background:#1f6b3a;border-radius:8px;text-align:center;font:700 30px/1.5 'Cairo';margin-left:18px;vertical-align:middle}
.t2{position:absolute;top:60px;right:64px;left:64px;font:700 60px/1.35 'Cairo';color:#1d1a16}"""
page('s5', 'w48c/ai-shared.jpg', f"""<div class="t2">و5 مشتركة مع دول عربية تانية</div>
<ul class="ls"><li><b>2021</b>الخط العربي</li><li><b>2022</b>النخلة</li><li><b>2023</b>النقش على المعادن</li><li><b>2024</b>الحِنّة</li><li><b>2025</b>الكحل العربي</li></ul>
<div class="s">{SRC}</div>""", '5/5', LIST_CSS)
CTA_CSS = COVER_CSS.replace('w48b/ai-tatreez.png', 'w48b/ai-olives.png') + """
.q{position:absolute;top:330px;right:70px;left:70px;text-align:center;font:700 84px/1.45 'Cairo';color:#fff;text-shadow:0 4px 24px rgba(0,0,0,.95)}
.cta{position:absolute;top:760px;right:90px;left:90px;text-align:center;font:400 46px/1.6 'Cairo';color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.95)}
.cta b{background:#f7efe0;color:#1d1a16;padding:2px 18px;border-radius:10px;font-weight:700;text-shadow:none}
.src2{position:absolute;bottom:110px;right:80px;left:80px;text-align:center;font:400 26px/1.5 'Cairo';color:rgba(255,255,255,.85)}"""
open(os.path.join(here, 's6.html'), 'w').write(f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{CTA_CSS}</style></head><body>
<div class="cv"></div><div class="cvg"></div>
<div class="q">أنهي واحدة فيهم<br>أول مرة تعرفها؟</div>
<div class="cta">قولنا في الكومنت 👇<br><br><b>ابعتها لحد بيحب فلسطين</b></div>
<div class="src2">{SRC}</div>
<div class="ai2">الخلفية مولّدة بالذكاء الاصطناعي</div><div class="h2">@batagonun</div><div class="strip"></div></body></html>""")
print('ok')
