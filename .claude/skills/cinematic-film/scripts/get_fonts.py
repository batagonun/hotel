#!/usr/bin/env python3
"""Fetch open-licensed fonts for any text role this machine cannot match (Linux and Windows lack the
Mac faces the looks were designed with), into <project>/fonts/<role>.ttf where the engine finds them.

  python3 get_fonts.py --project my-film            # only roles that would fall back to the system default
  python3 get_fonts.py --project my-film --force    # replace them all
  python3 get_fonts.py --project my-film --arabic   # also Arabic faces, into fonts/<role>_ar.ttf

  cond -> Bebas Neue (SIL Open Font License): condensed caps for labels, numbers, stamps, captions
  hand -> Homemade Apple (Apache 2.0): handwriting for ledger entries

  Arabic (--arabic, SIL Open Font License): Tajawal for labels, numbers and captions, Amiri for
  document text, Aref Ruqaa for handwriting. Fetched only for roles whose Arabic face would fall back.

All come from the Google Fonts repository on GitHub. Keep the licence notes with the project if
you share it.
"""
import argparse
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
UA = "cinematic-film/1.0 (+https://github.com/Moh4696/cinematic-skill)"
FONTS = {
    "cond": ("https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf", "Bebas Neue", "SIL Open Font License 1.1"),
    "hand": ("https://raw.githubusercontent.com/google/fonts/main/apache/homemadeapple/HomemadeApple-Regular.ttf", "Homemade Apple", "Apache License 2.0"),
}
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
OFL = "SIL Open Font License 1.1"
ARABIC_FONTS = {
    "serif": (GF + "amiri/Amiri-Regular.ttf", "Amiri", OFL),
    "hand": (GF + "arefruqaa/ArefRuqaa-Regular.ttf", "Aref Ruqaa", OFL),
    "cond": (GF + "tajawal/Tajawal-ExtraBold.ttf", "Tajawal ExtraBold", OFL),
    "label": (GF + "tajawal/Tajawal-Bold.ttf", "Tajawal Bold", OFL),
    "labelm": (GF + "tajawal/Tajawal-Medium.ttf", "Tajawal Medium", OFL),
    "mono": (GF + "tajawal/Tajawal-Bold.ttf", "Tajawal Bold", OFL),
}


def fetch(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        dst.write_bytes(r.read())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--arabic", action="store_true", help="also fetch Arabic faces (fonts/<role>_ar.ttf)")
    a = ap.parse_args()
    from engine import resolve_arabic_typeface, resolve_typeface
    fdir = pathlib.Path(a.project) / "fonts"; fdir.mkdir(parents=True, exist_ok=True)
    notes = []
    for role, (url, name, lic) in FONTS.items():
        _, desc = resolve_typeface(role, fdir)
        if not a.force and not desc.startswith("system default"):
            print(f"{role:<5} already {desc}"); continue
        fetch(url, fdir / f"{role}.ttf")
        print(f"{role:<5} -> fonts/{role}.ttf  ({name}, {lic})")
        notes.append(f"{role}.ttf: {name}, {lic}, from {url}")
    for role, (url, name, lic) in (ARABIC_FONTS.items() if a.arabic else ()):
        _, desc = resolve_arabic_typeface(role, fdir)
        weak = desc.startswith(("system fallback", "NO ARABIC", "DejaVu"))
        if not a.force and not weak:
            print(f"{role + '_ar':<9} already {desc}"); continue
        fetch(url, fdir / f"{role}_ar.ttf")
        print(f"{role + '_ar':<9} -> fonts/{role}_ar.ttf  ({name}, {lic})")
        notes.append(f"{role}_ar.ttf: {name}, {lic}, from {url}")
    if notes:
        with open(fdir / "LICENSES.txt", "a") as f:
            f.write("\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
