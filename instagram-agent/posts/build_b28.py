# Builds overlays + story specs for reels 28-31 Oct (same readability rules as build_b19.py:
# headline >= 80px, sub >= 48px, 6.5-10s per scene).
import json, pathlib
P = 'assets/photos/b28/'
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

reels = {
 '2026-10-28-clock': dict(
  date='2026-10-28T10:00',
  scenes=[
   (P+'cl_roman.png', 7.5, ov(1, 'خد بالك يوم الخميس', 'الساعة هترجع<br>ساعة لورا ⏰', 'آخر يوم الخميس 29 أكتوبر<br>الساعة 12 بالليل تبقى 11', size=96)),
   (P+'cl_bed.png', 8, ov(2, 'يعني إيه؟', 'ساعة نوم زيادة…', 'بس جسمك ممكن يتلخبط كام يوم<br>خصوصًا الأطفال', size=100)),
   (P+'cl_forest.png', 8, ov(3, '1 · أول ما تصحى', 'افتح الشباك ☀️', 'نور الصبح بيظبط الساعة اللي جوّه جسمك', size=100, sub_size=50)),
   (P+'cl_laptop.png', 8, ov(4, '2 · قبل النوم', 'قلّل الشاشات<br>والقهوة بالليل', 'الموبايل والكافيين بيأخّروا النوم', size=96)),
   (P+'cl_peaks.png', 8.5, ov(5, '3 · مع الأطفال', 'شوية شوية', 'أخّر معاد نومهم 15 لـ 20 دقيقة كل ليلة<br>لحد ما يوصلوا للمعاد الجديد', size=100, sub_size=48)),
   (P+'cl_roman.png', 7, ov(6, '', 'وثبّت مواعيدك 🌙', 'ابعته لحد بيصحى بدري للشغل 👇'
                            + SMALL.format('المصادر: القانون 34 لسنة 2023 · Sleep Foundation · AASM<br>الصور: Ales Krivec · Quin Stevenson · Kristine Weilert · Jay Wennington · Christopher Burns (CC0)'), size=96)),
  ],
  caption='''خد بالك: آخر يوم الخميس 29 أكتوبر، الساعة 12 بالليل هترجع 11. يعني التوقيت الصيفي خلص ⏰

ساعة نوم زيادة… بس جسمك ممكن يتلخبط كام يوم، خصوصًا الأطفال.

3 حاجات بسيطة تساعدك:
أول ما تصحى افتح الشباك. نور الصبح بيظبط الساعة اللي جوّه جسمك.
قبل النوم قلّل الشاشات والقهوة، لأنهم بيأخّروا النوم.
ومع الأطفال، أخّر معاد نومهم 15 لـ 20 دقيقة كل ليلة لحد ما يوصلوا للمعاد الجديد.

وثبّت مواعيد نومك وصحيانك 🌙

ابعته لحد بيصحى بدري للشغل 👇

📚 المصادر: قانون التوقيت الصيفي رقم 34 لسنة 2023 · Sleep Foundation · American Academy of Sleep Medicine
📷 الصور: ويكيميديا كومنز (Ales Krivec · Quin Stevenson · Kristine Weilert · Jay Wennington · Christopher Burns، CC0)

#التوقيت_الشتوي #تغيير_الساعة #نوم #صحة'''),
 '2026-10-29-repair': dict(
  date='2026-10-29T10:00',
  scenes=[
   (P+'rp_snuggle.png', 7.5, ov(1, 'بين الزوجين', 'الخناقة بدأت تعلى…<br>تعمل إيه؟', 'في جملة صغيرة ممكن تنقذ الموقف', size=96)),
   (P+'rp_bridge.png', 9, ov(2, 'جون جوتمان سمّاها', '«محاولة إصلاح»', 'أي كلمة أو حركة… حتى لو هزار<br>بتمنع الزعل إنه يكبر ويخرج عن السيطرة'
                              + SMALL.format('The Gottman Institute'), size=100, sub_size=48)),
   (P+'rp_snow.png', 9, ov(3, 'أمثلة من «قائمة الإصلاح» بتاعته', '«ممكن أرجع في كلامي؟»', '«خلّينا ناخد بريك… وهرجعلك»<br>«بالراحة عليّا شوية»', size=88, sub_size=52)),
   (P+'rp_sunset.png', 8.5, ov(4, 'والسر', 'بدري… وكتير', 'الأزواج الناجحين بيصلّحوا بدري…<br>والتاني بيقبل المحاولة', size=100, sub_size=48)),
   (P+'rp_marina.png', 7, ov(5, '', 'إيه جملتك اللي<br>بتهدّي الدنيا؟ 👇', 'ابعته لشريكك 🤍'
                             + SMALL.format('الصور: Priscilla Du Preez · Tord Sollie · Ezra Jeffrey · Gerrit Vermeulen · Alice Donovan Rouse (CC0)'), size=92)),
  ],
  caption='''الخناقة بدأت تعلى… وكل واحد عايز يكسب. تعمل إيه؟

جون جوتمان، من أشهر الباحثين في العلاقات الزوجية، سمّى الحاجة دي «محاولة إصلاح»: أي كلمة أو حركة، حتى لو هزار، بتمنع الزعل إنه يكبر ويخرج عن السيطرة.

أمثلة من «قائمة الإصلاح» بتاعته:
«ممكن أرجع في كلامي؟»
«خلّينا ناخد بريك… وهرجعلك»
«بالراحة عليّا شوية»

والسر إن الأزواج الناجحين بيصلّحوا بدري ومن غير ما يستنّوا، والتاني بيقبل المحاولة.

إيه جملتك اللي بتهدّي الدنيا؟ اكتبها 👇 وابعت الريل لشريكك 🤍

📚 المصدر: The Gottman Institute، «R is for Repair» و«Repair Checklist»
📷 الصور: ويكيميديا كومنز (Priscilla Du Preez · Tord Sollie · Ezra Jeffrey · Gerrit Vermeulen · Alice Donovan Rouse، CC0)

#بين_الزوجين #الحياة_الزوجية #علاقات_صحية #جوتمان'''),
 '2026-10-30-marcus': dict(
  date='2026-10-30T10:00',
  scenes=[
   (P+'ma_bust.png', 7, en(1, 'Weekly Wisdom', 'The soul is dyed<br>by the thoughts.', 'Marcus Aurelius · Meditations 5.16', size=96, sub_size=60)),
   (P+'ma_rider.png', 8, en(2, 'Who wrote it?', 'A Roman emperor’s<br>private notes.', 'Never meant to be published.', size=92, sub_size=58)),
   (P+'ma_yarn.png', 8.5, en(3, '', 'Like wool in dye,', 'your mind slowly takes the color<br>of what you think about every day.', size=100, sub_size=62)),
   (P+'ma_ball.png', 8.5, ov(4, '🔸', 'الروح تتلوّن بأفكارها', 'كما تكون أفكارك المعتادة…<br>تكون طبيعة عقلك', size=96, sub_size=56)),
   (P+'ma_bust.png', 7, en(5, '', 'What color are your<br>thoughts today?', 'Tell me in one word 👇'
                           + SMALL.format('Photos: Wilfredor · julian mora · Philip Estrada (CC0) · Alvesgaspar (public domain)'), size=92, sub_size=62)),
  ],
  caption='''“Such as are thy habitual thoughts, such also will be the character of thy mind; for the soul is dyed by the thoughts.”
— Marcus Aurelius, Meditations 5.16 (trans. George Long)

He was a Roman emperor, and these were private notes to himself, never meant for us.

Like wool in dye, your mind slowly takes the color of what you think about every day. So choose the thoughts you keep coming back to.

🔸 كما تكون أفكارك المعتادة تكون طبيعة عقلك؛ فالروح تتلوّن بأفكارها.

What color are your thoughts today? One word 👇

📚 Source: Marcus Aurelius, Meditations, Book 5.16, George Long translation (MIT Classics)
📷 Photos: Wikimedia Commons (Wilfredor · julian mora · Philip Estrada, CC0 · Alvesgaspar, public domain)

#WeeklyWisdom #MarcusAurelius #Stoicism #Mindset'''),
 '2026-10-31-eyes': dict(
  date='2026-10-31T10:00',
  scenes=[
   (P+'ey_dark.png', 7, ov(1, 'لو قاعد قدام شاشة طول اليوم', 'عينك محتاجة<br>20 ثانية بس', 'قاعدة اسمها 20-20-20', size=100)),
   (P+'ey_eye.png', 8.5, ov(2, 'ليه بتتعب؟', 'بترمش أقل', 'الطبيعي حوالي 15 مرة في الدقيقة<br>وقدام الشاشة بتقل للنص أو أقل', size=100, sub_size=50)),
   (P+'ey_desk.png', 9, ov(3, 'القاعدة', 'كل 20 دقيقة…', 'بص على حاجة بعيدة حوالي 6 متر<br>لمدة 20 ثانية', size=100, sub_size=48)),
   (P+'ey_sea.png', 9, ov(4, 'والخبر الحلو', 'الشاشة مش بتأذي<br>عينك بشكل دائم', 'التعب بيروح بالراحة…<br>ولو مستمر، اكشف عند دكتور عيون', size=92, sub_size=50)),
   (P+'ey_dark.png', 7, ov(5, '', 'جرّبها دلوقتي 👀', 'وابعته لصاحبك اللي عايش على اللابتوب 👇'
                            + SMALL.format('المصدر: الأكاديمية الأمريكية لطب العيون (AAO)<br>الصور: Mark Cruz · Liam Welch · Taduuda · Good Free Photos (CC0)'), size=100, sub_size=48)),
  ],
  caption='''لو قاعد قدام شاشة طول اليوم، عينك محتاجة 20 ثانية بس 👀

ليه بتتعب؟ لأنك بترمش أقل. الطبيعي حوالي 15 مرة في الدقيقة، وقدام الشاشة بتقل للنص أو أقل، فعينك بتنشف وتتعب.

القاعدة اسمها 20-20-20: كل 20 دقيقة، بص على حاجة بعيدة عنك حوالي 6 متر (20 قدم) لمدة 20 ثانية.

والخبر الحلو إن الشاشة مش بتأذي عينك بشكل دائم، والتعب بيروح بالراحة. ولو مستمر، اكشف عند دكتور عيون.

جرّبها دلوقتي، وابعت الريل لصاحبك اللي عايش على اللابتوب 👇

📚 المصدر: الأكاديمية الأمريكية لطب العيون (AAO)، «Computers, Digital Devices and Eye Strain»
📷 الصور: ويكيميديا كومنز (Mark Cruz · Liam Welch · Taduuda · Good Free Photos، CC0)

#صحة_العين #شاشات #نصيحة #20_20_20'''),
}

for name, r in reels.items():
    ovs = dict(width=1080, height=1920, posts=[s[2] for s in r['scenes']])
    pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
    story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(r['scenes'])])
    pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
    meta = dict(batch='2026-10-28-batch', post=name, date=r['date'], status='pending_review', format='REEL',
                caption=r['caption'], media=f'out/{name}/{name}.mp4')
    pathlib.Path(f'posts/{name}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    total = sum(s[1] for s in r['scenes']) - 0.7 * (len(r['scenes']) - 1)
    print(name, f'{total:.1f}s', len(r['caption']), 'chars')
