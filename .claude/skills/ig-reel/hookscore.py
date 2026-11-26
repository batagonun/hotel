#!/usr/bin/env python3
"""
hookscore.py - score the first line of a Reel on the five things strong hooks
have in common, and rank a batch of them against each other.

What this is:  five local heuristics, computed on your machine from the text
alone. They measure properties that hooks which hold attention tend to share -
a length you can say in under three seconds, a concrete marker, something at stake,
the payload at the front rather than the back, and a viewer to aim it at.

What this is NOT:  a view predictor. It was tested against 74 real short-form
hooks, transcribed from the first three seconds of the top eight and bottom
eight performers on five channels. Separating a real hook from a deliberately
bad one it does well: AUC 0.83, and 9 of 10 written-to-be-bad hooks scored
below the real median. Separating a good creator's hits from that same
creator's misses it barely does at all: AUC 0.56, where 0.50 is a coin flip.

So use it for what it measured well. It catches greetings, preambles, hooks
with nothing concrete in them and hooks that take five seconds to say. It will
not tell you which of two decent hooks will travel, and nothing that reads text
can, because that is decided by your face, your edit, your audio and who
Instagram shows it to. Trust the retention graph over this script.

Each check returns 0 to 100. Higher is better.

Usage
  python3 hookscore.py hooks.txt              # one hook per line, ranked
  python3 hookscore.py --hook "I lost $18,000 on one missing contract."
  pbpaste | python3 hookscore.py -
  python3 hookscore.py hooks.txt --json

Arabic: hooks in Egyptian colloquial or Modern Standard Arabic are scored with
Arabic word lists (numbers, money, stakes, greetings, preambles, "you"). The
74-hook validation above was English only; treat Arabic scores as a filter for
obviously weak hooks, never as a verdict on a good one.
"""

import argparse
import json
import re
import statistics
import sys

# Arabic letters, Arabic-Indic digits, harakat and tatweel count as word characters,
# so Arabic hooks are tokenised instead of scoring zero words (see ARABIC below).
WORD_RE = re.compile(r"[A-Za-z0-9$%'’\-\u0621-\u063A\u0640-\u0652\u0660-\u0669\u0670]+")
NUMBER_RE = re.compile(
    r"\$\s?\d[\d,]*(?:\.\d+)?"                       # money, whole
    r"|\b\d[\d,]*(?:\.\d+)?\s?"                      # a figure, with or
    r"(?:%|k\b|x\b|hrs?\b|hours?\b|mins?\b|minutes?\b"  # without a unit
    r"|days?\b|weeks?\b|months?\b|years?\b)?",
    re.IGNORECASE)
PROPER_RE = re.compile(r"(?<!^)\b[A-Z][a-z]{2,}\b")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Spoken hooks say their numbers out loud. "Zero dollars" and "twenty grand"
# are as concrete as "$0" and "$20,000", and counting only digits missed them.
# "one" and "first" are deliberately absent: they are filler far more often
# than they are a quantity.
SPOKEN_NUMBERS = {
    "zero", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "fifteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
    "billion", "dozen", "half", "twice", "triple",
}
MONEY_WORDS = {
    "dollars", "dollar", "bucks", "grand", "percent", "cents",
    "millionaire", "billionaire", "revenue", "profit", "salary", "rent",
}

# Words that put something on the line. A hook with none of these is a
# statement; a hook with one is a reason to keep watching.
STAKES = {
    "stop", "never", "wrong", "mistake", "mistakes", "lost", "lose", "losing",
    "cost", "costs", "broke", "broken", "failed", "failure", "fail", "nobody",
    "no", "not", "don't", "dont", "doesn't", "didn't", "can't", "won't",
    "quit", "quitting", "fired", "deleted", "delete", "killed", "kills", "kill",
    "replaced", "replaces", "cut", "beat", "free", "paid", "charged", "hired",
    "saved", "first",
    "banned", "illegal", "worst", "hate", "hated", "wasted", "waste", "scam",
    "lie", "lied", "lying", "truth", "secret", "hidden", "stole", "stolen",
    "before", "until", "instead", "but", "except", "unless", "problem",
    "risk", "danger", "warning", "regret", "wish", "should", "shouldn't",
    "still", "already", "only", "without", "versus", "vs", "actually",
}

# Openers that spend the first second saying nothing.
WEAK_OPENERS = [
    "so", "ok", "okay", "hey", "hi", "hello", "guys", "yo", "alright",
    "welcome", "today", "basically", "honestly", "look", "listen", "um",
    "just", "let", "lets", "let's", "i wanted", "i want", "one of",
    "have you", "did you", "do you", "are you", "in this", "in today",
    "the thing", "a lot", "there is", "there are", "this is", "it is",
    "as a", "when it", "if you've", "you know",
]

# Imperatives that earn the front position.
IMPERATIVES = {
    "stop", "steal", "copy", "delete", "try", "watch", "read", "save",
    "use", "build", "make", "write", "send", "take", "start", "quit",
    "never", "always", "don't", "dont", "do", "put", "run", "check",
}

DEALBREAKERS = [
    (re.compile(r"(?i)^\s*(?:stop scrolling|don'?t scroll)"),
     "Opens with \"stop scrolling\". Asking for attention proves you have not earned it."),
    (re.compile(r"(?i)\b(?:in (?:this|today'?s) (?:video|reel)|i'?m going to show you|i'?ll show you how)\b"),
     "Video preamble. Delete it and open on the payoff."),
    (re.compile(r"(?i)^\s*(?:hey |hi |what'?s up |welcome )"),
     "Greeting. Nobody came to the feed to be greeted."),
    (HASHTAG_RE,
     "Hashtag in the hook. Hashtags belong at the bottom of the caption, if anywhere."),
    (EMOJI_RE,
     "Emoji in the hook. On-screen text at hook size has room for words or for an emoji, not both."),
]


# ---------------------------------------------------------------------------
# ARABIC (Egyptian colloquial + Modern Standard). Added for batagonun/hotel.
# Every word below is written in normalised form: no harakat or tatweel,
# alef variants as "ا", taa marbuta as "ه", alef maqsura as "ي". Tokens are
# normalised the same way and tried with and without common proclitics
# (و، ف، ب، ل، ال) before lookup.
# ---------------------------------------------------------------------------
AR_LETTER = re.compile(r"[\u0621-\u064A]")
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_HARAKAT = re.compile(r"[\u0640\u064B-\u0652\u0670]")


def is_arabic(text):
    return len(AR_LETTER.findall(text)) > len(re.findall(r"[A-Za-z]", text))


def norm(token):
    t = _HARAKAT.sub("", token.translate(AR_DIGITS))
    t = re.sub("[أإآٱ]", "ا", t)
    return t.replace("ة", "ه").replace("ى", "ي").lower().strip("'’")


def forms(token):
    """The token plus the same token with a leading proclitic removed."""
    t = norm(token)
    out = {t}
    for pre in ("وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ل"):
        if t.startswith(pre) and len(t) - len(pre) >= 2:
            out.add(t[len(pre):])
    return out


def hit(token, *sets):
    f = forms(token)
    return any(f & s for s in sets)


SPOKEN_NUMBERS_AR = {
    "صفر", "اتنين", "اثنين", "تلاته", "ثلاثه", "اربعه", "اربع", "خمسه", "خمس",
    "سته", "ست", "سبعه", "سبع", "تمانيه", "ثمانيه", "تسعه", "تسع", "عشره", "عشر",
    "عشرين", "تلاتين", "ثلاثين", "اربعين", "خمسين", "ميه", "مايه", "مئه", "مائه",
    "ميتين", "الف", "الاف", "مليون", "ملايين", "مليار", "نص", "نصف", "ربع",
    "ضعف", "اضعاف", "دسته", "مرتين",
}
MONEY_WORDS_AR = {
    "جنيه", "جنيهات", "دولار", "دولارات", "ريال", "درهم", "يورو", "فلوس",
    "سعر", "اسعار", "ثمن", "مرتب", "راتب", "ايجار", "مكسب", "ربح", "ارباح",
    "خساره", "فاتوره", "الميه", "بالميه", "نسبه", "ليله", "ليالي",
    # Egyptian places: Arabic has no capital letters, so names need a list.
    "القاهره", "اسكندريه", "الاسكندريه", "اسوان", "الاقصر", "الغردقه", "شرم", "دهب",
    "النيل", "الساحل", "العلمين", "السويس", "بورسعيد", "سيناء", "الجونه", "الفيوم",
    "سيوه", "مطروح", "الزمالك", "المعادي", "الهرم", "الاهرامات", "طابا", "نويبع",
}
STAKES_AR = {
    "محدش", "ماحدش", "مفيش", "مافيش", "ابدا", "غلط", "غلطه", "اخطاء", "خطا",
    "خسرت", "خسر", "خسرنا", "ضيع", "ضيعت", "ضاع", "مش", "ما", "لا", "لم", "لن",
    "ليس", "ممنوع", "تحذير", "خطر", "سر", "اسرار", "الحقيقه", "حقيقه", "اسوا",
    "وحش", "كدب", "كذب", "بدل", "الا", "لسه", "بس", "قبل", "لحد", "حتي", "ندم",
    "ندمت", "رفض", "اترفض", "مجاني", "ببلاش", "مستحيل", "فشل", "فشلت", "صدمه",
    "عيب", "مشكله", "اول", "اخر", "متعملش", "ماتعملش", "اوعي", "بطل",
}
IMPERATIVES_AR = {
    "ابعت", "ابعته", "ابعتها", "شوف", "شوفوا", "جرب", "جربوا", "احفظ", "احفظه",
    "اسمع", "اسمعوا", "خلي", "اعمل", "بطل", "متعملش", "ماتعملش", "اوعي", "اقرا",
    "ركز", "افتكر", "خد", "حط", "اكتب", "قول", "امسح", "سيب", "اطلب", "احجز",
}
# Normalised starts of a line that spend the first second saying nothing.
WEAK_OPENERS_AR = (
    "اهلا", "مرحبا", "السلام", "ازيكم", "ازيك", "يا جماعه", "النهارده", "انهارده",
    "اليوم", "في الفيديو", "في هذا", "فالفيديو", "تعالوا", "بص ", "بصوا", "طيب",
    "اوك", "خلينا", "هنتكلم", "سنتحدث", "حابب", "عايز اكلمكم", "في البدايه",
)
ADDRESS_AR = {
    "انت", "انتي", "انتو", "انتوا", "انتم", "لك", "ليك", "ليكي", "ليكم", "عندك",
    "عندكم", "بتاعك", "معاك", "نفسك", "حضرتك", "حضرتكم",
}
# Words that end in "ك" without being "you".
NOT_ADDRESS_AR = {
    "ذلك", "كذلك", "لذلك", "هناك", "هنالك", "تلك", "ملك", "الملك", "بنك", "البنك",
    "سمك", "السمك", "شباك", "الشباك", "ضحك", "مسك", "سلك", "شبك", "ديك", "كدك",
}
FIRST_PERSON_AR = {"انا", "احنا", "نحن", "عندي", "ليا", "بتاعي", "عندنا", "بتاعنا"}

DEALBREAKERS_AR = [
    (re.compile(r"^\s*(?:متقلبش|ما تقلبش|ماتقلبش|استني|استنا|اوعي تقلب)"),
     "Opens with \"don't scroll\" (متقلبش). Asking for attention proves you have not earned it."),
    (re.compile(r"(?:في|ف) (?:الفيديو|الريل) (?:ده|دا|هذا)|في هذا (?:الفيديو|المقطع)|هنتكلم عن|سنتحدث عن|هوريكم|خليني اوريك|هقولكم ازاي"),
     "Video preamble (في الفيديو ده / هنتكلم عن). Delete it and open on the payoff."),
    (re.compile(r"^\s*(?:اهلا|مرحبا|السلام عليكم|ازيكم|ازيك|يا جماعه|صباح الخير|مساء الخير)"),
     "Greeting. Nobody came to the feed to be greeted."),
]


def clamp(n):
    return max(0.0, min(100.0, n))


def words(text):
    # "$18,000" is one word when it is spoken, so it is one word here too.
    return WORD_RE.findall(re.sub(r"(?<=\d),(?=\d)", "", text))


def check_length(text):
    """A hook has to land before the thumb moves. Roughly two seconds."""
    w = words(text)
    n = len(w)
    ar = is_arabic(text)
    # Arabic words carry their prepositions and pronouns, so the same idea
    # takes fewer of them; Egyptian speech also runs ~150 wpm, not 165.
    lo, hi, wps = (4, 11, 2.5) if ar else (5, 12, 2.75)
    secs = n / wps
    chars = len(text.strip())
    if lo <= n <= hi:
        score = 100.0
    elif n < lo:
        score = clamp(100 - (lo - n) * 20)
    else:
        score = clamp(100 - (n - hi) * 11)
    if chars > 60:                       # two lines of big on-screen text
        score -= 12
    return clamp(score), f"{n} words, {chars} chars, ~{secs:.1f}s spoken (want {lo}-{hi} words)"


def check_specificity(text):
    """One concrete thing beats three abstract ones."""
    nums = [n.strip() for n in NUMBER_RE.findall(text.translate(AR_DIGITS)) if n.strip()]
    propers = set(PROPER_RE.findall(text))
    low = [w.lower().strip("'’") for w in words(text)]
    spoken = [w for w in low if w in SPOKEN_NUMBERS or w in MONEY_WORDS
              or hit(w, SPOKEN_NUMBERS_AR, MONEY_WORDS_AR)]
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (f"{hits} concrete marker(s)" + (f": {found}" if found else
                   " - no number, no name, nothing checkable"))


def check_stakes(text):
    """Tension, cost, negation. Something the viewer might lose."""
    w = [x.lower().strip("'’") for x in words(text)]
    hits = [x for x in w if x in STAKES or hit(x, STAKES_AR)]
    markers = sorted(set(hits))
    if re.search(r"\$\s?\d", text):
        markers.append("a price")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} tension marker(s)" + (f": {', '.join(markers[:4])}" if markers else
                                         " - nothing is at stake in this line")
    return clamp(score), detail


def check_frontload(text):
    """The interesting word cannot be in position nine."""
    w = words(text)
    if not w:
        return 0.0, "empty"
    low = [x.lower().strip("'’") for x in w]
    opener = " ".join(low[:2])
    penalty = 0
    hit_opener = None
    for weak in WEAK_OPENERS:
        if opener.startswith(weak) or low[0] == weak:
            penalty, hit_opener = 30, weak
            break
    ar_opener = " ".join(norm(x) for x in w[:3]) + " "
    for weak in WEAK_OPENERS_AR:
        if hit_opener is None and ar_opener.startswith(weak):
            penalty, hit_opener = 30, weak.strip()
            break
    payload = None
    for i, token in enumerate(low):
        if (token in STAKES or token in SPOKEN_NUMBERS or token in MONEY_WORDS
                or hit(token, STAKES_AR, SPOKEN_NUMBERS_AR, MONEY_WORDS_AR)
                or NUMBER_RE.match(w[i].translate(AR_DIGITS)) or (i and PROPER_RE.match(w[i]))):
            payload = i
            break
    if payload is None:
        base = 30.0
        where = "no payload word anywhere in the line"
    elif payload <= 3:
        base = 100.0
        where = f"payload at word {payload + 1}"
    elif payload <= 6:
        base = 70.0
        where = f"payload at word {payload + 1}, could move forward"
    else:
        base = 40.0
        where = f"payload at word {payload + 1}, too late"
    detail = where + (f"; weak opener \"{hit_opener}\"" if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text):
    """Aimed at one viewer, or floating in the air."""
    low = text.lower()
    w = [x.lower().strip("'’") for x in words(text)]
    if re.search(r"\b(you|your|you're|youre|yourself)\b", low):
        return 100.0, "speaks to the viewer"
    for x in w:
        f = forms(x)
        if f & ADDRESS_AR or any(len(t) >= 4 and t.endswith(("ك", "كم")) and t not in NOT_ADDRESS_AR
                                 for t in f):
            return 100.0, f"speaks to the viewer (\"{x}\")"
    if w and (w[0] in IMPERATIVES or hit(w[0], IMPERATIVES_AR)):
        return 90.0, f"imperative opener (\"{w[0]}\")"
    if re.search(r"\b(i|my|me|we|our)\b", low) or any(hit(x, FIRST_PERSON_AR) for x in w):
        return 70.0, "first person, no viewer named"
    return 35.0, "third person, nobody in the room"


CHECKS = ["LENGTH", "SPECIFICITY", "STAKES", "FRONTLOAD", "ADDRESS"]


def run(text):
    results = {
        "LENGTH": check_length(text),
        "SPECIFICITY": check_specificity(text),
        "STAKES": check_stakes(text),
        "FRONTLOAD": check_frontload(text),
        "ADDRESS": check_address(text),
    }
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(text)]
    flat = " ".join(norm(t) for t in text.split())
    flags += [msg for pattern, msg in DEALBREAKERS_AR if pattern.search(flat)]
    scores = [results[c][0] for c in CHECKS]
    # The weakest property caps the hook, same logic as detect.py: one bad
    # property is enough for the thumb to keep moving.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15
    overall = clamp(overall)
    verdict = "STRONG" if overall >= 70 and min(scores) >= 55 and not flags else (
        "OK" if overall >= 50 else "WEAK")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, out=sys.stdout):
    print("\nHOOK SCORE", file=out)
    print("=" * 62, file=out)
    print(f"  \"{text.strip()}\"\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'HOOK SCORE':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  DEALBREAKER  {f}", file=out)
    if verdict != "STRONG":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Weakest property: {weakest}. Fix that one and re-run.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nHOOK RANKING\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 62 else r["hook"][:59] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<7} {hook}", file=out)
        print(f"        weakest: {r['weakest']} ({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"        dealbreaker: {f}", file=out)
    print("\nShoot the top one. If the top one is under 50, none of these are the hook.\n",
          file=out)


def main():
    ap = argparse.ArgumentParser(description="Score a Reel hook on five properties.")
    ap.add_argument("input", nargs="?", default="-", help="file with one hook per line, or -")
    ap.add_argument("--hook", help="score a single hook given on the command line")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print("nothing to score", file=sys.stderr)
        sys.exit(2)

    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line)
        payload.append({
            "hook": line,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return

    if len(payload) == 1:
        results, overall, verdict, flags = run(lines[0])
        render_one(lines[0], results, overall, verdict, flags)
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))

    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
