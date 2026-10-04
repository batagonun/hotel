'use strict';
/* ============================================================
   ملف الإضافات: ملف تعريف المنشأة، المرافق، أماكن التفتيش وربط القوائم
   والمفتشين، التفتيش المتعدد القوائم، التقرير الشامل، وطباعة القائمة.
   يُحمَّل بعد app.js ويستبدل الدوال المذكورة فيه.
   ============================================================ */

/* ===== ثوابت ===== */
const SERVICES = ['الإقامة الفندقية', 'الأغذية والمشروبات', 'الحفلات والمؤتمرات', 'النشاط الرياضي', 'النشاط الترفيهي', 'النشاط الثقافي'];
const VENUE_TYPES = {
  hotel: { name: 'فندق', fields: [['عدد النجوم', 'text'], ['عدد الأدوار', 'number'], ['عدد الغرف في كل دور', 'text'], ['إجمالي عدد الغرف', 'number'], ['أنواع الغرف وأعدادها', 'rows']] },
  restaurant: { name: 'مطعم', fields: [['عدد الطاولات', 'number'], ['عدد الكراسي', 'number'], ['الطاقة الاستيعابية', 'number'], ['مواعيد التشغيل', 'text']] },
  cafe: { name: 'كوفي شوب', fields: [['عدد الطاولات', 'number'], ['عدد الكراسي', 'number'], ['الطاقة الاستيعابية', 'number'], ['مواعيد التشغيل', 'text']] },
  banquet: { name: 'قاعة احتفالات', fields: [['الطاقة الاستيعابية', 'number'], ['المساحة (م²)', 'number'], ['عدد الطاولات', 'number'], ['مواعيد التشغيل', 'text']] },
  conference: { name: 'قاعة مؤتمرات', fields: [['الطاقة الاستيعابية', 'number'], ['المساحة (م²)', 'number'], ['التجهيزات السمعية والبصرية', 'text'], ['مواعيد التشغيل', 'text']] },
  fields: { name: 'ملاعب', fields: [['عدد الملاعب', 'number'], ['أنواع الملاعب وأعدادها', 'rows'], ['مواعيد التشغيل', 'text']] },
  pool: { name: 'حمام سباحة', fields: [['عدد الأحواض', 'number'], ['أبعاد وأعماق الأحواض', 'text'], ['عدد المنقذين', 'number'], ['مواعيد التشغيل', 'text']] },
  kids: { name: 'ألعاب أطفال', fields: [['عدد الألعاب', 'number'], ['الفئة العمرية', 'text'], ['عدد المشرفين', 'number'], ['مواعيد التشغيل', 'text']] }
};
/* أماكن التفتيش المقترحة لكل نوع مرفق، مع قوائم التحقق الجاهزة لها */
const VENUE_UNITS = {
  hotel: v => [{ name: 'الاستقبال', dept: 'الاستقبال', lists: ['L_frontoffice'] }, { name: 'الإشراف الداخلي', dept: 'الإشراف الداخلي', lists: ['L_housekeeping'] }],
  restaurant: v => [{ name: v.name || 'المطعم', dept: 'المطعم', lists: ['L_restaurant'] }, { name: 'مطبخ ' + (v.name || 'المطعم'), dept: 'المطبخ', lists: ['L_kitchen'] }]
};

/* ===== أدوات ===== */
const val = (o, p) => p.split('.').reduce((a, k) => (a == null ? a : a[k]), o);
const setPath = (o, p, v) => { const ks = p.split('.'); const last = ks.pop(); ks.reduce((a, k) => a[k], o)[last] = v; };
const inp = (tgt, obj, path, o = {}) => `<input type="${o.type || 'text'}" ${o.type === 'number' ? 'inputmode="numeric"' : ''} data-tgt="${tgt}" data-bind="${path}" value="${esc(val(obj, path) ?? '')}" placeholder="${esc(o.ph || '')}">`;
const bindTarget = t => ({ ef: V.ef, ep: V.editPlace, nv: V, hd: V.hd }[t]);
V.det = {};
const newFac = () => ({ id: uid('F'), name: '', address: '', manager: '', assistants: '', staff: { permanent: '', insured: '', temporary: '', security: '' }, services: [], venues: [], contacts: { phone: '', fax: '', email: '', extra: [] }, transport: [''] });
const newVenue = type => ({ id: uid('V'), type, name: '', fields: VENUE_TYPES[type].fields.map(([label, t]) => ({ id: uid('f'), label, t, v: t === 'rows' ? [{ n: '', c: '' }] : '' })) });
const facOf = id => S.facilities.find(f => f.id === id) || S.facilities[0] || newFac();
const listTitle = id => (S.lists.find(l => l.id === id) || {}).title;
const batchOf = i => S.inspections.filter(x => (x.batchId || x.id) === (i.batchId || i.id));
const groupBatches = arr => { const m = new Map(); arr.forEach(i => { const k = i.batchId || i.id; if (!m.has(k)) m.set(k, []); m.get(k).push(i); }); return [...m.values()]; };
const unitsForMe = () => S.places.filter(p => isSup() || !(p.inspectorIds || []).length || p.inspectorIds.includes(S.session));
const toNum = x => +x || 0;
const bandFor = sc => BANDS.find(b => sc >= b[0]);
const rkey = i => (i.header.place || '') + '|' + i.header.date;
const groupRounds = arr => { const m = new Map(); arr.forEach(i => { const k = rkey(i); if (!m.has(k)) m.set(k, []); m.get(k).push(i); }); return [...m.entries()].map(([k, v]) => ({ key: k, items: v.sort((a, b) => (a.header.time || '').localeCompare(b.header.time || '')) })); };
const placeOfInsp = i => S.places.find(p => p.id === i.placeId) || S.places.find(p => p.name === i.header.place);
const missingLists = items => { const p = placeOfInsp(items[0]); if (!p) return []; const have = items.map(i => i.listId); return p.listIds.filter(id => !have.includes(id)).map(listTitle).filter(Boolean); };
const distinct = a => [...new Set(a.filter(Boolean))];
const todayStr = () => nowParts().date;

/* ===== ترحيل البيانات القديمة إلى الهيكل الجديد ===== */
function migrate() {
  if (!S.facilities) S.facilities = [];
  if (!S.facilities.length && S.places.length && !S.facDeleted) {
    const f = newFac(); f.id = 'F1'; f.name = (S.settings && S.settings.facility) || ''; S.facilities = [f];
  }
  S.places.forEach(p => {
    if (!p.facilityId && S.facilities[0]) p.facilityId = S.facilities[0].id;
    if (!p.listIds) p.listIds = p.listId ? [p.listId] : [];
    delete p.listId;
    p.inspectorIds = p.inspectorIds || []; p.venueId = p.venueId || '';
  });
  S.inspections.forEach(i => { if (!i.batchId) i.batchId = i.id; });
}

/* ===== التشغيل ===== */
async function init() {
  await DB.open();
  S = await DB.get('state');
  if (!S) { S = { ...clone(SEED), inspections: [], session: null, seedVersion: SEED.version }; }
  if (S.seedVersion !== SEED.version) {
    SEED.lists.forEach(l => { const k = S.lists.findIndex(x => x.id === l.id); if (k >= 0) S.lists[k] = clone(l); else S.lists.push(clone(l)); });
    S.places = S.places.filter(p => p.id !== 'P1');
    SEED.places.forEach(p => { if (!S.places.some(x => x.id === p.id)) S.places.push(clone(p)); });
    S.seedVersion = SEED.version;
  }
  migrate(); await save();
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
  V.view = S.session && me() ? 'home' : 'login';
  render();
  window.addEventListener('online', () => autoSync());
  autoSync();
}

const NO_NAV = ['login', 'insp', 'finish', 'report', 'editlist', 'editfac', 'printlist', 'batch'];
function render() {
  const v = V.view;
  const views = {
    login: viewLogin, home: viewHome, inspections: viewInspections, admin: viewAdmin, new: viewNew, insp: viewInsp, finish: viewFinish,
    report: viewReport, lists: viewLists, editlist: viewEditList, places: viewPlaces, users: viewUsers, settings: viewSettings,
    facs: viewFacs, editfac: viewEditFac, batch: viewBatch, printlist: viewPrintList
  };
  if (['home', 'inspections', 'admin'].includes(v)) V.tab = v;
  const h = (views[v] || viewLogin)();
  const keep = V.keepScroll, y = window.scrollY;
  app().innerHTML = h + (NO_NAV.includes(V.view) ? '' : nav());
  if (keep) window.scrollTo(0, y); else window.scrollTo(0, 0);
  V.keepScroll = false;
  document.body.classList.toggle('nosup', !(S.session && isSup()));
  if (V.view === 'finish') initSig();
}
const rerender = () => { V.keepScroll = true; render(); };

/* ===== الرئيسية والتفتيشات ===== */
function viewHome() {
  const mine = S.inspections.filter(i => i.inspectorId === S.session);
  const drafts = groupBatches(mine).filter(b => b.some(i => i.status === 'draft'));
  const pending = S.inspections.filter(i => i.status === 'done' && !i.synced).length;
  return bar(`مرحباً ${me().name}`) + `<div class="wrap">
  <button class="btn block" style="padding:18px;font-size:18px" data-act="new">＋ بدء تفتيش جديد</button>
  ${drafts.length ? `<div class="card" style="margin-top:12px"><h3>تفتيشات غير مكتملة</h3>${drafts.map(b => `<div class="listrow"><div class="sp"><b>${esc(b[0].header.place)}</b><div class="mut">${esc(b[0].header.date)} ${esc(b[0].header.time)} · اكتملت ${b.filter(i => i.status === 'done').length} من ${b.length} قوائم</div></div><button class="btn sm" data-act="openbatch" data-b="${b[0].batchId || b[0].id}">متابعة</button></div>`).join('')}</div>` : ''}
  <div class="card" style="margin-top:12px"><h3>حالة المزامنة</h3><p class="mut">${S.settings.syncUrl ? `بانتظار الرفع: ${pending} تفتيش` : 'المزامنة غير مفعّلة، البيانات محفوظة على هذا الهاتف فقط.'}</p>
  ${S.settings.syncUrl ? `<button class="btn sec sm" data-act="sync">مزامنة الآن</button>` : ''}</div></div>`;
}
function viewInspections() {
  const done = S.inspections.filter(i => i.status === 'done');
  if (!isSup()) {
    const mine = groupBatches(done.filter(i => i.inspectorId === S.session)).sort((x, y) => Math.max(...y.map(i => i.finishedAt)) - Math.max(...x.map(i => i.finishedAt)));
    return bar('التفتيشات المكتملة') + `<div class="wrap"><p class="mut">أرسل التفتيش المكتمل إلى المشرف بزر «مشاركة مع المشرف». التقرير الشامل والطباعة من اختصاص المشرف.</p>${mine.length ? mine.map(b => {
      const h = b[0].header; const ids = b.map(i => i.id).join(',');
      return `<div class="card"><div class="row"><b class="sp">${esc(h.place)}</b>${b.some(i => i.result.veto) ? '<span class="tag bad">بوابة حرجة</span>' : ''}</div>
      <div class="mut">${esc(h.date)} ${esc(h.time)}</div>
      ${b.map(i => `<div class="row" style="margin-top:6px"><span class="sp">${esc(i.snap.title)}</span><span class="tag ${i.result.bandCls}">${i.result.score}%</span></div>`).join('')}
      <div class="row" style="margin-top:8px"><button class="btn sm" data-act="share" data-ids="${ids}">مشاركة مع المشرف</button><button class="btn sec sm" data-act="rep" data-ids="${ids}" data-back="inspections">عرض على الشاشة</button></div></div>`;
    }).join('') : '<p class="mut">لا توجد تفتيشات مكتملة بعد.</p>'}</div>`;
  }
  const rounds = groupRounds(done).sort((x, y) => Math.max(...y.items.map(i => i.finishedAt || 0)) - Math.max(...x.items.map(i => i.finishedAt || 0)));
  const today = todayStr(); const tr = rounds.filter(r => r.items[0].header.date === today);
  const placesToday = distinct(tr.map(r => r.items[0].header.place));
  const notYet = S.places.filter(p => p.listIds.length && !placesToday.includes(p.name)).map(p => p.name);
  const todayCard = `<div class="card"><h3>جولة اليوم (${esc(today)})</h3>${tr.length ? tr.map(r => { const m = missingLists(r.items); return `<div class="row" style="padding:4px 0"><b class="sp">${esc(r.items[0].header.place)}</b><span class="tag ${m.length ? 'warn' : 'ok'}">${m.length ? 'ناقصة: ' + m.length : 'مكتملة'}</span></div>${m.length ? `<div class="mut">لم تُستلم: ${m.map(esc).join('، ')}</div>` : ''}`; }).join('') : '<p class="mut">لا توجد تفتيشات اليوم بعد.</p>'}
  ${notYet.length ? `<div class="mut" style="margin-top:6px">أماكن لم تُفتَّش اليوم: ${notYet.map(esc).join('، ')}</div>` : ''}</div>`;
  return bar('التفتيشات المكتملة') + `<div class="wrap">
  <div class="row" style="margin-bottom:10px"><button class="btn sm" data-act="importpick">استيراد تفتيشات من مفتش</button><input type="file" id="impf" accept=".json,application/json" multiple style="display:none"></div>
  ${todayCard}${rounds.length ? rounds.map(r => {
    const h = r.items[0].header; const ids = r.items.map(i => i.id).join(','); const m = missingLists(r.items);
    return `<div class="card"><div class="row"><b class="sp">${esc(h.place)}</b>${r.items.some(i => i.result.veto) ? '<span class="tag bad">بوابة حرجة</span>' : ''}</div>
    <div class="mut">${esc(h.date)} · ${r.items.length} قائمة${m.length ? ` · ناقصة: ${m.map(esc).join('، ')}` : ''}</div>
    ${r.items.map(i => `<div class="row" style="margin-top:6px"><span class="sp">${esc(i.snap.title)}<span class="mut"> · ${esc(i.header.inspector)} · ${esc(i.header.time)}</span></span><span class="tag ${i.result.bandCls}">${i.result.score}%</span></div>`).join('')}
    <div class="row" style="margin-top:8px"><button class="btn sm" data-act="rep" data-ids="${ids}" data-back="inspections">${r.items.length > 1 ? 'التقرير الشامل' : 'عرض التقرير'}</button><button class="btn sm bad" data-act="delids" data-ids="${ids}">حذف</button></div></div>`;
  }).join('') : '<p class="mut">لا توجد تفتيشات مكتملة بعد. استورد ملفات المفتشين أو أجرِ تفتيشاً بنفسك.</p>'}</div>`;
}

/* ===== بدء تفتيش: اختيار المكان والقوائم ===== */
function viewNew() {
  const units = unitsForMe();
  const p = units.find(x => x.id === V.newPlace) || units[0]; V.newPlace = p ? p.id : null;
  const ls = p ? p.listIds.map(id => S.lists.find(l => l.id === id)).filter(Boolean) : [];
  if (p && V.newSelFor !== p.id) { V.newSel = ls.map(l => l.id); V.newSelFor = p.id; }
  const fac = p ? facOf(p.facilityId) : null;
  return bar('تفتيش جديد', 'home') + `<div class="wrap"><div class="card">
  <label class="f">المكان / القسم</label><select id="np">${units.map(x => `<option value="${x.id}" ${p && x.id === p.id ? 'selected' : ''}>${esc(x.name)}${S.facilities.length > 1 ? ' (' + esc(facOf(x.facilityId).name) + ')' : ''}</option>`).join('')}</select>
  ${p ? `<p class="mut" style="margin-top:10px">المنشأة: ${esc(fac.name || 'غير محددة')}<br>العاملون: ${esc(p.staff)} · الورديات: ${esc(p.shifts)} · المسؤول: ${esc(p.responsible || 'غير محدد')}</p>
  <h3 style="margin-top:12px">قوائم التحقق</h3>
  ${ls.length ? ls.map(l => `<div class="row" style="padding:6px 0"><label class="row sp" style="gap:8px"><input type="checkbox" data-ms="newSel" data-tgt="nv" data-val="${l.id}" ${V.newSel.includes(l.id) ? 'checked' : ''}> <span>${esc(l.title)}</span></label>${isSup() ? `<button class="btn sec sm" data-act="printlist" data-id="${l.id}" data-place="${p.id}" data-back="new">طباعة</button>` : ''}</div>`).join('') : '<p class="mut">لا توجد قوائم مرتبطة بهذا المكان. اربطها من الإدارة ثم أماكن التفتيش.</p>'}` : '<p class="mut">لا توجد أماكن متاحة لك. يحددها المشرف من الإدارة.</p>'}
  <button class="btn block" style="margin-top:12px" data-act="startb" ${p && ls.length ? '' : 'disabled'}>ابدأ التفتيش</button></div></div>`;
}
function startBatch(placeId, listIds) {
  const p = S.places.find(x => x.id === placeId); const fac = facOf(p.facilityId); const t = nowParts(); const batchId = uid('B'); const ids = [];
  listIds.forEach(lid => {
    const l = S.lists.find(x => x.id === lid); if (!l) return;
    const insp = { id: uid('N'), batchId, listId: lid, placeId: p.id, snap: clone(l), fac: clone(fac), status: 'draft', synced: false, inspectorId: S.session,
      header: { facility: fac.name || S.settings.facility, place: p.name, dept: p.dept, staff: p.staff, shifts: p.shifts, responsible: p.responsible, inspector: me().name, date: t.date, time: t.time },
      answers: {}, esc: {}, sig: {}, startedAt: Date.now() };
    S.inspections.push(insp); ids.push(insp.id);
  });
  save(); V.batch = batchId;
  if (ids.length === 1) { V.cur = ids[0]; V.view = 'insp'; } else V.view = 'batch';
  render();
}
function viewBatch() {
  const arr = S.inspections.filter(i => (i.batchId || i.id) === V.batch);
  if (!arr.length) { V.view = 'home'; return viewHome(); }
  const h = arr[0].header; const done = arr.filter(i => i.status === 'done');
  return bar('قوائم هذا التفتيش', 'home') + `<div class="wrap"><div class="card"><b>${esc(h.place)}</b><div class="mut">${esc(h.date)} ${esc(h.time)} · ${esc(h.inspector)}</div></div>
  ${arr.map(i => { const r = compute(i.snap, i.answers, i.esc); return `<div class="card"><div class="row"><b class="sp">${esc(i.snap.title)}</b>${i.status === 'done' ? `<span class="tag ${i.result.bandCls}">${i.result.score}%</span>` : `<span class="mut">${r.answered} من ${r.total}</span>`}</div>
   <div class="pbar" style="margin:8px 0"><i style="width:${i.status === 'done' ? 100 : (r.total ? r.answered / r.total * 100 : 0)}%"></i></div>
   <div class="row">${i.status === 'done' ? `<button class="btn sm" data-act="rep" data-ids="${i.id}" data-back="batch">التقرير</button>` : `<button class="btn sm" data-act="open" data-id="${i.id}">${r.answered ? 'متابعة' : 'ابدأ'}</button>`}</div></div>`; }).join('')}
  ${isSup() ? `<button class="btn block" data-act="rep" data-ids="${done.map(i => i.id).join(',')}" data-back="batch" ${done.length ? '' : 'disabled'}>التقرير الشامل (${done.length} من ${arr.length})</button>` : `<button class="btn block" data-act="share" data-ids="${done.map(i => i.id).join(',')}" ${done.length ? '' : 'disabled'}>مشاركة مع المشرف (${done.length} من ${arr.length})</button>`}</div>`;
}
const _viewInsp = viewInsp;
viewInsp = function () {
  const i = cur(); V.batch = i.batchId || i.id;
  const h = _viewInsp();
  return batchOf(i).length > 1 ? h.replace('data-act="go" data-v="home"', 'data-act="go" data-v="batch"') : h;
};
function finalize() {
  const i = cur(); i.result = compute(i.snap, i.answers, i.esc); i.status = 'done'; i.finishedAt = Date.now(); i.synced = false; save();
  toast('تم حفظ التفتيش'); autoSync();
  if (batchOf(i).length > 1) { V.batch = i.batchId; V.view = 'batch'; }
  else { V.rep = { ids: [i.id] }; V.back = 'inspections'; V.view = 'report'; }
  render();
}

/* ===== التقرير (يبدأ ببيانات المنشأة، ويشمل كل قوائم المكان) ===== */
function facilityBlock(f) {
  if (!f) return '';
  const st = f.staff || {}; const c = f.contacts || {};
  const total = toNum(st.permanent) + toNum(st.insured) + toNum(st.temporary);
  const rowsTxt = v => (v || []).filter(r => r.n || r.c).map(r => `${esc(r.n)}: ${esc(r.c)}`).join('، ');
  const venues = (f.venues || []).map(v => {
    const vt = (VENUE_TYPES[v.type] || { name: v.type }).name;
    const facts = v.fields.map(fl => { const t = fl.t === 'rows' ? rowsTxt(fl.v) : esc(fl.v); return t ? `${esc(fl.label)}: ${t}` : ''; }).filter(Boolean).join(' · ');
    return `<tr><td>${esc(vt)}${v.name ? ' (' + esc(v.name) + ')' : ''}</td><td>${facts || '-'}</td></tr>`;
  }).join('');
  const contacts = [c.phone && `هاتف أرضي: ${esc(c.phone)}`, c.fax && `فاكس: ${esc(c.fax)}`, c.email && `بريد إلكتروني: ${esc(c.email)}`, ...(c.extra || []).filter(x => x.label || x.value).map(x => `${esc(x.label)}: ${esc(x.value)}`)].filter(Boolean).join(' · ');
  const transport = (f.transport || []).filter(Boolean).map(esc).join('، ');
  return `<div class="card"><h3>بيانات المنشأة</h3>
  <table class="rep"><tr><th>اسم المنشأة</th><td>${esc(f.name)}</td><th>العنوان</th><td>${esc(f.address)}</td></tr>
  <tr><th>اسم المدير</th><td>${esc(f.manager)}</td><th>عدد معاونيه</th><td>${esc(f.assistants)}</td></tr>
  <tr><th>العاملون</th><td colspan="3">مثبت: ${esc(st.permanent || 0)} · مؤمَّن: ${esc(st.insured || 0)} · مؤقت: ${esc(st.temporary || 0)} · الإجمالي: ${total} · أفراد الأمن: ${esc(st.security || 0)}</td></tr>
  <tr><th>الخدمات المقدمة</th><td colspan="3">${(f.services || []).map(esc).join('، ') || '-'}</td></tr></table>
  ${venues ? `<table class="rep"><tr><th style="width:30%">المرفق</th><th>البيانات</th></tr>${venues}</table>` : ''}
  ${contacts ? `<p><b>وسائل الاتصال:</b> ${contacts}</p>` : ''}${transport ? `<p><b>وسائل المواصلات:</b> ${transport}</p>` : ''}</div>`;
}
function reportSection(i, multi) {
  const r = i.result || compute(i.snap, i.answers, i.esc);
  const fails = i.snap.axes.flatMap(a => a.items.map(it => ({ it, x: i.answers[it.id] })).filter(o => o.x && (o.x.v === 'ف' || o.x.v === 'ت')));
  const hh = i.header;
  return `<div class="${multi ? 'pb' : ''}"><h2 style="text-align:center">${esc(i.snap.title)}</h2>
  ${multi ? `<table class="rep"><tr><th>القائم بالتفتيش</th><td>${esc(hh.inspector)}</td><th>الساعة</th><td>${esc(hh.time)}</td></tr><tr><th>عدد العاملين</th><td>${esc(hh.staff)}</td><th>عدد الورديات</th><td>${esc(hh.shifts)}</td></tr><tr><th>المسؤول عن المكان</th><td colspan="3">${esc(hh.responsible)}</td></tr></table>` : ''}
  <div class="card"><div class="score">${r.score}%</div><div style="text-align:center"><span class="tag ${r.bandCls}">${r.band}</span></div></div>
  ${r.veto ? `<div class="veto"><b>البوابة الحرجة مفعّلة</b>${r.critFails.map(c => `<div>• ${esc(c.text)}</div>`).join('')}${r.escHits.map(c => `<div>• تصعيد فوري: ${esc(c)}</div>`).join('')}</div>` : ''}
  <table class="rep"><tr><th>المحور</th><th>الوزن</th><th>النسبة</th></tr>${r.axes.map(a => `<tr><td>${esc(a.name)}</td><td>${a.weight}</td><td>${a.pct === null ? 'غير منطبق' : a.pct.toFixed(1) + '%'}</td></tr>`).join('')}</table>
  <h3>الملاحظات والإجراءات المطلوبة (${fails.length})</h3>
  ${fails.length ? `<table class="rep"><tr><th>البند</th><th>التصنيف</th><th>التقدير</th><th>الملاحظة</th></tr>${fails.map(o => `<tr><td>${esc(o.it.text)}${(o.x.photos || []).map(p => `<br><img src="${esc(p)}" style="width:90px;margin:3px;border-radius:6px">`).join('')}</td><td>${CLS_NAME[o.it.cls]}</td><td>${o.x.v}</td><td>${esc(o.x.note || '')}</td></tr>`).join('')}</table>` : '<p class="mut">لا توجد ملاحظات.</p>'}
  <div class="grid2"><div><b>توقيع المفتش</b><br>${i.sig.inspector ? `<img src="${esc(i.sig.inspector)}" style="width:100%;max-height:110px;object-fit:contain">` : ''}</div><div><b>توقيع المسؤول</b><br>${i.sig.responsible ? `<img src="${esc(i.sig.responsible)}" style="width:100%;max-height:110px;object-fit:contain">` : ''}</div></div></div>`;
}
function viewReport() {
  const list = ((V.rep && V.rep.ids) || [V.cur]).map(id => S.inspections.find(i => i.id === id)).filter(i => i && i.status === 'done')
    .sort((a, b) => (a.header.time || '').localeCompare(b.header.time || ''));
  if (!list.length) return bar('التقرير', V.back || 'inspections') + '<div class="wrap"><p class="mut">لا توجد تفتيشات مكتملة لعرضها.</p></div>';
  const i0 = list[0], multi = list.length > 1;
  const sup = isSup();
  if (multi && !sup) return bar('التقرير', V.back || 'inspections') + '<div class="wrap"><p class="mut">التقرير الشامل متاح للمشرف فقط.</p></div>';
  const key = rkey(i0); S.heads = S.heads || {};
  const h = S.heads[key] = Object.assign({ staff: i0.header.staff, shifts: i0.header.shifts, responsible: i0.header.responsible }, S.heads[key] || {}); V.hd = h;
  const fac = i0.fac || facOf((placeOfInsp(i0) || {}).facilityId);
  const hv = (k) => sup ? `<input type="text" data-tgt="hd" data-bind="${k}" value="${esc(h[k] ?? '')}" style="padding:4px 6px">` : esc(h[k]);
  const minI = list.reduce((m, i) => (i.result.score < m.result.score ? i : m), list[0]);
  const overall = bandFor(minI.result.score); const anyVeto = list.some(i => i.result.veto);
  return `<div class="overlay"><div class="bar noprint"><button data-act="go" data-v="${V.back || 'inspections'}">رجوع</button><h1>${multi ? 'التقرير الشامل' : 'التقرير'}</h1>${sup ? '<button data-act="print">طباعة / PDF</button>' : ''}</div><div class="wrap">
  ${facilityBlock(fac)}
  <table class="rep"><tr><th>المنشأة</th><td>${esc(i0.header.facility)}</td><th>المكان / القسم</th><td>${esc(i0.header.place)}</td></tr>
  <tr><th>عدد العاملين</th><td>${hv('staff')}</td><th>عدد الورديات</th><td>${hv('shifts')}</td></tr>
  <tr><th>المسؤول عن المكان</th><td>${hv('responsible')}</td><th>القائمون بالتفتيش</th><td>${distinct(list.map(i => i.header.inspector)).map(esc).join('، ')}</td></tr>
  <tr><th>التاريخ</th><td>${esc(i0.header.date)}</td><th>الساعة</th><td>${distinct(list.map(i => i.header.time)).map(esc).join('، ')}</td></tr></table>
  ${multi ? `<div class="card"><div class="mut" style="text-align:center">التقدير العام للمكان (أدنى تقدير بين القوائم)</div><div style="text-align:center;margin-top:6px"><span class="tag ${overall[2]}" style="font-size:18px">${overall[1]}</span></div><div class="mut" style="text-align:center;margin-top:6px">أدنى درجة: ${minI.result.score}% في «${esc(minI.snap.title)}»</div></div>
  ${anyVeto ? '<div class="veto"><b>توجد بوابة حرجة مفعّلة في إحدى القوائم، راجع تفاصيلها أدناه.</b></div>' : ''}
  <h3>ملخص جميع القوائم</h3><table class="rep"><tr><th>القائمة</th><th>المفتش</th><th>الساعة</th><th>الدرجة</th><th>التقدير</th><th>البوابة الحرجة</th></tr>${list.map(i => `<tr><td>${esc(i.snap.title)}</td><td>${esc(i.header.inspector)}</td><td>${esc(i.header.time)}</td><td>${i.result.score}%</td><td>${i.result.band}</td><td>${i.result.veto ? 'مفعّلة' : 'لا'}</td></tr>`).join('')}</table>
  ${(() => { const m = missingLists(list); return m.length ? `<p class="mut">قوائم لم يُستلم تفتيشها لهذه الجولة: ${m.map(esc).join('، ')}</p>` : ''; })()}` : ''}
  ${list.map(i => reportSection(i, multi)).join('')}</div></div>`;
}

/* ===== طباعة القائمة نفسها ===== */
function viewPrintList() {
  const l = S.lists.find(x => x.id === V.pl.listId); const p = S.places.find(x => x.id === V.pl.placeId);
  const fac = p ? facOf(p.facilityId) : null; const b = '__________';
  const hd = (a, c, d, e) => `<tr><th>${a}</th><td>${c}</td><th>${d}</th><td>${e}</td></tr>`;
  const cell = (cls, o) => OPTS[cls].includes(o) ? '' : ' style="background:#ddd"';
  let n = 0;
  return `<div class="overlay"><div class="bar noprint"><button data-act="go" data-v="${V.pl.back || 'lists'}">رجوع</button><h1>طباعة القائمة</h1>${isSup() ? '<button data-act="print">طباعة / PDF</button>' : ''}</div><div class="wrap">
  <h2 style="text-align:center">${esc(l.title)}</h2>
  <table class="rep">${hd('المنشأة', esc((fac && fac.name) || b), 'المكان / القسم', esc(p ? p.name : b))}${hd('عدد العاملين', esc(p && p.staff ? p.staff : b), 'عدد الورديات', esc(p && p.shifts ? p.shifts : b))}${hd('المسؤول عن المكان', esc(p && p.responsible ? p.responsible : b), 'القائم بالتفتيش', b)}${hd('التاريخ', b, 'الساعة', b)}</table>
  <p class="mut">م = مُرضٍ · ت = يحتاج إلى تحسين · ف = تصحيح فوري · غ = غير منطبق · المظلل: خيار غير متاح لهذا البند</p>
  <table class="rep"><tr><th>#</th><th>البند</th><th>التصنيف</th><th>م</th><th>ت</th><th>ف</th><th>غ</th><th>الإجراء المتخذ</th></tr>
  ${l.axes.map(a => `<tr><th colspan="8">${esc(a.name)} (وزن المحور: ${a.weight})</th></tr>${a.items.map(it => `<tr><td>${++n}</td><td>${esc(it.text)}</td><td>${CLS_NAME[it.cls]}</td><td${cell(it.cls, 'م')}></td><td${cell(it.cls, 'ت')}></td><td${cell(it.cls, 'ف')}></td><td${cell(it.cls, 'غ')}></td><td style="min-width:90px"></td></tr>`).join('')}`).join('')}</table>
  ${(l.escalation || []).length ? `<h3>حالات تستوجب التصعيد الفوري إلى الإدارة</h3><ul>${l.escalation.map(e => `<li>☐ ${esc(e)}</li>`).join('')}</ul>` : ''}
  <div class="grid2" style="margin-top:20px"><div>ملاحظات إضافية: ${b}${b}</div><div>توقيع المفتش: ${b}<br>اعتماد المسؤول: ${b}</div></div></div></div>`;
}

/* ===== قوائم التحقق: تعديل ونسخ وطباعة وحذف ===== */
function viewLists() {
  return bar('قوائم التحقق', 'admin') + `<div class="wrap"><button class="btn block" data-act="newlist">＋ قائمة جديدة</button><div class="card" style="margin-top:12px">${S.lists.map(l => `<div class="listrow" style="flex-wrap:wrap"><div class="sp" style="min-width:60%"><b>${esc(l.title)}</b><div class="mut">${l.axes.length} محاور · ${l.axes.reduce((n, a) => n + a.items.length, 0)} بنداً · إصدار ${l.version}</div></div>
  <div class="row"><button class="btn sm" data-act="editlist" data-id="${l.id}">تعديل</button><button class="btn sec sm" data-act="duplist" data-id="${l.id}">نسخ</button>${isSup() ? `<button class="btn sec sm" data-act="printlist" data-id="${l.id}" data-back="lists">طباعة</button>` : ''}<button class="btn bad sm" data-act="dellist2" data-id="${l.id}">حذف</button></div></div>`).join('')}</div></div>`;
}

/* ===== المنشآت: الملف التعريفي ===== */
function viewAdmin() {
  const row = (v, t, d) => `<div class="card row" data-act="go" data-v="${v}" style="cursor:pointer"><div class="sp"><b>${t}</b><div class="mut">${d}</div></div><span>‹</span></div>`;
  return bar('الإدارة') + `<div class="wrap">${row('lists', 'قوائم التحقق', 'إنشاء قوائم جديدة أو تعديل أو طباعة أو حذف الموجودة')}${row('facs', 'المنشآت ووصف الأماكن', 'بيانات المنشأة والعاملين والخدمات والمرافق ووسائل الاتصال')}${row('places', 'أماكن التفتيش', 'ربط كل مكان بقوائم التحقق وبالمفتشين')}${row('users', 'المستخدمون والصلاحيات', 'المشرف والمفتشون')}${row('settings', 'الإعدادات والمزامنة', 'اسم المنشأة والنسخ الاحتياطي')}</div>`;
}
function viewFacs() {
  return bar('المنشآت', 'admin') + `<div class="wrap"><button class="btn block" data-act="newfac">＋ منشأة جديدة</button>${S.facilities.map(f => `<div class="card" style="margin-top:12px"><b>${esc(f.name || 'منشأة بلا اسم')}</b><div class="mut">${esc(f.address || '')}${f.manager ? ' · المدير: ' + esc(f.manager) : ''}</div>
  <div class="mut">${(f.services || []).length} خدمات · ${(f.venues || []).length} مرافق · ${S.places.filter(p => p.facilityId === f.id).length} أماكن تفتيش</div>
  <div class="row" style="margin-top:8px"><button class="btn sm" data-act="editfac" data-id="${f.id}">تعديل</button><button class="btn sec sm" data-act="genunits" data-id="${f.id}">توليد أماكن التفتيش</button><button class="btn bad sm" data-act="delfac" data-id="${f.id}">حذف</button></div></div>`).join('')}</div>`;
}
function fieldRow(vi, fi, fl) {
  const base = `venues.${vi}.fields.${fi}`; const f = V.ef;
  const del = `<button class="btn bad sm" data-act="flddel" data-vi="${vi}" data-fi="${fi}">حذف الحقل</button>`;
  if (fl.t === 'rows') {
    const sum = (fl.v || []).reduce((s, r) => s + toNum(r.c), 0);
    return `<div class="item"><div class="row"><b class="sp">${esc(fl.label)}</b>${del}</div>
    ${fl.v.map((r, ri) => `<div class="row" style="margin-top:6px;flex-wrap:nowrap"><div style="flex:1">${inp('ef', f, `${base}.v.${ri}.n`, { ph: 'الاسم' })}</div><div style="width:90px">${inp('ef', f, `${base}.v.${ri}.c`, { type: 'number', ph: 'العدد' })}</div><button class="btn sec sm" data-act="rowdel" data-vi="${vi}" data-fi="${fi}" data-ri="${ri}">×</button></div>`).join('')}
    <div class="row" style="margin-top:6px"><button class="btn sec sm" data-act="rowadd" data-vi="${vi}" data-fi="${fi}">＋ سطر</button><span class="mut">المجموع: <b data-sumfor="${base}.v">${sum}</b></span></div></div>`;
  }
  return `<div class="item"><div class="row"><label class="f sp">${esc(fl.label)}</label>${del}</div>${inp('ef', f, `${base}.v`, { type: fl.t === 'number' ? 'number' : 'text' })}</div>`;
}
function venueCard(vi) {
  const f = V.ef, v = f.venues[vi]; const vt = VENUE_TYPES[v.type] || { name: v.type };
  return `<details class="axis" data-dk="${v.id}" ${V.det[v.id] ? 'open' : ''}><summary><span>${esc(vt.name)}${v.name ? ': ' + esc(v.name) : ''}</span></summary>
  <div class="item"><label class="f">اسم المرفق</label>${inp('ef', f, `venues.${vi}.name`, { ph: 'مثال: مطعم النيل' })}</div>
  ${v.fields.map((fl, fi) => fieldRow(vi, fi, fl)).join('')}
  <div class="item"><label class="f">إضافة حقل جديد</label><div class="row" style="flex-wrap:nowrap"><input type="text" id="nf_${v.id}" placeholder="اسم الحقل" style="flex:1"><select id="nt_${v.id}" style="width:auto"><option value="text">نص</option><option value="number">رقم</option><option value="rows">جدول (اسم وعدد)</option></select><button class="btn sec sm" data-act="fldadd" data-vi="${vi}" data-vid="${v.id}">إضافة</button></div></div>
  <div class="item"><button class="btn bad sm" data-act="venuedel" data-vi="${vi}">حذف هذا المرفق</button></div></details>`;
}
function viewEditFac() {
  const f = V.ef; const st = f.staff; const total = toNum(st.permanent) + toNum(st.insured) + toNum(st.temporary);
  const allSvc = [...SERVICES, ...f.services.filter(s => !SERVICES.includes(s))];
  const c = f.contacts;
  return bar(S.facilities.some(x => x.id === f.id) ? 'تعديل المنشأة' : 'منشأة جديدة', 'home') + `<div class="wrap">
  <div class="card"><h3>بيانات المنشأة</h3><div class="grid2"><div><label class="f">اسم المنشأة</label>${inp('ef', f, 'name')}</div><div><label class="f">العنوان</label>${inp('ef', f, 'address')}</div>
  <div><label class="f">اسم المدير</label>${inp('ef', f, 'manager')}</div><div><label class="f">عدد معاونيه</label>${inp('ef', f, 'assistants', { type: 'number' })}</div></div></div>
  <div class="card"><h3>العاملون</h3><div class="grid2"><div><label class="f">مثبت</label>${inp('ef', f, 'staff.permanent', { type: 'number' })}</div><div><label class="f">مؤمَّن</label>${inp('ef', f, 'staff.insured', { type: 'number' })}</div>
  <div><label class="f">مؤقت</label>${inp('ef', f, 'staff.temporary', { type: 'number' })}</div><div><label class="f">عدد أفراد الأمن</label>${inp('ef', f, 'staff.security', { type: 'number' })}</div></div>
  <p class="mut" style="margin-top:8px">إجمالي العاملين (مثبت ومؤمَّن ومؤقت): <b id="stTotal">${total}</b></p></div>
  <div class="card"><h3>الخدمات المقدمة</h3>
  <details class="axis ms" data-dk="svc" ${V.det.svc ? 'open' : ''}><summary><span class="selTxt">${f.services.length ? f.services.map(esc).join('، ') : 'اختر الخدمات'}</span></summary>
  ${allSvc.map(s => `<label class="item row" style="gap:8px"><input type="checkbox" data-ms="services" data-tgt="ef" data-val="${esc(s)}" ${f.services.includes(s) ? 'checked' : ''}> <span>${esc(s)}</span></label>`).join('')}
  <div class="item row" style="flex-wrap:nowrap"><input type="text" id="newsvc" placeholder="خدمة أخرى" style="flex:1"><button class="btn sec sm" data-act="addsvc">إضافة</button></div></details></div>
  <div class="card"><h3>المرافق التي تقدم الخدمات</h3>
  <div class="row" style="flex-wrap:nowrap;margin-bottom:10px"><select id="vtype" style="flex:1">${Object.entries(VENUE_TYPES).map(([k, t]) => `<option value="${k}">${t.name}</option>`).join('')}</select><button class="btn sm" data-act="addvenue">＋ إضافة مرفق</button></div>
  ${f.venues.length ? f.venues.map((v, vi) => venueCard(vi)).join('') : '<p class="mut">لم تُضف مرافق بعد. الحقول الظاهرة عند الإضافة مقترحة ويمكنك تعديلها وإضافة حقول جديدة.</p>'}</div>
  <div class="card"><h3>وسائل الاتصال</h3><div class="grid2"><div><label class="f">هاتف أرضي</label>${inp('ef', f, 'contacts.phone')}</div><div><label class="f">فاكس</label>${inp('ef', f, 'contacts.fax')}</div></div>
  <label class="f" style="margin-top:8px">بريد إلكتروني</label>${inp('ef', f, 'contacts.email')}
  ${c.extra.map((x, k) => `<div class="row" style="margin-top:8px;flex-wrap:nowrap"><div style="flex:1">${inp('ef', f, `contacts.extra.${k}.label`, { ph: 'الوسيلة' })}</div><div style="flex:1">${inp('ef', f, `contacts.extra.${k}.value`, { ph: 'البيان' })}</div><button class="btn sec sm" data-act="cexdel" data-k="${k}">×</button></div>`).join('')}
  <button class="btn sec sm" style="margin-top:8px" data-act="cexadd">＋ وسيلة اتصال أخرى</button></div>
  <div class="card"><h3>وسائل المواصلات</h3>
  ${f.transport.map((x, k) => `<div class="row" style="margin-bottom:6px;flex-wrap:nowrap"><div style="flex:1">${inp('ef', f, `transport.${k}`, { ph: 'اكتب الوسيلة' })}</div><button class="btn sec sm" data-act="trdel" data-k="${k}">×</button></div>`).join('')}
  <button class="btn sec sm" data-act="tradd">＋ وسيلة أخرى</button></div>
  <div class="row"><button class="btn sp" data-act="savefac">حفظ المنشأة</button><button class="btn sec" data-act="go" data-v="home">إلغاء</button></div></div>`;
}

/* ===== أماكن التفتيش وربطها بالقوائم والمفتشين ===== */
function suggestLists(f, venueId) {
  const v = (f.venues || []).find(x => x.id === venueId); if (!v || !VENUE_UNITS[v.type]) return [];
  return [...new Set(VENUE_UNITS[v.type](v).flatMap(u => u.lists))].filter(id => S.lists.some(l => l.id === id));
}
function viewPlaces() {
  const ed = V.editPlace; const f = ed ? facOf(ed.facilityId) : null;
  return bar('أماكن التفتيش', 'admin') + `<div class="wrap"><div class="row"><button class="btn sp" data-act="newunit">＋ مكان تفتيش</button></div>
  <p class="mut">مكان التفتيش هو الموقع الذي يُفتَّش فعلياً (مثل المطبخ أو الاستقبال). اربط به قائمة تحقق أو أكثر وحدد المفتشين المسؤولين عنه. إن لم تحدد مفتشاً يراه جميع المفتشين.</p>
  ${ed ? `<div class="card"><h3>${ed.isNew ? 'مكان تفتيش جديد' : 'تعديل مكان تفتيش'}</h3><div class="grid2">
   <div><label class="f">المنشأة</label><select data-tgt="ep" data-bind="facilityId" data-rerender="1">${S.facilities.map(x => `<option value="${x.id}" ${x.id === ed.facilityId ? 'selected' : ''}>${esc(x.name || 'منشأة بلا اسم')}</option>`).join('')}</select></div>
   <div><label class="f">المرفق (اختياري)</label><select data-tgt="ep" data-bind="venueId"><option value="">بلا</option>${f.venues.map(v => `<option value="${v.id}" ${v.id === ed.venueId ? 'selected' : ''}>${esc((VENUE_TYPES[v.type] || {}).name)}${v.name ? ': ' + esc(v.name) : ''}</option>`).join('')}</select></div>
   <div><label class="f">اسم المكان</label>${inp('ep', ed, 'name')}</div><div><label class="f">القسم</label>${inp('ep', ed, 'dept')}</div>
   <div><label class="f">عدد العاملين</label>${inp('ep', ed, 'staff', { type: 'number' })}</div><div><label class="f">عدد الورديات</label>${inp('ep', ed, 'shifts', { type: 'number' })}</div></div>
   <label class="f" style="margin-top:8px">المسؤول عن المكان</label>${inp('ep', ed, 'responsible')}
   <h3 style="margin-top:12px">قوائم التحقق المرتبطة</h3>${S.lists.map(l => `<label class="row" style="gap:8px;padding:4px 0"><input type="checkbox" data-ms="listIds" data-tgt="ep" data-val="${l.id}" ${ed.listIds.includes(l.id) ? 'checked' : ''}> <span>${esc(l.title)}</span></label>`).join('')}
   <button class="btn sec sm" style="margin-top:6px" data-act="suggest">اقتراح القوائم حسب نوع المرفق</button>
   <h3 style="margin-top:12px">المفتشون المسؤولون</h3>${S.users.map(u => `<label class="row" style="gap:8px;padding:4px 0"><input type="checkbox" data-ms="inspectorIds" data-tgt="ep" data-val="${u.id}" ${ed.inspectorIds.includes(u.id) ? 'checked' : ''}> <span>${esc(u.name)}</span></label>`).join('')}
   <div class="row" style="margin-top:12px"><button class="btn sp" data-act="saveunit">حفظ</button><button class="btn sec" data-act="cancelunit">إلغاء</button></div></div>` : ''}
  ${S.facilities.map(fc => { const ps = S.places.filter(p => p.facilityId === fc.id); return `<div class="card" style="margin-top:12px"><h3>${esc(fc.name || 'منشأة بلا اسم')}</h3>${ps.length ? ps.map(p => `<div class="listrow" style="flex-wrap:wrap"><div class="sp" style="min-width:55%"><b>${esc(p.name)}</b><div class="mut">القوائم: ${p.listIds.map(listTitle).filter(Boolean).map(esc).join('، ') || 'لا توجد'}</div><div class="mut">المفتشون: ${p.inspectorIds.map(id => (S.users.find(u => u.id === id) || {}).name).filter(Boolean).map(esc).join('، ') || 'الجميع'}</div></div>
   <div class="row"><button class="btn sm" data-act="editunit" data-id="${p.id}">تعديل</button><button class="btn bad sm" data-act="delunit" data-id="${p.id}">حذف</button></div></div>`).join('') : '<p class="mut">لا توجد أماكن تفتيش لهذه المنشأة.</p>'}</div>`; }).join('')}</div>`;
}

/* ===== المزامنة: تشمل بيانات المنشآت ===== */
async function pushConfig() { try { await api('saveConfig', { config: { lists: S.lists, places: S.places, users: S.users, facilities: S.facilities, facility: S.settings.facility } }); toast('تم رفع الإعدادات'); } catch (e) { toast('تعذر الرفع: ' + e.message); } }
async function pullConfig() {
  try {
    const j = await api('getConfig', {}); if (!j.config) return toast('لا توجد إعدادات محفوظة');
    S.lists = j.config.lists; S.places = j.config.places; S.users = j.config.users; if (j.config.facilities) S.facilities = j.config.facilities;
    if (j.config.facility) S.settings.facility = j.config.facility; migrate(); await save(); toast('تم سحب الإعدادات'); render();
  } catch (e) { toast('تعذر السحب: ' + e.message); }
}

/* ===== الأحداث ===== */
document.addEventListener('toggle', e => { const d = e.target; if (d && d.dataset && d.dataset.dk) V.det[d.dataset.dk] = d.open; }, true);
const refreshSums = path => { const pre = path.split('.v.')[0] + '.v'; const arr = val(V.ef, pre); const el = document.querySelector(`[data-sumfor="${pre}"]`); if (el && Array.isArray(arr)) el.textContent = arr.reduce((s, r) => s + toNum(r.c), 0); };
document.addEventListener('input', e => {
  const t = e.target; if (t.dataset.bind === undefined || t.tagName === 'SELECT') return;
  const o = bindTarget(t.dataset.tgt); if (!o) return; setPath(o, t.dataset.bind, t.value);
  if (t.dataset.tgt === 'hd') save();
  if (/\.v\.\d+\.c$/.test(t.dataset.bind)) refreshSums(t.dataset.bind);
  if (t.dataset.bind.startsWith('staff.')) { const s = V.ef.staff; const el = $('#stTotal'); if (el) el.textContent = toNum(s.permanent) + toNum(s.insured) + toNum(s.temporary); }
});
document.addEventListener('change', e => {
  const t = e.target;
  if (t.dataset.bind !== undefined && t.tagName === 'SELECT') {
    const o = bindTarget(t.dataset.tgt); setPath(o, t.dataset.bind, t.value);
    if (t.dataset.bind === 'facilityId') o.venueId = '';
    if (t.dataset.rerender) rerender();
  } else if (t.dataset.ms !== undefined) {
    const o = bindTarget(t.dataset.tgt); const arr = o[t.dataset.ms] || (o[t.dataset.ms] = []);
    const k = arr.indexOf(t.dataset.val);
    if (t.checked && k < 0) arr.push(t.dataset.val); if (!t.checked && k >= 0) arr.splice(k, 1);
    const st = t.closest('details') && t.closest('details').querySelector('.selTxt');
    if (st) st.textContent = arr.length ? arr.join('، ') : 'اختر الخدمات';
  }
});
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act]'); if (!t) return; const a = t.dataset.act, d = t.dataset;
  switch (a) {
    case 'share': shareInspections(d.ids.split(',').filter(Boolean)); break;
    case 'importpick': { const f = $('#impf'); if (f) f.click(); break; }
    case 'delids': if (confirm('حذف هذه التفتيشات من هذا الجهاز نهائياً؟')) { const ids = d.ids.split(','); S.inspections = S.inspections.filter(i => !ids.includes(i.id)); await save(); render(); } break;
    case 'openbatch': { const arr = S.inspections.filter(i => (i.batchId || i.id) === d.b); V.batch = d.b; if (arr.length === 1) { V.cur = arr[0].id; V.view = 'insp'; } else V.view = 'batch'; render(); break; }
    case 'startb': if (V.newSel && V.newSel.length) startBatch(V.newPlace, V.newSel); else toast('اختر قائمة واحدة على الأقل'); break;
    case 'rep': V.rep = { ids: d.ids.split(',').filter(Boolean) }; V.back = d.back || 'inspections'; V.view = 'report'; render(); break;
    case 'delbatch': if (confirm('حذف هذا التفتيش بكل قوائمه من هذا الجهاز نهائياً؟')) { S.inspections = S.inspections.filter(i => (i.batchId || i.id) !== d.b); await save(); render(); } break;
    case 'printlist': if (!isSup()) { toast('الطباعة متاحة للمشرف فقط'); break; } V.pl = { listId: d.id, placeId: d.place || '', back: d.back || 'lists' }; V.view = 'printlist'; render(); break;
    case 'dellist2': {
      const l = S.lists.find(x => x.id === d.id); const used = S.places.filter(p => p.listIds.includes(l.id));
      if (confirm(`حذف قائمة "${l.title}"؟` + (used.length ? `\nستُفصل عن ${used.length} من أماكن التفتيش.` : '') + '\nالتفتيشات السابقة تبقى محفوظة بنسختها.')) {
        S.lists = S.lists.filter(x => x.id !== l.id); S.places.forEach(p => { p.listIds = p.listIds.filter(id => id !== l.id); }); await save(); toast('تم حذف القائمة'); render();
      } break; }
    /* المنشآت */
    case 'newfac': V.ef = newFac(); V.det = {}; V.view = 'editfac'; render(); break;
    case 'editfac': V.ef = clone(S.facilities.find(f => f.id === d.id)); V.ef.contacts = V.ef.contacts || { phone: '', fax: '', email: '', extra: [] }; V.ef.contacts.extra = V.ef.contacts.extra || []; V.ef.transport = V.ef.transport && V.ef.transport.length ? V.ef.transport : ['']; V.det = {}; V.view = 'editfac'; render(); break;
    case 'delfac': { const f = S.facilities.find(x => x.id === d.id);
      if (S.places.some(p => p.facilityId === f.id)) toast('انقل أماكن التفتيش أو احذفها أولاً');
      else if (S.facilities.length < 2) toast('لا يمكن حذف المنشأة الوحيدة');
      else if (confirm(`حذف منشأة "${f.name}"؟`)) { S.facilities = S.facilities.filter(x => x.id !== f.id); await save(); render(); } break; }
    case 'addsvc': { const el = $('#newsvc'); const s = el.value.trim(); if (s && !V.ef.services.includes(s)) { V.ef.services.push(s); V.det.svc = true; rerender(); } break; }
    case 'addvenue': { const v = newVenue($('#vtype').value); V.ef.venues.push(v); V.det[v.id] = true; rerender(); break; }
    case 'venuedel': if (confirm('حذف هذا المرفق؟')) { V.ef.venues.splice(+d.vi, 1); rerender(); } break;
    case 'fldadd': { const label = $('#nf_' + d.vid).value.trim(); if (!label) return toast('اكتب اسم الحقل'); const tp = $('#nt_' + d.vid).value; V.ef.venues[+d.vi].fields.push({ id: uid('f'), label, t: tp, v: tp === 'rows' ? [{ n: '', c: '' }] : '' }); V.det[d.vid] = true; rerender(); break; }
    case 'flddel': if (confirm('حذف هذا الحقل؟')) { V.ef.venues[+d.vi].fields.splice(+d.fi, 1); rerender(); } break;
    case 'rowadd': V.ef.venues[+d.vi].fields[+d.fi].v.push({ n: '', c: '' }); rerender(); break;
    case 'rowdel': { const arr = V.ef.venues[+d.vi].fields[+d.fi].v; arr.splice(+d.ri, 1); if (!arr.length) arr.push({ n: '', c: '' }); rerender(); break; }
    case 'cexadd': V.ef.contacts.extra.push({ label: '', value: '' }); rerender(); break;
    case 'cexdel': V.ef.contacts.extra.splice(+d.k, 1); rerender(); break;
    case 'tradd': V.ef.transport.push(''); rerender(); break;
    case 'trdel': V.ef.transport.splice(+d.k, 1); if (!V.ef.transport.length) V.ef.transport.push(''); rerender(); break;
    case 'savefac': {
      const f = V.ef; if (!f.name.trim()) return toast('أدخل اسم المنشأة');
      f.transport = f.transport.map(x => x.trim()).filter(Boolean); f.contacts.extra = f.contacts.extra.filter(x => x.label.trim() || x.value.trim());
      f.venues.forEach(v => v.fields.forEach(fl => { if (fl.t === 'rows') { fl.v = fl.v.filter(r => String(r.n).trim() || String(r.c).trim()); if (!fl.v.length) fl.v = [{ n: '', c: '' }]; } }));
      const k = S.facilities.findIndex(x => x.id === f.id); if (k >= 0) S.facilities[k] = f; else S.facilities.push(f);
      S.places.filter(p => p.facilityId === f.id).forEach(() => {}); if (S.facilities[0].id === f.id) S.settings.facility = f.name;
      await save(); toast('تم حفظ المنشأة'); V.view = 'home'; render(); break; }
    case 'genunits': {
      const f = S.facilities.find(x => x.id === d.id); let made = 0; const noList = [];
      f.venues.forEach(v => {
        const mk = VENUE_UNITS[v.type]; const nm = (VENUE_TYPES[v.type] || {}).name;
        if (!mk) { noList.push(nm); return; }
        mk(v).forEach(u => {
          if (S.places.some(p => p.facilityId === f.id && p.name === u.name)) return;
          S.places.push({ id: uid('P'), facilityId: f.id, venueId: v.id, name: u.name, dept: u.dept, staff: '', shifts: '', responsible: '', listIds: u.lists.filter(id => S.lists.some(l => l.id === id)), inspectorIds: [] }); made++;
        });
      });
      await save(); V.view = 'places'; render();
      toast(`أُنشئ ${made} مكان تفتيش` + (noList.length ? `. لا توجد قوائم جاهزة لـ: ${[...new Set(noList)].join('، ')}` : '')); break; }
    /* أماكن التفتيش */
    case 'newunit': V.editPlace = { isNew: true, id: uid('P'), facilityId: S.facilities[0].id, venueId: '', name: '', dept: '', staff: '', shifts: '', responsible: '', listIds: [], inspectorIds: [] }; render(); break;
    case 'editunit': V.editPlace = clone(S.places.find(p => p.id === d.id)); render(); break;
    case 'cancelunit': V.editPlace = null; render(); break;
    case 'suggest': { const p = V.editPlace; const s = suggestLists(facOf(p.facilityId), p.venueId); if (!s.length) toast('لا توجد قوائم مقترحة لهذا المرفق، اختر يدوياً'); else { p.listIds = [...new Set([...p.listIds, ...s])]; rerender(); } break; }
    case 'saveunit': { const p = V.editPlace; if (!p.name.trim()) return toast('أدخل اسم المكان'); delete p.isNew; const k = S.places.findIndex(x => x.id === p.id); if (k >= 0) S.places[k] = p; else S.places.push(p); await save(); V.editPlace = null; render(); break; }
    case 'delunit': if (confirm('حذف مكان التفتيش؟ التفتيشات السابقة تبقى محفوظة.')) { S.places = S.places.filter(p => p.id !== d.id); await save(); render(); } break;
  }
});


/* ===== مشاركة التفتيش واستيراده (ملف JSON يُنقل بواتساب أو بلوتوث أو غيرهما) ===== */
async function shareInspections(ids) {
  const arr = S.inspections.filter(i => ids.includes(i.id) && i.status === 'done');
  if (!arr.length) { toast('لا توجد تفتيشات مكتملة للمشاركة'); return; }
  const payload = { app: 'inspect', v: 1, exportedAt: Date.now(), by: me().name, inspections: arr };
  const name = ('تفتيش_' + arr[0].header.place + '_' + arr[0].header.date + '.json').replace(/[\\/:*?"<>|\s]+/g, '_');
  const file = new File([JSON.stringify(payload)], name, { type: 'application/json' });
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], title: name }); return; } catch (e) { if (e && e.name === 'AbortError') return; }
  }
  const a = document.createElement('a'); a.href = URL.createObjectURL(file); a.download = name; document.body.appendChild(a); a.click(); a.remove();
  toast('تم حفظ الملف على الهاتف، أرسله إلى المشرف');
}
const okImg = v => typeof v === 'string' && /^data:image\/(jpeg|png|webp);base64,/.test(v);
function cleanImported(x) {
  Object.values(x.answers || {}).forEach(a => { if (a && a.photos) a.photos = a.photos.filter(okImg); });
  ['inspector', 'responsible'].forEach(k => { if (x.sig && x.sig[k] && !okImg(x.sig[k])) x.sig[k] = ''; });
  return x;
}
async function importFiles(files) {
  if (!isSup()) { toast('الاستيراد متاح للمشرف فقط'); return; }
  let added = 0, replaced = 0, skipped = 0, bad = 0;
  for (const f of files) {
    let p;
    try { p = JSON.parse(await f.text()); if (p.app !== 'inspect' || !Array.isArray(p.inspections)) throw 0; } catch (e) { bad++; continue; }
    const ok = p.inspections.filter(x => x && x.id && x.snap && x.snap.axes && x.header && x.result && x.status === 'done');
    bad += p.inspections.length - ok.length;
    if (!ok.length) continue;
    const summary = ok.map(x => `• ${x.header.place} / ${x.snap.title} / ${x.result.score}% / ${x.header.inspector}`).join('\n');
    if (!confirm(`الملف: ${f.name}\nمن: ${p.by || 'غير معروف'}\n${summary}\n\nإضافة هذه التفتيشات؟`)) { skipped += ok.length; continue; }
    for (const x of ok) {
      cleanImported(x);
      const k = S.inspections.findIndex(y => y.id === x.id);
      if (k < 0) { x.synced = false; x.imported = true; S.inspections.push(x); added++; }
      else if ((x.finishedAt || 0) > (S.inspections[k].finishedAt || 0) && confirm(`يوجد تفتيش «${x.snap.title}» لمكان «${x.header.place}» بنسخة أقدم. هل تستبدلها بالأحدث؟`)) { x.synced = false; x.imported = true; S.inspections[k] = x; replaced++; }
      else skipped++;
    }
  }
  await save(); render();
  toast(`أُضيف ${added} · استُبدل ${replaced} · تُجوهل ${skipped}${bad ? ' · غير صالح ' + bad : ''}`);
}
document.addEventListener('change', e => {
  const t = e.target; if (t.id === 'impf' && t.files && t.files.length) { importFiles([...t.files]); t.value = ''; }
});
