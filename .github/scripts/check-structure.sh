#!/usr/bin/env bash
# فحص هيكل المستودع: الملفات الإلزامية، والملفات الحساسة، والملفات الكبيرة.
set -u
fail=0
err() { echo "::error::$1"; fail=1; }

for f in README.md SECURITY.md .gitignore .github/CODEOWNERS; do
  [ -f "$f" ] || err "الملف الإلزامي مفقود: $f"
done

# ملفات حساسة يجب ألا تُرفع أبداً
while IFS= read -r f; do
  case "$f" in
    *.env|.env|.env.*|*.pem|*.key|*.p12|*.pfx|*id_rsa*|*credentials*.json|*service-account*.json|*.keystore)
      [ "$f" = ".env.example" ] || err "ملف حساس مرفوع: $f";;
  esac
done < <(git ls-files)

# ملفات أكبر من 5 ميغابايت
# استثناء مبرَّر: وسائط وكيل إنستقرام (instagram-agent/out و instagram-agent/assets).
# الوكيل ينشر الريلز من روابط raw.githubusercontent المثبّتة على commit، فلازم الملف
# يكون في Git نفسه: Git LFS بيخلي الرابط يرجّع ملف مؤشر مش الفيديو، وإزالة out/ بتوقف
# النشر. لذلك الحد هنا 50 MB (توصية GitHub القصوى للملف، والحد المطلق 100 MB)،
# وبامتدادات الوسائط فقط. أي ملف كبير في أي مكان آخر يظل ممنوعًا فوق 5 MB.
MEDIA_LIMIT=52428800
media_big=0
media_bytes=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  size=$(stat -c %s "$f")
  [ "$size" -gt 5242880 ] || continue
  case "$f" in
    instagram-agent/out/*.mp4|instagram-agent/out/*.jpg|instagram-agent/out/*.png|\
    instagram-agent/assets/*.mp3|instagram-agent/assets/*.wav|instagram-agent/assets/*.m4a|\
    instagram-agent/assets/*.mp4|instagram-agent/assets/*.png|instagram-agent/assets/*.jpg|instagram-agent/assets/*.jpeg)
      if [ "$size" -gt "$MEDIA_LIMIT" ]; then
        err "وسائط أكبر من 50 MB ($((size/1048576)) MB): $f - اضغطها قبل الرفع"
      else
        media_big=$((media_big+1)); media_bytes=$((media_bytes+size))
      fi;;
    *) err "ملف كبير ($((size/1048576)) MB): $f - استخدم Git LFS أو أزله";;
  esac
done < <(git ls-files)
[ $media_big -gt 0 ] && echo "::notice::وسائط إنستقرام بين 5 و50 MB مسموح بها: $media_big ملف ($((media_bytes/1048576)) MB)"

# كل مشروع فرعي يجب أن يحتوي README
for d in wifi-manager google-apps-script; do
  [ -d "$d" ] && [ ! -f "$d/README.md" ] && err "المجلد $d بلا README.md"
done

[ $fail -eq 0 ] && echo "✓ هيكل المستودع سليم"
exit $fail
