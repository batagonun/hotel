# Builds the "Plan Badr" carousel (9 slides). Facts: Wikipedia "Operation Badr (1973)", "Bar Lev Line";
# Library of Congress Egypt country study (80,000 troops by midnight).
import json
G='#d9b25f'; INK='#f2ead8'; MUT='#9fb0c6'; SAND='#d8b47a'; WATER='#3f6f96'
def t(x,y,txt,size=30,fill=INK,w=700,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="Cairo" font-weight="{w}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" direction="rtl">{txt}</text>'

# Slide 2: Bar Lev cross-section (west bank on the right as seen by Egyptian viewer facing east? keep canal center-right, east bank wall left)
barlev = f'''
<g>
 <rect x="80" y="1060" width="920" height="10" fill="#2a3d57"/>
 <path d="M640 1060 L1000 1060 L1000 1120 L640 1120Z" fill="{WATER}"/>
 {''.join(f'<path d="M{660+i*60} 1085 q15 -8 30 0 t30 0" stroke="#8fb5d6" stroke-width="3" fill="none"/>' for i in range(5))}
 <path d="M640 1060 L560 760 L380 760 L300 1060Z" fill="{SAND}"/>
 <path d="M640 1060 L560 760 L585 760 L660 1060Z" fill="#f0d39d" opacity=".5"/>
 <rect x="410" y="715" width="120" height="45" fill="#6b7686"/><rect x="430" y="700" width="20" height="15" fill="#6b7686"/><rect x="490" y="700" width="20" height="15" fill="#6b7686"/>
 <path d="M300 1060 L80 1060 L80 1040 L300 1040Z" fill="#c9a46a"/>
 <rect x="150" y="1010" width="90" height="30" rx="6" fill="#525c6a"/><rect x="185" y="996" width="45" height="16" fill="#525c6a"/><rect x="225" y="1000" width="45" height="5" fill="#525c6a"/>
 <line x1="700" y1="760" x2="700" y2="1060" stroke="{G}" stroke-width="3"/><line x1="688" y1="760" x2="712" y2="760" stroke="{G}" stroke-width="3"/><line x1="688" y1="1060" x2="712" y2="1060" stroke="{G}" stroke-width="3"/>
 {t(800,900,'من 20 إلى 25 م',32,G)}{t(800,945,'ارتفاع الساتر',26,MUT,400)}
 {t(470,690,'نقطة حصينة',26,INK)}
 {t(470,880,'ساتر ترابي',30,'#3a2a14')}{t(470,920,'ميل من 45° إلى 65°',24,'#3a2a14',400)}
 {t(820,1170,'قناة السويس',30,'#8fb5d6')}
 {t(195,975,'دبابات للدعم',24,MUT,400)}
 {t(950,1240,'الضفة الغربية ←',24,MUT,400)}{t(170,1240,'→ سيناء',24,MUT,400)}
</g>'''

# Slide 5: zero hour timeline
def node(x,label,time):
    return f'<circle cx="{x}" cy="960" r="18" fill="{G}"/>{t(x,915,time,34,G)}{t(x,1020,label,26,INK,400)}'
timeline = f'''<line x1="160" y1="960" x2="920" y2="960" stroke="{G}" stroke-width="4"/>
{node(920,'ضربة جوية','14:00')}{node(540,'تمهيد نيراني','14:05')}{node(160,'بدء العبور','14:20')}
{t(540,1120,'أكثر من 200 طائرة • نحو 2000 قطعة مدفعية • 53 دقيقة',28,MUT,400)}'''

# Slide 6: boats crossing
boats = ''.join(f'''<g transform="translate({x},{y}) scale({k})"><path d="M-90 0 Q0 30 90 0 L78 22 Q0 44 -78 22Z" fill="#0b1422"/>{''.join(f'<circle cx="{o}" cy="-16" r="9" fill="#0b1422"/><rect x="{o-7}" y="-10" width="14" height="14" fill="#0b1422"/>' for o in (-48,-16,16,48))}</g>''' for x,y,k in [(300,960,1),(620,1010,1.1),(860,940,.9),(450,1110,1.15)])
crossing = f'''<rect x="80" y="880" width="920" height="300" fill="{WATER}" opacity=".85"/>
<path d="M80 880 L1000 880 L1000 860 L80 860Z" fill="{SAND}"/>{boats}
<path d="M80 1180 L1000 1180 L1000 1200 L80 1200Z" fill="#c9a46a"/>'''

# Slide 7: water cannon breach
water = f'''<path d="M120 1150 L520 1150 L520 1120 L120 1120Z" fill="{WATER}"/>
<rect x="150" y="1080" width="120" height="40" rx="6" fill="#525c6a"/><rect x="250" y="1090" width="60" height="12" fill="#525c6a"/>
<path d="M310 1096 Q 520 880 690 960" stroke="#bfe0f7" stroke-width="12" fill="none" stroke-linecap="round"/>
<path d="M310 1096 Q 520 900 690 990" stroke="#8fc4ea" stroke-width="6" fill="none" stroke-linecap="round" opacity=".8"/>
<path d="M560 1150 L640 860 L960 860 L960 1150Z" fill="{SAND}"/>
<path d="M680 1150 L720 960 L800 960 L840 1150Z" fill="#16263b"/>
{t(760,1210,'ثغرة في الساتر',28,G)}{t(220,1210,'مضخة مياه',26,MUT,400)}'''

# Slide 3: preparation timeline
def yr(x,y,l): return f'<circle cx="{x}" cy="1000" r="20" fill="{G}"/>{t(x,950,y,40,G)}{t(x,1065,l,26,INK,400)}'
prep = f'<line x1="200" y1="1000" x2="880" y2="1000" stroke="{G}" stroke-width="4"/>' + yr(880,'1968','بدء التدريبات') + yr(540,'1971','التخطيط العملياتي') + yr(200,'1973','ساعة الصفر')
# Slide 4: calendar card
cal = f'''<rect x="340" y="980" width="400" height="250" rx="18" fill="#f2ead8"/><rect x="340" y="980" width="400" height="70" rx="18" fill="#a1121f"/><rect x="340" y="1030" width="400" height="20" fill="#a1121f"/>
{t(540,1028,'أكتوبر 1973',32,'#fff')}{t(540,1150,'6',96,'#1b1b1b',700)}{t(540,1205,'السبت • 10 رمضان 1393',26,'#5a4a3a',400)}'''
# Slide 8: numbers grid
def stat(x,y,n,l): return f'<rect x="{x-200}" y="{y-80}" width="400" height="190" rx="14" fill="#13233a" stroke="{G}" stroke-opacity=".4"/>{t(x,y+15,n,68,G)}{t(x,y+75,l,26,INK,400)}'
numbers = stat(760,830,'10','كباري ثقيلة')+stat(320,830,'10','كباري عائمة')+stat(760,1060,'35','معدية')+stat(320,1060,'≈ 80 ألف','جندي عبروا بحلول منتصف الليل')

CR='ويكيميديا كومنز · ملكية عامة'
def P(i,tag,head,sub,photo,credit,size=72,subSize=30,boxTop=600,boxH=600,boxPos='center'):
    return dict(id=i,scene='brief',tag=tag,headline=head,size=size,sub=sub,subSize=subSize,top=100,box='assets/photos/'+photo,boxTop=boxTop,boxH=boxH,boxPos=boxPos,credit=credit)
slides = [
 P('s01','٦ أكتوبر ١٩٧٣ | ١٠ رمضان ١٣٩٣','كيف عبرنا؟ خطة «بدر»','اسحب ← واعرف القصة في ١٠ صور حقيقية','flag.png','جنود مصريون يرفعون العلم فوق أحد حصون خط بارليف بعد الاستيلاء عليه · '+CR,size=80,boxTop=480,boxH=700,boxPos='30% center'),
 dict(id='s02',scene='photo',photo='assets/photos/barlev_fort.png',photoPos='center 80%',tag='١ | العائق',headline='خط بارليف',size=96,sub='ساتر ترابي على الضفة الشرقية للقناة،<br>تعلوه نقاط حصينة وخنادق، واعتُبر عائقًا يستحيل اختراقه',subSize=32,credit='خندق ونقطة حصينة من خط بارليف · من كتاب «المعارك الحربية على الجبهة المصرية» لجمال حماد · '+CR),
 P('s03','١ | العائق','ساتر بارتفاع ٧ أدوار تقريبًا','من 20 إلى 25 مترًا، بميل من 45° إلى 65°،<br>تعلوه حصون من الخرسانة وأكياس الرمل والأسلاك الشائكة','storming.png','جنود مصريون أثناء اقتحام خط بارليف · '+CR,boxTop=560,boxH=640),
 P('s04','٢ | الإعداد','سنوات من التدريب وخطة خداع محكمة','تدريبات منذ 1968، وتخطيط عملياتي منذ 1971،<br>وخطة خداع استراتيجي أخفت نية الهجوم وموعده','preparing.png','دبابات وجنود مصريون يستعدون للحرب، 1973 · '+CR,size=64,boxTop=560,boxH=640),
 P('s05','٣ | اختيار الموعد','لماذا ٦ أكتوبر؟','تيار ومدّ مناسبان للعبور، وقمر معظم الليل لبناء الكباري،<br>وتوقيت مفاجئ للعدو، وتنسيق كامل مع سوريا','sadat.png','الرئيس السادات وقادته على الجبهة المصرية · '+CR,size=84,boxTop=560,boxH=640,boxPos='center 30%'),
 P('s06','٤ | ساعة الصفر','الساعة الثانية ظهرًا','14:00 ضربة جوية بأكثر من 200 طائرة<br>14:05 تمهيد نيراني من نحو 2000 مدفع لمدة 53 دقيقة','aircraft.png','طائرات مصرية في طريقها لضرب أهداف في سيناء · '+CR,size=80,boxTop=560,boxH=640),
 P('s07','٥ | الموجة الأولى','٤٠٠٠ مقاتل في الموجة الأولى','عبروا القناة في نحو 2500 قارب مطاطي وخشبي،<br>وتسلّقوا الساتر بسلالم الحبال','boat.png','جنود مصريون في قارب أثناء عبور قناة السويس · '+CR,size=68,boxTop=560,boxH=640),
 P('s08','٦ | الفكرة العبقرية','الماء يهزم الرمل','مضخات مياه بضغط عالٍ جرفت الساتر وفتحت الثغرات لعبور الدبابات<br>فكرة المهندس العسكري باقي زكي يوسف','bridge2.png','شاحنات مصرية تعبر كوبري فوق القناة عبر ثغرة في الساتر، 7 أكتوبر 1973 · '+CR,size=84,boxTop=560,boxH=640),
 P('s09','٧ | الكباري والمعديات','جسور فوق القناة','10 كباري ثقيلة • 5 خفيفة • 10 عائمة • 35 معدية<br>ونحو 80 ألف جندي عبروا بحلول منتصف الليل','bridge.png','مركبات مصرية تعبر قناة السويس في 7 أكتوبر 1973 · '+CR,size=84,boxTop=560,boxH=640),
 P('s10','٨ | النتيجة','بحلول ٨ أكتوبر: رأس جسر بعمق ١٥ كم','التخطيط الدقيق + السرية + الإرادة = نصر<br>شاركنا: ما الدرس الذي تتعلمه من أكتوبر؟','celebrate.png','جنود مصريون يحتفلون بنجاح عبور قناة السويس · '+CR,size=62,boxTop=560,boxH=640),
]
for s in slides: s['lang']='ar'
caption = """كيف عبر المصريون قناة السويس وأسقطوا خط بارليف؟ 🇪🇬
اسحب ← واقرأ خطة «بدر» في 10 صور حقيقية من الحرب.

🔸 العائق: خط بارليف، ساتر ترابي بارتفاع 20 إلى 25 مترًا على الضفة الشرقية، تعلوه نقاط حصينة.
🔸 الإعداد: تدريبات منذ 1968، وتخطيط منذ 1971، وخطة خداع استراتيجي أخفت موعد الهجوم.
🔸 الموعد: 6 أكتوبر 1973 (10 رمضان)، لملاءمة التيار والمدّ وضوء القمر، وبالتنسيق مع سوريا.
🔸 ساعة الصفر 14:00: ضربة جوية بأكثر من 200 طائرة، ثم تمهيد نيراني من نحو 2000 قطعة مدفعية لمدة 53 دقيقة.
🔸 14:20: الموجة الأولى من 4000 مقاتل تعبر في نحو 2500 قارب.
🔸 خراطيم المياه تفتح ثغرات في الساتر، بفكرة المهندس باقي زكي يوسف.
🔸 10 كباري ثقيلة و5 خفيفة و10 عائمة و35 معدية، وعبر نحو 80 ألف جندي بحلول منتصف الليل.
🔸 بحلول 8 أكتوبر: رأس جسر بعمق نحو 15 كم على طول الضفة الشرقية.

احفظ البوست 🔖 وشاركه مع من يحب التاريخ.
ما الدرس الذي تتعلمه من أكتوبر؟ 👇

المصادر: موسوعة ويكيبيديا (Operation Badr 1973، Bar Lev Line)، ودراسة مكتبة الكونغرس عن مصر.\nالصور: ويكيميديا كومنز (ملكية عامة)، ومنها صور من كتاب «المعارك الحربية على الجبهة المصرية» لجمال حماد.

#نصر_أكتوبر #خط_بارليف #العبور #مصر #6_أكتوبر"""
json.dump({"batch":"2026-10-badr-plan","status":"pending_review","publish":"immediately_after_approval","caption":caption,"posts":slides},open('posts/2026-10-badr-plan.json','w'),ensure_ascii=False,indent=2)
print(len(caption))
