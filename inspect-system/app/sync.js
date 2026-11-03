/* الاتصال بخادم الإدارة على الشبكة الداخلية (بديل مزامنة Google)
   - المفتش: يبحث عن الخادم على Wi-Fi الإدارة ← يطلب الاتصال ← يعتمده المشرف ← تُرفع تفتيشاته المنتهية وتُسحب الإعدادات.
   - الاعتماد لجلسة واحدة: ينتهي بإنهاء المشرف أو المفتش أو بانقطاع الهاتف عن الشبكة، ثم يلزم طلب جديد.
   - المشرف على كمبيوتر الإدارة: يتصل تلقائياً، ويرفع الإعدادات (منشآت، تعيينات، قوائم، مستخدمون) ويستلم كل التفتيشات. */
const SERVER_PORT = 8770;
const SY = { busy: false, timer: null, fails: 0, next: null };
const CN = { state: 'off', found: [], requestId: '', base: '', msg: '', poll: null };
const isPC = () => ['127.0.0.1', 'localhost'].includes(location.hostname);
const bridge = () => window.AndroidBridge || null;

/* داخل تطبيق Android: طلبات خادم الإدارة (http على الشبكة الداخلية) ينفّذها التطبيق نفسه،
   لأن عارض الصفحات يمنع الصفحة من مخاطبة عناوين الشبكة المحلية. */
if (window.AndroidBridge && AndroidBridge.http) {
  const pend = {}; let seq = 0; const _fetch = window.fetch.bind(window);
  window.__nativeResp = (id, status, body) => {
    const p = pend[id]; if (!p) return; delete pend[id];
    if (!status) return p.reject(new TypeError('Network error: ' + body));
    p.resolve({ ok: status >= 200 && status < 300, status, text: async () => body, json: async () => JSON.parse(body) });
  };
  window.fetch = (url, opt) => {
    url = String(url); opt = opt || {};
    if (!/^http:\/\//.test(url)) return _fetch(url, opt);
    return new Promise((resolve, reject) => {
      const id = 'r' + (++seq); pend[id] = { resolve, reject };
      if (opt.signal) {
        if (opt.signal.aborted) { delete pend[id]; return reject(new DOMException('aborted', 'AbortError')); }
        opt.signal.addEventListener('abort', () => { if (pend[id]) { delete pend[id]; reject(new DOMException('aborted', 'AbortError')); } });
      }
      AndroidBridge.http(id, opt.method || 'GET', url, opt.body == null ? null : String(opt.body), 8000);
    });
  };
}

/* إيقاف مزامنة Google نهائياً: أي إعداد قديم يُمسح */
function dropGoogle() {
  if (S && /script\.google\.com/.test(S.settings.syncUrl || '')) {
    S.settings.syncUrl = ''; S.settings.token = ''; S.sync = null;
    /* نقل البيانات: نسخة احتياطية قادمة من نظام Google تُستورد في كمبيوتر الإدارة ← تُرفع تفتيشاتها كلها إلى الخادم المحلي */
    if (isPC()) { S.inspections.forEach(i => { if (i.status === 'done') i.synced = false; }); S.settings.forcePush = true; }
    save();
  }
}
function deviceId() { if (!S.settings.deviceId) S.settings.deviceId = uid('D'); return S.settings.deviceId; }
function deviceName() {
  try { if (bridge() && bridge().deviceName) return bridge().deviceName(); } catch (e) {}
  return isPC() ? 'كمبيوتر الإدارة' : (navigator.userAgent.match(/\(([^;)]+;[^;)]+)/) || [, 'متصفح'])[1];
}

/* طلب إلى الخادم: مهلة وإعادة محاولة عند الانقطاع */
async function api(action, payload, opt) {
  opt = opt || {}; const tries = opt.tries || 3; let last;
  const url = opt.base ? opt.base + '/api' : S.settings.syncUrl;
  for (let n = 0; n < tries; n++) {
    const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), opt.timeout || 30000);
    try {
      const r = await fetch(url, { method: 'POST', body: JSON.stringify({ action, token: S.settings.token, ...payload }), signal: ctl.signal });
      const txt = await r.text(); clearTimeout(to); let j;
      try { j = JSON.parse(txt); } catch (e) { throw new Error('رد غير متوقع من الخادم'); }
      if (!j.ok) { const er = new Error(j.error || 'خطأ'); er.fatal = true; er.code = j.code; throw er; }
      return j;
    } catch (e) {
      clearTimeout(to);
      if (e.code === 'SESSION') { sessionLost(); throw e; }
      last = e.name === 'AbortError' ? new Error('انتهت مهلة الاتصال') : (e instanceof TypeError ? new Error('تعذر الوصول إلى خادم الإدارة، تأكد من الاتصال بشبكة الإدارة') : e);
      if (last.fatal) throw last;
      if (n < tries - 1) await new Promise(res => setTimeout(res, 1200 * (n + 1)));
    }
  }
  throw last;
}

/* ===== البحث عن الخادم على الشبكة ===== */
async function probe(base, ms) {
  const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), ms || 1500);
  try { const r = await fetch(base + '/api/hello', { signal: ctl.signal }); const j = await r.json(); clearTimeout(to); return j && j.app === 'inspect-server' ? { base, name: j.name } : null; }
  catch (e) { clearTimeout(to); return null; }
}
function normBase(v) {
  v = String(v || '').trim().replace(/\/+$/, '').replace(/\/api$/, ''); if (!v) return '';
  if (!/^https?:\/\//.test(v)) v = 'http://' + v;
  if (!/:\d+$/.test(v.replace(/^https?:\/\//, ''))) v += ':' + SERVER_PORT;
  return v;
}
async function discover() {
  CN.state = 'searching'; CN.found = []; CN.msg = ''; rerenderConn();
  const seen = new Set(); const add = x => { if (x && !seen.has(x.base)) { seen.add(x.base); CN.found.push(x); rerenderConn(); } };
  const first = [];
  if (location.protocol === 'http:' && location.port === String(SERVER_PORT)) first.push(location.origin);
  if (S.settings.server) first.push(S.settings.server);
  for (const b of first) add(await probe(b, 1500));
  let ip = '';
  try { if (bridge() && bridge().wifiIp) ip = bridge().wifiIp(); } catch (e) {}
  if (/^\d+\.\d+\.\d+\.\d+$/.test(ip) && ip !== '0.0.0.0') {
    const pre = ip.split('.').slice(0, 3).join('.'); const hosts = [];
    for (let i = 1; i < 255; i++) hosts.push(`http://${pre}.${i}:${SERVER_PORT}`);
    let k = 0; const worker = async () => { while (k < hosts.length) add(await probe(hosts[k++], 900)); };
    await Promise.all(Array.from({ length: 48 }, worker));
  } else if (!CN.found.length && !isPC()) CN.msg = 'لم يُعثر على الخادم تلقائياً. اكتب عنوانه الظاهر في لوحة المشرف.';
  CN.state = S.settings.token ? 'on' : 'off';
  if (!CN.found.length && !CN.msg) CN.msg = 'لم يُعثر على خادم الإدارة. تأكد أن الهاتف متصل بـ Wi-Fi الإدارة وأن الخادم يعمل.';
  rerenderConn();
}

/* ===== طلب الاتصال وانتظار الاعتماد ===== */
async function requestConn(base) {
  base = normBase(base); if (!base) return toast('اكتب عنوان الخادم');
  CN.base = base; CN.msg = '';
  try {
    const j = await api('requestAccess', { deviceId: deviceId(), deviceName: deviceName(), inspectorName: me() ? me().name : '', inspectorId: S.session || '', role: me() ? me().role : '' }, { base, tries: 1, timeout: 8000 });
    CN.requestId = j.requestId; CN.state = 'pending'; rerenderConn(); waitApproval();
  } catch (e) { CN.state = 'off'; CN.msg = e.message; rerenderConn(); }
}
function waitApproval() {
  clearTimeout(CN.poll);
  CN.poll = setTimeout(async () => {
    if (CN.state !== 'pending') return;
    let j; try { j = await api('accessStatus', { deviceId: deviceId(), requestId: CN.requestId }, { base: CN.base, tries: 1, timeout: 8000 }); }
    catch (e) { return waitApproval(); }
    if (j.status === 'approved' && j.token) {
      S.settings.server = CN.base; S.settings.syncUrl = CN.base + '/api'; S.settings.token = j.token; S.settings.identifiedAs = '';
      if ((S.sync || {}).server !== CN.base) S.sync = { rev: 0, hash: '', dirty: false, since: {}, lastOk: 0, err: '', server: CN.base };
      CN.state = 'on'; await save(); if (!isPC()) toast('اعتمد المشرف الاتصال'); SY.fails = 0; await syncAll(true); rerenderConn();
    } else if (j.status === 'pending') waitApproval();
    else { CN.state = j.status === 'rejected' ? 'rejected' : 'off'; CN.msg = j.status === 'rejected' ? 'رفض المشرف طلب الاتصال' : 'انتهت مهلة الطلب، أعد المحاولة'; rerenderConn(); }
  }, 2000);
}
async function endConn() {
  try { await api('endSession', {}, { tries: 1, timeout: 5000 }); } catch (e) {}
  S.settings.token = ''; CN.state = 'off'; await save(); toast('تم إنهاء الاتصال بالإدارة'); rerenderConn();
}
function sessionLost() {
  if (!S.settings.token) return;
  S.settings.token = ''; CN.state = 'off'; save();
  if (isPC()) { setTimeout(() => requestConn(location.origin), 500); return; }
  toast('انتهى الاتصال بالإدارة. اطلب اتصالاً جديداً عند الحاجة'); rerenderConn();
}

/* ===== المزامنة (نفس منطق الإصدار السابق) ===== */
const syS = () => (S.sync = S.sync || { rev: 0, hash: '', dirty: false, since: {}, lastOk: 0, err: '' });
const cfgOf = () => ({ lists: S.lists, places: S.places, users: S.users, facilities: S.facilities || [], facDeleted: !!S.facDeleted,
  facility: S.settings.facility || '', heroImg: S.settings.heroImg || '', inspDeleted: S.inspDeleted || [] });
function hashStr(s) { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return h + ':' + s.length; }
const cfgHash = () => hashStr(JSON.stringify(cfgOf()));

const _dbSet = DB.set.bind(DB);
DB.set = function (k, v) {
  const r = _dbSet(k, v);
  if (k === 'state') clearTimeout(SY.timer), SY.timer = setTimeout(cfgCheck, 1500);
  return r;
};
function cfgCheck() {
  if (!S || !S.settings.token || !isSup()) return;
  const y = syS();
  if (cfgHash() !== y.hash) { y.dirty = true; syncAll(true); }
}
function applyLink() { if (/#sync=/.test(location.hash)) history.replaceState(null, '', location.pathname + location.search); return false; }

async function applyConfig(c) {
  if (c.lists) S.lists = c.lists; if (c.places) S.places = c.places; if (c.users) S.users = c.users;
  S.facilities = c.facilities || []; S.facDeleted = !!c.facDeleted;
  if (c.facility) S.settings.facility = c.facility;
  if (c.heroImg) S.settings.heroImg = c.heroImg; else delete S.settings.heroImg;
  S.inspDeleted = c.inspDeleted || [];
  S.inspections = S.inspections.filter(i => !S.inspDeleted.includes(i.id));
  if (S.session && !S.users.some(u => u.id === S.session)) { S.session = null; V.view = 'login'; }
}
async function syncCfg(force, pl) {
  /* المشرف يرفع الإعدادات (المنشآت والتعيينات والقوائم) من كمبيوتر الإدارة أو من تطبيقه على الهاتف */
  const y = syS(); const r = pl; const canPush = isSup();
  const localChanged = y.dirty || (canPush && cfgHash() !== y.hash);
  /* الرفع يحمل رقم الإصدار الذي بُني عليه؛ إن كان الخادم أحدث يرفض (CONFLICT) فنسحب بدل الكتابة فوقه */
  const push = async base => { const h = cfgHash(); const j = await api('saveConfig', { config: cfgOf(), baseRev: base }); y.rev = j.rev; y.hash = h; y.dirty = false; };
  const pull = async () => {
    if (!r.rev) return false;
    const j = await api('getConfig'); if (!j.config) return false;
    await applyConfig(j.config); y.rev = j.rev; y.hash = cfgHash(); y.dirty = false; return true;
  };
  /* إعدادات مستوردة على كمبيوتر الإدارة (نقل من النظام القديم أو استيراد نسخة): لا تُسحب فوقها،
     وتُرفع للخادم مرة واحدة عند دخول المشرف فتصبح هي المرجع */
  if (isPC() && S.settings.forcePush) {
    if (canPush) { await push(r.rev); delete S.settings.forcePush; toast('رُفعت الإعدادات المستوردة إلى خادم الإدارة'); }
    return false;
  }
  if (force === 'push') { if (canPush) await push(r.rev); return false; }
  if (force === 'pull' || (r.rev > y.rev && !(canPush && y.rev > 0 && localChanged))) return pull();
  try {
    if (canPush && r.rev === 0) { await push(0); return false; }
    if (canPush && localChanged && y.rev > 0) await push(y.rev);
  } catch (e) {
    if (e.code !== 'CONFLICT') throw e;
    toast('الإعدادات على الخادم أحدث من هذا الجهاز، تم سحبها'); return pull();
  }
  return false;
}
async function syncInsp(pl) {
  const y = syS(); let pushed = 0, got = 0;
  if (!S.session) return { pushed, got };
  for (const i of S.inspections.filter(x => x.status === 'done' && !x.synced && (isPC() || x.inspectorId === S.session))) {
    await api('saveInspection', { inspection: i }); i.synced = true; pushed++; await save();
  }
  const key = isSup() ? 'all' : S.session;
  y.seen = y.seen || {}; if (pl && pl.lastInsp !== undefined && pl.lastInsp === y.seen[key]) return { pushed, got };
  let since = y.since[key] || 0, more = true, guard = 0;
  while (more && guard++ < 50) {
    const j = await api('getInspections', { since, inspectorId: isSup() ? '' : S.session });
    for (const it of j.items || []) {
      if ((S.inspDeleted || []).includes(it.id)) continue;
      it.synced = true; const k = S.inspections.findIndex(x => x.id === it.id);
      if (k < 0) { S.inspections.push(it); got++; }
      else if (it.status === 'done' && V.cur !== it.id && !S.inspections[k].reopened &&
        (S.inspections[k].status !== 'done' || (it.finishedAt || 0) > (S.inspections[k].finishedAt || 0))) { S.inspections[k] = it; got++; }
    }
    since = j.next || since; more = !!j.more;
  }
  y.since[key] = since; if (pl && pl.lastInsp !== undefined) y.seen[key] = pl.lastInsp; return { pushed, got };
}

const SAFE_VIEWS = ['home', 'inspections', 'admin', 'login', 'lists', 'facs', 'users', 'settings'];
function safeRender() {
  if (!SAFE_VIEWS.includes(V.view) || V.editUser || V.editPlace) return;
  if (V.view === 'login' && ($('#lp') || {}).value) return;
  render();
}
function rerenderConn() { if (['login', 'home', 'settings'].includes(V.view) && !($('#lp') || {}).value && !(document.activeElement && document.activeElement.id === 'cn_addr')) render(); }

async function syncAll(silent, force) {
  if (!S || !S.settings.token) { if (!silent) toast('غير متصل بالإدارة'); return; }
  if (SY.busy) return; SY.busy = true; const y = syS(); let changed = false, info = null;
  const sig = () => `${y.rev}|${y.hash}|${y.dirty}|${JSON.stringify(y.since)}|${JSON.stringify(y.seen || {})}`; const before = sig(); let pushedAny = false;
  try {
    if (S.session && me() && S.settings.identifiedAs !== S.session && !isPC()) {
      await api('identify', { inspectorId: S.session, inspectorName: me().name }); S.settings.identifiedAs = S.session;
    }
    const pl = await api('poll');
    changed = await syncCfg(force, pl); info = await syncInsp(pl); changed = changed || info.got > 0; pushedAny = info.pushed > 0;
    y.lastOk = Date.now(); y.err = ''; SY.fails = 0;
    if (!silent) toast(force === 'push' ? 'تم رفع الإعدادات' : force === 'pull' ? 'تم سحب الإعدادات' : 'اكتملت المزامنة');
  } catch (e) { SY.fails++; y.err = e.message; if (!silent && e.code !== 'SESSION') toast('تعذرت المزامنة: ' + e.message); }
  SY.busy = false;
  if (changed || pushedAny || sig() !== before) await save();
  if (changed) safeRender();
  if (!silent && V.view === 'settings') render();
  scheduleSync();
}
/* كل 30 ثانية أثناء الاتصال (تُبقي الجلسة حيّة)، وتتباعد عند تكرار الفشل */
function scheduleSync() {
  clearTimeout(SY.next); if (!S || !S.settings.token) return;
  const d = SY.fails ? Math.min(300000, 30000 * Math.pow(2, SY.fails - 1)) : 30000;
  SY.next = setTimeout(() => { if (S && S.settings.token) syncAll(true); }, d);
}

async function autoSync() {
  applyLink(); dropGoogle();
  if (isPC() && !S.settings.token) return requestConn(location.origin);
  await syncAll(true);
}
async function syncInspections(silent) { await syncAll(silent); }
async function pushConfig() { await syncAll(false, 'push'); }
async function pullConfig() { if (confirm('سحب الإعدادات من خادم الإدارة سيستبدل الإعدادات الحالية في هذا الجهاز. متابعة؟')) await syncAll(false, 'pull'); }

window.addEventListener('online', () => { SY.fails = 0; syncAll(true); });
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && S) { SY.fails = 0; syncAll(true); } });

/* ===== بطاقة الاتصال بالإدارة (في شاشة الدخول والرئيسية والإعدادات) ===== */
function connCard() {
  if (isPC()) {
    const y = syS(); const on = !!S.settings.token;
    return `<div class="card"><h3>خادم الإدارة</h3><p class="mut" style="margin:0">${on ? 'هذا الجهاز هو كمبيوتر الإدارة ومتصل بالخادم.' : 'جارٍ الاتصال بالخادم…'}
      ${y.lastOk ? ' آخر مزامنة: ' + esc(new Date(y.lastOk).toLocaleTimeString('ar-EG')) : ''}</p>
      <p class="mut" style="margin:6px 0 0">اعتماد هواتف المفتشين من <a href="/admin" target="_blank">لوحة المشرف</a>.</p></div>`;
  }
  const pending = S.inspections.filter(i => i.status === 'done' && !i.synced && i.inspectorId === S.session).length;
  const st = S.settings.token ? 'on' : CN.state;
  let body = '';
  if (st === 'on') {
    const y = syS();
    body = `<p style="margin:0;color:var(--ok);font-weight:700">● متصل بالإدارة</p>
      <p class="mut" style="margin:4px 0">${S.session ? `بانتظار الرفع: ${pending} تفتيش · ` : ''}آخر مزامنة: ${y.lastOk ? esc(new Date(y.lastOk).toLocaleTimeString('ar-EG')) : 'لم تتم بعد'}</p>
      ${SY.fails && y.err ? `<p class="mut" style="color:var(--bad);margin:4px 0">${esc(y.err)}</p>` : ''}
      <div class="row"><button class="btn sm" data-act="sync">مزامنة الآن</button><button class="btn sec sm" data-act="cn_end">إنهاء الاتصال</button></div>`;
  } else if (st === 'pending') {
    body = `<p style="margin:0;font-weight:700">⏳ بانتظار اعتماد المشرف…</p><p class="mut" style="margin:4px 0">اطلب من المشرف اعتماد هذا الهاتف من لوحة المشرف.</p>
      <button class="btn sec sm" data-act="cn_cancel">إلغاء</button>`;
  } else if (st === 'searching') {
    body = `<p style="margin:0">جارٍ البحث عن خادم الإدارة على الشبكة…</p>${CN.found.map(f => `<div class="listrow"><div class="sp"><b>${esc(f.name)}</b><div class="mut">${esc(f.base.replace(/^https?:\/\//, ''))}</div></div><button class="btn sm" data-act="cn_req" data-b="${esc(f.base)}">طلب اتصال</button></div>`).join('')}`;
  } else {
    body = `<p class="mut" style="margin:0 0 8px">${S.session ? 'غير متصل. تفتيشاتك محفوظة على هذا الهاتف، وتُرفع عند الاتصال بشبكة الإدارة.' : 'اتصل بشبكة Wi-Fi الإدارة ثم ابحث عن الخادم واطلب الاتصال.'}${S.session && pending ? ` (بانتظار الرفع: ${pending})` : ''}</p>
      ${CN.msg ? `<p class="mut" style="color:var(--bad);margin:0 0 8px">${esc(CN.msg)}</p>` : ''}
      ${CN.found.map(f => `<div class="listrow"><div class="sp"><b>${esc(f.name)}</b><div class="mut">${esc(f.base.replace(/^https?:\/\//, ''))}</div></div><button class="btn sm" data-act="cn_req" data-b="${esc(f.base)}">طلب اتصال</button></div>`).join('')}
      <button class="btn block" data-act="cn_find">البحث عن خادم الإدارة</button>
      <details style="margin-top:8px"><summary class="mut">إدخال العنوان يدوياً</summary><div class="row" style="margin-top:6px">
      <input type="text" id="cn_addr" placeholder="192.168.1.10" value="${esc((S.settings.server || '').replace(/^https?:\/\//, '').replace(':' + SERVER_PORT, ''))}" style="flex:1" inputmode="decimal">
      <button class="btn sm" data-act="cn_req_manual">طلب اتصال</button></div></details>`;
  }
  return `<div class="card"><h3>الاتصال بالإدارة</h3>${body}</div>`;
}

/* شاشة الدخول: بطاقة الاتصال أسفلها (لهاتف جديد لم يستلم المستخدمين بعد) */
const _viewLogin = viewLogin;
viewLogin = function () { return _viewLogin() + `<div class="wrap" style="padding-top:0">${connCard()}</div>`; };

viewSettings = function () {
  return bar('الإعدادات والاتصال', 'admin') + `<div class="wrap"><div class="card"><label class="f">اسم المنشأة (يظهر في الترويسة)</label><input type="text" id="s_fac" value="${esc(S.settings.facility)}">
  <button class="btn block" style="margin-top:12px" data-act="savesettings">حفظ</button></div>
  ${connCard()}
  ${isSup() ? `<div class="card"><h3>نقل البيانات</h3><div class="row"><button class="btn sec sm" data-act="pushcfg">رفع الإعدادات للخادم</button><button class="btn sec sm" data-act="pullcfg">سحب الإعدادات من الخادم</button></div></div>` : ''}
  <div class="card"><h3>نسخة احتياطية</h3><div class="row"><button class="btn sec" data-act="export">تصدير ملف</button><label class="btn sec" style="cursor:pointer">استيراد ملف<input type="file" accept=".json" hidden id="imp"></label></div></div></div>`;
};

document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act]'); if (!t) return; const a = t.dataset.act;
  if (a === 'cn_find') discover();
  else if (a === 'cn_req') requestConn(t.dataset.b);
  else if (a === 'cn_req_manual') requestConn(($('#cn_addr') || {}).value);
  else if (a === 'cn_end') { if (confirm('إنهاء الاتصال بالإدارة؟ ستحتاج إلى اعتماد جديد للاتصال مرة أخرى.')) endConn(); }
  else if (a === 'cn_cancel') { CN.state = 'off'; clearTimeout(CN.poll); rerenderConn(); }
  else if (a === 'savesettings') { S.settings.facility = ($('#s_fac') || {}).value || S.settings.facility; await save(); }
});

/* حذف التفتيش من كل الأجهزة عبر علامة حذف تنتقل مع الإعدادات */
function tombstone(ids) { S.inspDeleted = [...new Set([...(S.inspDeleted || []), ...ids])]; }
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act="delinsp"],[data-act="delbatch"],[data-act="delids"]'); if (!t) return;
  e.stopImmediatePropagation();
  const where = S.settings.token ? 'من كل الأجهزة' : 'من هذا الجهاز';
  if (!confirm(`حذف هذا التفتيش نهائياً ${where}؟`)) return;
  const d = t.dataset;
  const ids = (d.ids || '').split(',');
  const gone = S.inspections.filter(i => t.dataset.act === 'delinsp' ? i.id === d.id : t.dataset.act === 'delids' ? ids.includes(i.id) : (i.batchId || i.id) === d.b).map(i => i.id);
  tombstone(gone); S.inspections = S.inspections.filter(i => !gone.includes(i.id)); await save(); render();
}, true);

/* ===== داخل تطبيق Android: حفظ الملفات والطباعة عبر الهاتف ===== */
if (window.AndroidBridge) {
  const _click = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && /^blob:/.test(this.href)) {
      const name = this.download;
      fetch(this.href).then(r => r.blob()).then(b => new Promise(res => { const fr = new FileReader(); fr.onload = () => res([fr.result, b.type]); fr.readAsDataURL(b); }))
        .then(([d, type]) => AndroidBridge.saveFile(name, String(d).split(',')[1], type || 'application/octet-stream'));
      return;
    }
    return _click.call(this);
  };
  window.print = () => AndroidBridge.print(document.title || 'تقرير التفتيش');
  if (navigator.canShare) navigator.canShare = () => false; // المشاركة عبر التطبيقات معطلة: الحفظ في التنزيلات بدلاً منها
}
