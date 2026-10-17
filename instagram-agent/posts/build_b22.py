# Builds overlays + story specs for reels 22-24 Oct (same readability rules as build_b19.py:
# headline >= 80px, sub >= 48px, 6.5-10s per scene).
import json, pathlib
P = 'assets/photos/b22/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52, lang='ar'):
    return dict(id=f'o{i}', scene='none', lang=lang, transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

def en(i, tag, head, sub, **kw):
    return ov(i, tag, head, sub, lang='en', **kw)

ILL = 'الصورة: عازف سمسمية · للتوضيح'

reels = {
 '2026-10-22-durant': dict(
  date='2026-10-22T10:00',
  scenes=[
   (P+'du_wheel.png', 7, en(1, 'Weekly Wisdom', 'We are what we repeatedly do.', 'Not what we plan. Not what we promise.', size=92)),
   (P+'du_pottery.png', 7.5, en(2, '', 'Excellence, then,<br>is not an act…', '…but a habit.', size=96, sub_size=60)),
   (P+'du_keys.png', 8, ov(3, '🔸', 'نحن ما نفعله مرارًا', 'فالتميّز ليس فعلًا عابرًا…<br>بل عادة.', size=96, sub_size=56)),
   (P+'du_draw.png', 9, en(4, 'Plot twist', 'Aristotle never<br>said it.', 'Will Durant wrote these words in 1926, summing up Aristotle’s idea.'
                           + SMALL.format('The Story of Philosophy · via Quote Investigator'), size=92, sub_size=50)),
   (P+'du_journal.png', 7, en(5, '', 'One small thing.<br>Every day.', 'What habit are you building this week? 👇'
                              + SMALL.format('Photos: Quino Al · Jared Sluyter · João Silas · Tamarcus Brown · Thought Catalog (CC0)'), size=92)),
  ],
  caption='''“We are what we repeatedly do. Excellence, then, is not an act, but a habit.”
— Will Durant, The Story of Philosophy (1926)

It’s usually credited to Aristotle, but the words are Durant’s. He wrote them to sum up Aristotle’s idea that we become good at things by doing them, again and again.

You don’t become a writer the day you publish. You become one on every ordinary morning you sit down and write.

🔸 نحن ما نفعله مرارًا؛ فالتميّز ليس فعلًا عابرًا، بل عادة.

What’s one small habit you’re repeating this week? 👇

📚 Source: Will Durant, The Story of Philosophy (1926); Quote Investigator
📷 Photos: Wikimedia Commons (Quino Al · Jared Sluyter · João Silas · Tamarcus Brown · Thought Catalog, CC0)

#WeeklyWisdom #Habits #Aristotle #WillDurant'''),
 '2026-10-23-harvard': dict(
  date='2026-10-23T10:00',
  scenes=[
   (P+'hv_fifty.png', 7, ov(1, 'سؤال', 'إيه اللي بيخلّينا نعجّز<br>وإحنا مبسوطين وبصحتنا؟', 'فلوس؟ شهرة؟ شغل كويس؟', size=84)),
   (P+'hv_friends.png', 9, ov(2, 'من أطول الدراسات عن السعادة', 'بدأت سنة 1938', 'هارفارد تابعت 268 طالب عندها…<br>وبعدين انضم لهم 456 من أفقر أحياء بوسطن'
                              + SMALL.format('Harvard Study of Adult Development'), size=100, sub_size=50)),
   (P+'hv_snuggle.png', 8, ov(3, 'النتيجة اللي فاجأتهم', 'مش الكوليسترول…', 'اللي توقّع مين هيعجّز بصحة كان:<br>رضاه عن علاقاته وهو عنده 50 سنة', size=96, sub_size=50)),
   (P+'hv_grass.png', 9.5, ov(4, 'روبرت والدينجر · مدير الدراسة', 'الأرضى عن علاقاتهم في الخمسين…<br>كانوا الأصحّ في التمانين', 'العلاقات الحلوة مش رفاهية'
                             + SMALL.format('Harvard Gazette · أبريل 2017'), size=80, sub_size=50)),
   (P+'hv_fifty.png', 7, ov(5, '', 'كلّم حد وحشك النهارده 📞', 'ومين أول حد جه في بالك؟ 👇'
                            + SMALL.format('الصور: Lotte Meijer · Aman Shrivastava · Priscilla Du Preez · Scott Webb (CC0)'), size=84)),
  ],
  caption='''لو سألتك: إيه اللي بيخلّي الواحد يعجّز وهو مبسوط وصحته كويسة… هتقول إيه؟

سنة 1938 جامعة هارفارد بدأت تتابع 268 طالب عندها، وبعدين انضم للدراسة 456 راجل من أفقر أحياء بوسطن. وفضلوا يتابعوهم عشرات السنين.

النتيجة؟ مش الفلوس ولا الشهرة. روبرت والدينجر، مدير الدراسة، بيقول إن اللي كانوا أرضى عن علاقاتهم وهم عندهم 50 سنة كانوا الأصحّ لما وصلوا 80.

يعني القعدة مع صحابك، والتليفون لأخوك، والعشا مع أهلك… مش رفاهية.

كلّم حد وحشك النهارده. ومين أول حد جه في بالك؟ 👇

📚 المصدر: Harvard Gazette (أبريل 2017)، «Over nearly 80 years, Harvard study has been showing how to live a healthy and happy life»
📷 الصور: ويكيميديا كومنز (Lotte Meijer · Aman Shrivastava · Priscilla Du Preez · Scott Webb، CC0)

#سعادة #علاقات #صحة_نفسية #دراسة_هارفارد'''),
 '2026-10-24-suez': dict(
  date='2026-10-24T10:00',
  scenes=[
   (P+'sz_city.png', 7.5, ov(1, '24 أكتوبر · العيد القومي للسويس', 'مدينة قالت: لأ', 'في أكتوبر 1973 القوات الإسرائيلية حاولت تاخدها…<br>وما عرفتش', size=100, sub_size=50)),
   (P+'sz_canal.png', 7.5, ov(2, 'بأهلها قبل أي حد', 'المقاومة الشعبية', 'ناس عادية: عمّال وصنايعية وشباب…<br>وقفوا جنب الجيش يحموا بيوتهم', size=96)),
   (P+'sz_player.png', 9, ov(3, 'ومن الناس دي', 'الكابتن غزالي', 'محمد أحمد غزالي: مصارع ومدرّب… وشاعر<br>وكان من رجالة المقاومة في السويس'
                             + SMALL.format(ILL), size=100, sub_size=50)),
   (P+'sz_player2.png', 8.5, ov(4, 'سلاح تاني جنب البندقية', 'فرقة «أولاد الأرض»', 'شباب عمّال وحرفيين حوالين السمسمية…<br>بيغنّوا للمقاومة'
                              + SMALL.format(ILL), size=92, sub_size=50)),
   (P+'sz_port.png', 8, ov(5, 'من أشهر أغانيهم · كلمات الكابتن غزالي', '«غنّي يا سمسمية<br>لرصاص البندقية»', '', size=96)),
   (P+'sz_boats.png', 7, ov(6, '', 'كل سنة والسويس بخير 🇪🇬', 'تعرف حد من السويس؟ منشنه 👇'
                            + SMALL.format('المصدر: السفير العربي (2022)<br>الصور: Face Potter · patano · TheEgyptian (CC BY-SA 3.0)<br>Jean-Pierre Dalbéra (CC BY 2.0)'), size=88)),
  ],
  caption='''تعرف ليه 24 أكتوبر هو العيد القومي للسويس؟ 🇪🇬

في أكتوبر 1973 القوات الإسرائيلية حاولت تقتحم المدينة… والسويس صمدت، بأهلها والمقاومة الشعبية جنب الجيش.

ومن الناس دي كان «الكابتن غزالي»، محمد أحمد غزالي: مصارع ومدرّب، وشاعر. مع المقاومة جمع شباب عمّال وحرفيين حوالين آلة السمسمية، وعمل فرقة «أولاد الأرض». كان شايف إن الكلمة سلاح زي البندقية.

ومن أشهر أغانيهم:
«غنّي يا سمسمية لرصاص البندقية»

كل سنة والسويس بخير.
تعرف حد من السويس؟ منشنه وابعتله الريل 👇

📚 المصدر: السفير العربي، إسلام ضيف، «عن فرقة أولاد الأرض ومدينة السويس وآلة السمسمية» (2022)
📷 الصور: ويكيميديا كومنز (Face Potter · patano · TheEgyptian، CC BY-SA 3.0 · Jean-Pierre Dalbéra، CC BY 2.0). صور عازفي السمسمية للتوضيح، ومش للكابتن غزالي.

#السويس #عيد_السويس #الكابتن_غزالي #السمسمية #أكتوبر'''),
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
