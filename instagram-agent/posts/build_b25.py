# Builds overlays + story specs for reels 25-27 Oct (same readability rules as build_b19.py:
# headline >= 80px (verses 66px like build_b19), sub >= 48px, 6.5-10s per scene).
import json, pathlib
P = 'assets/photos/b25/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"
VERSE = "<span style='display:inline-block;line-height:2'>{}<br>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52, lang='ar'):
    return dict(id=f'o{i}', scene='none', lang=lang, transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

reels = {
 '2026-10-25-nizar': dict(
  date='2026-10-25T10:00',
  scenes=[
   (P+'nz_clouds.png', 7, ov(1, 'نزار قباني · «رصاصة الرحمة»', 'حد كسر قلبك؟', 'وفاكر إنك مش هتعدّيها؟<br>نزار عنده رد', size=100)),
   (P+'nz_trees.png', 9.5, ov(2, '', VERSE.format('مِثلَما تَطرُدُ الغُيومُ الغُيوما', 'الغَرامُ الجَديدُ يَمحو القَديما'),
                              'زي ما سحابة بتيجي تزقّ اللي قبلها…<br>الحب الجديد بيمسح القديم', size=66, sub_size=48)),
   (P+'nz_rain.png', 9, ov(3, '', VERSE.format('قُضِيَ الأمرُ.. والتَقَيتُ بأُخرى', 'والسماءَ استَعَدتُها، والنُّجوما'),
                            'خلاص، اللي فات فات…<br>ورجعتلي سمايا ونجومي', size=66, sub_size=48)),
   (P+'nz_horse.png', 9.5, ov(4, 'وأحلى بيت فيها', VERSE.format('لا تَموتُ الخُيولُ بَرداً وجوعاً', 'إنَّ لِلعاشِقينَ رَبّاً رَحيما'),
                              'الوجع مش هيموّتك…<br>ربنا رحيم بالقلوب', size=66, sub_size=48)),
   (P+'nz_alley.png', 9, ov(5, '', VERSE.format('انتَهَت أزمَتي، وفُكَّت قُيودي', 'بَعدَما كُنتُ قاصِراً ويَتيما'),
                             'من ديوان «أشعار خارجة على القانون» (1972)', size=66, sub_size=48)),
   (P+'nz_waves.png', 7, ov(6, '', 'هتعدّي 🤍', 'أنهي بيت فيهم وصلّك؟ 👇'
                            + SMALL.format('الصور: Jamie Kern · Norbert Fulep · Francesco Gallarotti · Lisa Lyne Blevins · Hector Bango (CC0)<br>Vyacheslav Argenberg (CC BY 4.0)'), size=100)),
  ],
  caption='''حد كسر قلبك… وفاكر إنك مش هتعدّيها؟
نزار قباني عنده رد:

«مِثلَما تَطرُدُ الغُيومُ الغُيوما
الغَرامُ الجَديدُ يَمحو القَديما»

زي ما سحابة بتيجي تزقّ اللي قبلها… الحب الجديد بيمسح القديم.

وفي نفس القصيدة بيت يتكتب على الحيطة:
«لا تَموتُ الخُيولُ بَرداً وجوعاً
إنَّ لِلعاشِقينَ رَبّاً رَحيما»

الوجع مش هيموّتك. هتعدّي 🤍

القصيدة اسمها «رصاصة الرحمة»، من ديوان «أشعار خارجة على القانون» (1972).

أنهي بيت فيهم وصلّك؟ 👇

📚 النص: بوابة الشعراء · قافية
📷 الصور: ويكيميديا كومنز (Jamie Kern · Norbert Fulep · Francesco Gallarotti · Lisa Lyne Blevins · Hector Bango، CC0 · Vyacheslav Argenberg، CC BY 4.0)

#نزار_قباني #شعر #شعر_عربي #رصاصة_الرحمة'''),
 '2026-10-26-tea': dict(
  date='2026-10-26T10:00',
  scenes=[
   (P+'te_cup.png', 7, ov(1, 'عادة مصرية جدًا', 'الشاي بعد الأكل<br>على طول؟', 'استنى شوية… وهقولك ليه', size=100)),
   (P+'te_lentil.png', 9, ov(2, 'الحديد اللي في العدس والفول والخضار', 'الشاي بيعطّل امتصاصه', 'فيه مواد بتمسك في الحديد…<br>فالجسم ما يستفيدش منه كله', size=90, sub_size=48)),
   (P+'te_beans.png', 9, ov(3, 'دراسة 2017 · ستات بصحة كويسة في بريطانيا', 'الامتصاص قلّ<br>حوالي الثلث', 'لما شربوا الشاي مع الوجبة… مقارنةً بالمية'
                            + SMALL.format('Ahmad Fuzi et al. · Am J Clin Nutr 2017'), size=100, sub_size=48)),
   (P+'te_clock.png', 8.5, ov(4, 'طب والحل؟', 'استنى ساعة ⏳', 'لما الشاي اتشرب بعد الأكل بساعة…<br>التأثير قلّ للنص تقريبًا', size=100, sub_size=50)),
   (P+'te_pitcher.png', 7.5, ov(5, '', 'مش لازم تبطّل الشاي ☕', 'بس أخّره شوية… خصوصًا لو عندك أنيميا<br>مين في بيتكم بيشرب الشاي على الأكل؟ 👇'
                               + SMALL.format('الصور: Sylwia Bartyzel · James Sutton · paul morris · Loic Djim · bady qb (CC0)'), size=84, sub_size=48)),
  ],
  caption='''بتشرب الشاي بعد الأكل على طول؟ زي معظمنا 😅

الشاي فيه مواد اسمها «بوليفينولات» بتمسك في الحديد اللي في الأكل (العدس والفول والخضار)، فالجسم ما يستفيدش منه كله.

في دراسة سنة 2017 على ستات بصحة كويسة في بريطانيا: لما شربوا الشاي مع الوجبة، امتصاص الحديد قلّ حوالي الثلث مقارنةً بالمية. ولما شربوه بعد الأكل بساعة، التأثير قلّ للنص تقريبًا.

يعني مش لازم تبطّل الشاي. بس أخّره ساعة، خصوصًا لو عندك أنيميا أو حامل.

مين في بيتكم بيشرب الشاي على الأكل؟ منشنه 👇

ملحوظة: دي معلومة عامة، ومش بديل لكلام دكتورك.

📚 المصدر: Ahmad Fuzi SF et al., American Journal of Clinical Nutrition (2017), PubMed 29046302
📷 الصور: ويكيميديا كومنز (Sylwia Bartyzel · James Sutton · paul morris · Loic Djim · bady qb، CC0)

#صحة #الشاي #أنيميا #تغذية #معلومة'''),
 '2026-10-27-abu-firas': dict(
  date='2026-10-27T10:00',
  scenes=[
   (P+'af_moon.png', 7, ov(1, 'أبو فراس الحمداني', 'إزاي تبان جامد…<br>وانت من جوّه موجوع؟', 'فارس كتب الإجابة من أكتر من ألف سنة', size=96)),
   (P+'af_citadel.png', 9, ov(2, 'حلب · القرن العاشر الميلادي', 'فارس… وأسير', 'ابن عم سيف الدولة الحمداني، أمير حلب<br>أسره الروم… وابن عمه اتأخر يفديه'
                              + SMALL.format('قلعة حلب'), size=100, sub_size=48)),
   (P+'af_tower.png', 9.5, ov(3, 'من الأسر كتب', VERSE.format('أَراكَ عَصِيَّ الدَمعِ شيمَتُكَ الصَبرُ', 'أَما لِلهَوى نَهيٌ عَلَيكَ وَلا أَمرُ'),
                              'شايفك ما بتعيّطش والصبر طبعك…<br>هو الحب مالوش عليك حكم؟', size=66, sub_size=48)),
   (P+'af_horses.png', 9.5, ov(4, 'وبيرد على نفسه', VERSE.format('بَلى أَنا مُشتاقٌ وَعِندِيَ لَوعَةٌ', 'وَلَكِنَّ مِثلي لا يُذاعُ لَهُ سِرُّ'),
                               'أيوه مشتاق وموجوع…<br>بس اللي زيّي ما بيطلّعش سرّه', size=66, sub_size=48)),
   (P+'af_umm.png', 9, ov(5, 'وبعد ألف سنة', 'أم كلثوم غنّتها<br>3 مرات', '1926 بلحن عبده الحامولي · 1944 لزكريا أحمد<br>وسنة 1965 لرياض السنباطي', size=100, sub_size=48)),
   (P+'af_moon.png', 8, ov(6, '', VERSE.format('سَيَذكُرُني قَومي إِذا جَدَّ جِدُّهُم', 'وَفي اللَيلَةِ الظَلماءِ يُفتَقَدُ البَدرُ'),
                           'مين «البدر» اللي بتفتقده؟ 👇'
                           + SMALL.format('الصور: Gabriel Santiago · Kevin Hou (CC0) · Vyacheslav Argenberg (CC BY 4.0)<br>Bernard Gagnon (CC BY-SA 3.0) · أم كلثوم 1969 (ملكية عامة)'), size=66, sub_size=50)),
  ],
  caption='''إزاي تبان جامد قدام الناس… وانت من جوّه موجوع؟

أبو فراس الحمداني كان فارس وشاعر، وابن عم سيف الدولة الحمداني أمير حلب. في معركة أسره الروم، وابن عمه اتأخر في فدائه. ومن الأسر كتب قصيدة من أجمل ما اتكتب في الشعر العربي (من «الروميات»):

«أَراكَ عَصِيَّ الدَمعِ شيمَتُكَ الصَبرُ
أَما لِلهَوى نَهيٌ عَلَيكَ وَلا أَمرُ
بَلى أَنا مُشتاقٌ وَعِندِيَ لَوعَةٌ
وَلَكِنَّ مِثلي لا يُذاعُ لَهُ سِرُّ»

أيوه مشتاق وموجوع… بس اللي زيّي ما بيطلّعش سرّه.

ويُروى إنه خرج من الأسر بعد سنين.

وبعد ألف سنة، أم كلثوم غنّتها 3 مرات: سنة 1926 بلحن عبده الحامولي، و1944 بلحن زكريا أحمد، و1965 بلحن رياض السنباطي.

وفيها البيت اللي بقى مثل:
«وَفي اللَيلَةِ الظَلماءِ يُفتَقَدُ البَدرُ»

مين «البدر» اللي بتفتقده؟ 👇

📚 المصدر: ويكيبيديا العربية، «أراك عصي الدمع»
📷 الصور: ويكيميديا كومنز (Gabriel Santiago · Kevin Hou، CC0 · Vyacheslav Argenberg، CC BY 4.0 · Bernard Gagnon، CC BY-SA 3.0 · صورة أم كلثوم 1969، ملكية عامة)

#أبو_فراس_الحمداني #أم_كلثوم #شعر_عربي #أراك_عصي_الدمع'''),
}

for name, r in reels.items():
    ovs = dict(width=1080, height=1920, posts=[s[2] for s in r['scenes']])
    pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
    story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(r['scenes'])])
    pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
    meta = dict(batch='2026-10-25-batch', post=name, date=r['date'], status='pending_review', format='REEL',
                caption=r['caption'], media=f'out/{name}/{name}.mp4')
    pathlib.Path(f'posts/{name}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    total = sum(s[1] for s in r['scenes']) - 0.7 * (len(r['scenes']) - 1)
    print(name, f'{total:.1f}s', len(r['caption']), 'chars')
