#!/usr/bin/env bash
# تثبيت Graphify تلقائيًا في جلسات Claude Code السحابية فقط، بإصدار مثبَّت من الحزمة الرسمية.
# على جهاز المستخدم لا يُثبَّت شيء تلقائيًا؛ التثبيت يدوي (انظر .claude/skills/graphify/SOURCE.md).
GRAPHIFY_VERSION="0.9.120"   # الاسم الرسمي للحزمة graphifyy (بحرفَي y)
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
if command -v graphify >/dev/null 2>&1 || [ -x "$HOME/.local/bin/graphify" ]; then exit 0; fi
if command -v uv >/dev/null 2>&1; then
  uv tool install -q "graphifyy==${GRAPHIFY_VERSION}" >/dev/null 2>&1
elif command -v pipx >/dev/null 2>&1; then
  pipx install -q "graphifyy==${GRAPHIFY_VERSION}" >/dev/null 2>&1
fi
exit 0
