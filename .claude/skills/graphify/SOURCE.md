# مصدر مهارة Graphify

| البند | القيمة |
|---|---|
| المستودع الرسمي | https://github.com/Graphify-Labs/graphify |
| الحزمة الرسمية | `graphifyy` على PyPI (بحرفَي y؛ احذر الأسماء المشابهة) |
| الإصدار المثبَّت | 0.9.120 |
| الترخيص | Apache-2.0 (ملف NOTICE في المستودع الأصلي) |
| طريقة التوليد | `graphify install --project` دون أي تعديل على ملفات المهارة |
| التقييم | 7/10، تقرير المحطة: evaluations/graphify-evaluation.html |

## ما يضيفه هذا التكامل

- مهارة `/graphify` داخل Claude Code لبناء رسم معرفي للمستودع والاستعلام عنه.
- خطافات تذكّر Claude بالاستعلام من الرسم قبل قراءة الملفات واحدًا واحدًا (وضع إرشادي فقط، لا يمنع شيئًا).
- تثبيت تلقائي للأداة في جلسات Claude Code السحابية فقط (`.claude/hooks/graphify-setup.sh`).
- مجلد `graphify-out/` مستبعد من Git؛ يُبنى محليًا بالأمر `graphify update .` (مجاني، بلا ذكاء اصطناعي، نحو 30 ثانية).

## التفعيل على جهازك (مرة واحدة)

```bash
uv tool install graphifyy==0.9.120    # أو: pipx install graphifyy==0.9.120
```

بدون هذه الخطوة تعمل الخطافات بصمت ولا تؤثر على شيء.

## التحديث

غيّر رقم الإصدار في `.claude/hooks/graphify-setup.sh` وهنا، ثم أعد تشغيل `graphify install --project` عبر طلب دمج.
