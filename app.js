'use strict';
/* ===== أدوات عامة ===== */
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const uid = p => p + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const clone = o => JSON.parse(JSON.stringify(o));
const toast = m => { const t = $('#toast'); t.textContent = m; t.classList.add('show'); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2400); };
const pad = n => String(n).padStart(2, '0');
const nowParts = () => { const d = new Date(); return { date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`, time: `${pad(d.getHours())}:${pad(d.getMinutes())}` }; };

/* ===== تخزين محلي (IndexedDB) يعمل بدون إنترنت ===== */
const DB = {
  db: null,
  open() { return new Promise((res, rej) => { const r = indexedDB.open('inspect-app', 1); r.onupgradeneeded = () => r.result.createObjectStore('kv'); r.onsuccess = () => { DB.db = r.result; res(); }; r.onerror = () => rej(r.error); }); },
  get(k) { return new Promise(res => { const q = DB.db.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result); q.onerror = () => res(undefined); }); },
  set(k, v) { return new Promise(res => { const t = DB.db.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, k); t.oncomplete = res; t.onerror = res; }); }
};

/* ===== محرك التقييم (نفس منهجية المشروع) ===== */
const W = { c: 3, e: 2, s: 1 };
const CLS_NAME = { c: 'حرج', e: 'أساسي', s: 'قياسي' };
const OPTS = { c: ['م', 'ف'], e: ['م', 'ت', 'ف', 'غ'], s: ['م', 'ت', 'ف'] };
const VAL = { 'م': 1, 'ت': 0.5, 'ف': 0 };
const BANDS = [[90, 'ممتاز', 'ok'], [80, 'جيد جداً', 'ok'], [70, 'جيد', 'warn'], [0, 'دون المستوى', 'bad']];

function compute(snap, answers, esc_) {
  const axes = []; let sumW = 0, acc = 0, critFails = [], answered = 0, total = 0;
  for (const a of snap.axes) {
    let earned = 0, max = 0;
    for (const it of a.items) {
      total++;
      const ans = answers[it.id]; if (!ans || !ans.v) continue; answered++;
      if (ans.v === 'غ') continue;
      max += W[it.cls]; earned += W[it.cls] * VAL[ans.v];
      if (it.cls === 'c' && ans.v === 'ف') critFails.push({ axis: a.name, text: it.text });
    }
    const pct = max ? earned / max * 100 : null;
    axes.push({ id: a.id, name: a.name, weight: a.weight, pct, earned, max });
    if (pct !== null) { acc += pct * a.weight; sumW += a.weight; }
  }
  const score = sumW ? acc / sumW : 0; // تُعاد معايرة الأوزان تلقائياً إن استُبعد محور كاملاً بـ"غ"
  const escHits = (snap.escalation || []).filter((_, i) => esc_ && esc_[i]);
  const band = BANDS.find(b => score >= b[0]);
  return { axes, score: Math.round(score * 10) / 10, critFails, escHits, veto: critFails.length > 0 || escHits.length > 0, band: band[1], bandCls: band[2], answered, total };
}

/* ===== الحالة ===== */
let S = null;          // البيانات الدائمة
let V = { view: 'login' }; // حالة العرض المؤقتة
const save = () => DB.set('state', S);
const me = () => S.users.find(u => u.id === S.session);
const isSup = () => me() && me().role === 'supervisor';

async function init() {
  await DB.open();
  S = await DB.get('state');
  if (!S) { S = { ...clone(SEED), inspections: [], session: null, seedVersion: SEED.version }; await save(); }
  if (S.seedVersion !== SEED.version) { // تحديث قوائم المنشأة المضمّنة دون المساس بالتفتيشات المحفوظة
    SEED.lists.forEach(l => { const k = S.lists.findIndex(x => x.id === l.id); if (k >= 0) S.lists[k] = clone(l); else S.lists.push(clone(l)); });
    S.places = S.places.filter(p => p.id !== 'P1');
    SEED.places.forEach(p => { if (!S.places.some(x => x.id === p.id)) S.places.push(clone(p)); });
    S.seedVersion = SEED.version; await save();
  }
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
  V.view = S.session && me() ? 'home' : 'login';
  render();
  window.addEventListener('online', () => autoSync());
  autoSync();
}

/* ===== العرض ===== */
const app = () => $('#app');
function bar(title, back) {
  return `<div class="bar">${back ? `<button data-act="go" data-v="${back}">رجوع</button>` : ''}<h1>${esc(title)}</h1>${me() ? `<button data-act="logout">خروج</button>` : ''}</div>`;
}
function nav() {
  if (!me()) return '';
  const t = [['home', '🏠', 'الرئيسية'], ['inspections', '📋', 'التفتيشات']];
  if (isSup()) t.push(['admin', '⚙️', 'الإدارة']);
  return `<div class="nav">${t.map(([v, i, l]) => `<button class="${V.tab === v ? 'on' : ''}" data-act="tab" data-v="${v}"><b>${i}</b>${l}</button>`).join('')}</div>`;
}
function render() {
  const v = V.view;
  let h = '';
  if (v === 'login') h = viewLogin();
  else if (v === 'home') { V.tab = 'home'; h = viewHome(); }
  else if (v === 'inspections') { V.tab = 'inspections'; h = viewInspections(); }
  else if (v === 'admin') { V.tab = 'admin'; h = viewAdmin(); }
  else if (v === 'new') h = viewNew();
  else if (v === 'insp') h = viewInsp();
  else if (v === 'finish') h = viewFinish();
  else if (v === 'report') h = viewReport();
  else if (v === 'lists') h = viewLists();
  else if (v === 'editlist') h = viewEditList();
  else if (v === 'places') h = viewPlaces();
  else if (v === 'users') h = viewUsers();
  else if (v === 'settings') h = viewSettings();
  const keepScroll = V.keepScroll; const y = window.scrollY;
  app().innerHTML = h + (['login', 'insp', 'finish', 'report', 'editlist'].includes(v) ? '' : nav());
  if (keepScroll) window.scrollTo(0, y); else window.scrollTo(0, 0);
  V.keepScroll = false;
  if (v === 'finish') initSig();
}

function viewLogin() {
  return `<div class="wrap" style="padding-top:12vh"><div class="card">
  <h2 style="font-size:20px">تسجيل الدخول</h2><p class="mut">قوائم التحقق والتفتيش</p>
  <label class="f">المستخدم</label><select id="lu">${S.users.map(u => `<option value="${u.id}">${esc(u.name)} (${u.role === 'supervisor' ? 'مشرف' : 'مفتش'})</option>`).join('')}</select>
  <label class="f" style="margin-top:10px">الرمز السري</label><input type="password" id="lp" inputmode="numeric" autocomplete="off">
  <button class="btn block" style="margin-top:14px" data-act="login">دخول</button></div></div>`;
}
function viewHome() {
  const drafts = S.inspections.filter(i => i.status === 'draft' && i.inspectorId === S.session);
  const pending = S.inspections.filter(i => i.status === 'done' && !i.synced).length;
  return bar(`مرحباً ${me().name}`) + `<div class="wrap">
  <button class="btn block" style="padding:18px;font-size:18px" data-act="new">＋ بدء تفتيش جديد</button>
  ${drafts.length ? `<div class="card" style="margin-top:12px"><h3>تفتيشات غير مكتملة</h3>${drafts.map(i => `<div class="listrow"><div class="sp"><b>${esc(i.header.place)}</b><div class="mut">${esc(i.header.date)} ${esc(i.header.time)}</div></div><button class="btn sm" data-act="open" data-id="${i.id}">متابعة</button></div>`).join('')}</div>` : ''}
  <div class="card" style="margin-top:12px"><h3>حالة المزامنة</h3><p class="mut">${S.settings.syncUrl ? `بانتظار الرفع: ${pending} تفتيش` : 'المزامنة غير مفعّلة، البيانات محفوظة على هذا الهاتف فقط.'}</p>
  ${S.settings.syncUrl ? `<button class="btn sec sm" data-act="sync">مزامنة الآن</button>` : ''}</div></div>`;
}
function viewInspections() {
  const list = S.inspections.filter(i => i.status === 'done' && (isSup() || i.inspectorId === S.session)).sort((a, b) => b.finishedAt - a.finishedAt);
  return bar('التفتيشات المكتملة') + `<div class="wrap">${list.length ? list.map(i => `<div class="card"><div class="row"><b class="sp">${esc(i.header.place)}</b><span class="tag ${i.result.bandCls}">${i.result.score}%</span>${i.result.veto ? '<span class="tag bad">بوابة حرجة</span>' : ''}</div>
  <div class="mut">${esc(i.header.dept)} · ${esc(i.header.date)} ${esc(i.header.time)} · ${esc(i.header.inspector)} ${i.synced ? '· تمت المزامنة' : '· لم تُرفع'}</div>
  <div class="row" style="margin-top:8px"><button class="btn sm" data-act="report" data-id="${i.id}">عرض التقرير</button>${isSup() ? `<button class="btn sm bad" data-act="delinsp" data-id="${i.id}">حذف</button>` : ''}</div></div>`).join('') : '<p class="mut">لا توجد تفتيشات مكتملة بعد.</p>'}</div>`;
}
function viewAdmin() {
  const row = (v, t, d) => `<div class="card row" data-act="go" data-v="${v}" style="cursor:pointer"><div class="sp"><b>${t}</b><div class="mut">${d}</div></div><span>‹</span></div>`;
  return bar('الإدارة') + `<div class="wrap">${row('lists', 'قوائم التحقق', 'إنشاء قوائم جديدة أو تعديل الموجودة')}${row('places', 'الأماكن والأقسام', 'عدد العاملين والمسؤول والورديات لكل مكان')}${row('users', 'المستخدمون والصلاحيات', 'المشرف والمفتشون')}${row('settings', 'الإعدادات والمزامنة', 'اسم المنشأة والنسخ الاحتياطي')}</div>`;
}

/* ===== بدء تفتيش ===== */
function viewNew() {
  const places = S.places;
  const p = places.find(x => x.id === V.newPlace) || places[0];
  V.newPlace = p ? p.id : null;
  return bar('تفتيش جديد', 'home') + `<div class="wrap"><div class="card">
  <label class="f">المكان / القسم</label><select id="np">${places.map(x => `<option value="${x.id}" ${p && x.id === p.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select>
  ${p ? `<p class="mut" style="margin-top:10px">قائمة التحقق: ${esc((S.lists.find(l => l.id === p.listId) || {}).title || 'غير محددة')}<br>العاملون: ${esc(p.staff)} · الورديات: ${esc(p.shifts)} · المسؤول: ${esc(p.responsible || 'غير محدد')}</p>` : '<p class="mut">لا توجد أماكن. أضف مكاناً من الإدارة.</p>'}
  <button class="btn block" data-act="start" ${p && S.lists.find(l => l.id === p.listId) ? '' : 'disabled'}>ابدأ التفتيش</button></div></div>`;
}
function startInspection(placeId) {
  const p = S.places.find(x => x.id === placeId); const l = S.lists.find(x => x.id === p.listId);
  const t = nowParts();
  const insp = { id: uid('N'), listId: l.id, snap: clone(l), status: 'draft', synced: false, inspectorId: S.session,
    header: { facility: S.settings.facility, place: p.name, dept: p.dept, staff: p.staff, shifts: p.shifts, responsible: p.responsible, inspector: me().name, date: t.date, time: t.time },
    answers: {}, esc: {}, sig: {}, startedAt: Date.now() };
  S.inspections.push(insp); save(); V.cur = insp.id; V.view = 'insp'; render();
}
const cur = () => S.inspections.find(i => i.id === V.cur);

/* ===== شاشة التفتيش ===== */
function viewInsp() {
  const i = cur(); const r = compute(i.snap, i.answers, i.esc); const h = i.header;
  const open = V.open || {};
  return bar(i.snap.title, 'home') + `<div class="wrap">
  <div class="card"><div class="grid2">
   <div><label class="f">المنشأة</label><input type="text" data-h="facility" value="${esc(h.facility)}"></div>
   <div><label class="f">المكان / القسم</label><input type="text" data-h="place" value="${esc(h.place)}"></div>
   <div><label class="f">عدد العاملين</label><input type="number" inputmode="numeric" data-h="staff" value="${esc(h.staff)}"></div>
   <div><label class="f">عدد الورديات</label><input type="number" inputmode="numeric" data-h="shifts" value="${esc(h.shifts)}"></div>
   <div><label class="f">المسؤول عن المكان</label><input type="text" data-h="responsible" value="${esc(h.responsible)}"></div>
   <div><label class="f">القائم بالتفتيش</label><input type="text" data-h="inspector" value="${esc(h.inspector)}"></div>
   <div><label class="f">التاريخ</label><input type="text" data-h="date" value="${esc(h.date)}"></div>
   <div><label class="f">الساعة</label><input type="text" data-h="time" value="${esc(h.time)}"></div></div></div>
  <div class="prog"><div class="row mut"><span>${r.answered} من ${r.total}</span><span class="sp"></span><span>الدرجة الحالية <bdi>${r.score}%</bdi></span></div><div class="pbar"><i style="width:${r.total ? r.answered / r.total * 100 : 0}%"></i></div></div>
  <div class="legend mut" style="margin-bottom:8px"><span>م: مُرضٍ</span><span>ت: يحتاج إلى تحسين</span><span>ف: تصحيح فوري</span><span>غ: غير منطبق</span></div>
  ${i.snap.axes.map((a, ai) => {
    const done = a.items.filter(it => i.answers[it.id] && i.answers[it.id].v).length;
    return `<details class="axis" data-ax="${a.id}" ${open[a.id] ? 'open' : ''}><summary><span>${ai + 1}. ${esc(a.name)}</span><span class="cnt">${done}/${a.items.length}</span></summary>
    ${a.items.map((it, k) => itemHtml(i, it, k)).join('')}</details>`;
  }).join('')}
  <button class="btn block" style="margin-top:14px" data-act="tofinish">إنهاء التفتيش والمراجعة</button></div>`;
}
function itemHtml(i, it, k) {
  const a = i.answers[it.id] || {}; const needNote = a.v === 'ف' || a.v === 'ت';
  const cls = { 'م': 'm', 'ت': 't', 'ف': 'f', 'غ': 'g' };
  return `<div class="item"><div class="t"><span class="tag ${it.cls}">${CLS_NAME[it.cls]}</span> ${k + 1}. ${esc(it.text)}</div>
  <div class="ans">${OPTS[it.cls].map(o => `<button class="${a.v === o ? 'on ' + cls[o] : ''}" data-act="ans" data-it="${it.id}" data-v="${o}">${o}</button>`).join('')}</div>
  ${needNote ? `<textarea placeholder="اكتب الملاحظة أو الإجراء المطلوب (إلزامي)" data-note="${it.id}" style="margin-top:8px">${esc(a.note || '')}</textarea>` : ''}
  <div class="ph">${(a.photos || []).map((p, pi) => `<div class="x"><img src="${p}" alt=""><b data-act="delph" data-it="${it.id}" data-pi="${pi}">×</b></div>`).join('')}
   <label class="btn sec sm" style="cursor:pointer">📷 صورة<input type="file" accept="image/*" capture="environment" multiple hidden data-photo="${it.id}"></label></div></div>`;
}
function setAnswer(itId, v) {
  const i = cur(); const a = i.answers[itId] || (i.answers[itId] = {});
  a.v = a.v === v ? '' : v; save(); V.keepScroll = true; captureOpen(); render();
}
function captureOpen() { V.open = {}; document.querySelectorAll('details.axis[open]').forEach(d => V.open[d.dataset.ax] = true); }

function compress(file, max = 1024, q = 0.6) {
  return new Promise(res => {
    const fr = new FileReader();
    fr.onload = () => { const im = new Image(); im.onload = () => {
      const k = Math.min(1, max / Math.max(im.width, im.height)); const c = document.createElement('canvas');
      c.width = Math.round(im.width * k); c.height = Math.round(im.height * k); c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
      res(c.toDataURL('image/jpeg', q)); }; im.onerror = () => res(null); im.src = fr.result; };
    fr.onerror = () => res(null); fr.readAsDataURL(file);
  });
}

/* ===== المراجعة والإنهاء ===== */
function viewFinish() {
  const i = cur(); const r = compute(i.snap, i.answers, i.esc);
  const missing = i.snap.axes.flatMap(a => a.items.filter(it => !(i.answers[it.id] && i.answers[it.id].v)));
  const noNote = i.snap.axes.flatMap(a => a.items.filter(it => { const x = i.answers[it.id]; return x && (x.v === 'ف' || x.v === 'ت') && !(x.note || '').trim(); }));
  return bar('مراجعة وإنهاء', 'insp') + `<div class="wrap">
  <div class="card"><div class="score">${r.score}%</div><div style="text-align:center"><span class="tag ${r.bandCls}">${r.band}</span></div>
  ${r.veto ? `<div class="veto" style="margin-top:12px"><b>تفعيل البوابة الحرجة</b><div class="mut">${r.critFails.length ? `بنود حرجة غير مطابقة: ${r.critFails.length}` : ''} ${r.escHits.length ? ` · حالات تصعيد فوري: ${r.escHits.length}` : ''}</div></div>` : ''}</div>
  ${missing.length ? `<div class="card"><b>بنود لم تُجب بعد: ${missing.length}</b><div class="mut">أكمل جميع البنود قبل الإنهاء.</div></div>` : ''}
  ${noNote.length ? `<div class="card"><b>بنود تحتاج ملاحظة: ${noNote.length}</b><div class="mut">كل بند غير مطابق أو مطابق جزئياً يتطلب ملاحظة.</div></div>` : ''}
  <div class="card"><h3>حالات تستوجب التصعيد الفوري إلى الإدارة</h3>${(i.snap.escalation || []).map((e, k) => `<label class="row" style="padding:6px 0"><input type="checkbox" data-esc="${k}" ${i.esc[k] ? 'checked' : ''}> <span>${esc(e)}</span></label>`).join('') || '<span class="mut">لا توجد حالات معرّفة.</span>'}</div>
  <div class="card"><h3>ملخص المحاور</h3><table class="rep"><tr><th>المحور</th><th>الوزن</th><th>النسبة</th></tr>${r.axes.map(a => `<tr><td>${esc(a.name)}</td><td>${a.weight}</td><td>${a.pct === null ? 'غير منطبق' : a.pct.toFixed(1) + '%'}</td></tr>`).join('')}</table></div>
  <div class="card"><h3>التوقيعات</h3><label class="f">توقيع المفتش</label><canvas class="sig" id="sg1"></canvas><button class="btn sec sm" data-act="clrsig" data-k="1">مسح</button>
  <label class="f" style="margin-top:10px">توقيع المسؤول عن المكان</label><canvas class="sig" id="sg2"></canvas><button class="btn sec sm" data-act="clrsig" data-k="2">مسح</button></div>
  <button class="btn block" data-act="finalize" ${missing.length || noNote.length ? 'disabled' : ''}>اعتماد التفتيش وحفظه</button></div>`;
}
function initSig() {
  const i = cur(); if (!i) return;
  [['sg1', 'inspector'], ['sg2', 'responsible']].forEach(([id, key]) => {
    const c = $('#' + id); if (!c) return; const w = c.clientWidth, h = c.clientHeight; c.width = w; c.height = h;
    const x = c.getContext('2d'); x.lineWidth = 2; x.lineCap = 'round'; x.strokeStyle = '#000';
    if (i.sig[key]) { const im = new Image(); im.onload = () => x.drawImage(im, 0, 0, w, h); im.src = i.sig[key]; }
    let d = false; const pos = e => { const r = c.getBoundingClientRect(); const t = e.touches ? e.touches[0] : e; return [t.clientX - r.left, t.clientY - r.top]; };
    const st = e => { d = true; const [a, b] = pos(e); x.beginPath(); x.moveTo(a, b); e.preventDefault(); };
    const mv = e => { if (!d) return; const [a, b] = pos(e); x.lineTo(a, b); x.stroke(); e.preventDefault(); };
    const en = () => { if (!d) return; d = false; i.sig[key] = c.toDataURL('image/png'); save(); };
    c.addEventListener('pointerdown', st); c.addEventListener('pointermove', mv); c.addEventListener('pointerup', en); c.addEventListener('pointerleave', en);
  });
}
function finalize() {
  const i = cur(); const r = compute(i.snap, i.answers, i.esc);
  i.result = r; i.status = 'done'; i.finishedAt = Date.now(); i.synced = false; save();
  toast('تم حفظ التفتيش'); V.view = 'report'; render(); autoSync();
}

/* ===== التقرير ===== */
function viewReport() {
  const i = S.inspections.find(x => x.id === V.cur); const r = i.result || compute(i.snap, i.answers, i.esc); const h = i.header;
  const fails = i.snap.axes.flatMap(a => a.items.map(it => ({ a, it, x: i.answers[it.id] })).filter(o => o.x && (o.x.v === 'ف' || o.x.v === 'ت')));
  return `<div class="overlay"><div class="bar noprint"><button data-act="go" data-v="${V.back || 'inspections'}">رجوع</button><h1>التقرير</h1><button data-act="print">طباعة / PDF</button></div><div class="wrap">
  <h2 style="text-align:center">${esc(i.snap.title)}</h2>
  <table class="rep"><tr><th>المنشأة</th><td>${esc(h.facility)}</td><th>المكان / القسم</th><td>${esc(h.place)}</td></tr>
  <tr><th>عدد العاملين</th><td>${esc(h.staff)}</td><th>عدد الورديات</th><td>${esc(h.shifts)}</td></tr>
  <tr><th>المسؤول عن المكان</th><td>${esc(h.responsible)}</td><th>القائم بالتفتيش</th><td>${esc(h.inspector)}</td></tr>
  <tr><th>التاريخ</th><td>${esc(h.date)}</td><th>الساعة</th><td>${esc(h.time)}</td></tr></table>
  <div class="card"><div class="score">${r.score}%</div><div style="text-align:center"><span class="tag ${r.bandCls}">${r.band}</span></div></div>
  ${r.veto ? `<div class="veto"><b>البوابة الحرجة مفعّلة</b>${r.critFails.map(c => `<div>• ${esc(c.text)}</div>`).join('')}${r.escHits.map(c => `<div>• تصعيد فوري: ${esc(c)}</div>`).join('')}</div>` : ''}
  <table class="rep"><tr><th>المحور</th><th>الوزن</th><th>النسبة</th></tr>${r.axes.map(a => `<tr><td>${esc(a.name)}</td><td>${a.weight}</td><td>${a.pct === null ? 'غير منطبق' : a.pct.toFixed(1) + '%'}</td></tr>`).join('')}</table>
  <h3>الملاحظات والإجراءات المطلوبة (${fails.length})</h3>
  ${fails.length ? `<table class="rep"><tr><th>البند</th><th>التصنيف</th><th>التقدير</th><th>الملاحظة</th></tr>${fails.map(o => `<tr><td>${esc(o.it.text)}${(o.x.photos || []).map(p => `<br><img src="${p}" style="width:90px;margin:3px;border-radius:6px">`).join('')}</td><td>${CLS_NAME[o.it.cls]}</td><td>${o.x.v}</td><td>${esc(o.x.note || '')}</td></tr>`).join('')}</table>` : '<p class="mut">لا توجد ملاحظات.</p>'}
  <div class="grid2"><div><b>توقيع المفتش</b><br>${i.sig.inspector ? `<img src="${i.sig.inspector}" style="width:100%;max-height:110px;object-fit:contain">` : ''}</div><div><b>توقيع المسؤول</b><br>${i.sig.responsible ? `<img src="${i.sig.responsible}" style="width:100%;max-height:110px;object-fit:contain">` : ''}</div></div>
  </div></div>`;
}

/* ===== المشرف: قوائم التحقق ===== */
function viewLists() {
  return bar('قوائم التحقق', 'admin') + `<div class="wrap"><button class="btn block" data-act="newlist">＋ قائمة جديدة</button><div class="card" style="margin-top:12px">${S.lists.map(l => `<div class="listrow"><div class="sp"><b>${esc(l.title)}</b><div class="mut">${l.axes.length} محاور · ${l.axes.reduce((n, a) => n + a.items.length, 0)} بنداً · إصدار ${l.version}</div></div>
  <button class="btn sm" data-act="editlist" data-id="${l.id}">تعديل</button><button class="btn sec sm" data-act="duplist" data-id="${l.id}">نسخ</button></div>`).join('')}</div></div>`;
}
function viewEditList() {
  const l = V.draft; const sumW = l.axes.reduce((s, a) => s + (+a.weight || 0), 0);
  return bar('تحرير القائمة', 'lists') + `<div class="wrap">
  <div class="card"><label class="f">عنوان القائمة</label><input type="text" data-l="title" value="${esc(l.title)}">
  <p class="mut" style="margin-top:8px">مجموع أوزان المحاور: <b style="color:${sumW === 100 ? 'var(--ok)' : 'var(--bad)'}">${sumW}</b> (يُفضَّل 100)</p></div>
  ${l.axes.map((a, ai) => `<div class="card"><div class="row"><input type="text" style="flex:1 1 60%" data-a="${ai}" data-f="name" value="${esc(a.name)}"><input type="number" style="width:76px" data-a="${ai}" data-f="weight" value="${esc(a.weight)}"></div>
   <div class="row" style="margin:8px 0"><button class="btn sec sm" data-act="axup" data-a="${ai}">▲</button><button class="btn sec sm" data-act="axdn" data-a="${ai}">▼</button><button class="btn bad sm" data-act="axdel" data-a="${ai}">حذف المحور</button></div>
   ${a.items.map((it, ii) => `<div class="listrow" style="align-items:flex-start"><div class="sp"><textarea data-a="${ai}" data-i="${ii}" data-f="text" style="min-height:48px">${esc(it.text)}</textarea>
    <div class="row" style="margin-top:4px"><select data-a="${ai}" data-i="${ii}" data-f="cls" style="width:auto">${['c', 'e', 's'].map(c => `<option value="${c}" ${it.cls === c ? 'selected' : ''}>${CLS_NAME[c]}</option>`).join('')}</select>
    <button class="btn sec sm" data-act="itup" data-a="${ai}" data-i="${ii}">▲</button><button class="btn sec sm" data-act="itdn" data-a="${ai}" data-i="${ii}">▼</button><button class="btn bad sm" data-act="itdel" data-a="${ai}" data-i="${ii}">حذف</button></div></div></div>`).join('')}
   <button class="btn sec sm" data-act="itadd" data-a="${ai}" style="margin-top:8px">＋ بند</button></div>`).join('')}
  <button class="btn sec block" data-act="axadd">＋ محور جديد</button>
  <div class="card" style="margin-top:12px"><h3>حالات التصعيد الفوري</h3><textarea data-l="escalation" placeholder="كل سطر حالة">${esc((l.escalation || []).join('\n'))}</textarea></div>
  <p class="mut">التفتيشات السابقة تحتفظ بنسختها القديمة من القائمة ولا تتأثر بالتعديل.</p>
  <button class="btn block" data-act="savelist">حفظ القائمة</button>${V.isNewList ? '' : `<button class="btn bad block" style="margin-top:8px" data-act="dellist">حذف القائمة</button>`}</div>`;
}
function syncDraftFields() { // قراءة الحقول الحالية قبل أي إعادة رسم
  const l = V.draft; if (!l) return;
  document.querySelectorAll('[data-l]').forEach(e => { if (e.dataset.l === 'escalation') l.escalation = e.value.split('\n').map(s => s.trim()).filter(Boolean); else l[e.dataset.l] = e.value; });
  document.querySelectorAll('[data-f]').forEach(e => { const a = l.axes[+e.dataset.a]; if (!a) return; if (e.dataset.i !== undefined) { const it = a.items[+e.dataset.i]; if (it) it[e.dataset.f] = e.value; } else a[e.dataset.f] = e.dataset.f === 'weight' ? +e.value || 0 : e.value; });
}
const mv = (arr, i, d) => { const j = i + d; if (j < 0 || j >= arr.length) return; [arr[i], arr[j]] = [arr[j], arr[i]]; };

/* ===== المشرف: الأماكن والمستخدمون والإعدادات ===== */
function viewPlaces() {
  const ed = V.editPlace;
  return bar('الأماكن والأقسام', 'admin') + `<div class="wrap"><button class="btn block" data-act="newplace">＋ مكان جديد</button>
  ${ed ? `<div class="card" style="margin-top:12px"><h3>${ed.isNew ? 'مكان جديد' : 'تعديل مكان'}</h3><div class="grid2">
   <div><label class="f">اسم المكان</label><input type="text" data-p="name" value="${esc(ed.name)}"></div>
   <div><label class="f">القسم</label><input type="text" data-p="dept" value="${esc(ed.dept)}"></div>
   <div><label class="f">عدد العاملين</label><input type="number" data-p="staff" value="${esc(ed.staff)}"></div>
   <div><label class="f">عدد الورديات</label><input type="number" data-p="shifts" value="${esc(ed.shifts)}"></div>
   <div><label class="f">المسؤول عن المكان</label><input type="text" data-p="responsible" value="${esc(ed.responsible)}"></div>
   <div><label class="f">قائمة التحقق</label><select data-p="listId">${S.lists.map(l => `<option value="${l.id}" ${l.id === ed.listId ? 'selected' : ''}>${esc(l.title)}</option>`).join('')}</select></div></div>
   <div class="row" style="margin-top:10px"><button class="btn" data-act="saveplace">حفظ</button><button class="btn sec" data-act="cancelplace">إلغاء</button></div></div>` : ''}
  <div class="card" style="margin-top:12px">${S.places.map(p => `<div class="listrow"><div class="sp"><b>${esc(p.name)}</b><div class="mut">${esc(p.dept)} · عاملون ${esc(p.staff)} · ورديات ${esc(p.shifts)} · ${esc(p.responsible || 'بلا مسؤول')}</div></div><button class="btn sm" data-act="editplace" data-id="${p.id}">تعديل</button><button class="btn bad sm" data-act="delplace" data-id="${p.id}">حذف</button></div>`).join('')}</div></div>`;
}
function viewUsers() {
  const ed = V.editUser;
  return bar('المستخدمون', 'admin') + `<div class="wrap"><button class="btn block" data-act="newuser">＋ مستخدم جديد</button>
  ${ed ? `<div class="card" style="margin-top:12px"><div class="grid2"><div><label class="f">الاسم</label><input type="text" data-u="name" value="${esc(ed.name)}"></div>
  <div><label class="f">الرمز السري</label><input type="text" data-u="pin" value="${esc(ed.pin)}"></div>
  <div><label class="f">الدور</label><select data-u="role"><option value="inspector" ${ed.role === 'inspector' ? 'selected' : ''}>مفتش</option><option value="supervisor" ${ed.role === 'supervisor' ? 'selected' : ''}>مشرف</option></select></div></div>
  <div class="row" style="margin-top:10px"><button class="btn" data-act="saveuser">حفظ</button><button class="btn sec" data-act="canceluser">إلغاء</button></div></div>` : ''}
  <div class="card" style="margin-top:12px">${S.users.map(u => `<div class="listrow"><div class="sp"><b>${esc(u.name)}</b><div class="mut">${u.role === 'supervisor' ? 'مشرف' : 'مفتش'}</div></div><button class="btn sm" data-act="edituser" data-id="${u.id}">تعديل</button>${u.id !== S.session ? `<button class="btn bad sm" data-act="deluser" data-id="${u.id}">حذف</button>` : ''}</div>`).join('')}</div>
  <p class="mut">الرموز السرية الافتراضية للتجربة فقط، غيّرها قبل الاستخدام الفعلي.</p></div>`;
}
function viewSettings() {
  return bar('الإعدادات والمزامنة', 'admin') + `<div class="wrap"><div class="card"><label class="f">اسم المنشأة (يظهر في الترويسة)</label><input type="text" id="s_fac" value="${esc(S.settings.facility)}">
  <label class="f" style="margin-top:10px">رابط المزامنة (Google Apps Script)</label><input type="url" id="s_url" value="${esc(S.settings.syncUrl)}" placeholder="https://script.google.com/macros/s/.../exec">
  <label class="f" style="margin-top:10px">مفتاح الربط السري</label><input type="text" id="s_tok" value="${esc(S.settings.token)}">
  <button class="btn block" style="margin-top:12px" data-act="savesettings">حفظ الإعدادات</button></div>
  <div class="card"><h3>المزامنة وإدارة الإعدادات المشتركة</h3><div class="row"><button class="btn sec" data-act="pushcfg">رفع القوائم والأماكن والمستخدمين</button><button class="btn sec" data-act="pullcfg">سحب الإعدادات</button><button class="btn sec" data-act="sync">رفع التفتيشات</button></div></div>
  <div class="card"><h3>نسخة احتياطية</h3><div class="row"><button class="btn sec" data-act="export">تصدير ملف</button><label class="btn sec" style="cursor:pointer">استيراد ملف<input type="file" accept=".json" hidden id="imp"></label></div></div></div>`;
}

/* ===== المزامنة (اختيارية ومجانية عبر Google Apps Script) ===== */
async function api(action, payload) {
  const r = await fetch(S.settings.syncUrl, { method: 'POST', body: JSON.stringify({ action, token: S.settings.token, ...payload }) });
  const j = await r.json(); if (!j.ok) throw new Error(j.error || 'خطأ'); return j;
}
let syncing = false;
async function autoSync() { if (S && S.settings.syncUrl && navigator.onLine) await syncInspections(true); }
async function syncInspections(silent) {
  if (!S.settings.syncUrl || syncing) { if (!silent) toast('المزامنة غير مفعّلة'); return; }
  syncing = true; let n = 0;
  try {
    for (const i of S.inspections.filter(x => x.status === 'done' && !x.synced)) { await api('saveInspection', { inspection: i }); i.synced = true; n++; await save(); }
    if (!silent || n) toast(n ? `تم رفع ${n} تفتيش` : 'لا يوجد ما يُرفع');
  } catch (e) { if (!silent) toast('تعذرت المزامنة: ' + e.message); }
  syncing = false; if (n) render();
}
async function pushConfig() { try { await api('saveConfig', { config: { lists: S.lists, places: S.places, users: S.users, facility: S.settings.facility } }); toast('تم رفع الإعدادات'); } catch (e) { toast('تعذر الرفع: ' + e.message); } }
async function pullConfig() {
  try { const j = await api('getConfig', {}); if (!j.config) return toast('لا توجد إعدادات محفوظة');
    S.lists = j.config.lists; S.places = j.config.places; S.users = j.config.users; if (j.config.facility) S.settings.facility = j.config.facility; await save(); toast('تم سحب الإعدادات'); render(); } catch (e) { toast('تعذر السحب: ' + e.message); }
}

/* ===== الأحداث ===== */
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act]'); if (!t) return; const a = t.dataset.act, d = t.dataset;
  if (V.view === 'editlist' && !['go', 'logout'].includes(a)) syncDraftFields();
  switch (a) {
    case 'login': { const u = S.users.find(x => x.id === $('#lu').value); if (u && u.pin === $('#lp').value) { S.session = u.id; await save(); V.view = 'home'; render(); } else toast('الرمز السري غير صحيح'); break; }
    case 'logout': S.session = null; await save(); V.view = 'login'; render(); break;
    case 'tab': V.view = d.v; render(); break;
    case 'go': V.view = d.v; V.editPlace = V.editUser = null; render(); break;
    case 'new': V.view = 'new'; render(); break;
    case 'start': startInspection(V.newPlace); break;
    case 'open': V.cur = d.id; V.view = 'insp'; render(); break;
    case 'ans': setAnswer(d.it, d.v); break;
    case 'delph': { const x = cur().answers[d.it]; x.photos.splice(+d.pi, 1); await save(); V.keepScroll = true; captureOpen(); render(); break; }
    case 'tofinish': captureOpen(); V.view = 'finish'; render(); break;
    case 'clrsig': { const i = cur(); const k = d.k === '1' ? 'inspector' : 'responsible'; delete i.sig[k]; await save(); initSig(); const c = $('#sg' + d.k); c.getContext('2d').clearRect(0, 0, c.width, c.height); break; }
    case 'finalize': finalize(); break;
    case 'report': V.cur = d.id; V.back = 'inspections'; V.view = 'report'; render(); break;
    case 'print': window.print(); break;
    case 'delinsp': if (confirm('حذف هذا التفتيش نهائياً من هذا الجهاز؟')) { S.inspections = S.inspections.filter(x => x.id !== d.id); await save(); render(); } break;
    case 'sync': syncInspections(false); break;
    case 'pushcfg': pushConfig(); break;
    case 'pullcfg': pullConfig(); break;
    /* القوائم */
    case 'newlist': V.draft = { id: uid('L'), title: 'قائمة جديدة', version: 1, axes: [{ id: uid('A'), name: 'محور جديد', weight: 100, items: [{ id: uid('I'), cls: 'e', text: '' }] }], escalation: [] }; V.isNewList = true; V.view = 'editlist'; render(); break;
    case 'editlist': V.draft = clone(S.lists.find(l => l.id === d.id)); V.isNewList = false; V.view = 'editlist'; render(); break;
    case 'duplist': { const c = clone(S.lists.find(l => l.id === d.id)); c.id = uid('L'); c.title += ' (نسخة)'; c.version = 1; c.axes.forEach(x => { x.id = uid('A'); x.items.forEach(it => it.id = uid('I')); }); S.lists.push(c); await save(); render(); break; }
    case 'axadd': V.draft.axes.push({ id: uid('A'), name: 'محور جديد', weight: 0, items: [{ id: uid('I'), cls: 'e', text: '' }] }); V.keepScroll = true; render(); break;
    case 'axdel': if (confirm('حذف المحور وبنوده؟')) { V.draft.axes.splice(+d.a, 1); V.keepScroll = true; render(); } break;
    case 'axup': mv(V.draft.axes, +d.a, -1); V.keepScroll = true; render(); break;
    case 'axdn': mv(V.draft.axes, +d.a, 1); V.keepScroll = true; render(); break;
    case 'itadd': V.draft.axes[+d.a].items.push({ id: uid('I'), cls: 'e', text: '' }); V.keepScroll = true; render(); break;
    case 'itdel': V.draft.axes[+d.a].items.splice(+d.i, 1); V.keepScroll = true; render(); break;
    case 'itup': mv(V.draft.axes[+d.a].items, +d.i, -1); V.keepScroll = true; render(); break;
    case 'itdn': mv(V.draft.axes[+d.a].items, +d.i, 1); V.keepScroll = true; render(); break;
    case 'savelist': {
      const l = V.draft; l.axes.forEach(x => x.items = x.items.filter(it => it.text.trim()));
      const idx = S.lists.findIndex(x => x.id === l.id);
      if (idx >= 0) { l.version = (S.lists[idx].version || 1) + 1; S.lists[idx] = l; } else S.lists.push(l);
      await save(); toast('تم حفظ القائمة'); V.view = 'lists'; render(); break; }
    case 'dellist': if (S.places.some(p => p.listId === V.draft.id)) toast('القائمة مربوطة بمكان، غيّر الربط أولاً'); else if (confirm('حذف القائمة؟')) { S.lists = S.lists.filter(l => l.id !== V.draft.id); await save(); V.view = 'lists'; render(); } break;
    /* الأماكن */
    case 'newplace': V.editPlace = { isNew: true, id: uid('P'), name: '', dept: '', staff: '', shifts: '', responsible: '', listId: (S.lists[0] || {}).id }; render(); break;
    case 'editplace': V.editPlace = clone(S.places.find(p => p.id === d.id)); render(); break;
    case 'cancelplace': V.editPlace = null; render(); break;
    case 'saveplace': { const p = V.editPlace; if (!p.name.trim()) return toast('أدخل اسم المكان'); delete p.isNew; const k = S.places.findIndex(x => x.id === p.id); if (k >= 0) S.places[k] = p; else S.places.push(p); await save(); V.editPlace = null; render(); break; }
    case 'delplace': if (confirm('حذف المكان؟')) { S.places = S.places.filter(p => p.id !== d.id); await save(); render(); } break;
    /* المستخدمون */
    case 'newuser': V.editUser = { isNew: true, id: uid('U'), name: '', pin: '', role: 'inspector' }; render(); break;
    case 'edituser': V.editUser = clone(S.users.find(u => u.id === d.id)); render(); break;
    case 'canceluser': V.editUser = null; render(); break;
    case 'saveuser': { const u = V.editUser; if (!u.name.trim() || !u.pin.trim()) return toast('أدخل الاسم والرمز'); delete u.isNew; const k = S.users.findIndex(x => x.id === u.id); if (k >= 0) S.users[k] = u; else S.users.push(u); await save(); V.editUser = null; render(); break; }
    case 'deluser': if (confirm('حذف المستخدم؟')) { S.users = S.users.filter(u => u.id !== d.id); await save(); render(); } break;
    case 'savesettings': S.settings.facility = $('#s_fac').value; S.settings.syncUrl = $('#s_url').value.trim(); S.settings.token = $('#s_tok').value.trim(); await save(); toast('تم الحفظ'); break;
    case 'export': { const b = new Blob([JSON.stringify(S)], { type: 'application/json' }); const a2 = document.createElement('a'); a2.href = URL.createObjectURL(b); a2.download = `inspect-backup-${nowParts().date}.json`; a2.click(); break; }
  }
});
document.addEventListener('input', e => {
  const t = e.target;
  if (t.dataset.h !== undefined) { cur().header[t.dataset.h] = t.value; save(); }
  else if (t.dataset.note !== undefined) { const x = cur().answers[t.dataset.note] || (cur().answers[t.dataset.note] = {}); x.note = t.value; save(); }
  else if (t.dataset.p !== undefined) V.editPlace[t.dataset.p] = t.value;
  else if (t.dataset.u !== undefined) V.editUser[t.dataset.u] = t.value;
});
document.addEventListener('change', async e => {
  const t = e.target;
  if (t.id === 'np') { V.newPlace = t.value; render(); }
  else if (t.dataset.esc !== undefined) { const i = cur(); i.esc[t.dataset.esc] = t.checked; await save(); V.keepScroll = true; render(); }
  else if (t.dataset.photo) {
    const i = cur(); const x = i.answers[t.dataset.photo] || (i.answers[t.dataset.photo] = {}); x.photos = x.photos || [];
    for (const f of t.files) { const p = await compress(f); if (p) x.photos.push(p); }
    await save(); captureOpen(); V.keepScroll = true; render();
  } else if (t.id === 'imp') {
    const f = t.files[0]; if (!f) return; try { const j = JSON.parse(await f.text()); if (!j.lists || !j.users) throw 0; S = j; await save(); toast('تم الاستيراد'); V.view = 'login'; S.session = null; render(); } catch { toast('ملف غير صالح'); }
  }
});
init();
