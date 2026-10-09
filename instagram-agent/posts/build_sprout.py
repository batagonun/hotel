# Builds posts/2026-10-sprout.json: carousel (7 slides) + reel frames for the World Food Day post (Oct 16).
# All photos are real, free-licensed files from Wikimedia Commons (see assets/photos/sprout/CREDITS.md).
import json, pathlib

P = 'assets/photos/sprout/'

def rows(items, numbered=False):
    out = ''.join(
        f'<div>{"<span class=n>%d</span>" % (i + 1) if numbered else ""}<span class=t>{a}</span>{f"<b>{b}</b>" if b else ""}</div>'
        for i, (a, b) in enumerate(items))
    return f'<div class="rows">{out}</div>'

slides = [
    dict(id='s1', scene='earth', lang='ar', top=100, size=74,
         tag='اليوم العالمي للأغذية · 16 أكتوبر',
         headline='بروتين أرخص بحوالي 10 مرات<br>من علبة الواي…<br>وجدتك كانت بتعمله في المطبخ',
         sub='العدس المنبّت والفول النابت: بالأرقام والمصادر · اسحب ←',
         box=P + 'sprouts01.png', boxTop=760, boxH=440, boxPos='center 60%',
         credit='عدس ناشف وعدس منبّت · صورة: L Maule · CC0 · ويكيميديا كومنز'),
    dict(id='s2', scene='earth', lang='ar', top=100, size=70, rowSize=31,
         tag='الحسبة',
         headline='تمن جرام البروتين',
         sub='حساب تقريبي بأسعار السوق المصري 2026',
         html=rows([('عدس أبو جبة (الكيلو ≈ 70 ج)', '0.30 ج تقريبًا'),
                    ('فول بلدي (الكيلو ≈ 60 ج)', '0.25 ج تقريبًا'),
                    ('واي بروتين (2 كيلو بـ 3200 لـ 5500 ج)', 'من 2 لـ 3.7 ج')])
              + '<div class="note" style="font-size:24px">الأسعار: مصراوي (يوليو 2026)، اليوم السابع (مايو 2026)، متوسط أسعار المكملات في مصر 2026 · نسبة البروتين: العدس 24% والفول 26% (USDA) والواي نحو 75%<br>ملحوظة: بروتين الواي أعلى جودة، لكن البقول مع العيش أو الرز بتقرّب الفرق جدًا</div>',
         box=P + 'fuul.png', boxTop=880, boxH=340, boxPos='center 70%',
         credit='عربية فول في القاهرة · صورة: David Stanley · CC BY 2.0'),
    dict(id='s3', scene='earth', lang='ar', top=100, size=66, rowSize=30,
         tag='العلم بيقول إيه؟',
         headline='إيه اللي بيحصل للحبّة لما تنبت؟',
         sub='',
         html=rows([('حمض الفايتيك اللي بيعطّل امتصاص الحديد والزنك بيقل في العدس بحوالي <b>75%</b> بعد 48 ساعة إنبات', ''),
                    ('فيتامين C في العدس النابت حوالي <b>3.5 أضعاف</b> العدس الناشف (16.5 مقابل 4.5 مجم/100 جم)', ''),
                    ('الحبّة بتطرى وبتستوي أسرع في الطبخ', '')])
              + '<div class="note">المصادر: مجلة Food Science & Nutrition (2025) دراسة أثر الإنبات على البقول · قاعدة بيانات USDA للقيم الغذائية</div>',
         box=P + 'sprouted.png', boxTop=800, boxH=420,
         credit='عدس منبّت · صورة: Veganbaking.net · CC BY-SA 2.0'),
    dict(id='s4', scene='earth', lang='ar', top=100, size=70, rowSize=31,
         tag='الطريقة',
         headline='4 خطوات… وبرطمان',
         sub='',
         html=rows([('انقع كوب عدس أبو جبة من 8 لـ 12 ساعة، أو فول بلدي من 12 لـ 24 ساعة', ''),
                    ('صفّيه واشطفه، وحطه في برطمان مغطّى بشاش ومايل لتحت عشان المية تنزل', ''),
                    ('اشطفه مرتين في اليوم وسيبه بعيد عن الشمس', ''),
                    ('أول ما الجذر يطلع نص سنتي لـ سنتي (بعد يومين لـ 4 أيام) يبقى جاهز ويتحفظ في التلاجة', '')], numbered=True),
         box=P + 'sprouts02.png', boxTop=860, boxH=360, boxPos='center 45%',
         credit='عدس بعد الإنبات · صورة: L Maule · CC0'),
    dict(id='s5', scene='earth', lang='ar', top=100, size=70, rowSize=31,
         tag='تختار إيه؟',
         headline='ينفع… وما ينفعش',
         sub='',
         html=rows([('✓ فول بلدي: أساس شوربة الفول النابت', 'من 3 لـ 4 أيام'),
                    ('✓ عدس أبو جبة (بني أو أخضر)', 'من 2 لـ 3 أيام'),
                    ('✓ حمص', 'من 2 لـ 3 أيام'),
                    ('✗ العدس الأصفر المقشور: مش هينبت', ''),
                    ('✗ تقاوي الزراعة: ممكن تكون معالجة بمبيدات', '')]),
         box=P + 'fava_seedling.png', boxTop=790, boxH=430, boxPos='center 35%',
         credit='حبّة فول نابتة · صورة: Josef Schlaghecken · CC BY-SA 4.0'),
    dict(id='s6', scene='earth', lang='ar', top=100, size=70, rowSize=30,
         tag='قاعدتين ذهبيتين',
         headline='اطبخه… وكمّله',
         sub='',
         html=rows([('<b>اطبخه:</b> هيئة الغذاء والدواء الأمريكية (FDA) تنصح الحوامل والأطفال وكبار السن وأصحاب المناعة الضعيفة بعدم أكل البراعم نيئة، والطبخ الكويس بيقلل الخطر جدًا. وعشان كده الفول النابت عندنا بيتاكل شوربة.', ''),
                    ('<b>كمّله:</b> بروتين البقول ناقصه حمض «الميثيونين»، وبروتين الحبوب ناقصه «الليسين». كُله مع عيش أو رز (زي الكشري) يكمّلوا بعض.', '')]),
         box=P + 'cairo_breakfast.png', boxTop=700, boxH=520, boxPos='center 60%',
         credit='فطار مصري: فول وعيش بلدي · صورة: H. Hakan Atik · CC BY-SA 4.0'),
    dict(id='s7', scene='photo', lang='ar', top=130, size=88,
         photo=P + 'cairo_breakfast.png', photoPos='center 70%',
         tag='الخلاصة',
         headline='جدتك سبقت الموضة',
         sub='احفظ البوست، وجرّب البرطمان الأسبوع ده،<br>وابعته لحد بيصرف كتير على البروتين 💪',
         credit='صورة: H. Hakan Atik · CC BY-SA 4.0 · ويكيميديا كومنز'),
]

caption = '''بروتين أرخص بحوالي 10 مرات من علبة الواي… وجدتك كانت بتعمله في المطبخ 🌱

في اليوم العالمي للأغذية، خلّينا نحسبها بالأرقام:
🔹 جرام البروتين من العدس ≈ 0.30 جنيه، ومن الفول البلدي ≈ 0.25 جنيه
🔹 جرام البروتين من علبة واي 2 كيلو ≈ من 2 لـ 3.7 جنيه

والإنبات بيزوّد القيمة:
🔹 حمض الفايتيك (اللي بيعطّل امتصاص الحديد والزنك) بيقل في العدس بحوالي 75% بعد 48 ساعة إنبات
🔹 فيتامين C في العدس النابت حوالي 3.5 أضعاف العدس الناشف

⚠️ قاعدتين: اطبخه دايمًا (خصوصًا للحوامل والأطفال وكبار السن)، وكُله مع عيش أو رز عشان البروتين يكمل.

الخطوات كاملة في الصور. احفظ البوست وجرّب الأسبوع ده، وقولنا في الكومنتات: الفول النابت عندكم بيتعمل إزاي؟ 👇

📚 المصادر: Food Science & Nutrition (2025) · قاعدة بيانات USDA · إرشادات FDA لسلامة البراعم · أسعار: مصراوي يوليو 2026، اليوم السابع مايو 2026
📷 الصور: ويكيميديا كومنز (L Maule CC0 · Veganbaking.net · David Stanley · J. Schlaghecken · H. Hakan Atik)

#اليوم_العالمي_للأغذية #عادات_صحية #الفول_النابت #أكل_صحي'''

batch = dict(batch='2026-10-sprout', date='2026-10-16T09:00', status='pending_review',
             replaces=dict(metricool_id=387937215, post='p07-food'),
             caption=caption, posts=slides)
pathlib.Path(__file__).with_name('2026-10-sprout.json').write_text(json.dumps(batch, ensure_ascii=False, indent=1))
print(len(caption), 'chars')
