# Builds overlays + story spec for the 2 Nov reel (same readability rules as build_b19.py:
# headline >= 80px, sub >= 48px, 6.5-10s per scene). Dramatic frame is fictional; poem text is Nizar's «اختاري».
import json, pathlib
P = 'assets/photos/b33/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52, lang='ar'):
    return dict(id=f'o{i}', scene='none', lang=lang, transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

reels = {
 '2026-11-02-nizar-choose': dict(
  date='2026-11-02T10:00',
  scenes=[
   (P+'tc_platform.png', 6.5, ov(1, '', 'الساعة 11:50', 'وآخر قطر… الساعة 12', size=110, sub_size=58)),
   (P+'tc_waiting.png', 7, ov(2, '', 'هو جاب تذكرتين…', 'وهي لسه ما جاتش', size=100, sub_size=58)),
   (P+'tc_clock.png', 8, ov(3, '', 'جت… بس وقفت بعيد', 'خايفة تقرّب…<br>وخايفة تمشي', size=96, sub_size=56)),
   (P+'tc_rain.png', 9, ov(4, 'قالّها:', '«مُرهقةٌ أنتِ… وخائفةٌ<br>وطويلٌ جداً… مشواري»', '', size=84)),
   (P+'tc_sea.png', 8, ov(5, '', '«غوصي في البحرِ<br>أو ابتعدي»', 'لا بحرٌ من غيرِ دوارِ', size=96, sub_size=58)),
   (P+'tc_train.png', 8.5, ov(6, 'القطر صفّر…', '«لا توجدُ منطقةٌ وسطى<br>ما بينَ الجنّةِ والنارِ»', '', size=84)),
   (P+'tc_books.png', 7, ov(7, 'نزار قباني', '«اختاري»', 'أول قصيدة في ديوان<br>«قصائد متوحشة» · 1970'
                            + SMALL.format('النص: بوابة الشعراء · الحكاية تخيّلية<br>الصور: ويكيميديا كومنز (CC0)'), size=110, sub_size=52, top=200)),
  ],
  caption='''الساعة 11:50… وآخر قطر الساعة 12.
هو ماسك تذكرتين، وهي واقفة في نص الرصيف: لا قرّبت… ولا مشيت.

نزار قباني كتب اللحظة دي بالظبط:
«مُرهقةٌ أنتِ وخائفةٌ
وطويلٌ جداً مشواري
غوصي في البحرِ أو ابتعدي
لا بحرٌ من غيرِ دوارِ»

وقالها من غير تجميل:
«لا توجدُ منطقةٌ وسطى
ما بينَ الجنّةِ والنارِ»

القصيدة اسمها «اختاري»، وهي أول قصيدة في ديوان «قصائد متوحشة» (1970)، وكاظم الساهر غنّاها بعد كده «إني خيرتك فاختاري».

تفتكر هي ركبت القطر… ولا مشيت؟ 👇

📚 النص: بوابة الشعراء · الديوان: رسالة «دلالات الألوان في شعر نزار قباني»، جامعة النجاح الوطنية
🎬 حكاية المحطة تخيّلية، والأبيات لنزار
📷 الصور: ويكيميديا كومنز (Piron Guillaume · Clem Onojeghuo · Jiyeon Park · Milada Vigerova · Mike Wilson · Kayle Kaupanger · Eli Francis، CC0)

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
