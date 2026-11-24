"""Arabic right-to-left test: the story reads right to left, so the camera travels right to left."""
from engine import BigText, Card, Counter, Film, PaperDoc, PenMark, Route, Stamp

ACCENT = (176, 24, 20)
INK = (34, 32, 30)
CARD_W, CARD_H = 3400, 2000
CX = [-4600, -8600, -12600]          # three findings, laid out leftwards


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="studio")

    # 1  title (types on from the right), then the visit report with a highlighted phrase
    film.add(BigText("نتائج التدقيق الميداني", 0, -2300, 620, L(1) - 0.1, rgb=INK, shadow=False, grunge=False, type_on=0.8))
    film.add(PenMark("underline", 0, -2050, 5600, 60, t_in=W(1, "الميداني") - 0.1, dur=0.5, width=34, rgb=ACCENT))
    rep = PaperDoc(5400, 600, 2800, 3600, rot=2.0, t_in=W(1, "النخيل"),
                   header=(("تقرير الزيارة الميدانية", 130, "label"), ("فندق النخيل · الربع الثالث", 84, "mono")),
                   rows=16, sentence="يلتزم الفندق بتطبيق إجراءات التشغيل القياسية في جميع الأقسام دون استثناء", sentence_row=6,
                   sentence_size=96)
    film.add(rep)
    (hx, hy), hw = rep.phrase_pos(doc.res(), "جميع الأقسام")           # RTL phrase position
    film.add(PenMark("highlight", hx, hy, hw + 60, 0, t_in=E(1) + 0.6, dur=0.45, width=120, rot=2.0))

    # 2  the compliance score rolls up
    film.add(Counter(0, 600, 1100, 78, W(2, "ثمانية") - 0.1, dur=1.2, suffix="%", caption="نسبة الامتثال", rgb=ACCENT))

    # 3-6  three gaps, one card each, arrows leftwards
    gaps = [("الاستقبال", ["زمن تسجيل الوصول: ١٢ دقيقة", "المعيار: ٥ دقائق"], 4),
            ("الأغذية والمشروبات", ["سجلات سلامة الغذاء ناقصة", "آخر مراجعة: قبل ٤٠ يوماً"], 5),
            ("الصيانة", ["الصيانة الوقائية متأخرة", "١٨ أمر عمل مفتوح"], 6)]
    for (title, lines, line), x in zip(gaps, CX):
        film.add(Card(x, 600, CARD_W, CARD_H, L(line) + 0.05, title=title, lines=lines, accent=ACCENT, title_size=230, body_size=135))
    film.add(Route((-1400, 600), (CX[0] + CARD_W / 2 + 120, 600), t_in=L(4) - 0.3, dur=0.5, bend=-0.3, width=24, rgb=INK))
    for a, b, line in zip(CX, CX[1:], (5, 6)):
        film.add(Route((a - CARD_W / 2 - 80, 600), (b + CARD_W / 2 + 80, 600), t_in=L(line) - 0.2, dur=0.5, bend=-0.3, width=24, rgb=INK))

    # 7  the recommendation: big words, then a stamp
    film.add(BigText("خطة تصحيحية خلال ٣٠ يوماً", -17600, 300, 520, L(7) + 0.2, rgb=INK, shadow=False, grunge=False, bar=(246, 206, 46)))
    film.add(Stamp("عاجل", -17600, 1500, size=360, rot=-8, t_in=W(7, "ثلاثين")))

    # camera: right to left
    film.shot(0.0, 0, -2200, 0.55)
    film.shot(W(1, "النخيل") + 0.2, 3200, -600, 0.42)
    film.shot(E(1) + 0.2, 5400, 700, 0.62, rot=0.6)
    film.shot(W(2, "ثمانية") - 0.2, 0, 500, 0.6)
    film.shot(E(2) - 0.2, 0, 550, 0.56)                          # hold on the score
    film.shot(L(3) + 0.3, -6500, 600, 0.33)
    for (_, _, line), x in zip(gaps, CX):
        film.shot(L(line) + 0.4, x, 650, 0.72, rot=-0.4 if line % 2 else 0.4)
        film.shot(E(line) - 0.1, x - 300, 650, 0.68)
    film.shot(L(7) + 0.5, -17600, 700, 0.6)
    film.shot(film.duration, -9000, 300, 0.22, radius=20000, strength=0.1)
    return film
