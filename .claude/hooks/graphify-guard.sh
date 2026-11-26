#!/usr/bin/env bash
# غلاف لخطافات Graphify: يمرّر الاستدعاء إلى graphify إن كان مثبّتًا، ويصمت تمامًا إن لم يكن،
# حتى لا تظهر أخطاء الخطافات على الأجهزة أو الجلسات التي لم تُثبَّت فيها الأداة.
GRAPHIFY_BIN="$(command -v graphify 2>/dev/null || true)"
[ -z "$GRAPHIFY_BIN" ] && [ -x "$HOME/.local/bin/graphify" ] && GRAPHIFY_BIN="$HOME/.local/bin/graphify"
[ -z "$GRAPHIFY_BIN" ] && exit 0
exec "$GRAPHIFY_BIN" hook-guard "$@"
