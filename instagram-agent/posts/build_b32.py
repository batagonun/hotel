# Builds overlays + story spec for the 1 Nov reel (same readability rules as build_b19.py:
# headline >= 80px, sub >= 48px, 6.5-10s per scene).
import json, pathlib
P = 'assets/photos/b32/'
GRAD = ("<defs><linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#000' stop-opacity='.85'/>"
        "<stop offset='.42' stop-color='#000' stop-opacity='.55'/><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
        "<stop offset='.88' stop-color='#000' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.7'/></linearGradient></defs>"
        "<rect width='1080' height='1920' fill='url(#t)'/>")
SMALL = "<br><span style='font-size:36px;opacity:.85'>{}</span>"

def ov(i, tag, head, sub, size=88, top=240, sub_size=52, lang='ar'):
    return dict(id=f'o{i}', scene='none', lang=lang, transparent=True, glow=True, top=top, size=size,
                tag=tag, headline=head, sub=sub, svg=GRAD, subSize=sub_size, tagSize=42, noHandle=False)

reels = {
 '2026-11-01-ambiguous': dict(
  date='2026-11-01T10:00',
  scenes=[
   (P+'ab_window.png', 7, ov(1, '', 'في إحساس<br>مالوش اسم…', 'أو كده كنا فاكرين', size=100, sub_size=56)),
   (P+'ab_chair.png', 8, ov(2, '', '«لا أنت بعيد فأنتظرك…<br>ولا أنت قريب فألقاك»', '', size=84)),
   (P+'ab_phone.png', 8.5, ov(3, '', '«ولا أنت لي فيطمئن قلبي…<br>ولا أنا محرومٌ منك لأنساك»', '', size=80)),
   (P+'ab_door.png', 8.5, ov(4, 'علم النفس سمّاه', 'الفقد الغامض', 'Ambiguous Loss<br>الدكتورة بولين بوس · السبعينات', size=110, sub_size=52)),
   (P+'ab_beach.png', 9, ov(5, 'يعني إيه؟', 'إنك تفقد حد…<br>وهو لسه موجود', 'أو يغيب عنك وهو لسه جوّه قلبك<br>وأصعب ما فيه إنه مالوش نهاية', size=96, sub_size=50)),
   (P+'ab_town.png', 7.5, ov(6, '', '«أنت في منتصف<br>كل شيء»', 'حسّيت بيه قبل كده؟ 👇'
                            + SMALL.format('المصدر: Pauline Boss · Ambiguous Loss (1999)<br>الصور: ويكيميديا كومنز (CC0)'), size=100, sub_size=52)),
  ],
  caption='''في ناس مش موجودين… ومش غايبين.
والإحساس ده ليه اسم في علم النفس 👇

«لا أنت بعيد فأنتظرك، ولا أنت قريب فألقاك،
ولا أنت لي فيطمئن قلبي، ولا أنا محرومٌ منك لأنساك…
أنت في منتصف كل شيء.»

في السبعينات، الدكتورة بولين بوس، أستاذة علم النفس الأسري، سمّت الإحساس ده «الفقد الغامض» (Ambiguous Loss).

وليه نوعين:
حد غايب عنك بجسمه… بس لسه حاضر جوّاك.
وحد قدّامك بجسمه… بس مش حاضر معاك.

وأصعب ما فيه إنه مالوش نهاية واضحة. لا وداع تقفل بيه، ولا لقاء ترتاح بيه، فبتفضل في النص.

وبوس بتقول إن الحل مش إنك «تقفل الصفحة» بالعافية، لكن إنك تتعلم تعيش مع السؤال من غير ما يوقف حياتك.

حسّيت بيه قبل كده؟ ومين أول حد جه في بالك؟ 👇

📚 المصدر: Pauline Boss، كتاب «Ambiguous Loss» (Harvard University Press، 1999)، وموقع ambiguousloss.com
📷 الصور: ويكيميديا كومنز (Rosalind Chang · Luca Bravo · Daria Nepriakhina · Hermes Rivera · Jean Gerber · Illia Cherednychenko، CC0)

#الفقد_الغامض #علم_النفس #مشاعر #خواطر'''),
}

for name, r in reels.items():
    ovs = dict(width=1080, height=1920, posts=[s[2] for s in r['scenes']])
    pathlib.Path(f'posts/{name}-overlays.json').write_text(json.dumps(ovs, ensure_ascii=False, indent=1))
    story = dict(fade=0.7, scenes=[dict(photo=s[0], overlay=f'out/{name}/ov/o{i+1}.png', dur=s[1]) for i, s in enumerate(r['scenes'])])
    pathlib.Path(f'posts/{name}-reel.json').write_text(json.dumps(story, ensure_ascii=False, indent=1))
    meta = dict(batch='2026-11-01-single', post=name, date=r['date'], status='pending_review', format='REEL',
                caption=r['caption'], media=f'out/{name}/{name}.mp4')
    pathlib.Path(f'posts/{name}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    total = sum(s[1] for s in r['scenes']) - 0.7 * (len(r['scenes']) - 1)
    print(name, f'{total:.1f}s', len(r['caption']), 'chars')
