#!/usr/bin/env python3
"""Arabic voiceover for reels with Google Gemini TTS (free tier of the Gemini API).

Language rule (user request, 26 Nov 2026):
  * heritage, history and poetry topics -> fusha: Modern Standard Arabic, fully
    voweled, delivered with an Egyptian accent and classic Egyptian recitation style.
  * everything else -> masri: natural Cairene Egyptian colloquial.

The API key is never stored in the repo. Set it in the environment first:
    export GEMINI_API_KEY="..."        # from https://aistudio.google.com/apikey

usage:
  python3 tools/tts.py <script.txt> <out.wav> [--topic "شعر"] [--mode auto|fusha|masri]
                       [--voice Charon] [--model gemini-3.8-flash-tts] [--style "..."]

  --topic   the post's content axis or subject; used when --mode is auto (default)
  --style   extra delivery notes appended to the built-in style instructions
  --dry-run print the chosen mode and full prompt without calling the API

Only stdlib is used. Output: 24 kHz mono 16-bit WAV, ready for ffmpeg muxing:
  ffmpeg -i reel.mp4 -i voice.wav -filter_complex "[1:a]volume=1.0[v];[0:a]volume=0.25[m];[m][v]amix=inputs=2:duration=first" -c:v copy out.mp4
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
import wave

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")

# words that send a script to fusha when --mode auto
FUSHA_TOPICS = [
    "شعر", "قصيد", "بيت", "ديوان", "تراث", "تاريخ", "تاريخي", "حكمة", "أثر", "آثار",
    "مأثور", "سيرة", "أدب", "فصحى", "poetry", "poem", "heritage", "history", "verse",
]

STYLE = {
    "fusha": (
        "اقرأ النص بالعربية الفصحى السليمة كما هو مشكول تمامًا، بإلقاء مصري أصيل "
        "على طريقة كبار مذيعي الإذاعة المصرية وقرّاء الشعر: مخارج حروف واضحة، "
        "ونطق مصري طبيعي للحروف، وتنغيم رصين دافئ. "
        "احترم الحركات وأواخر الكلمات، ولا تحوّل أي كلمة إلى العامية. "
        "في الشعر: التزم بوزن البيت وإيقاعه، وتوقّف وقفة قصيرة بين الشطرين، "
        "ووقفة أطول بعد كل بيت، وأبطئ قليلًا في الكلمة المحورية. "
        "السرعة هادئة متأنية تناسب التأمل، والنبرة وقورة فيها حنين، دون مبالغة مسرحية."
    ),
    "masri": (
        "اقرأ النص باللهجة المصرية القاهرية الطبيعية، كأنك صاحب بيحكي لصاحبه موقف "
        "من الحياة اليومية، مش مذيع نشرة. "
        "النبرة دافئة وقريبة وفيها ابتسامة وحماس هادي من غير صريخ. "
        "السرعة متوسطة مائلة للحيوية تناسب ريل من 15 لـ 25 ثانية. "
        "اقف وقفة قصيرة بعد أول جملة، وقبل المعلومة المهمة، وقبل الجملة الأخيرة. "
        "انطق الكلمات الإنجليزية بنطق مصري طبيعي."
    ),
}
COMMON = "لا تضف أي كلمة غير موجودة في النص."

# Gemini TTS speaks everything in the prompt unless the delivery notes are fenced off
# from the words to say. A flat "instructions + النص:" prompt (or "Say ...: text") made
# gemini-3.8-flash-tts read the style notes aloud (a 5 s line came out 31 s). The
# DIRECTOR'S NOTES / TRANSCRIPT layout below keeps only the transcript spoken (tested
# 26 Nov 2026: 5.7 s, clean). systemInstruction is rejected by this model (400).
PROFILE = {
    "fusha": "Egyptian radio narrator reciting classical Arabic",
    "masri": "Cairene Egyptian storyteller",
}

DIACRITICS = re.compile(r"[ً-ْ]")
ARABIC_LETTER = re.compile(r"[ء-ي]")


def choose_mode(mode, topic):
    if mode != "auto":
        return mode
    t = (topic or "").lower()
    return "fusha" if any(k in t for k in FUSHA_TOPICS) else "masri"


def vowel_ratio(text):
    letters = len(ARABIC_LETTER.findall(text))
    return len(DIACRITICS.findall(text)) / letters if letters else 0.0


def build_prompt(text, mode, extra):
    style = STYLE[mode] + (" " + extra if extra else "") + " " + COMMON
    return (
        f"# AUDIO PROFILE: {PROFILE[mode]}\n"
        f"### DIRECTOR'S NOTES\n{style}\n"
        "Only the transcript below is spoken. Never read these notes aloud.\n\n"
        f"#### TRANSCRIPT\n{text.strip()}"
    )


def synthesize(prompt, voice, model, key):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    req = urllib.request.Request(
        API.format(model=model),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        if e.code == 429:
            sys.exit("الحصة المجانية انتهت مؤقتًا (429 RESOURCE_EXHAUSTED). جرّب بعد قليل ولا تحوّل لمفتاح مدفوع إلا بموافقة المستخدم.\n" + detail)
        sys.exit(f"خطأ من Gemini API ({e.code}):\n{detail}")
    try:
        part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    except (KeyError, IndexError):
        sys.exit("لم يرجع صوت من الـ API:\n" + json.dumps(data, ensure_ascii=False)[:600])
    return base64.b64decode(part["data"]), part.get("mimeType", "")


def save_wav(audio, mime, out):
    if audio[:4] == b"RIFF":  # already a complete WAV
        with open(out, "wb") as f:
            f.write(audio)
        return
    rate = 24000
    m = re.search(r"rate=(\d+)", mime or "")
    if m:
        rate = int(m.group(1))
    with wave.open(out, "wb") as w:  # raw 16-bit little-endian mono PCM
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(audio)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script")
    p.add_argument("out")
    p.add_argument("--topic", default="")
    p.add_argument("--mode", choices=["auto", "fusha", "masri"], default="auto")
    p.add_argument("--voice", default="Charon")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--style", default="")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    with open(a.script, encoding="utf-8") as f:
        text = f.read()
    mode = choose_mode(a.mode, a.topic)
    if mode == "fusha" and vowel_ratio(text) < 0.35:
        print("تنبيه: النص الفصيح غير مشكول بما يكفي. اضبط الكلمات بالشكل قبل التوليد لتفادي أخطاء النطق والإعراب.", file=sys.stderr)
    prompt = build_prompt(text, mode, a.style)
    print(f"mode={mode} voice={a.voice} model={a.model}", file=sys.stderr)
    if a.dry_run:
        print(prompt)
        return

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY غير مضبوط. أنشئ مفتاحًا مجانيًا من https://aistudio.google.com/apikey وضعه في متغير البيئة، ولا تحفظه في المستودع.")
    audio, mime = synthesize(prompt, a.voice, a.model, key)
    save_wav(audio, mime, a.out)
    print(f"✓ {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
