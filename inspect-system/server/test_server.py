# -*- coding: utf-8 -*-
"""اختبار آلي لخادم التفتيش: يشغّله على منفذ ومجلدات مؤقتة ويمر على سير العمل كاملًا."""
import base64
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8790
tmp = tempfile.mkdtemp(prefix="inspect_test_")
env = dict(os.environ, INSPECT_PORT=str(PORT), INSPECT_DATA=os.path.join(tmp, "data"),
           INSPECT_CLUBS=os.path.join(tmp, "clubs"), INSPECT_IDLE="3", PYTHONIOENCODING="utf-8")
proc = subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "server.py")], env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))
    ip = s.getsockname()[0]
    s.close()
    return ip


LOCAL = f"http://127.0.0.1:{PORT}"
REMOTE = f"http://{lan_ip()}:{PORT}"  # نفس الجهاز عبر عنوان الشبكة = يُعامل كهاتف على Wi-Fi


def call(base, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw or b"{}")
            except ValueError:
                return r.status, {"_raw": len(raw)}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


passed = failed = 0


def check(name, cond, info=""):
    global passed, failed
    if cond:
        passed += 1
        print("  ✓", name)
    else:
        failed += 1
        print("  ✗", name, info)


for _ in range(50):
    try:
        call(LOCAL, "/api/hello")
        break
    except Exception:  # noqa: BLE001
        time.sleep(0.1)

try:
    print("الخادم على", REMOTE)
    st, r = call(REMOTE, "/api/hello")
    check("الاكتشاف على الشبكة (hello)", r.get("app") == "inspect-server")
    st, r = call(REMOTE, "/api", {"action": "poll", "token": "x"})
    check("رفض طلب بلا جلسة", r.get("code") == "SESSION")
    st, r = call(REMOTE, "/admin/api/state")
    check("لوحة المشرف مغلقة أمام الشبكة", st == 403)

    dev = {"deviceId": "DEV-A", "deviceName": "Samsung A54", "inspectorName": "أحمد", "inspectorId": "U1"}
    st, r = call(REMOTE, "/api", {"action": "requestAccess", **dev})
    rid = r.get("requestId")
    check("طلب اتصال من الهاتف", r.get("ok") and rid)
    st, r = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid})
    check("الطلب معلّق", r.get("status") == "pending")
    st, s = call(LOCAL, "/admin/api/state")
    check("الطلب ظاهر في لوحة المشرف", any(q["id"] == rid for q in s["requests"]))
    st, r = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-OTHER", "requestId": rid})
    check("جهاز آخر لا يستلم المفتاح", r.get("status") == "unknown")
    st, r = call(LOCAL, "/admin/api/approve", {"id": rid})
    check("المشرف يعتمد", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid})
    tok = r.get("token")
    check("الهاتف يستلم مفتاح الجلسة", r.get("status") == "approved" and tok)
    st, r = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid})
    check("المفتاح يُسلَّم مرة واحدة", "token" not in r)
    st, r = call(REMOTE, "/api", {"action": "poll", "token": tok})
    check("المزامنة تعمل بالمفتاح", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "saveConfig", "token": tok, "config": {}})
    check("الهاتف لا يعدّل الإعدادات", not r.get("ok"))

    photo = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0fakejpeg").decode()
    insp = {"id": "N1", "inspectorId": "U1", "status": "done",
            "header": {"facility": "نادي الشروق", "place": "المطبخ", "date": "2026-10-10"},
            "snap": {"title": "قائمة التحقق لقسم المطبخ", "axes": [{"items": [{"id": "I1"}, {"id": "I2"}]}]},
            "answers": {"I2": {"v": "ت", "note": "ملاحظة", "photos": [photo]}}}
    st, r = call(REMOTE, "/api", {"action": "saveInspection", "token": tok, "inspection": {**insp, "inspectorId": "U9"}})
    check("رفض رفع تفتيش باسم مفتش آخر", not r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "saveInspection", "token": tok, "inspection": insp})
    check("رفع التفتيش", r.get("ok"))
    club = os.path.join(tmp, "clubs", "نادي الشروق")
    files = os.listdir(os.path.join(club, "مدخلات", "تفتيشات"))
    check("التفتيش في مجلد النادي", len(files) == 1 and "[N1]" in files[0], files)
    pics = [f for d, _, fs in os.walk(os.path.join(club, "مدخلات", "صور")) for f in fs]
    check("الصورة مستخرجة باسم البند", pics == ["بند 2 - 1.jpg"], pics)
    check("مجلد المخرجات موجود", os.path.isdir(os.path.join(club, "مخرجات")))
    call(REMOTE, "/api", {"action": "saveInspection", "token": tok, "inspection": {**insp, "answers": {}}})
    check("تحديث التفتيش لا يكرر الملف", len(os.listdir(os.path.join(club, "مدخلات", "تفتيشات"))) == 1)

    st, r = call(LOCAL, "/api", {"action": "requestAccess", "deviceId": "PC", "inspectorName": "المشرف"})
    lrid = r["requestId"]
    st, r = call(LOCAL, "/api", {"action": "accessStatus", "deviceId": "PC", "requestId": lrid})
    ltok = r.get("token")
    check("كمبيوتر الإدارة يُعتمد تلقائيًا", r.get("status") == "approved" and ltok)
    st, r = call(LOCAL, "/api", {"action": "getInspections", "token": ltok, "since": 0})
    check("المشرف يرى كل التفتيشات", len(r.get("items", [])) == 1)
    call(LOCAL, "/api", {"action": "saveInspection", "token": ltok, "inspection": {**insp, "id": "N2", "inspectorId": "U2"}})
    st, r = call(REMOTE, "/api", {"action": "getInspections", "token": tok, "since": 0})
    check("المفتش يرى تفتيشاته فقط", [i["id"] for i in r.get("items", [])] == ["N1"], r)
    st, r = call(LOCAL, "/api", {"action": "saveConfig", "token": ltok, "config": {"lists": []}})
    check("رفض رفع إعدادات بلا رقم إصدار (نسخة قديمة)", r.get("code") == "CONFLICT")
    st, r = call(LOCAL, "/api", {"action": "saveConfig", "token": ltok, "baseRev": 0, "config": {"lists": [], "inspDeleted": ["N2"]}})
    check("المشرف يحفظ الإعدادات", r.get("ok") and r.get("rev") == 1)
    st, r = call(LOCAL, "/api", {"action": "saveConfig", "token": ltok, "baseRev": 0, "config": {"lists": []}})
    check("رفض الكتابة فوق إعدادات أحدث", r.get("code") == "CONFLICT" and r.get("rev") == 1)

    # المشرف من تطبيقه على الهاتف: يرفع التعيينات ويرى كل التفتيشات
    users = [{"id": "U1", "name": "أحمد", "role": "inspector"}, {"id": "U9", "name": "المشرف", "role": "supervisor"}]
    st, r = call(LOCAL, "/api", {"action": "saveConfig", "token": ltok, "baseRev": 1, "config": {"lists": [], "users": users}})
    check("إعدادات فيها مشرف ومفتش", r.get("ok") and r.get("rev") == 2)
    srid = call(REMOTE, "/api", {"action": "requestAccess", "deviceId": "DEV-SUP", "deviceName": "هاتف المشرف",
                                 "inspectorName": "المشرف", "inspectorId": "U9"})[1]["requestId"]
    call(LOCAL, "/admin/api/approve", {"id": srid})
    stok = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-SUP", "requestId": srid})[1]["token"]
    st, r = call(REMOTE, "/api", {"action": "saveConfig", "token": stok, "baseRev": 2, "config": {"lists": [], "users": users, "places": [{"id": "P1"}]}})
    check("هاتف المشرف يرفع التعيينات", r.get("ok") and r.get("rev") == 3, r)
    st, r = call(REMOTE, "/api", {"action": "saveConfig", "token": tok, "baseRev": 3, "config": {}})
    check("هاتف المفتش لا يرفع التعيينات", not r.get("ok") and r.get("code") != "CONFLICT", r)
    st, r = call(REMOTE, "/api", {"action": "getInspections", "token": stok, "since": 0})
    check("هاتف المشرف يرى كل التفتيشات", [i["id"] for i in r.get("items", [])] == ["N1"], r)
    st, r = call(REMOTE, "/api", {"action": "saveInspection", "token": stok, "inspection": {**insp, "id": "N9", "inspectorId": "U9"}})
    check("المشرف يرفع تفتيشه من الهاتف", r.get("ok"))
    check("الحذف ينقل التفتيش إلى المحذوفات",
          not os.path.exists(os.path.join(tmp, "data", "تفتيشات", "i_N2.json"))
          and os.path.exists(os.path.join(tmp, "data", "محذوفات", "i_N2.json")))

    sid = call(LOCAL, "/admin/api/state")[1]["sessions"][0]["id"]
    st, r = call(LOCAL, "/admin/api/end", {"id": sid})
    check("المشرف يُنهي الاتصال", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "poll", "token": tok})
    check("بعد الإنهاء يُرفض الهاتف", r.get("code") == "SESSION")

    rid2 = call(REMOTE, "/api", {"action": "requestAccess", **dev})[1]["requestId"]
    call(LOCAL, "/admin/api/reject", {"id": rid2})
    st, r = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid2})
    check("الرفض يصل للهاتف", r.get("status") == "rejected")

    rid3 = call(REMOTE, "/api", {"action": "requestAccess", **dev})[1]["requestId"]
    call(LOCAL, "/admin/api/approve", {"id": rid3})
    tok3 = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid3})[1]["token"]
    time.sleep(4.2)
    st, r = call(REMOTE, "/api", {"action": "poll", "token": tok3})
    check("الجلسة تنتهي بانقطاع الهاتف", r.get("code") == "SESSION")

    rid4 = call(REMOTE, "/api", {"action": "requestAccess", **dev})[1]["requestId"]
    call(LOCAL, "/admin/api/approve", {"id": rid4})
    tok4 = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-A", "requestId": rid4})[1]["token"]
    st, r = call(REMOTE, "/api", {"action": "endSession", "token": tok4})
    check("المفتش يُنهي جلسته", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "poll", "token": tok4})
    check("بعد خروج المفتش يُرفض المفتاح", r.get("code") == "SESSION")

    # هاتف جديد قبل الدخول: جلسة بلا اسم مفتش
    rid5 = call(REMOTE, "/api", {"action": "requestAccess", "deviceId": "DEV-NEW", "deviceName": "هاتف جديد"})[1]["requestId"]
    call(LOCAL, "/admin/api/approve", {"id": rid5})
    tok5 = call(REMOTE, "/api", {"action": "accessStatus", "deviceId": "DEV-NEW", "requestId": rid5})[1]["token"]
    st, r = call(REMOTE, "/api", {"action": "getConfig", "token": tok5})
    check("قبل الدخول: سحب الإعدادات مسموح", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "getInspections", "token": tok5, "since": 0})
    check("قبل الدخول: لا تفتيشات", r.get("items") == [])
    st, r = call(REMOTE, "/api", {"action": "saveInspection", "token": tok5, "inspection": insp})
    check("قبل الدخول: الرفع ممنوع", not r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "identify", "token": tok5, "inspectorId": "U1", "inspectorName": "أحمد"})
    check("بعد الدخول: ربط الجلسة باسم المفتش", r.get("ok"))
    st, r = call(REMOTE, "/api", {"action": "getInspections", "token": tok5, "since": 0})
    check("بعد الربط: يرى تفتيشاته", [i["id"] for i in r.get("items", [])] == ["N1"], r)
    st, r = call(REMOTE, "/api", {"action": "identify", "token": tok5, "inspectorId": "U2", "inspectorName": "آخر"})
    check("لا يمكن تغيير المفتش داخل نفس الجلسة", r.get("code") == "SESSION")

    st, r = call(REMOTE, "/app/index.html")
    check("البرنامج يُفتح من الخادم", st == 200)
    log = open(os.path.join(tmp, "data", "سجل.jsonl"), encoding="utf-8").read()
    check("كل الأحداث مسجلة", all(e in log for e in [
        "access_requested", "access_approved", "access_rejected", "session_ended_by_supervisor",
        "session_expired", "session_closed_by_device", "inspection_received"]))
finally:
    proc.terminate()
print(f"\nالنتيجة: {passed} ناجح، {failed} فاشل")
sys.exit(1 if failed else 0)
