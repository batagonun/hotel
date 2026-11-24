# Media reel: kinetic text (transparent frames from build_kinetic + anim.mjs --alpha) over real photos/videos.
# Usage: python3 reels/w48/build_media.py <spec.json> <out.mp4> [--music=file.mp3]
# Each segment may carry "bg": {"video": path, "ss": seconds} or {"img": path}; the bg covers from that
# segment's t0 until the next segment's t0 (first one from 0, last one until duration).
import json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
spec_path, out = sys.argv[1], sys.argv[2]
music = next((a[8:] for a in sys.argv if a.startswith('--music=')), None)
spec = json.load(open(spec_path))
tmp = tempfile.mkdtemp()
fps = 25
dur = spec['duration']

# 1) transparent text layer
html = os.path.join(here, os.path.basename(spec_path).replace('.json', '-media.html'))
subprocess.run(['python3', os.path.join(here, 'build_kinetic.py'), spec_path, html], check=True)
h = open(html).read()
h = h.replace("x.fillStyle=g;x.fillRect(0,0,1080,1920);", "x.clearRect(0,0,1080,1920);")
h = h.replace("x.globalAlpha=.22+.22*Math.sin", "x.globalAlpha=.10+.10*Math.sin")
h = h.replace("background:#0d0b1a", "background:transparent")
h = h.replace("</style>", ".seg,.series,.src,.handle{text-shadow:0 3px 18px rgba(0,0,0,.95),0 0 4px rgba(0,0,0,.9)}</style>")
open(html, 'w').write(h)
frames = os.path.join(tmp, 'f') + '/'
subprocess.run(['node', os.path.join(root, 'tools', 'anim.mjs'), html, str(dur), frames, str(fps), '--alpha'], check=True)

# 2) background track
segs = spec['segments']
clips = []
for i, s in enumerate(segs):
    a = 0 if i == 0 else s['t0']
    b = segs[i + 1]['t0'] if i + 1 < len(segs) else dur
    d = b - a
    bg = dict(s['bg'])
    for k in ('video', 'img'):
        if k in bg: bg[k] = os.path.join(os.path.dirname(os.path.abspath(spec_path)), bg[k])
    c = os.path.join(tmp, f'b{i}.mp4')
    look = "eq=brightness=-0.20:saturation=0.85,vignette=PI/4" + (f",boxblur={bg['blur']}:2" if bg.get('blur') else '')
    if 'video' in bg:
        vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={fps},{look}"
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(bg.get('ss', 0)), '-i', bg['video'], '-t', f'{d:.3f}', '-an', '-vf', vf]
    elif bg.get('fit') == 'top':
        # Small archival photo: sharp copy framed near the top over a blurred, darkened cover of itself.
        n = int(d * fps) + 1
        fc = (f"[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:3,eq=brightness=-0.30[bg];"
              f"[b]scale=960:560:force_original_aspect_ratio=decrease,pad=iw+12:ih+12:6:6:color=0xf2c75c[fg];"
              f"[bg][fg]overlay=(W-w)/2:150,scale=2160:3840,"
              f"zoompan=z='min(zoom+0.0005,1.06)':x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)':d={n}:s=1080x1920:fps={fps},vignette=PI/4[v]")
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', bg['img'], '-t', f'{d:.3f}', '-filter_complex', fc, '-map', '[v]']
    else:
        n = int(d * fps) + 1
        z = bg.get('zoom', 'in')
        zexp = "min(zoom+0.0007,1.12)" if z == 'in' else "if(eq(on,0),1.12,max(zoom-0.0007,1.0))"
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=2160:3840,"
              f"zoompan=z='{zexp}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps={fps},{look}")
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', bg['img'], '-t', f'{d:.3f}', '-vf', vf]
    subprocess.run(cmd + ['-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '18', c], check=True)
    clips.append(c)
lst = os.path.join(tmp, 'l.txt')
open(lst, 'w').write(''.join(f"file '{c}'\n" for c in clips))
bgv = os.path.join(tmp, 'bg.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', bgv], check=True)

# 3) overlay + audio
if music:
    ain = ['-i', music]
    af = f"[2:a]volume=0.5,afade=t=in:d=1,afade=t=out:st={dur - 1.5:.2f}:d=1.5[a]"
else:
    ain = ['-f', 'lavfi', '-i', f"anullsrc=r=44100:cl=stereo"]
    af = "[2:a]anull[a]"
fc = f"[0:v][1:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.6:.2f}:d=0.6,format=yuv420p[v];{af}"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', bgv, '-framerate', str(fps), '-i', frames + 'f%05d.png', *ain,
                '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{dur:.2f}', '-c:v', 'libx264', '-crf', '19',
                '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], check=True)
print('media reel', out)
