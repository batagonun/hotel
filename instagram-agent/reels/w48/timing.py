# Auto-times a w48 spec: each screen lasts long enough to read (words-per-screen rule, STRATEGY 3-ب-3).
# talk: 1.4s + 0.42s/word, verse: 1.8s + 0.5s/word, +1.6s if a note; min 3.0s; 0.2s gap. Last screen holds the source.
import json, sys
spec = json.load(open(sys.argv[1])); t = 0.0
for s in spec['segments']:
    w = sum(len(l.replace('*', '').split()) for l in s['lines'])
    d = (1.8 + 0.5 * w) if s['kind'] == 'verse' else (1.4 + 0.42 * w)
    if s.get('note'): d += 0.42 * len(s['note'].split()) + 0.6
    d = max(3.0, round(d, 1))
    s['t0'] = round(t, 1); s['t1'] = round(t + d, 1)
    s.setdefault('step', 0.28 if s['kind'] == 'verse' else 0.2)
    if s.get('note'): s['note_at'] = round(t + 0.6 + 0.2 * w + 0.6, 1)
    t += d + 0.2
spec['src_at'] = spec['segments'][-1]['t0']
spec['duration'] = round(t + 0.6, 1)
json.dump(spec, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
print(sys.argv[1], 'duration', spec['duration'], [(s['t0'], s['t1']) for s in spec['segments']])
