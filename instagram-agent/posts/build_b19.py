# Builds overlays + story specs for the first three reels of the Oct 19-31 daily batch.
# Readability rule (user, Oct 16): big type (headline >= 80px, sub >= 50px) and >= 6.5s per scene.
import json, pathlib
P = 'assets/photos/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52):
    return dict(id=f'o{i}', scene='none', lang='ar', transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

reels = {
 '2026-10-19-bids': dict(
  date='2026-10-19T10:00',
  scenes=[
   (P+'b19/cpl_sunset.png', 6.5, ov(1, 'بين الزوجين', '«تعرف حصل إيه النهارده؟»', 'جملة عادية خالص…<br>بس ردّك عليها بيفرق أكتر ما تتخيّل')),
   (P+'b19/cpl_latte.png', 7.5, ov(2, 'العلم بيسمّيها', '«محاولة تواصل»', 'أي كلمة صغيرة شريكك بيطلب بيها انتباهك:<br>تعليق، ضحكة، «شوف ده»')),
   (P+'b19/cpl_two.png', 9.5, ov(3, 'دراسة تابعت 130 زوج جديد', '86% مقابل 33%', 'اللي فضلوا مع بعض بعد 6 سنين كانوا بيردّوا على المحاولات دي 86% من الوقت…<br>واللي انفصلوا 33% بس' + SMALL.format('جون جوتمان · معهد جوتمان'), size=104, sub_size=48)),
   (P+'b19/cpl_umbrella.png', 7.5, ov(4, 'طب أردّ إزاي؟', 'مش محتاج خطبة', '«بجد؟ احكيلي» · بصّة · إنك تسيب الموبايل<br>المهم ما تطنّشش')),
   (P+'couple/tea_glasses.png', 7, ov(5, 'جرّب النهارده', 'خد بالك من المحاولات الصغيرة', 'وردّ عليها… ولو بكلمة', size=80)),
   (P+'couple/hands_wedding.png', 7, ov(6, '', 'ابعته لشريك حياتك 🤍', 'وقولنا: إيه أصغر حاجة بتفرّحك منه؟' + SMALL.format('الصور: Gerrit Vermeulen · Sabri Tuzcu · Sebastien Gabriel · Pavel Badrtdinov (CC0) · AdhiRajamanickam (CC BY-SA 4.0) · Shixart1985 (CC BY 2.0)'), size=84)),
  ],
  caption='''شريكك رجع البيت وقالك «تعرف حصل إيه النهارده؟»… بتعمل إيه؟

بتسيب الموبايل وتسمع؟ ولا بتقول «آه» وعينك على الشاشة؟

جون جوتمان تابع 130 زوج جديد في معمله، ورجع لهم بعد 6 سنين. اللي فضلوا مع بعض كانوا بيردّوا على المحاولات الصغيرة دي 86% من الوقت. واللي انفصلوا؟ 33% بس.

ومش محتاج كلام كتير. «بجد؟ احكيلي» أو إنك تسيب الموبايل وتبصّله كفاية.

النهارده خد بالك من المحاولات الصغيرة دي وردّ عليها. وابعت الريل لشريك حياتك 🤍

إيه أصغر حاجة بتفرّحك منه؟ 👇

📚 المصدر: The Gottman Institute، «Turn Toward Instead of Away»
📷 الصور: ويكيميديا كومنز (Gerrit Vermeulen · Sabri Tuzcu · Sebastien Gabriel · Pavel Badrtdinov، CC0 · AdhiRajamanickam، CC BY-SA 4.0 · Shixart1985، CC BY 2.0)

#بين_الزوجين #الحياة_الزوجية #مودة_ورحمة #علاقات_صحية'''),
 '2026-10-20-walk': dict(
  date='2026-10-20T10:00',
  scenes=[
   (P+'b19/walk_silhouette.png', 6.5, ov(1, 'عادة صغيرة', 'قبل ما تترمي على الكنبة بعد الغدا…', 'استنى ثانية 👇', size=84)),
   (P+'b19/walk_meal.png', 7.5, ov(2, 'اللي بيحصل جوّاك', 'بعد الأكل السكر في الدم بيعلى', 'ده طبيعي…<br>بس كل ما يعلى بهدوء يبقى أحسن', size=84)),
   (P+'b19/walk_zamalek.png', 10, ov(3, 'مراجعة علمية جمعت 7 دراسات', 'مشي خفيف<br>من دقيقتين لـ 5', 'بعد الأكل قلّل ارتفاع السكر أكتر من القعدة… وكمان أكتر من الوقوف' + SMALL.format('Buffey وزملاؤه · Sports Medicine · 2022'), size=96, sub_size=48)),
   (P+'b19/walk_kids.png', 7.5, ov(4, 'مش محتاج جيم', 'لِف في الشقة', 'انزل هات حاجة من تحت · اتمشّى مع ولادك')),
   (P+'b19/walk_woman.png', 7, ov(5, 'خلي بالك', 'ده مش علاج', 'لو عندك سكر:<br>علاجك وكلام دكتورك الأول')),
   (P+'b19/walk_silhouette.png', 7, ov(6, '', 'احفظه وجرّبه النهارده 🚶', 'وقولنا: بتعمل إيه بعد الغدا عادةً؟' + SMALL.format('الصور: Islam Hassan · Jamie Taylor · Kevin Young (CC0) · Jorge Láscar (CC BY 2.0) · H. Hakan Atik (CC BY-SA 4.0)'), size=84)),
  ],
  caption='''إنت من اللي بيتغدّوا وعلى الكنبة على طول؟ 😅

مراجعة علمية جمعت 7 دراسات، ولقت إن المشي الخفيف بعد الأكل بيقلّل ارتفاع السكر في الدم، حتى لو دقيقتين لـ 5 دقايق بس. وكان أحسن من القعدة، وكمان من الوقوف.

مش محتاج جيم ولا لبس رياضة. لِف في الشقة، أو انزل هات حاجة من تحت، أو اتمشّى مع ولادك.

ولو عندك سكر، ده مش بديل عن علاجك ولا عن كلام دكتورك.

احفظ الريل وجرّبه النهارده، وقولنا: بتعمل إيه بعد الغدا عادةً؟ 👇

📚 المصدر: Buffey et al., Sports Medicine (2022)
📷 الصور: ويكيميديا كومنز (Islam Hassan · Jamie Taylor · Kevin Young، CC0 · Jorge Láscar، CC BY 2.0 · H. Hakan Atik، CC BY-SA 4.0)

#عادات_صحية #صحتك #مشي #أكل_صحي'''),
 '2026-10-21-ibn-zurayq': dict(
  date='2026-10-21T10:00',
  scenes=[
   (P+'b19/iz_baghdad.png', 7, ov(1, 'شعر بقصة', 'راجل ساب مراته في بغداد<br>وسافر يدوّر على رزق…', 'وما رجعش.', size=84)),
   (P+'b19/iz_tigris.png', 7.5, ov(2, 'قبل ما يسافر', 'لامِته كتير…', 'وهو كان شايف إن الرزق في السفر')),
   (P+'b19/iz_cordoba.png', 8, ov(3, 'في الأندلس', 'يُروى إنه ما لقاش اللي حلم بيه', 'وتعب ومرض… وهو غريب', size=80)),
   (P+'b19/iz_ms.png', 10, ov(4, 'ابن زريق البغدادي', "<span style='display:inline-block;line-height:2'>وَكَم تَشَبَّثَ بي يَومَ الرَحيلِ ضُحًى<br>وَأَدمُعي مُستَهِلّاتٌ وَأَدمُعُهُ</span>", 'يوم السفر اتشبّثت فيه… ودموعهم الاتنين نازلة', size=66, sub_size=48)),
   (P+'b19/iz_arcos.png', 10, ov(5, 'وأشهر بيت فيها', "<span style='display:inline-block;line-height:2'>رُزِقتُ مُلكًا فَلَم أُحسِن سِياسَتَهُ<br>وَكُلُّ مَن لا يَسُوسُ المُلكَ يَخلَعُهُ</span>", 'كان عنده «مُلك»: بيت وحب… وما عرفش يحافظ عليه', size=66, sub_size=48)),
   (P+'b19/iz_tigris.png', 8.5, ov(6, 'والنهاية', 'يُروى إنهم لقوا القصيدة<br>جنب راسه بعد ما مات', 'قصيدة «لا تعذليه»… 39 بيت', size=80)),
   (P+'b19/iz_baghdad.png', 7.5, ov(7, '', 'اللي جنبك النهارده «مُلك» 🤍', 'احفظه، وابعته لحد مسافر بعيد عن بيته' + SMALL.format('الصور: Synaps commons · Benjamin Smith · Alvaro Viñuela (CC BY-SA 4.0) · مجموعة Matson ومخطوط فارسي لسعدي (ملكية عامة، للتوضيح)'), size=80)),
  ],
  caption='''مين فينا ما سابش حد بيحبه عشان «لقمة العيش»؟

يُروى إن ابن زريق البغدادي ساب مراته في الكرخ ببغداد، وسافر الأندلس يدوّر على رزق. وهناك ما لقاش اللي كان بيحلم بيه، وتعب ومرض وهو غريب. ويُروى إنهم لقوا قصيدته جنب راسه بعد ما مات.

القصيدة اسمها «لا تعذليه»، وأشهر بيت فيها:
«رُزِقتُ مُلكًا فَلَم أُحسِن سِياسَتَهُ
وَكُلُّ مَن لا يَسُوسُ المُلكَ يَخلَعُهُ»

كان عنده «مُلك»: بيت وحب وونس… وما عرفش يحافظ عليه.

اللي جنبك النهارده «مُلك». ابعت الريل لحد مسافر بعيد عن بيته 🤍

ملحوظة: تفاصيل قصة موته رواية أدبية مشهورة، مش حقيقة تاريخية مؤكدة.

📚 النص: عالم الأدب، «لا تعذليه فإن العذل يولعه»
📷 الصور: ويكيميديا كومنز (Synaps commons · Benjamin Smith · Alvaro Viñuela، CC BY-SA 4.0 · مجموعة Matson ومخطوط فارسي لسعدي الشيرازي، ملكية عامة، للتوضيح)

#شعر #شعر_عربي #ابن_زريق #لا_تعذليه'''),
}

for name, r in reels.items():
    ovs = dict(width=1080, height=1920, posts=[s[2] for s in r['scenes']])
    pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
    story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(r['scenes'])])
    pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
    meta = dict(batch='2026-10-19-batch', post=name, date=r['date'], status='pending_review', format='REEL',
                caption=r['caption'], media=f'out/{name}/{name}.mp4')
    pathlib.Path(f'posts/{name}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    total = sum(s[1] for s in r['scenes']) - 0.7 * (len(r['scenes']) - 1)
    print(name, f'{total:.1f}s', len(r['caption']), 'chars')
