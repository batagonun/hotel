/* ============================================================
   خادم المزامنة لتطبيق قوائم التحقق والتفتيش (Google Apps Script)
   يُلصق في: جدول Google جديد ← الإضافات ← Apps Script
   ثم تُشغَّل الدالة setup مرة واحدة، ثم يُنشر كتطبيق ويب بصلاحية "أي شخص".

   التخزين:
   - ورقة "الإعداد": مفتاح الربط السري ومعلومات النشر.
   - ورقة "التفتيشات": سجل مقروء لكل تفتيش (المنشأة، المكان، القائمة، الدرجة...).
   - مجلد في Google Drive: ملف الإعدادات وملف JSON لكل تفتيش (يحوي الصور والتوقيعات).
   ============================================================ */

var SHEET_SETUP = 'الإعداد';
var SHEET_INSP = 'التفتيشات';
var INSP_HEAD = ['التسلسل', 'المعرّف', 'معرّف المفتش', 'المفتش', 'المنشأة', 'المكان', 'القائمة', 'التاريخ', 'الساعة', 'الدرجة %', 'التقدير', 'بوابة حرجة', 'آخر تحديث', 'معرّف الملف'];
var PAGE = 20; // عدد التفتيشات في كل دفعة سحب
var APP_URL = 'https://batagonun.github.io/hotel/'; // رابط التطبيق

/* قائمة في الجدول لإنشاء رابط ربط الأجهزة بضغطة واحدة */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('مزامنة التفتيش')
    .addItem('1) الإعداد الأول', 'setup')
    .addItem('2) إنشاء رابط ربط الأجهزة (بعد النشر)', 'makeLink')
    .addItem('تغيير مفتاح الربط', 'resetToken')
    .addToUi();
}
/* ينشئ رابطاً يفتحه المشرف على هاتفه فيرتبط التطبيق بالمزامنة تلقائياً */
function makeLink() {
  var url = ScriptApp.getService().getUrl();
  if (!url || !/\/exec$/.test(url)) {
    SpreadsheetApp.getUi().alert('انشر السكربت أولاً: نشر ← نشر جديد ← تطبيق ويب ← من يمكنه الوصول: أي شخص، ثم أعد المحاولة.');
    return;
  }
  var props = PropertiesService.getScriptProperties(); if (!props.getProperty('TOKEN')) setup();
  var link = APP_URL + '#sync=' + encodeURIComponent(Utilities.base64Encode(JSON.stringify({ u: url, t: props.getProperty('TOKEN') })));
  var st = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_SETUP);
  st.getRange(6, 1, 3, 2).setValues([['رابط تطبيق الويب', url], ['رابط ربط الأجهزة', link],
    ['طريقة الاستخدام', 'افتح «رابط ربط الأجهزة» على هاتف المشرف مرة واحدة، ثم ادخل برمز المشرف. ومن الإعدادات أرسل رابط الربط لكل مفتش.']]);
  st.getRange('A6:A8').setFontWeight('bold');
  SpreadsheetApp.getUi().alert('تم إنشاء رابط ربط الأجهزة في ورقة «الإعداد» (الخلية B7). افتحه على هاتف المشرف.');
}

/* ===== الإعداد الأول: شغّلها مرة واحدة من المحرر ===== */
function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var props = PropertiesService.getScriptProperties();
  if (!props.getProperty('TOKEN')) props.setProperty('TOKEN', newToken_());
  if (!props.getProperty('FOLDER')) props.setProperty('FOLDER', DriveApp.createFolder('مزامنة التفتيش - ' + ss.getName()).getId());
  if (!props.getProperty('REV')) props.setProperty('REV', '0');
  if (!props.getProperty('SEQ')) props.setProperty('SEQ', '0');
  var ins = ss.getSheetByName(SHEET_INSP) || ss.insertSheet(SHEET_INSP);
  if (ins.getLastRow() === 0) { ins.appendRow(INSP_HEAD); ins.setFrozenRows(1); ins.setRightToLeft(true); }
  var st = ss.getSheetByName(SHEET_SETUP) || ss.insertSheet(SHEET_SETUP, 0);
  st.clear(); st.setRightToLeft(true);
  st.getRange(1, 1, 4, 2).setValues([
    ['مفتاح الربط السري', props.getProperty('TOKEN')],
    ['الخطوة التالية', 'في محرر Apps Script: نشر ← نشر جديد ← تطبيق ويب ← التنفيذ بصفتي ← من يمكنه الوصول: أي شخص'],
    ['ثم', 'من قائمة «مزامنة التفتيش» أعلى الجدول اختر «إنشاء رابط ربط الأجهزة»، وافتح الرابط على هاتف المشرف'],
    ['تنبيه', 'لا تشارك المفتاح أو رابط النشر علناً. لتغيير المفتاح شغّل الدالة resetToken ثم حدّث المفتاح في أجهزة المشرف.']
  ]);
  st.getRange('A1:A4').setFontWeight('bold'); st.setColumnWidth(1, 160); st.setColumnWidth(2, 620);
  Logger.log('مفتاح الربط السري: ' + props.getProperty('TOKEN'));
}
function resetToken() {
  PropertiesService.getScriptProperties().setProperty('TOKEN', newToken_());
  setup();
}
function newToken_() { return Utilities.getUuid().replace(/-/g, '').slice(0, 24); }

/* ===== نقاط الاتصال ===== */
function doGet() { return out_({ ok: true, msg: 'خادم المزامنة يعمل. استخدم هذا الرابط في إعدادات التطبيق.' }); }

function doPost(e) {
  var req;
  try { req = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (x) { return out_({ ok: false, error: 'طلب غير صالح' }); }
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('TOKEN');
  if (!token) return out_({ ok: false, error: 'الخادم غير مُعَدّ، شغّل الدالة setup من محرر Apps Script' });
  if (req.token !== token) return out_({ ok: false, error: 'مفتاح الربط غير صحيح' });
  try {
    switch (req.action) {
      case 'poll': return out_({ ok: true, rev: +props.getProperty('REV') || 0, lastInsp: +props.getProperty('SEQ') || 0 });
      case 'getConfig': return out_(getConfig_(props));
      case 'saveConfig': return withLock_(function () { return saveConfig_(props, req.config); });
      case 'saveInspection': return withLock_(function () { return saveInspection_(props, req.inspection); });
      case 'getInspections': return out_(getInspections_(+req.since || 0, req.inspectorId || ''));
      default: return out_({ ok: false, error: 'إجراء غير معروف: ' + req.action });
    }
  } catch (err) {
    return out_({ ok: false, error: String(err && err.message || err) });
  }
}

/* ===== الإعدادات ===== */
function getConfig_(props) {
  var id = props.getProperty('CONFIG_FILE');
  if (!id) return { ok: true, config: null, rev: 0 };
  return { ok: true, config: JSON.parse(DriveApp.getFileById(id).getBlob().getDataAsString('UTF-8')), rev: +props.getProperty('REV') || 0 };
}
function saveConfig_(props, config) {
  if (!config || typeof config !== 'object') throw new Error('إعدادات غير صالحة');
  var text = JSON.stringify(config); var id = props.getProperty('CONFIG_FILE');
  if (id) DriveApp.getFileById(id).setContent(text);
  else props.setProperty('CONFIG_FILE', folder_(props).createFile('config.json', text, 'application/json').getId());
  var rev = (+props.getProperty('REV') || 0) + 1; props.setProperty('REV', String(rev));
  return { ok: true, rev: rev };
}

/* ===== التفتيشات ===== */
function saveInspection_(props, i) {
  if (!i || !i.id || !i.header) throw new Error('تفتيش غير صالح');
  var sh = inspSheet_(); var text = JSON.stringify(i);
  var seq = (+props.getProperty('SEQ') || 0) + 1;
  var h = i.header || {}, r = i.result || {}, snap = i.snap || {};
  var row = [seq, i.id, i.inspectorId || '', h.inspector || '', h.facility || '', h.place || '', snap.title || '', h.date || '', h.time || '',
    r.score == null ? '' : r.score, r.band || '', r.veto ? 'نعم' : 'لا', new Date()];
  var found = sh.getLastRow() > 1 ? sh.getRange(2, 2, sh.getLastRow() - 1, 1).createTextFinder(i.id).matchEntireCell(true).findNext() : null;
  if (found) {
    var rn = found.getRow(); var fileId = sh.getRange(rn, 14).getValue();
    try { DriveApp.getFileById(fileId).setContent(text); } catch (x) { fileId = folder_(props).createFile('insp_' + i.id + '.json', text, 'application/json').getId(); }
    sh.getRange(rn, 1, 1, 14).setValues([row.concat([fileId])]);
  } else {
    var fid = folder_(props).createFile('insp_' + i.id + '.json', text, 'application/json').getId();
    sh.appendRow(row.concat([fid]));
  }
  props.setProperty('SEQ', String(seq));
  return { ok: true, seq: seq };
}
/* يعيد التفتيشات التي تسلسلها أكبر من since، مرتبة تصاعدياً، على دفعات */
function getInspections_(since, inspectorId) {
  var sh = inspSheet_(); var n = sh.getLastRow() - 1;
  if (n < 1) return { ok: true, items: [], next: since, more: false };
  var rows = sh.getRange(2, 1, n, 14).getValues()
    .filter(function (x) { return +x[0] > since && (!inspectorId || x[2] === inspectorId); })
    .sort(function (a, b) { return a[0] - b[0]; });
  var page = rows.slice(0, PAGE), items = [];
  page.forEach(function (x) {
    try { items.push(JSON.parse(DriveApp.getFileById(x[13]).getBlob().getDataAsString('UTF-8'))); } catch (err) {}
  });
  return { ok: true, items: items, next: page.length ? +page[page.length - 1][0] : since, more: rows.length > PAGE };
}

/* ===== أدوات ===== */
function inspSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet(); var sh = ss.getSheetByName(SHEET_INSP);
  if (!sh) { sh = ss.insertSheet(SHEET_INSP); sh.appendRow(INSP_HEAD); sh.setFrozenRows(1); sh.setRightToLeft(true); }
  return sh;
}
function folder_(props) {
  var id = props.getProperty('FOLDER');
  if (id) { try { return DriveApp.getFolderById(id); } catch (x) {} }
  var f = DriveApp.createFolder('مزامنة التفتيش'); props.setProperty('FOLDER', f.getId()); return f;
}
function withLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(25000)) return out_({ ok: false, error: 'الخادم مشغول (Lock)، ستُعاد المحاولة' });
  try { return out_(fn()); } finally { lock.releaseLock(); }
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
