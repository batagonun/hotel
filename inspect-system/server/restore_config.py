# -*- coding: utf-8 -*-
"""استرجاع إعدادات البرنامج (المنشآت والأماكن والقوائم والمستخدمين) من نسخة احتياطية إلى الخادم.

الاستخدام:  python restore_config.py <inspect-backup.json>
- يحفظ نسخة من الإعدادات الحالية قبل الاستبدال.
- يرفع رقم الإصدار فتسحب كل الأجهزة الإعدادات المسترجعة عند اتصالها.
- ينفّذ علامات الحذف الموجودة في النسخة (نقل إلى «المحذوفات»، لا حذف نهائي).
"""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server as S  # noqa: E402

FIELDS = ("lists", "places", "users", "facilities", "facDeleted", "facility", "heroImg", "inspDeleted")


def main(path):
    with open(path, encoding="utf-8") as f:
        b = json.load(f)
    cfg = {"lists": b["lists"], "places": b["places"], "users": b["users"], "facilities": b.get("facilities") or [],
           "facDeleted": bool(b.get("facDeleted")), "facility": b["settings"].get("facility", ""),
           "heroImg": b["settings"].get("heroImg", ""), "inspDeleted": b.get("inspDeleted") or []}
    cur_path = os.path.join(S.DATA, "config.json")
    with S.LOCK:
        cur = S.config_doc()
        if os.path.exists(cur_path):
            keep = os.path.join(S.DATA, "نسخ_احتياطية", f"config قبل الاسترجاع rev{cur['rev']} {time.strftime('%Y-%m-%d %H%M%S')}.json")
            os.makedirs(os.path.dirname(keep), exist_ok=True)
            shutil.copy2(cur_path, keep)
            print("نسخة من الإعدادات السابقة:", keep)
        rev = cur["rev"] + 1
        S.jwrite(cur_path, {"rev": rev, "updatedAt": time.time(), "config": cfg})
        for iid in cfg["inspDeleted"]:
            S.remove_inspection(iid)
    S.log("config_restored", rev=rev, source=os.path.basename(path))
    print(f"تم الاسترجاع: الإصدار {rev} | المنشآت: {[f.get('name') for f in cfg['facilities']]} | "
          f"المستخدمون: {len(cfg['users'])} | الأماكن: {len(cfg['places'])} | القوائم: {len(cfg['lists'])}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1])
