/* مزامنة الأجهزة عبر Google Apps Script
   - المشرف: يرفع الإعدادات (منشآت، تعيينات، قوائم، مستخدمون) عند أي تعديل، ويستلم التفتيشات المنتهية من كل المفتشين.
   - المفتش: يسحب الإعدادات تلقائياً، ويرفع تفتيشاته المنتهية. */
const SY = { busy: false, timer: null, fails: 0, next: null };
/* اتصال متين بالخادم: مهلة وإعادة محاولة تلقائية عند الانقطاع أو الازدحام */
async function api(action, payload, opt) {
  opt = opt || {}; const tries = opt.tries || 3; let last;
  for (let n = 0; n < tries; n++) {
    const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), opt.timeout || 30000);
    try {
      const r = await fetch(S.settings.syncUrl, { method: 'POST', body: JSON.stringify({ action, token: S.settings.token, ...payload }), signal: ctl.signal, redirect: 'follow' });
      const txt = await r.text(); clearTimeout(to); let j;
      try { j = JSON.parse(txt); } catch (e) { throw new Error('رد غير متوقع من الخادم، تأكد أن النشر بصلاحية "أي شخص"'); }
      if (!j.ok) { const er = new Error(j.error || 'خطأ'); er.fatal = !/busy|مشغول|Lock|timed out/i.test(j.error || ''); throw er; }
      return j;
    } catch (e) {
      clearTimeout(to);
      last = e.name === 'AbortError' ? new Error('انتهت مهلة الاتصال') : (e instanceof TypeError ? new Error('تعذر الوصول إلى الخادم، تحقق من الإنترنت') : e);
      if (last.fatal) throw last;
      if (n < tries - 1) await new Promise(res => setTimeout(res, 1500 * (n + 1) * (n + 1)));
    }
  }
  throw last;
}
const syS = () => (S.sync = S.sync || { rev: 0, hash: '', dirty: false, since: {}, lastOk: 0, err: '' });
const cfgOf = () => ({ lists: S.lists, places: S.places, users: S.users, facilities: S.facilities || [], facDeleted: !!S.facDeleted,
  facility: S.settings.facility || '', heroImg: S.settings.heroImg || '', inspDeleted: S.inspDeleted || [] });
function hashStr(s) { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return h + ':' + s.length; }
const cfgHash = () => hashStr(JSON.stringify(cfgOf()));

/* مراقبة تعديلات المشرف على الإعدادات ثم رفعها بعد لحظات */
const _dbSet = DB.set.bind(DB);
DB.set = function (k, v) {
  const r = _dbSet(k, v);
  if (k === 'state') clearTimeout(SY.timer), SY.timer = setTimeout(cfgCheck, 1500);
  return r;
};
function cfgCheck() {
  if (!S || !S.settings || !S.settings.syncUrl || !isSup()) return;
  const y = syS();
  if (cfgHash() !== y.hash) { y.dirty = true; syncAll(true); }
}

/* رابط ربط جهاز جديد */
function linkOf() {
  return location.origin + location.pathname + '#sync=' + encodeURIComponent(btoa(JSON.stringify({ u: S.settings.syncUrl, t: S.settings.token })));
}
function applyLink() {
  const m = /#sync=([^&]+)/.exec(location.hash); if (!m || !S) return false;
  try {
    const o = JSON.parse(atob(decodeURIComponent(m[1])));
    if (!/^https:\/\/script\.google\.com\//.test(o.u || '') || !o.t) throw new Error('bad');
    if (S.settings.syncUrl !== o.u) S.sync = { rev: 0, hash: '', dirty: false, since: {}, lastOk: 0, err: '' };
    S.settings.syncUrl = o.u; S.settings.token = o.t; save();
    toast('تم ربط هذا الجهاز بالمزامنة');
  } catch (e) { toast('رابط الربط غير صالح'); }
  history.replaceState(null, '', location.pathname + location.search);
  return true;
}

async function applyConfig(c) {
  if (c.lists) S.lists = c.lists; if (c.places) S.places = c.places; if (c.users) S.users = c.users;
  S.facilities = c.facilities || []; S.facDeleted = !!c.facDeleted;
  if (c.facility) S.settings.facility = c.facility;
  if (c.heroImg) S.settings.heroImg = c.heroImg; else delete S.settings.heroImg;
  S.inspDeleted = c.inspDeleted || [];
  S.inspections = S.inspections.filter(i => !S.inspDeleted.includes(i.id));
  if (S.session && !S.users.some(u => u.id === S.session)) { S.session = null; V.view = 'login'; }
}

/* الإعدادات: ترجع true إن تغيّر شيء محلياً */
async function syncCfg(force, pl) {
  const y = syS(); const r = pl;
  const localChanged = y.dirty || (isSup() && cfgHash() !== y.hash);
  const push = async () => { const h = cfgHash(); const j = await api('saveConfig', { config: cfgOf() }); y.rev = j.rev; y.hash = h; y.dirty = false; };
  if (force === 'push') { await push(); return false; }
  if (force === 'pull' || (r.rev > y.rev && !(y.rev > 0 && localChanged))) {
    if (!r.rev) return false;
    const j = await api('getConfig'); if (!j.config) return false;
    await applyConfig(j.config); y.rev = j.rev; y.hash = cfgHash(); y.dirty = false; return true;
  }
  if (isSup() && r.rev === 0) { await push(); return false; }
  if (localChanged && y.rev > 0) { await push(); }
  return false;
}

/* التفتيشات: رفع المنتهية وسحب الواردة */
async function syncInsp(pl) {
  const y = syS(); let pushed = 0, got = 0;
  for (const i of S.inspections.filter(x => x.status === 'done' && !x.synced)) { await api('saveInspection', { inspection: i }); i.synced = true; pushed++; await save(); }
  const key = isSup() ? 'all' : (S.session || ''); if (!key) return { pushed, got };
  y.seen = y.seen || {}; if (pl && pl.lastInsp !== undefined && pl.lastInsp === y.seen[key]) return { pushed, got };
  let since = y.since[key] || 0, more = true, guard = 0;
  while (more && guard++ < 50) {
    const j = await api('getInspections', { since, inspectorId: isSup() ? '' : S.session });
    for (const it of j.items || []) {
      if ((S.inspDeleted || []).includes(it.id)) continue;
      it.synced = true; const k = S.inspections.findIndex(x => x.id === it.id);
      if (k < 0) { S.inspections.push(it); got++; }
      else if (S.inspections[k].status !== 'done' && it.status === 'done' && V.cur !== it.id) { S.inspections[k] = it; got++; }
    }
    since = j.next || since; more = !!j.more;
  }
  y.since[key] = since; if (pl && pl.lastInsp !== undefined) y.seen[key] = pl.lastInsp; return { pushed, got };
}

const SAFE_VIEWS = ['home', 'inspections', 'admin', 'login', 'lists', 'facs', 'users'];
function safeRender() {
  if (!SAFE_VIEWS.includes(V.view) || V.editUser || V.editPlace) return;
  if (V.view === 'login' && ($('#lp') || {}).value) return;
  render();
}

async function syncAll(silent, force) {
  if (!S || !S.settings.syncUrl) { if (!silent) toast('المزامنة غير مفعّلة'); return; }
  if (!navigator.onLine) { SY.fails++; if (!silent) toast('لا يوجد اتصال بالإنترنت'); return; }
  if (SY.busy) return; SY.busy = true; const y = syS(); let changed = false, info = null;
  const sig = () => `${y.rev}|${y.hash}|${y.dirty}|${JSON.stringify(y.since)}|${JSON.stringify(y.seen || {})}`; const before = sig(); let pushedAny = false;
  try {
    const pl = await api('poll');
    changed = await syncCfg(force, pl); info = await syncInsp(pl); changed = changed || info.got > 0; pushedAny = info.pushed > 0;
    y.lastOk = Date.now(); y.err = ''; SY.fails = 0;
    if (!silent) toast(force === 'push' ? 'تم رفع الإعدادات' : force === 'pull' ? 'تم سحب الإعدادات' : 'اكتملت المزامنة');
  } catch (e) { SY.fails++; y.err = e.message; if (!silent) toast('تعذرت المزامنة: ' + e.message); }
  SY.busy = false;
  if (changed || pushedAny || sig() !== before) await save();
  if (changed) safeRender();
  if (!silent && V.view === 'settings') render();
  scheduleSync();
}
/* جدولة المزامنة: كل دقيقة، وتتباعد تدريجياً (حتى 5 دقائق) عند تكرار الفشل */
function scheduleSync() {
  clearTimeout(SY.next); const d = SY.fails ? Math.min(300000, 60000 * Math.pow(2, SY.fails - 1)) : 60000;
  SY.next = setTimeout(() => { if (document.visibilityState === 'visible' && S) syncAll(true); else scheduleSync(); }, d);
}

/* إعادة تعريف دوال المزامنة القديمة */
async function autoSync() { applyLink(); await syncAll(true); }
async function syncInspections(silent) { await syncAll(silent); }
async function pushConfig() { await syncAll(false, 'push'); }
async function pullConfig() { if (confirm('سحب الإعدادات من السحابة سيستبدل الإعدادات الحالية في هذا الجهاز. متابعة؟')) await syncAll(false, 'pull'); }

scheduleSync();
window.addEventListener('online', () => { SY.fails = 0; syncAll(true); });
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && S) { SY.fails = 0; syncAll(true); } });

/* شاشة المزامنة في الإعدادات */
viewSettings = function () {
  const y = syS(); const on = !!S.settings.syncUrl; const pending = S.inspections.filter(i => i.status === 'done' && !i.synced).length;
  const t = y.lastOk ? new Date(y.lastOk).toLocaleString('ar-EG') : 'لم تتم بعد';
  return bar('الإعدادات والمزامنة', 'admin') + `<div class="wrap"><div class="card"><label class="f">اسم المنشأة (يظهر في الترويسة)</label><input type="text" id="s_fac" value="${esc(S.settings.facility)}">
  <label class="f" style="margin-top:10px">رابط المزامنة (Google Apps Script)</label><input type="url" id="s_url" value="${esc(S.settings.syncUrl)}" placeholder="https://script.google.com/macros/s/.../exec">
  <label class="f" style="margin-top:10px">مفتاح الربط السري</label><input type="text" id="s_tok" value="${esc(S.settings.token)}">
  <button class="btn block" style="margin-top:12px" data-act="savesettings">حفظ الإعدادات</button></div>
  <div class="card"><h3>حالة المزامنة بين الأجهزة</h3>
  <p class="mut" style="margin:0">${on ? 'المزامنة مفعّلة' : 'المزامنة غير مفعّلة. أدخل الرابط والمفتاح واحفظ.'}</p>
  ${on ? `<p class="mut" style="margin:4px 0">آخر مزامنة ناجحة: ${esc(t)}</p><p class="mut" style="margin:4px 0">تفتيشات بانتظار الرفع: ${pending}</p>${SY.fails ? `<p class="mut" style="margin:4px 0;color:var(--bad)">الاتصال متقطع حالياً، ستُعاد المحاولة تلقائياً. بياناتك محفوظة على الجهاز ولن تضيع.${y.err ? ' (' + esc(y.err) + ')' : ''}</p>` : ''}
  <div class="row" style="margin-top:8px"><button class="btn sm" data-act="sync">مزامنة الآن</button><button class="btn sec sm" data-act="pushcfg">رفع الإعدادات</button><button class="btn sec sm" data-act="pullcfg">سحب الإعدادات</button></div>` : ''}</div>
  ${on ? `<div class="card"><h3>ربط جهاز جديد</h3><p class="mut" style="margin:0 0 8px">أرسل هذا الرابط إلى المفتش مرة واحدة. يفتحه على هاتفه فيرتبط تلقائياً، ثم يدخل برمز التحقق. الرابط يحوي مفتاح الربط فلا تنشره علناً.</p>
  <div class="row"><button class="btn sm" data-act="copylink">نسخ الرابط</button><button class="btn sec sm" data-act="sharelink">مشاركة</button></div></div>` : ''}
  <div class="card"><h3>نسخة احتياطية</h3><div class="row"><button class="btn sec" data-act="export">تصدير ملف</button><label class="btn sec" style="cursor:pointer">استيراد ملف<input type="file" accept=".json" hidden id="imp"></label></div></div></div>`;
};

document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act]'); if (!t) return; const a = t.dataset.act;
  if (a === 'copylink' || a === 'sharelink') {
    const l = linkOf();
    if (a === 'sharelink' && navigator.share) { try { await navigator.share({ title: 'ربط جهاز بالمزامنة', url: l }); } catch (x) {} return; }
    try { await navigator.clipboard.writeText(l); toast('تم نسخ الرابط'); } catch (x) { prompt('انسخ الرابط:', l); }
  }
  if (a === 'savesettings') setTimeout(() => syncAll(false), 500);
});

/* حذف التفتيش من كل الأجهزة عبر علامة حذف تنتقل مع الإعدادات */
function tombstone(ids) { S.inspDeleted = [...new Set([...(S.inspDeleted || []), ...ids])]; }
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act="delinsp"],[data-act="delbatch"]'); if (!t) return;
  e.stopImmediatePropagation();
  const where = S.settings.syncUrl ? 'من كل الأجهزة' : 'من هذا الجهاز';
  if (!confirm(`حذف هذا التفتيش نهائياً ${where}؟`)) return;
  const d = t.dataset;
  const gone = S.inspections.filter(i => t.dataset.act === 'delinsp' ? i.id === d.id : (i.batchId || i.id) === d.b).map(i => i.id);
  tombstone(gone); S.inspections = S.inspections.filter(i => !gone.includes(i.id)); await save(); render();
}, true);
