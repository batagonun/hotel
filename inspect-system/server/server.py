# -*- coding: utf-8 -*-
"""خادم الإدارة المحلي لبرنامج قوائم التحقق (بديل Google Apps Script).

- يعمل على كمبيوتر الإدارة، ويقبل الاتصال من الشبكة الداخلية فقط (عناوين خاصة).
- المفتش يطلب الاتصال ← المشرف يعتمد من «لوحة المشرف» ← جلسة بمفتاح خاص بالجهاز.
- الجلسة تنتهي: بإنهاء المشرف، أو بخروج المفتش منها، أو بانقطاع الهاتف عن الشبكة
  مدة SESSION_IDLE، أو بعد SESSION_MAX. بعدها يلزم طلب اتصال جديد (اعتماد لكل جلسة).
- كل تفتيش يصل يُحفظ في بيانات الخادم، وتُنسخ منه نسخة مقروءة مع صوره في مجلد ناديه:
  D:\\W\\الأندية\\<النادي>\\مدخلات\\...

التشغيل:  python server.py            (لوحة المشرف: http://127.0.0.1:8770/admin)
"""
import base64
import ipaddress
import json
import mimetypes
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
APP_DIR = os.environ.get("INSPECT_APP") or os.path.join(ROOT, "app")
DATA = os.environ.get("INSPECT_DATA") or os.path.join(ROOT, "بيانات")
INSP_DIR = os.path.join(DATA, "تفتيشات")
TRASH = os.path.join(DATA, "محذوفات")
CLUBS = os.environ.get("INSPECT_CLUBS") or (r"D:\W\الأندية" if os.name == "nt" else os.path.join(ROOT, "الأندية"))
PORT = int(os.environ.get("INSPECT_PORT") or 8770)
SESSION_IDLE = int(os.environ.get("INSPECT_IDLE") or 15 * 60)  # ثوانٍ دون اتصال تنهي الجلسة
SESSION_MAX = 12 * 3600
REQUEST_TTL = 10 * 60  # طلب لم يُعتمد خلال 10 دقائق يسقط
MAX_BODY = 80 * 1024 * 1024
SERVER_NAME = "الإدارة العامة لأندية وفنادق الشرطة"
VERSION = "1.0"

LOCK = threading.RLock()


# ---------------------------------------------------------------- تخزين

def jread(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def jwrite(path, obj, pretty=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1 if pretty else None)
    os.replace(tmp, path)


def log(event, **kw):
    rec = {"t": time.time(), "event": event, **kw}
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "سجل.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


DEV_PATH = os.path.join(DATA, "الأجهزة.json")


def devices():
    return jread(DEV_PATH, {"requests": {}, "sessions": {}})


def save_devices(d):
    jwrite(DEV_PATH, d, pretty=True)


def safe(name, default="بدون اسم"):
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", str(name or "")).strip(" .")
    return name[:80] or default


# ---------------------------------------------------------------- الجلسات

def expire(d, now=None):
    """تنهي الجلسات المنقطعة والطلبات القديمة. ترجع True إذا تغيّر شيء."""
    now = now or time.time()
    changed = False
    for tok, s in list(d["sessions"].items()):
        if s.get("local"):
            continue
        reason = None
        if now - s["lastSeen"] > SESSION_IDLE:
            reason = "انقطاع الاتصال"
        elif now - s["approvedAt"] > SESSION_MAX:
            reason = "انتهاء المدة القصوى"
        if reason:
            del d["sessions"][tok]
            log("session_expired", device=s["deviceName"], inspector=s["inspectorName"], reason=reason)
            changed = True
    for rid, r in list(d["requests"].items()):
        if r["status"] == "pending" and now - r["at"] > REQUEST_TTL:
            r["status"] = "expired"
            changed = True
        if r["status"] != "pending" and now - r["at"] > 24 * 3600:
            del d["requests"][rid]
            changed = True
    return changed


def session_for(token, ip):
    with LOCK:
        d = devices()
        changed = expire(d)
        s = d["sessions"].get(token or "")
        if s:
            s["lastSeen"] = time.time()
            s["ip"] = ip
            changed = True
        if changed:
            save_devices(d)
        return s


# ---------------------------------------------------------------- التفتيشات

def config_doc():
    return jread(os.path.join(DATA, "config.json"), {"rev": 0, "config": None})


def is_supervisor(s):
    """كمبيوتر الإدارة، أو جلسة سجّل فيها مستخدم دوره «مشرف» في إعدادات الخادم."""
    if s.get("local"):
        return True
    users = (config_doc().get("config") or {}).get("users") or []
    return any(u.get("id") == s.get("inspectorId") and u.get("role") == "supervisor" for u in users if s.get("inspectorId"))


def insp_path(iid):
    return os.path.join(INSP_DIR, "i_" + re.sub(r"[^\w-]", "", iid) + ".json")


def last_insp():
    try:
        return max((os.path.getmtime(os.path.join(INSP_DIR, f)) for f in os.listdir(INSP_DIR)), default=0)
    except OSError:
        return 0


def club_dir(name):
    d = os.path.join(CLUBS, safe(name, "منشأة بدون اسم"))
    for sub in (("مدخلات", "تفتيشات"), ("مدخلات", "صور"), ("مدخلات", "مصادر"), ("مخرجات",)):
        os.makedirs(os.path.join(d, *sub), exist_ok=True)
    return d


def short_title(t):
    return t.replace("قائمة التحقق لل", "ال").replace("قائمة التحقق ل", "").replace("قائمة التحقق ", "")


def mirror_name(insp):
    """اسم ملف/مجلد التفتيش في مجلد النادي: التاريخ والمكان والقائمة (مختصرة) + رقم التفتيش كاملًا."""
    h = insp.get("header") or {}
    title = short_title((insp.get("snap") or {}).get("title", "قائمة"))
    return safe(f"{h.get('date', '')} {h.get('place', '')} - {title}")[:60].rstrip(" .-") + f" [{insp['id']}]"


def mirror_to_club(insp):
    """نسخة مقروءة من التفتيش وصوره في مجلد النادي."""
    h = insp.get("header") or {}
    club = club_dir(h.get("facility"))
    tag = f"[{insp['id']}]"
    tdir = os.path.join(club, "مدخلات", "تفتيشات")
    for f in os.listdir(tdir):  # نسخة أقدم من نفس التفتيش
        if tag in f:
            os.remove(os.path.join(tdir, f))
    title = short_title((insp.get("snap") or {}).get("title", "قائمة"))
    base = mirror_name(insp)  # رقم التفتيش دائمًا في الاسم (لا يُقص) حتى لا يحل تفتيش محل آخر
    jwrite(os.path.join(tdir, base + ".json"), insp, pretty=True)

    pdir = os.path.join(club, "مدخلات", "صور", mirror_name(insp))
    shutil.rmtree(pdir, ignore_errors=True)
    num = {}
    n = 0
    for ax in (insp.get("snap") or {}).get("axes", []):
        for it in ax.get("items", []):
            n += 1
            num[it.get("id")] = n
    for iid, ans in (insp.get("answers") or {}).items():
        for k, ph in enumerate((ans or {}).get("photos") or [], 1):
            m = re.match(r"data:image/(jpeg|png|webp);base64,(.+)", ph or "", re.S)
            if m:
                os.makedirs(pdir, exist_ok=True)
                ext = "jpg" if m.group(1) == "jpeg" else m.group(1)
                with open(os.path.join(pdir, f"بند {num.get(iid, iid)} - {k}.{ext}"), "wb") as f:
                    f.write(base64.b64decode(m.group(2)))
    return club


def remove_inspection(iid):
    p = insp_path(iid)
    if os.path.exists(p):
        os.makedirs(TRASH, exist_ok=True)
        insp = jread(p, {})
        shutil.move(p, os.path.join(TRASH, os.path.basename(p)))
        club = os.path.join(CLUBS, safe((insp.get("header") or {}).get("facility"), "منشأة بدون اسم"))
        tdir = os.path.join(club, "مدخلات", "تفتيشات")
        if os.path.isdir(tdir):
            for f in os.listdir(tdir):
                if f"[{iid}]" in f:
                    os.makedirs(os.path.join(club, "مدخلات", "محذوفات"), exist_ok=True)
                    shutil.move(os.path.join(tdir, f), os.path.join(club, "مدخلات", "محذوفات", f))
        log("inspection_deleted", id=iid)


# ---------------------------------------------------------------- واجهة البرنامج

def api(body, ip, local):
    action = body.get("action")

    if action == "hello":
        return {"ok": True, "app": "inspect-server", "name": SERVER_NAME, "version": VERSION}

    if action == "requestAccess":
        dev_id = str(body.get("deviceId") or "")[:64]
        if not dev_id:
            return {"ok": False, "error": "بيانات الجهاز ناقصة"}
        with LOCK:
            d = devices()
            expire(d)
            for tok, s in list(d["sessions"].items()):  # جلسة سابقة لنفس الجهاز تُستبدل
                if s["deviceId"] == dev_id:
                    del d["sessions"][tok]
            rid = secrets.token_hex(8)
            req = {"id": rid, "deviceId": dev_id, "deviceName": str(body.get("deviceName") or "")[:60],
                   "inspectorName": str(body.get("inspectorName") or "")[:60],
                   "inspectorId": str(body.get("inspectorId") or "")[:40], "role": str(body.get("role") or "")[:20],
                   "ip": ip, "at": time.time(), "status": "pending"}
            for r in d["requests"].values():  # طلب معلّق سابق من نفس الجهاز يُلغى
                if r["deviceId"] == dev_id and r["status"] == "pending":
                    r["status"] = "replaced"
            d["requests"][rid] = req
            if local:  # كمبيوتر الإدارة نفسه (المشرف) يُعتمد تلقائيًا
                approve(d, rid, auto=True)
            save_devices(d)
        log("access_requested", device=req["deviceName"], inspector=req["inspectorName"], ip=ip, local=local)
        return {"ok": True, "requestId": rid}

    if action == "accessStatus":
        with LOCK:
            d = devices()
            if expire(d):
                save_devices(d)
            r = d["requests"].get(str(body.get("requestId") or ""))
            if not r or r["deviceId"] != body.get("deviceId"):
                return {"ok": True, "status": "unknown"}
            out = {"ok": True, "status": r["status"]}
            if r["status"] == "approved" and not r.get("delivered"):
                out["token"] = r["token"]  # يُسلَّم المفتاح مرة واحدة
                r["delivered"] = True
                save_devices(d)
            return out

    # ---- ما يلي يحتاج جلسة معتمدة
    s = session_for(body.get("token"), ip)
    if not s:
        return {"ok": False, "error": "انتهت الجلسة أو لم تُعتمد", "code": "SESSION"}

    if action == "endSession":
        with LOCK:
            d = devices()
            d["sessions"].pop(body.get("token"), None)
            save_devices(d)
        log("session_closed_by_device", device=s["deviceName"], inspector=s["inspectorName"])
        return {"ok": True}

    if action == "identify":  # ربط الجلسة باسم المفتش بعد دخوله (مرة واحدة لكل جلسة)
        with LOCK:
            d = devices()
            ss = d["sessions"].get(body.get("token"))
            if ss and not ss.get("inspectorId"):
                ss["inspectorId"] = str(body.get("inspectorId") or "")[:40]
                ss["inspectorName"] = str(body.get("inspectorName") or "")[:60]
                save_devices(d)
                log("session_identified", device=ss["deviceName"], inspector=ss["inspectorName"])
                return {"ok": True}
            if ss and ss.get("inspectorId") == body.get("inspectorId"):
                return {"ok": True}
        return {"ok": False, "error": "هذه الجلسة لمفتش آخر، اطلب اتصالًا جديدًا", "code": "SESSION"}

    if action in ("rev", "poll"):
        c = config_doc()
        return {"ok": True, "rev": c["rev"], "lastInsp": last_insp()}

    if action == "getConfig":
        c = config_doc()
        return {"ok": True, "rev": c["rev"], "config": c["config"]}

    if action == "saveConfig":
        if not is_supervisor(s):
            return {"ok": False, "error": "تعديل الإعدادات للمشرف فقط"}
        with LOCK:
            c = config_doc()
            # حماية من الكتابة فوق إعدادات أحدث: الرفع يحمل رقم الإصدار الذي بُني عليه
            base = body.get("baseRev")
            if base is None or int(base) != c["rev"]:
                log("config_conflict", baseRev=base, rev=c["rev"])
                return {"ok": False, "error": "الإعدادات على الخادم أحدث من هذا الجهاز، تم سحبها", "code": "CONFLICT",
                        "rev": c["rev"]}
            rev = c["rev"] + 1
            cfg = body.get("config") or {}
            jwrite(os.path.join(DATA, "config.json"), {"rev": rev, "updatedAt": time.time(), "config": cfg})
            for iid in cfg.get("inspDeleted") or []:
                remove_inspection(iid)
        log("config_saved", rev=rev)
        return {"ok": True, "rev": rev}

    if action == "saveInspection":
        i = body.get("inspection")
        if not isinstance(i, dict) or not i.get("id"):
            return {"ok": False, "error": "تفتيش غير صالح"}
        if not s.get("local") and (not s.get("inspectorId") or i.get("inspectorId") != s["inspectorId"]):
            return {"ok": False, "error": "هذا التفتيش لمفتش آخر"}
        with LOCK:
            jwrite(insp_path(i["id"]), i)
            club = mirror_to_club(i)
        log("inspection_received", id=i["id"], club=os.path.basename(club), place=(i.get("header") or {}).get("place"),
            inspector=s["inspectorName"])
        return {"ok": True}

    if action == "getInspections":
        since = float(body.get("since") or 0)
        who = body.get("inspectorId") or ""
        if not is_supervisor(s):  # المشرف يرى كل التفتيشات، والمفتش تفتيشاته فقط
            if not s.get("inspectorId"):  # جلسة قبل الدخول: الإعدادات فقط
                return {"ok": True, "items": [], "next": since, "more": False}
            who = s["inspectorId"]  # المفتش يرى تفتيشاته فقط
        os.makedirs(INSP_DIR, exist_ok=True)
        metas = sorted((os.path.getmtime(os.path.join(INSP_DIR, f)), f) for f in os.listdir(INSP_DIR)
                       if f.endswith(".json"))
        metas = [m for m in metas if m[0] * 1000 > since]
        items, nxt, k = [], since, 0
        for k, (t, f) in enumerate(metas):
            if len(items) >= 20:
                break
            nxt = t * 1000
            o = jread(os.path.join(INSP_DIR, f))
            if o and (not who or o.get("inspectorId") == who):
                items.append(o)
        else:
            k = len(metas)
        return {"ok": True, "items": items, "next": nxt, "more": k < len(metas)}

    return {"ok": False, "error": "إجراء غير معروف"}


def approve(d, rid, auto=False):
    r = d["requests"][rid]
    tok = secrets.token_urlsafe(24)
    now = time.time()
    r.update(status="approved", token=tok, decidedAt=now)
    d["sessions"][tok] = {"deviceId": r["deviceId"], "deviceName": r["deviceName"], "inspectorName": r["inspectorName"],
                          "inspectorId": r["inspectorId"], "ip": r["ip"], "approvedAt": now, "lastSeen": now,
                          "local": auto, "requestId": rid}
    log("access_approved", device=r["deviceName"], inspector=r["inspectorName"], auto=auto)


# ---------------------------------------------------------------- لوحة المشرف

def admin_api(path, body):
    with LOCK:
        d = devices()
        changed = expire(d)
        if path == "/admin/api/state":
            if changed:
                save_devices(d)
            now = time.time()
            reqs = [r for r in d["requests"].values() if r["status"] == "pending"]
            sess = [{**{k: v for k, v in s.items() if k != "requestId"}, "token": tok[:6] + "…", "id": tok,
                     "idleSec": int(now - s["lastSeen"])} for tok, s in d["sessions"].items() if not s.get("local")]
            logs = []
            try:
                with open(os.path.join(DATA, "سجل.jsonl"), encoding="utf-8") as f:
                    logs = [json.loads(l) for l in f.readlines()[-40:]][::-1]
            except OSError:
                pass
            clubs = []
            if os.path.isdir(CLUBS):
                for c in sorted(os.listdir(CLUBS)):
                    t = os.path.join(CLUBS, c, "مدخلات", "تفتيشات")
                    o = os.path.join(CLUBS, c, "مخرجات")
                    if os.path.isdir(t):
                        clubs.append({"name": c, "inspections": len([f for f in os.listdir(t) if f.endswith(".json")]),
                                      "outputs": len(os.listdir(o)) if os.path.isdir(o) else 0})
            return {"ok": True, "requests": reqs, "sessions": sess, "log": logs, "clubs": clubs,
                    "ips": local_ips(), "port": PORT, "idleMin": SESSION_IDLE // 60}
        if path in ("/admin/api/approve", "/admin/api/reject"):
            r = d["requests"].get(body.get("id"))
            if not r or r["status"] != "pending":
                return {"ok": False, "error": "الطلب غير موجود أو انتهى"}
            if path.endswith("approve"):
                approve(d, r["id"])
            else:
                r.update(status="rejected", decidedAt=time.time())
                log("access_rejected", device=r["deviceName"], inspector=r["inspectorName"])
            save_devices(d)
            return {"ok": True}
        if path == "/admin/api/end":
            ids = [t for t, s in d["sessions"].items() if not s.get("local")] if body.get("all") else [body.get("id")]
            for t in ids:
                s = d["sessions"].pop(t, None)
                if s:
                    log("session_ended_by_supervisor", device=s["deviceName"], inspector=s["inspectorName"])
            save_devices(d)
            return {"ok": True}
        if path == "/admin/api/openclub":
            p = os.path.join(CLUBS, safe(body.get("name")))
            if os.path.isdir(p) and os.name == "nt":
                subprocess.Popen(["explorer", p])
            return {"ok": True}
    return {"ok": False, "error": "غير معروف"}


def local_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))  # لا يُرسل شيئًا؛ يحدد الواجهة المحلية فقط
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(i for i in ips if not i.startswith("127.") and ipaddress.ip_address(i).is_private)


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    server_version = "InspectLocal/" + VERSION

    def log_message(self, *a):
        pass

    def client(self):
        ip = self.client_address[0]
        try:
            a = ipaddress.ip_address(ip)
        except ValueError:
            return ip, False, False
        return ip, a.is_loopback, (a.is_private or a.is_loopback)

    def send(self, code, body, ctype="application/json; charset=utf-8", cors=False):
        if not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("حجم البيانات أكبر من المسموح")
        raw = self.rfile.read(n).decode("utf-8") if n else "{}"
        return json.loads(raw or "{}")

    def do_OPTIONS(self):
        ip, local, private = self.client()
        if not private:
            return self.send(403, {"ok": False})
        self.send(204, b"", cors=True)

    def do_GET(self):
        ip, local, private = self.client()
        if not private:
            return self.send(403, {"ok": False, "error": "خارج الشبكة الداخلية"})
        path = unquote(urlparse(self.path).path).strip()
        if path.lower().startswith("/admin") and not path.lower().startswith("/admin/api/"):
            path = "/admin"  # أي صيغة لعنوان اللوحة (/admin/index.html، حروف كبيرة، مسافة زائدة) تفتح اللوحة
        if path in ("/api/hello", "/api"):
            return self.send(200, api({"action": "hello"}, ip, local), cors=True)
        if path.startswith("/admin"):
            if not local:
                return self.send(403, {"ok": False, "error": "لوحة المشرف من كمبيوتر الإدارة فقط"})
            if path in ("/admin", "/admin/"):
                with open(os.path.join(HERE, "admin.html"), "rb") as f:
                    return self.send(200, f.read(), "text/html; charset=utf-8")
            return self.send(200, admin_api(path, {}))
        if path == "/" or path.startswith("/app"):
            rel = path[len("/app"):].lstrip("/") if path.startswith("/app") else ""
            rel = rel or "index.html"
            full = os.path.normpath(os.path.join(APP_DIR, rel))
            if not full.startswith(os.path.normpath(APP_DIR)) or not os.path.isfile(full):
                return self.send(404, {"ok": False})
            with open(full, "rb") as f:
                ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
                if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                    ctype += "; charset=utf-8"
                return self.send(200, f.read(), ctype)
        self.send(404, {"ok": False})

    def do_POST(self):
        ip, local, private = self.client()
        if not private:
            return self.send(403, {"ok": False, "error": "خارج الشبكة الداخلية"})
        path = unquote(urlparse(self.path).path)
        try:
            body = self.read_body()
            if path == "/api":
                return self.send(200, api(body, ip, local), cors=True)
            if path.startswith("/admin/api/"):
                if not local:
                    return self.send(403, {"ok": False, "error": "لوحة المشرف من كمبيوتر الإدارة فقط"})
                return self.send(200, admin_api(path, body))
        except Exception as e:  # noqa: BLE001
            log("error", path=path, error=str(e))
            return self.send(200, {"ok": False, "error": str(e)}, cors=True)
        self.send(404, {"ok": False})


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for p in (DATA, INSP_DIR, CLUBS):
        os.makedirs(p, exist_ok=True)
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("خادم التفتيش يعمل.")
    print("لوحة المشرف:  http://127.0.0.1:%d/admin" % PORT)
    for ip in local_ips():
        print("عنوان الخادم على الشبكة: %s:%d" % (ip, PORT))
    print("اترك هذه النافذة مفتوحة، وأغلقها لإيقاف الخادم.")
    if "--open" in sys.argv:
        import webbrowser
        webbrowser.open("http://127.0.0.1:%d/admin" % PORT)
    srv.serve_forever()


if __name__ == "__main__":
    main()
