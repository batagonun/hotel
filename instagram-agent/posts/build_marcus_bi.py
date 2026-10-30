# Rebuilds the 30 Oct Marcus reel as bilingual slides: every scene shows the English line with its
# Arabic translation underneath at a similar size, and runs 10s so both can be read.
# Writes overlays + story spec only (posts/2026-10-30-marcus.json keeps its schedule fields).
import json, pathlib
P = 'assets/photos/b28/'
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

name = '2026-10-30-marcus'
scenes = [
 (P+'ma_bust.png', 10, bi(1, 'Weekly Wisdom · حكمة الأسبوع', 'The soul is dyed<br>by the thoughts.', 'الروح تتلوّن بأفكارها',
                         'Marcus Aurelius · Meditations 5.16')),
 (P+'ma_rider.png', 10, bi(2, 'Who wrote it? · مين كتبها؟', 'A Roman emperor’s<br>private notes.', 'ملاحظات خاصة كتبها<br>إمبراطور روماني لنفسه',
                           size=76, ar_size=66, top=170)),
 (P+'ma_yarn.png', 10, bi(3, '', 'Like wool in dye,<br>your mind takes the color<br>of your daily thoughts.',
                          'زي الصوف في الصبغة…<br>عقلك بياخد لون أفكارك كل يوم', size=76, ar_size=68)),
 (P+'ma_ball.png', 10, bi(4, '', 'Such as are thy<br>habitual thoughts,<br>such will be thy mind.',
                          'كما تكون أفكارك المعتادة…<br>تكون طبيعة عقلك', size=74, ar_size=68)),
 (P+'ma_bust.png', 9, bi(5, '', 'What color are your<br>thoughts today?', 'أفكارك النهارده لونها إيه؟',
                         'One word · قولها في كلمة 👇<br><span style="font-size:28px;opacity:.85">Photos: Wilfredor · julian mora · Philip Estrada (CC0) · Alvesgaspar (PD)</span>')),
]
ovs = dict(width=1080, height=1920, posts=[s[2] for s in scenes])
pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(scenes)])
pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
print(name, f"{sum(s[1] for s in scenes) - 0.7 * (len(scenes) - 1):.1f}s")
