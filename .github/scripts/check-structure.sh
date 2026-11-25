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
while IFS= read -r f; do
  [ -f "$f" ] || continue
  size=$(stat -c %s "$f")
  [ "$size" -gt 5242880 ] && err "ملف كبير ($((size/1048576)) MB): $f - استخدم Git LFS أو أزله"
done < <(git ls-files)

# كل مشروع فرعي يجب أن يحتوي README
for d in wifi-manager google-apps-script; do
  [ -d "$d" ] && [ ! -f "$d/README.md" ] && err "المجلد $d بلا README.md"
done

[ $fail -eq 0 ] && echo "✓ هيكل المستودع سليم"
exit $fail
