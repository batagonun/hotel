# Builds overlays + story spec for the 2 Nov reel (replaces the cancelled «التذكرتين» script; same readability rules:
# headline >= 80px, sub >= 48px, 6.5-10s per scene). Opens with the user's line; Nizar's «اختاري» answers it.
import json, pathlib
A, B = 'assets/photos/b33/', 'assets/photos/b34/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52, lang='ar'):
    return dict(id=f'o{i}', scene='none', lang=lang, transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

reels = {
 '2026-11-02-nizar-afraid': dict(
  date='2026-11-02T10:00',
  scenes=[
   (A+'tc_rain.png', 7, ov(1, '', 'بتحبها…<br>بس شايفها خايفة ومترددة؟', '', size=92)),
   (B+'af_road.png', 7, ov(2, '', 'تقرّب خطوة…<br>وترجع اتنين', 'وإنت واقف مستني', size=100, sub_size=58)),
   (A+'tc_books.png', 6.5, ov(3, '', 'نزار قباني حسّ بيك<br>من 56 سنة…', 'وكتبلها:', size=92, sub_size=58)),
   (B+'af_shore.png', 9, ov(4, '', '«مُرهقةٌ أنتِ… وخائفةٌ<br>وطويلٌ جداً… مشواري»', '', size=84)),
   (A+'tc_sea.png', 8, ov(5, '', '«غوصي في البحرِ أو ابتعدي<br>لا بحرٌ من غيرِ دوارِ»', '', size=84)),
   (A+'tc_train.png', 8.5, ov(6, '', '«لا توجدُ منطقةٌ وسطى<br>ما بينَ الجنّةِ والنارِ»', '', size=84)),
   (B+'af_fog.png', 7, ov(7, 'نزار قباني · «اختاري» · قصائد متوحشة 1970', 'هتستنّاها…<br>ولا هتقول لها: اختاري؟', '👇'
                          + SMALL.format('النص: بوابة الشعراء · الصور: ويكيميديا كومنز (CC0)'), size=92, sub_size=56, top=200)),
  ],
  caption='''بتحبها… بس شايفها خايفة ومترددة.
تقرّب خطوة، وترجع اتنين، وإنت في النص مستني.

نزار قباني كتبلها من 56 سنة:
«مُرهقةٌ أنتِ وخائفةٌ
وطويلٌ جداً مشواري
غوصي في البحرِ أو ابتعدي
لا بحرٌ من غيرِ دوارِ»

وقالها بوضوح:
«لا توجدُ منطقةٌ وسطى
ما بينَ الجنّةِ والنارِ»

القصيدة اسمها «اختاري»، وهي أول قصيدة في ديوان «قصائد متوحشة» (1970)، وكاظم الساهر غنّاها «إني خيرتك فاختاري».

هتستنّاها… ولا هتقول لها: اختاري؟ 👇

📚 النص: بوابة الشعراء · الديوان: رسالة «دلالات الألوان في شعر نزار قباني»، جامعة النجاح الوطنية
📷 الصور: ويكيميديا كومنز (Milada Vigerova · Jamie Street · Eli Francis · Nicolas Prieto · Mike Wilson · Kayle Kaupanger · Joshua Sortino، CC0)

#نزار_قباني #اختاري #إني_خيرتك_فاختاري #شعر #قصائد_متوحشة'''),
}

for name, r in reels.items():
    ovs = dict(width=1080, height=1920, posts=[s[2] for s in r['scenes']])
    pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
    story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(r['scenes'])])
    pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
    meta = dict(batch='2026-11-02-single', post=name, date=r['date'], status='pending_review', format='REEL',
                caption=r['caption'], media=f'out/{name}/{name}.mp4')
    pathlib.Path(f'posts/{name}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    total = sum(s[1] for s in r['scenes']) - 0.7 * (len(r['scenes']) - 1)
    print(name, f'{total:.1f}s', len(r['caption']), 'chars')
