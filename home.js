'use strict';
/* ============================================================
   الواجهة الرئيسية الجديدة: الدخول برمز التحقق، صفحة المشرف (المنشآت وتعيين القوائم
   والمفتشين)، صفحة المفتش، الإعدادات، رفع قائمة تحقق، والتقرير الشامل حسب القطاعات.
   يُحمَّل بعد features.js ويستبدل الدوال المذكورة فيهما.
   ============================================================ */

/* ===== القطاعات ===== */
const SECTORS = { rooms: 'قطاع الغرف', fnb: 'قطاع الأغذية والمشروبات', other: 'قطاعات أخرى' };
const SECTOR_ORDER = ['rooms', 'fnb', 'other'];
function guessSector(l) {
  const t = (l.id || '') + ' ' + (l.title || '');
  if (/kitchen|restaurant|cafe|coffee|bar\b|buffet|مطعم|مطاعم|كوفي|كافيه|كافتيريا|كافيتيريا|مقهى|بوفيه|مطبخ|مطابخ|مخزن|مخازن|أغذية|اغذية|مشروبات/i.test(t)) return 'fnb';
  if (/housekeeping|frontoffice|laundry|استقبال|إشراف|اشراف|مغسل|الغرف|غرف|إقامة|اقامة/i.test(t) && !/اجتماعات|مؤتمرات/.test(t)) return 'rooms';
  return 'other';
}
const sectorOf = l => (l && SECTORS[l.sector] ? l.sector : guessSector(l || {}));
const shortTitle = l => String((l && l.title) || '').replace(/^قائمة التحقق\s*(ل?قسم\s*)?/, '').trim() || ((l && l.title) || '');
const autoName = id => { const l = S.lists.find(x => x.id === id); return l ? shortTitle(l).replace(/\s*\([A-Za-z ]+\)\s*$/, '') : ''; };
const namesOf = ids => (ids || []).map(id => (S.users.find(u => u.id === id) || {}).name).filter(Boolean);
const placeLabel = b => { const ps = [...new Set(b.map(i => i.header.place))]; return ps.length > 1 ? ps.join('، ') : ps[0]; };

/* ===== صورة الواجهة: رسم فندقي أصلي، أو صورة يرفعها المشرف ===== */
function heroSVG() {
  let seed = 7; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  let stars = ''; for (let i = 0; i < 38; i++) stars += `<circle cx="${(rnd() * 800).toFixed(0)}" cy="${(rnd() * 150).toFixed(0)}" r="${(rnd() * 1.3 + .4).toFixed(1)}" fill="#fff" opacity="${(rnd() * .6 + .25).toFixed(2)}"/>`;
  const win = (x, y, lit) => `<rect x="${x}" y="${y}" width="15" height="12" rx="1.5" fill="${lit ? '#ffd98a' : '#17566a'}" opacity="${lit ? .96 : .9}"/>`;
  let tower = '', wingL = '', wingR = '';
  for (let r = 0; r < 9; r++) for (let c = 0; c < 10; c++) tower += win(264 + c * 27.2, 132 + r * 22, (r * 5 + c * 3 + (r >> 1)) % 4 !== 0);
  for (let r = 0; r < 6; r++) for (let c = 0; c < 4; c++) { wingL += win(126 + c * 28, 208 + r * 22, (r * 3 + c * 5 + 1) % 3 !== 0); wingR += win(556 + c * 28, 208 + r * 22, (r * 5 + c * 2) % 3 !== 0); }
  const palm = (x, s) => {
    const fr = [[-70, -26], [-52, -62], [-18, -78], [24, -74], [58, -50], [74, -14], [-40, 8], [42, 10]];
    return `<g transform="translate(${x} 352) scale(${s} 1)"><path d="M0 0 C -6 -50 4 -92 10 -128" stroke="#10332b" stroke-width="7" fill="none" stroke-linecap="round"/>` +
      fr.map(([dx, dy]) => `<path d="M10 -128 Q ${10 + dx * .5} ${-128 + dy - 26} ${10 + dx} ${-128 + dy + 16}" stroke="#143f33" stroke-width="5" fill="none" stroke-linecap="round"/>`).join('') + '</g>';
  };
  let streaks = ''; for (let i = 0; i < 9; i++) streaks += `<rect x="${230 + rnd() * 340}" y="${360 + i * 6}" width="${40 + rnd() * 90}" height="1.6" rx=".8" fill="#ffd98a" opacity="${(.5 - i * .04).toFixed(2)}"/>`;
  return `<svg viewBox="0 0 800 420" preserveAspectRatio="xMidYMid slice" role="img" aria-label="واجهة فندق" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="hs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#082c38"/><stop offset=".55" stop-color="#1b7185"/><stop offset="1" stop-color="#f3c47c"/></linearGradient>
  <linearGradient id="hw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14566a"/><stop offset="1" stop-color="#082c38"/></linearGradient>
  <linearGradient id="hb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d4455"/><stop offset="1" stop-color="#0a3643"/></linearGradient>
  <radialGradient id="hg" cx=".5" cy="1" r=".6"><stop offset="0" stop-color="#ffd98a" stop-opacity=".75"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient></defs>
  <rect width="800" height="420" fill="url(#hs)"/>${stars}<ellipse cx="400" cy="352" rx="360" ry="130" fill="url(#hg)"/>
  <g fill="#0c3a49" opacity=".85"><rect x="20" y="250" width="70" height="100"/><rect x="92" y="280" width="48" height="70"/><rect x="660" y="262" width="62" height="88"/><rect x="724" y="236" width="58" height="114"/></g>
  <rect x="116" y="196" width="148" height="152" fill="url(#hb)"/><rect x="548" y="196" width="148" height="152" fill="url(#hb)"/>${wingL}${wingR}
  <rect x="116" y="190" width="148" height="8" fill="#c9a24b"/><rect x="548" y="190" width="148" height="8" fill="#c9a24b"/>
  <rect x="250" y="96" width="300" height="252" fill="url(#hb)"/>${tower}
  <rect x="244" y="88" width="312" height="10" fill="#d4af5a"/><rect x="326" y="62" width="148" height="28" fill="#0d4455"/><rect x="320" y="56" width="160" height="8" fill="#d4af5a"/>
  <g fill="#ffd98a">${[0, 1, 2, 3, 4].map(k => `<path transform="translate(${368 + k * 16} 44) scale(.62)" d="M10 0l2.9 6.6 7.1.7-5.4 4.8 1.6 7-6.2-3.7-6.2 3.7 1.6-7L0 7.3l7.1-.7z"/>`).join('')}</g>
  <rect x="318" y="318" width="164" height="9" rx="2" fill="#d4af5a"/><rect x="330" y="327" width="140" height="21" fill="#ffd98a" opacity=".92"/>
  <g fill="#0a3643"><rect x="346" y="327" width="3" height="21"/><rect x="398" y="327" width="4" height="21"/><rect x="451" y="327" width="3" height="21"/></g>
  <rect x="0" y="348" width="800" height="72" fill="url(#hw)"/><rect x="0" y="348" width="800" height="3" fill="#d4af5a" opacity=".7"/>${streaks}
  ${palm(64, 1)}${palm(742, -1)}${palm(150, .8)}${palm(656, -.8)}</svg>`;
}
const safeHero = () => { const h = S.settings && S.settings.heroImg; return typeof h === 'string' && /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+\/=]+$/.test(h) ? h : ''; };
const heroImg = () => (safeHero() ? `<img src="${safeHero()}" alt="">` : heroSVG());
const hero = inner => `<div class="hero">${heroImg()}<div class="heroshade"></div>${me() ? '<button class="herologout" data-act="logout">خروج</button>' : ''}${inner || ''}</div>`;

/* ===== الدخول برمز التحقق ===== */
function viewLogin() {
  return hero('<div class="herotxt">إدارة الفنادق</div>') + `<div class="wrap" style="padding-top:16px"><div class="card welcome">
  <h2>مرحباً بكم في منظومة الرقابة والمتابعة</h2>
  <p>الرقابة الميدانية المنتظمة تحفظ جودة الخدمة وسلامة الضيوف والعاملين، والمتابعة الدقيقة تكشف الخلل مبكراً وتحوّل الملاحظة إلى إجراء تصحيحي موثق. وبهما نصل إلى مستوى ثابت من التميز في كل منشأة.</p>
  <label class="f" style="margin-top:14px">رمز التحقق</label><input type="password" id="lp" inputmode="numeric" autocomplete="off" placeholder="اكتب رمز الدخول الخاص بك">
  <button class="btn block" style="margin-top:14px" data-act="login">دخول</button></div></div>`;
}
document.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target && e.target.id === 'lp') { const b = $('[data-act="login"]'); if (b) b.click(); } });

/* ===== الشريط السفلي ===== */
function nav() {
  if (!me()) return '';
  const t = [['home', '🏠', 'الرئيسية'], ['inspections', '📋', 'المرورات السابقة']];
  if (isSup()) t.push(['admin', '⚙️', 'الإعدادات']);
  return `<div class="nav">${t.map(([v, i, l]) => `<button class="${V.tab === v ? 'on' : ''}" data-act="tab" data-v="${v}"><b>${i}</b>${l}</button>`).join('')}</div>`;
}
const NO_NAV2 = ['login', 'insp', 'finish', 'report', 'editlist', 'editfac', 'printlist', 'batch', 'assign'];
function render() {
  const v = V.view;
  const views = { login: viewLogin, home: viewHome, inspections: viewInspections, admin: viewAdmin, new: viewNew, insp: viewInsp, finish: viewFinish, report: viewReport, lists: viewLists, editlist: viewEditList, places: viewPlaces, users: viewUsers, settings: viewSettings, facs: viewFacs, editfac: viewEditFac, batch: viewBatch, printlist: viewPrintList, assign: viewAssign };
  if (['home', 'inspections', 'admin'].includes(v)) V.tab = v;
  let h; try { h = (views[v] || viewLogin)(); } catch (err) { console.error(err); V.view = me() ? 'home' : 'login'; if (typeof toast === 'function') toast('حدث خطأ في عرض الشاشة'); h = (me() ? viewHome : viewLogin)(); }
  const keep = V.keepScroll, y = window.scrollY;
  app().innerHTML = h + (NO_NAV2.includes(V.view) ? '' : nav());
  if (keep) window.scrollTo(0, y); else window.scrollTo(0, 0);
  V.keepScroll = false;
  if (V.view === 'finish') initSig();
}

/* ===== الرئيسية ===== */
function viewHome() { return isSup() ? viewSupHome() : viewInspHome(); }


/* ===== زيارة المنشأة: تفتيش القوائم واحدة بعد أخرى ثم تقرير شامل ===== */
function visitFor(facId) {
  const today = nowParts().date;
  const mine = S.inspections.filter(i => i.inspectorId === S.session && i.header.date === today && (((i.fac && i.fac.id) || (S.places.find(p => p.id === i.placeId) || {}).facilityId) === facId));
  return groupBatches(mine).sort((a, b) => Math.max(...b.map(i => i.startedAt || 0)) - Math.max(...a.map(i => i.startedAt || 0)))[0] || [];
}
function placeRows(facId, places, showInspectors) {
  const visit = visitFor(facId); const rows = [];
  places.forEach(p => (p.listIds || []).forEach(lid => { const l = S.lists.find(x => x.id === lid); if (l) rows.push({ p, l, insp: visit.find(i => i.placeId === p.id && i.listId === lid) }); }));
  if (!rows.length) return '';
  const done = rows.filter(r => r.insp && r.insp.status === 'done');
  const html = rows.map(({ p, l, insp }) => {
    let st = '', btn = `<button class="btn sm" data-act="startone" data-id="${p.id}" data-l="${l.id}">ابدأ التفتيش</button>`;
    if (insp && insp.status === 'done') { st = `<span class="tag ${insp.result.bandCls}">تم · ${insp.result.score}%</span>`; btn = `<button class="btn sec sm" data-act="rep" data-ids="${insp.id}" data-back="home">التقرير</button>`; }
    else if (insp) { const r = compute(insp.snap, insp.answers, insp.esc); st = `<span class="mut">قيد التنفيذ: ${r.answered} من ${r.total}</span>`; btn = `<button class="btn sm" data-act="open" data-id="${insp.id}">متابعة</button>`; }
    return `<div class="listrow"><div class="sp"><b>${esc(p.name)}</b><div class="mut">${esc(l.title)}</div>${showInspectors ? `<div class="mut">المفتشون: ${esc(namesOf(p.inspectorIds).join('، ') || 'غير محدد')}</div>` : ''}<div style="margin-top:2px">${st}</div></div>${btn}</div>`;
  }).join('');
  const prog = rows.length > 1 ? `<p class="mut" style="margin:6px 0 0">أنجزت ${done.length} من ${rows.length} قوائم${done.length < rows.length ? '. اختر القائمة التالية لاستكمال التفتيش.' : '.'}</p>` : '';
  const all = done.length > 1 ? `<button class="btn block" style="margin-top:8px" data-act="rep" data-ids="${done.map(r => r.insp.id).join(',')}" data-back="home">التقرير الشامل (${done.length} من ${rows.length})</button>` : '';
  return html + prog + all;
}
function startOne(placeId, listId) {
  const p = S.places.find(x => x.id === placeId), l = S.lists.find(x => x.id === listId); if (!p || !l) return toast('تعذر بدء التفتيش');
  const fac = facOf(p.facilityId); const visit = visitFor(p.facilityId); const t = nowParts();
  const batchId = visit.length && !visit.some(i => i.placeId === placeId && i.listId === listId) ? (visit[0].batchId || visit[0].id) : uid('B');
  const insp = { id: uid('N'), batchId, listId, placeId, snap: clone(l), fac: clone(fac), status: 'draft', synced: false, inspectorId: S.session,
    header: { facility: fac.name || S.settings.facility, place: p.name, dept: p.dept, staff: p.staff, shifts: p.shifts, responsible: p.responsible, inspector: me().name, date: t.date, time: t.time },
    answers: {}, esc: {}, sig: {}, startedAt: Date.now() };
  S.inspections.push(insp); save(); V.batch = batchId; V.cur = insp.id; V.view = 'insp'; render();
}
/* بعد الحفظ يعود المستخدم إلى صفحة التخصيصات لاستكمال باقي القوائم */
function finalize() {
  const i = cur(); i.result = compute(i.snap, i.answers, i.esc); i.status = 'done'; i.finishedAt = Date.now(); i.synced = false; save();
  const rest = placeRowsLeft(i);
  toast(rest ? 'تم حفظ التفتيش. اختر القائمة التالية' : 'تم حفظ التفتيش. اكتملت كل القوائم');
  autoSync(); V.view = 'home'; render();
}
function placeRowsLeft(i) {
  const fid = (i.fac && i.fac.id) || (S.places.find(p => p.id === i.placeId) || {}).facilityId; const visit = visitFor(fid);
  return unitsForMe().filter(p => p.facilityId === fid).some(p => (p.listIds || []).some(lid => S.lists.some(l => l.id === lid) && !visit.some(x => x.placeId === p.id && x.listId === lid && x.status === 'done')));
}
const _viewInsp2 = viewInsp;
viewInsp = function () { return _viewInsp2().replace('data-act="go" data-v="batch"', 'data-act="go" data-v="home"'); };

function facCard(f) {
  const ps = S.places.filter(p => p.facilityId === f.id); const st = f.staff || {};
  const total = toNum(st.permanent) + toNum(st.insured) + toNum(st.temporary);
  const open = V.openFac && V.openFac[f.id];
  const info = [f.address, f.manager && 'المدير: ' + f.manager, total && 'العاملون: ' + total, (f.services || []).join('، ')].filter(Boolean).map(esc).join(' · ');
  const detail = ps.length ? placeRows(f.id, ps, true) || '<p class="mut">لا توجد قوائم صالحة مرتبطة بأماكن هذه المنشأة.</p>' : '<p class="mut">لم تُعيَّن قوائم تحقق لهذه المنشأة بعد. اضغط تعيين قائمة تحقق.</p>';
  return `<div class="card"><div data-act="togfac" data-id="${f.id}" style="cursor:pointer"><b style="font-size:17px">${esc(f.name || 'منشأة بلا اسم')}</b>
  ${info ? `<div class="mut">${info}</div>` : ''}<div class="mut">${ps.length} من أماكن المرور · ${open ? 'إخفاء التفاصيل ▴' : 'عرض القوائم والمفتشين ▾'}</div></div>
  <div class="row" style="margin-top:10px"><button class="btn sm" data-act="editfac" data-id="${f.id}">تعديل</button><button class="btn bad sm" data-act="delfac2" data-id="${f.id}">حذف</button><button class="btn sec sm" data-act="assign" data-id="${f.id}">تعيين قائمة تحقق</button>${ps.length ? `<button class="btn sm" style="background:var(--ok)" data-act="openstart" data-id="${f.id}">بدء تفتيش</button>` : ''}</div>
  ${open ? `<div style="margin-top:8px">${detail}</div>` : ''}</div>`;
}
function draftsCard() {
  const today0 = nowParts().date; const drafts = groupBatches(S.inspections.filter(i => i.inspectorId === S.session)).filter(b => b.some(i => i.status === 'draft') && b[0].header.date !== today0);
  return drafts.length ? `<div class="card"><h3>تفتيشات غير مكتملة</h3>${drafts.map(b => `<div class="listrow"><div class="sp"><b>${esc(placeLabel(b))}</b><div class="mut">${esc(b[0].header.date)} ${esc(b[0].header.time)} · اكتملت ${b.filter(i => i.status === 'done').length} من ${b.length} قوائم</div></div><button class="btn sm" data-act="openbatch" data-b="${b[0].batchId || b[0].id}">متابعة</button></div>`).join('')}</div>` : '';
}
function viewSupHome() {
  return hero('<div class="herotxt">إدارة الفنادق</div>') + `<div class="wrap" style="padding-top:14px"><p class="mut" style="margin:0 0 10px">مرحباً ${esc(me().name)}</p>
  <button class="btn block" style="padding:16px;font-size:17px;margin-bottom:14px" data-act="newvenue">＋ تعيين مكان جديد للمرور</button>
  ${draftsCard()}${S.facilities.length ? S.facilities.map(facCard).join('') : '<div class="card"><p class="mut">لا توجد منشآت بعد. اضغط تعيين مكان جديد للمرور لإضافة أول منشأة.</p></div>'}</div>`;
}
function viewInspHome() {
  const mine = S.inspections.filter(i => i.inspectorId === S.session);
  const today0 = nowParts().date; const drafts = groupBatches(mine).filter(b => b.some(i => i.status === 'draft') && b[0].header.date !== today0);
  const pending = S.inspections.filter(i => i.status === 'done' && !i.synced).length;
  const units = unitsForMe().filter(p => (p.listIds || []).some(id => S.lists.some(l => l.id === id)));
  const byFac = new Map(); units.forEach(p => { if (!byFac.has(p.facilityId)) byFac.set(p.facilityId, []); byFac.get(p.facilityId).push(p); });
  return hero('<div class="herotxt">إدارة الفنادق</div>') + `<div class="wrap" style="padding-top:14px"><div class="card welcome">
  <h2>مرحباً بك ${esc(me().name)}</h2>
  <p>نقدّر جهدك في أعمال الرقابة والمتابعة الميدانية، ونتمنى لك مروراً موفقاً ودقيقاً.</p>
  <p class="sign">مع تحيات إدارة الفنادق</p></div>
  ${byFac.size ? [...byFac.entries()].map(([fid, ps]) => { const f = facOf(fid); return `<div class="card"><h3>${esc(f.name || 'منشأة بلا اسم')}</h3><p class="mut" style="margin:0 0 6px">أماكن التفتيش المعيّنة لك</p>${placeRows(fid, ps, false)}</div>`; }).join('')
    : '<div class="card"><p class="mut">لا توجد أماكن تفتيش معيّنة لك حالياً. يحددها المشرف من الصفحة الرئيسية.</p></div>'}
  ${drafts.length ? `<div class="card"><h3>تفتيشات غير مكتملة</h3>${drafts.map(b => `<div class="listrow"><div class="sp"><b>${esc(placeLabel(b))}</b><div class="mut">${esc(b[0].header.date)} ${esc(b[0].header.time)} · اكتملت ${b.filter(i => i.status === 'done').length} من ${b.length} قوائم</div></div><button class="btn sm" data-act="openbatch" data-b="${b[0].batchId || b[0].id}">متابعة</button></div>`).join('')}</div>` : ''}
  <div class="card"><h3>حالة المزامنة</h3><p class="mut">${S.settings.syncUrl ? `بانتظار الرفع: ${pending} تفتيش` : 'المزامنة غير مفعّلة، البيانات محفوظة على هذا الهاتف فقط.'}</p>
  ${S.settings.syncUrl ? '<button class="btn sec sm" data-act="sync">مزامنة الآن</button>' : ''}</div></div>`;
}

/* ===== بدء التفتيش لمكان أو لعدة أماكن ===== */
function startMulti(placeIds) {
  const t = nowParts(), batchId = uid('B'), ids = [];
  placeIds.forEach(pid => {
    const p = S.places.find(x => x.id === pid); if (!p) return; const fac = facOf(p.facilityId);
    (p.listIds || []).forEach(lid => {
      const l = S.lists.find(x => x.id === lid); if (!l) return;
      const insp = { id: uid('N'), batchId, listId: lid, placeId: p.id, snap: clone(l), fac: clone(fac), status: 'draft', synced: false, inspectorId: S.session,
        header: { facility: fac.name || S.settings.facility, place: p.name, dept: p.dept, staff: p.staff, shifts: p.shifts, responsible: p.responsible, inspector: me().name, date: t.date, time: t.time },
        answers: {}, esc: {}, sig: {}, startedAt: Date.now() };
      S.inspections.push(insp); ids.push(insp.id);
    });
  });
  if (!ids.length) return toast('لا توجد قوائم تحقق مرتبطة بهذا المكان');
  save(); V.batch = batchId;
  if (ids.length === 1) { V.cur = ids[0]; V.view = 'insp'; } else V.view = 'batch';
  render();
}

/* ===== شاشة تعيين قوائم التحقق والمفتشين للمنشأة ===== */
function openAssign(facId) {
  const rows = [];
  S.places.filter(p => p.facilityId === facId).forEach(p => {
    const ls = (p.listIds || []).filter(id => S.lists.some(l => l.id === id));
    (ls.length ? ls : ['']).forEach((lid, k) => rows.push({ placeId: k === 0 ? p.id : null, listId: lid, name: p.name, inspectorIds: [...(p.inspectorIds || [])], responsible: p.responsible || '', staff: p.staff || '', shifts: p.shifts || '' }));
  });
  if (!rows.length) rows.push({ placeId: null, listId: '', name: '', inspectorIds: [], responsible: '', staff: '', shifts: '' });
  V.asg = { facId, rows }; V.view = 'assign'; render();
}
function viewAssign() {
  const a = V.asg, f = facOf(a.facId);
  const sec = new Set(); (f.services || []).forEach(s => { if (/إقامة|اقامة/.test(s)) sec.add('rooms'); if (/أغذية|اغذية|مشروبات/.test(s)) sec.add('fnb'); });
  const rec = S.lists.filter(l => !sec.size || sec.has(sectorOf(l))), oth = S.lists.filter(l => !rec.includes(l));
  const opts = (arr, sel) => arr.map(l => `<option value="${l.id}" ${sel === l.id ? 'selected' : ''}>${esc(l.title)}</option>`).join('');
  const insp = S.users.filter(u => u.role === 'inspector');
  return bar('تعيين قوائم التحقق', 'home') + `<div class="wrap"><div class="card"><b>${esc(f.name || 'منشأة بلا اسم')}</b>
  <div class="mut">الخدمات المقدمة: ${esc((f.services || []).join('، ') || 'لم تُحدد')}</div>
  <p class="mut" style="margin:8px 0 0">اختر قائمة التحقق ثم حدد المفتش المسؤول عنها، وكرر ذلك لباقي القوائم حسب الخدمات التي تقدمها المنشأة.</p></div>
  ${a.rows.map((r, k) => `<div class="card"><div class="row"><b class="sp">القائمة ${k + 1}</b>${a.rows.length > 1 ? `<button class="btn bad sm" data-act="asgdel" data-k="${k}">حذف</button>` : ''}</div>
   <label class="f" style="margin-top:6px">قائمة التحقق</label>
   <select data-asl="${k}"><option value="">اختر قائمة التحقق</option>${rec.length && oth.length ? `<optgroup label="مناسبة لخدمات المنشأة">${opts(rec, r.listId)}</optgroup><optgroup label="قوائم أخرى">${opts(oth, r.listId)}</optgroup>` : opts(S.lists, r.listId)}</select>
   <label class="f" style="margin-top:8px">اسم المكان</label><input type="text" data-asr="${k}" data-asf="name" value="${esc(r.name)}" placeholder="مثال: مطعم النيل">
   <label class="f" style="margin-top:8px">المفتشون المسؤولون</label>
   ${insp.length ? insp.map(u => `<label class="row" style="gap:8px;padding:4px 0"><input type="checkbox" data-asi="${k}" data-asu="${u.id}" ${r.inspectorIds.includes(u.id) ? 'checked' : ''}> <span>${esc(u.name)}</span></label>`).join('') : '<p class="mut">لا يوجد مفتشون. أضفهم من الإعدادات ثم المستخدمون والصلاحيات.</p>'}
   <details class="axis" style="margin-top:8px"><summary>بيانات اختيارية للمكان</summary><div class="item"><label class="f">المسؤول عن المكان</label><input type="text" data-asr="${k}" data-asf="responsible" value="${esc(r.responsible)}"></div>
   <div class="item grid2"><div><label class="f">عدد العاملين</label><input type="number" inputmode="numeric" data-asr="${k}" data-asf="staff" value="${esc(r.staff)}"></div><div><label class="f">عدد الورديات</label><input type="number" inputmode="numeric" data-asr="${k}" data-asf="shifts" value="${esc(r.shifts)}"></div></div></details></div>`).join('')}
  <button class="btn sec block" data-act="asgadd">＋ تعيين قائمة تحقق أخرى</button>
  <div class="row" style="margin-top:12px"><button class="btn sp" data-act="asgsave">حفظ</button><button class="btn sec" data-act="go" data-v="home">إلغاء</button></div></div>`;
}

/* ===== المرورات السابقة والدفعات ===== */
function viewInspections() {
  const arr = S.inspections.filter(i => i.status === 'done' && (isSup() || i.inspectorId === S.session));
  const batches = groupBatches(arr).sort((a, b) => Math.max(...b.map(i => i.finishedAt || 0)) - Math.max(...a.map(i => i.finishedAt)));
  return bar('المرورات السابقة') + `<div class="wrap">${batches.length ? batches.map(b => {
    const h = b[0].header; const ids = b.map(i => i.id).join(',');
    return `<div class="card"><div class="row"><b class="sp">${esc(h.facility || '')}${h.facility ? ' · ' : ''}${esc(placeLabel(b))}</b>${b.some(i => i.result.veto) ? '<span class="tag bad">بوابة حرجة</span>' : ''}</div>
    <div class="mut">${esc(h.date)} ${esc(h.time)} · ${esc(h.inspector)} ${b.every(i => i.synced) ? '· تمت المزامنة' : '· لم تُرفع'}</div>
    ${b.map(i => `<div class="row" style="margin-top:6px"><span class="sp">${esc(i.snap.title)}</span><span class="tag ${i.result.bandCls}">${i.result.score}%</span></div>`).join('')}
    <div class="row" style="margin-top:8px"><button class="btn sm" data-act="rep" data-ids="${ids}" data-back="inspections">${b.length > 1 ? 'التقرير الشامل' : 'عرض التقرير'}</button>${isSup() ? `<button class="btn sm bad" data-act="delbatch" data-b="${b[0].batchId || b[0].id}">حذف</button>` : ''}</div></div>`;
  }).join('') : '<p class="mut">لا توجد مرورات مكتملة بعد.</p>'}</div>`;
}
function viewBatch() {
  const arr = S.inspections.filter(i => (i.batchId || i.id) === V.batch);
  if (!arr.length) { V.view = 'home'; return viewHome(); }
  const h = arr[0].header; const done = arr.filter(i => i.status === 'done');
  return bar('قوائم هذا التفتيش', 'home') + `<div class="wrap"><div class="card"><b>${esc(h.facility || '')}</b><div class="mut">${esc(h.date)} ${esc(h.time)} · ${esc(h.inspector)}</div></div>
  ${arr.map(i => { const r = compute(i.snap, i.answers, i.esc); return `<div class="card"><div class="row"><div class="sp"><b>${esc(i.header.place)}</b><div class="mut">${esc(i.snap.title)}</div></div>${i.status === 'done' ? `<span class="tag ${i.result.bandCls}">${i.result.score}%</span>` : `<span class="mut">${r.answered} من ${r.total}</span>`}</div>
   <div class="pbar" style="margin:8px 0"><i style="width:${i.status === 'done' ? 100 : (r.total ? r.answered / r.total * 100 : 0)}%"></i></div>
   <div class="row">${i.status === 'done' ? `<button class="btn sm" data-act="rep" data-ids="${i.id}" data-back="batch">التقرير</button>` : `<button class="btn sm" data-act="open" data-id="${i.id}">${r.answered ? 'متابعة' : 'ابدأ'}</button>`}</div></div>`; }).join('')}
  <button class="btn block" data-act="rep" data-ids="${done.map(i => i.id).join(',')}" data-back="batch" ${done.length ? '' : 'disabled'}>التقرير الشامل (${done.length} من ${arr.length})</button></div>`;
}

/* ===== التقرير الشامل: قوائم قطاع الغرف ثم قطاع الأغذية والمشروبات ===== */
function viewReport() {
  const list = ((V.rep && V.rep.ids) || [V.cur]).map(id => S.inspections.find(i => i.id === id)).filter(i => i && i.status === 'done');
  if (!list.length) return bar('التقرير', V.back || 'inspections') + '<div class="wrap"><p class="mut">لا توجد تفتيشات مكتملة لعرضها.</p></div>';
  const i0 = list[0], h = i0.header, multi = list.length > 1;
  const fac = i0.fac || facOf((S.places.find(p => p.id === i0.placeId) || {}).facilityId);
  const places = [...new Set(list.map(i => i.header.place))]; const onePlace = places.length === 1;
  const groups = SECTOR_ORDER.map(k => ({ k, items: list.filter(i => sectorOf(i.snap) === k) })).filter(g => g.items.length);
  const summary = multi ? `<h3>ملخص جميع القوائم</h3><table class="rep"><tr><th class="sidehd">القطاع</th><th>المكان والقائمة</th><th>الدرجة</th><th>التقدير</th><th>البوابة الحرجة</th></tr>
    ${groups.map(g => g.items.map((i, n) => `<tr>${n === 0 ? `<td class="side" rowspan="${g.items.length}">${SECTORS[g.k]}</td>` : ''}<td><b>${esc(i.header.place)}</b><div class="mut">${esc(i.snap.title)}</div></td><td>${i.result.score}%</td><td>${i.result.band}</td><td>${i.result.veto ? 'مفعّلة' : 'لا'}</td></tr>`).join('')).join('')}</table>` : '';
  const sections = groups.map(g => g.items.map((i, n) => {
    const body = reportSection(i, false).replace('</h2>', `</h2><p class="mut" style="text-align:center;margin:0 0 8px">المكان: ${esc(i.header.place)}${i.header.responsible ? ' · المسؤول: ' + esc(i.header.responsible) : ''}</p>`);
    return `<div class="${multi ? 'pb' : ''}">${multi && n === 0 ? `<h2 class="sector">${SECTORS[g.k]}</h2>` : ''}${body}</div>`;
  }).join('')).join('');
  return `<div class="overlay"><div class="bar noprint"><button data-act="go" data-v="${V.back || 'inspections'}">رجوع</button><h1>${multi ? 'التقرير الشامل' : 'التقرير'}</h1><button data-act="print">طباعة / PDF</button></div><div class="wrap">
  ${facilityBlock(fac)}
  <table class="rep"><tr><th>المنشأة</th><td>${esc(h.facility)}</td><th>${onePlace ? 'المكان / القسم' : 'أماكن التفتيش'}</th><td>${places.map(esc).join('، ')}</td></tr>
  ${onePlace ? `<tr><th>عدد العاملين</th><td>${esc(h.staff)}</td><th>عدد الورديات</th><td>${esc(h.shifts)}</td></tr>
  <tr><th>المسؤول عن المكان</th><td>${esc(h.responsible)}</td><th>القائم بالتفتيش</th><td>${esc(h.inspector)}</td></tr>` : `<tr><th>القائم بالتفتيش</th><td colspan="3">${esc(h.inspector)}</td></tr>`}
  <tr><th>التاريخ</th><td>${esc(h.date)}</td><th>الساعة</th><td>${esc(h.time)}</td></tr></table>
  ${summary}${sections}</div></div>`;
}

/* ===== الإعدادات ===== */
function viewAdmin() {
  const row = (v, t, d) => `<div class="card row" data-act="go" data-v="${v}" style="cursor:pointer"><div class="sp"><b>${t}</b><div class="mut">${d}</div></div><span>‹</span></div>`;
  const custom = !!(S.settings && S.settings.heroImg);
  return bar('الإعدادات') + `<div class="wrap">${row('lists', 'قوائم التحقق', 'عرض القوائم وتعديلها ونسخها وطباعتها وحذفها، ورفع قائمة جديدة من ملف')}${row('users', 'المستخدمون والصلاحيات', 'إضافة المشرفين والمفتشين وتحديد رمز دخول كل مستخدم')}${row('settings', 'المزامنة والنسخ الاحتياطي', 'ربط التطبيق بالمزامنة وتصدير البيانات واستيرادها')}
  <div class="card"><h3>صورة الواجهة</h3><div class="heropv">${heroImg()}</div>
  <div class="row" style="margin-top:8px"><label class="btn sec sm" style="cursor:pointer">رفع صورة فندقية<input type="file" accept="image/*" hidden id="heroFile"></label>${custom ? '<button class="btn sec sm" data-act="herorst">استعادة الصورة الافتراضية</button>' : ''}</div></div></div>`;
}

/* ===== قوائم التحقق: عرض ورفع وتصدير ===== */
function viewLists() {
  return bar('قوائم التحقق', 'admin') + `<div class="wrap"><div class="row"><button class="btn sp" data-act="newlist">＋ قائمة جديدة</button><label class="btn sec" style="cursor:pointer">رفع قائمة تحقق<input type="file" accept=".json,application/json" multiple hidden id="impList"></label></div>
  <p class="mut">يقبل الرفع ملف قائمة بصيغة JSON، سواء قائمة واحدة أو مجموعة قوائم. القوائم المرفوعة تظهر هنا ويمكن تعديلها كأي قائمة أخرى.</p>
  <div class="card" style="margin-top:12px">${S.lists.map(l => `<div class="listrow" style="flex-wrap:wrap"><div class="sp" style="min-width:60%"><b>${esc(l.title)}</b><div class="mut">${l.axes.length} محاور · ${l.axes.reduce((n, a) => n + a.items.length, 0)} بنداً · الإصدار ${esc(l.version || 1)}</div>
  <select data-lsec="${l.id}" style="width:auto;margin-top:6px;padding:6px 10px">${SECTOR_ORDER.map(k => `<option value="${k}" ${sectorOf(l) === k ? 'selected' : ''}>${SECTORS[k]}</option>`).join('')}</select></div>
  <div class="row"><button class="btn sm" data-act="editlist" data-id="${l.id}">تعديل</button><button class="btn sec sm" data-act="duplist" data-id="${l.id}">نسخ</button><button class="btn sec sm" data-act="printlist" data-id="${l.id}" data-back="lists">طباعة</button><button class="btn sec sm" data-act="explist" data-id="${l.id}">تصدير</button><button class="btn bad sm" data-act="dellist2" data-id="${l.id}">حذف</button></div></div>`).join('')}</div></div>`;
}
const CLS_ALIAS = Object.assign(Object.create(null), { c: 'c', e: 'e', s: 's', 'حرج': 'c', 'حرجة': 'c', 'أساسي': 'e', 'اساسي': 'e', 'قياسي': 's' });
const cleanId = v => String(v == null ? '' : v).replace(/[^\w-]/g, '').slice(0, 60);
function normList(x) {
  if (!x || typeof x !== 'object' || Array.isArray(x)) throw new Error('بنية القائمة غير صحيحة');
  const title = String(x.title || '').trim(); if (!title) throw new Error('عنوان القائمة (title) مفقود');
  if (!Array.isArray(x.axes) || !x.axes.length) throw new Error(`القائمة "${title}" بلا محاور (axes)`);
  const usedI = new Set(), usedA = new Set();
  const axes = x.axes.map(a => {
    const name = String((a && a.name) || '').trim(); if (!name) throw new Error(`يوجد محور بلا اسم في "${title}"`);
    if (!Array.isArray(a.items) || !a.items.length) throw new Error(`المحور "${name}" بلا بنود (items)`);
    const items = a.items.map(it => {
      const text = String((it && it.text) || '').trim(); if (!text) throw new Error(`يوجد بند بلا نص في المحور "${name}"`);
      const cls = CLS_ALIAS[String(it.cls || '').trim().toLowerCase()]; if (!cls) throw new Error(`تصنيف غير صالح في المحور "${name}" (المسموح: c أو e أو s)`);
      let id = cleanId(it.id); if (!id || usedI.has(id)) id = uid('I'); usedI.add(id); return { id, cls, text };
    });
    let aid = cleanId(a.id); if (!aid || usedA.has(aid)) aid = uid('A'); usedA.add(aid);
    return { id: aid, name, weight: +a.weight || 0, items };
  });
  const out = { id: cleanId(x.id) || uid('L'), title, version: +x.version || 1, axes, escalation: Array.isArray(x.escalation) ? x.escalation.map(s => String(s).trim()).filter(Boolean) : [] };
  if (SECTORS[x.sector]) out.sector = x.sector;
  return out;
}
async function importLists(files) {
  let ok = 0, replaced = 0; const errs = []; const warn = [];
  for (const f of files) {
    let j; try { j = JSON.parse((await f.text()).replace(/^﻿/, '')); } catch { errs.push(`${f.name}: الملف ليس بصيغة JSON صحيحة`); continue; }
    if (j === null || typeof j !== 'object') { errs.push(`${f.name}: محتوى الملف غير صالح`); continue; }
    const cands = Array.isArray(j) ? j : Array.isArray(j.lists) ? j.lists : [j];
    for (const c of cands) {
      try {
        const l = normList(c); const k = S.lists.findIndex(x => x.id === l.id);
        if (k >= 0) { if (confirm(`توجد قائمة بنفس المعرف: "${S.lists[k].title}".\nموافق لاستبدالها، وإلغاء لحفظ القائمة المرفوعة كنسخة جديدة.`)) { S.lists[k] = l; replaced++; } else { l.id = uid('L'); S.lists.push(l); } }
        else S.lists.push(l);
        ok++; const sum = l.axes.reduce((s, a) => s + a.weight, 0); if (sum !== 100) warn.push(`"${l.title}": مجموع الأوزان ${sum}`);
      } catch (e) { errs.push(`${f.name}: ${e.message}`); }
    }
  }
  if (ok) await save();
  toast(ok ? `تم رفع ${ok} قائمة${replaced ? ` (استُبدلت ${replaced})` : ''}` : 'لم تُرفع أي قائمة');
  if (errs.length || warn.length) alert([errs.length ? 'تعذر رفع بعض القوائم:\n' + errs.join('\n') : '', warn.length ? 'تنبيه: مجموع أوزان المحاور ليس 100 في:\n' + warn.join('\n') : ''].filter(Boolean).join('\n\n'));
  render();
}

/* ===== معالجة الصورة المرفوعة ===== */
function fileToHero(file) {
  return new Promise((res, rej) => {
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => { const k = Math.min(1, 1400 / img.width); const c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k); c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url); res(c.toDataURL('image/jpeg', .82)); };
    img.onerror = () => { URL.revokeObjectURL(url); rej(new Error('تعذر قراءة الصورة')); }; img.src = url;
  });
}

/* ===== الأحداث ===== */
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act]'); if (!t) return; const a = t.dataset.act, d = t.dataset;
  switch (a) {
    case 'togfac': V.openFac = V.openFac || {}; V.openFac[d.id] = !V.openFac[d.id]; rerender(); break;
    case 'openstart': V.openFac = V.openFac || {}; V.openFac[d.id] = true; rerender(); toast('اختر المكان وابدأ التفتيش'); break;
    case 'newvenue': V.ef = newFac(); V.det = {}; V.view = 'editfac'; render(); break;
    case 'assign': openAssign(d.id); break;
    case 'delfac2': {
      const f = S.facilities.find(x => x.id === d.id); if (!f) break; const ps = S.places.filter(p => p.facilityId === f.id);
      if (confirm(`حذف منشأة "${f.name || 'بلا اسم'}"؟` + (ps.length ? `\nسيُحذف معها ${ps.length} من أماكن المرور وتعييناتها.` : '') + '\nالتقارير السابقة تبقى محفوظة.')) {
        S.facilities = S.facilities.filter(x => x.id !== f.id); S.places = S.places.filter(p => p.facilityId !== f.id); S.facDeleted = true; await save(); toast('تم حذف المنشأة'); render();
      } break; }
    case 'asgadd': V.asg.rows.push({ placeId: null, listId: '', name: '', inspectorIds: [], responsible: '', staff: '', shifts: '' }); rerender(); break;
    case 'asgdel': V.asg.rows.splice(+d.k, 1); if (!V.asg.rows.length) V.asg.rows.push({ placeId: null, listId: '', name: '', inspectorIds: [], responsible: '', staff: '', shifts: '' }); rerender(); break;
    case 'asgsave': {
      const g = V.asg; const empty = g.rows.every(r => !r.listId);
      for (let k = 0; k < g.rows.length; k++) {
        const r = g.rows[k]; if (!r.listId) { if (empty) continue; return toast(`القائمة ${k + 1}: اختر قائمة التحقق أو احذف هذا الصف`); }
        if (!r.name.trim()) return toast(`القائمة ${k + 1}: اكتب اسم المكان`);
        if (!r.inspectorIds.length) return toast(`القائمة ${k + 1}: حدد مفتشاً واحداً على الأقل`);
      }
      if (empty && S.places.some(p => p.facilityId === g.facId) && !confirm('لم تُحدد أي قائمة تحقق. سيؤدي الحفظ إلى حذف جميع أماكن المرور المعيّنة لهذه المنشأة. هل تريد المتابعة؟')) return;
      const keep = new Set();
      g.rows.filter(r => r.listId).forEach(r => {
        const dept = autoName(r.listId); const base = { name: r.name.trim(), dept, staff: r.staff, shifts: r.shifts, responsible: r.responsible.trim(), listIds: [r.listId], inspectorIds: [...r.inspectorIds] };
        const p = r.placeId && S.places.find(x => x.id === r.placeId);
        if (p) { Object.assign(p, base); keep.add(p.id); } else { const np = { id: uid('P'), facilityId: g.facId, venueId: '', ...base }; S.places.push(np); keep.add(np.id); }
      });
      S.places = S.places.filter(p => p.facilityId !== g.facId || keep.has(p.id));
      await save(); V.openFac = V.openFac || {}; V.openFac[g.facId] = true; V.asg = null; toast('تم حفظ التعيينات'); V.view = 'home'; render(); break; }
    case 'startone': startOne(d.id, d.l); break;
    case 'startplace': startMulti([d.id]); break;
    case 'startall': startMulti(unitsForMe().filter(p => p.facilityId === d.fac).map(p => p.id)); break;
    case 'explist': { const l = S.lists.find(x => x.id === d.id); if (!l) break; const o = clone(l); o.sector = sectorOf(l); const b = new Blob([JSON.stringify(o, null, 2)], { type: 'application/json' }); const a2 = document.createElement('a'); a2.href = URL.createObjectURL(b); a2.download = `checklist-${l.id}.json`; a2.click(); break; }
    case 'herorst': delete S.settings.heroImg; await save(); toast('تمت استعادة الصورة الافتراضية'); render(); break;
  }
});
document.addEventListener('input', e => {
  const t = e.target; if (t.dataset.asf === undefined || !V.asg) return;
  V.asg.rows[+t.dataset.asr][t.dataset.asf] = t.value;
});
document.addEventListener('change', async e => {
  const t = e.target;
  if (t.dataset.asl !== undefined && V.asg) {
    const r = V.asg.rows[+t.dataset.asl]; const prev = autoName(r.listId); r.listId = t.value;
    if (!r.name.trim() || r.name === prev) r.name = autoName(t.value); rerender();
  } else if (t.dataset.asi !== undefined && V.asg) {
    const r = V.asg.rows[+t.dataset.asi], k = r.inspectorIds.indexOf(t.dataset.asu);
    if (t.checked && k < 0) r.inspectorIds.push(t.dataset.asu); if (!t.checked && k >= 0) r.inspectorIds.splice(k, 1);
  } else if (t.dataset.lsec !== undefined) {
    const l = S.lists.find(x => x.id === t.dataset.lsec); if (l) { l.sector = t.value; await save(); toast('تم تحديد القطاع'); }
  } else if (t.id === 'impList') {
    const files = [...t.files]; t.value = ''; if (files.length) await importLists(files);
  } else if (t.id === 'heroFile') {
    const f = t.files[0]; t.value = ''; if (!f) return;
    try { S.settings.heroImg = await fileToHero(f); await save(); toast('تم تغيير صورة الواجهة'); render(); } catch (err) { toast(err.message); }
  }
});
