# Rebuilds the Durant reel as bilingual slides (same rule as build_marcus_bi.py): English line with its
# Arabic translation under it at a similar size, ~10s per slide. Writes overlays + story spec only.
import json, pathlib
P = 'assets/photos/b22/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.88'/>"
        "<stop offset='.45' stop-color='#000' stop-opacity='.6'/><stop offset='.56' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
AR = ("<div style=\"margin-top:34px;direction:rtl;font:700 {size}px/1.6 'Amiri',serif;color:#f0c96b;"
      "text-shadow:0 3px 18px rgba(0,0,0,.85),0 1px 3px rgba(0,0,0,.9)\">{}</div>")
SMALL = ("<div style=\"margin-top:26px;font:600 34px/1.5 'Cairo',sans-serif;opacity:.85;"
         "text-shadow:0 2px 10px rgba(0,0,0,.9)\">{}</div>")

def bi(i, tag, en, ar, small='', size=80, ar_size=72, top=230):
    return dict(id=f'o{i}', scene='none', lang='en', transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=en, sub='', html=AR.format(ar, size=ar_size) + (SMALL.format(small) if small else ''),
                svg=GRAD, tagSize=40, noHandle=False)

name = '2026-10-22-durant'
scenes = [
 (P+'du_wheel.png', 10, bi(1, 'Weekly Wisdom · حكمة الأسبوع', 'We are what we<br>repeatedly do.', 'إحنا اللي بنعمله<br>كل يوم وبنكرّره')),
 (P+'du_pottery.png', 10, bi(2, '', 'Excellence, then,<br>is not an act…<br>but a habit.', 'فالتميّز مش فعل عابر…<br>التميّز عادة', size=78, ar_size=70)),
 (P+'du_keys.png', 10, bi(3, 'Plot twist · المفاجأة', 'Aristotle never<br>said it.', 'أرسطو ما قالهاش', 'Will Durant · The Story of Philosophy (1926)<br>ويل ديورانت لخّص بيها فكرة أرسطو')),
 (P+'du_draw.png', 10, bi(4, '', 'You don’t become a writer<br>the day you publish.', 'مش بتبقى كاتب يوم ما تنشر…<br>بتبقى كاتب كل صبح بتكتب فيه', size=74, ar_size=64)),
 (P+'du_journal.png', 9, bi(5, '', 'One small thing.<br>Every day.', 'حاجة صغيرة… كل يوم',
                             'What habit are you building? · بتبني عادة إيه؟ 👇<br><span style="font-size:28px;opacity:.85">Photos: Quino Al · Jared Sluyter · João Silas · Tamarcus Brown · Thought Catalog (CC0)</span>')),
]
ovs = dict(width=1080, height=1920, posts=[s[2] for s in scenes])
pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(scenes)])
pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
print(name, f"{sum(s[1] for s in scenes) - 0.7 * (len(scenes) - 1):.1f}s")
