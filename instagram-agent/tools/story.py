# Builds a 1080x1920 reel from real photos / time-lapse frames + transparent text overlays (ffmpeg, free).
# Usage: python3 tools/story.py <story.json> <out.mp4>
# story.json: {"scenes":[{"photo":"path"} | {"frames":["p1","p2",...]}, "overlay":"path.png", "dur":3.2}], "fade":0.45}
import json, subprocess, sys, tempfile, os

spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
fade = spec.get('fade', 0.45)
fps = 30
tmp = tempfile.mkdtemp()
clips = []

# Photo sits in the lower part of the frame (text lives at the top); a blurred copy fills the rest.
PH = "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.22[bg];" \
     "[b]scale=1180:-2,crop=1180:'min(ih,1200)'[fg];[bg][fg]overlay=(W-w)/2+{dx}:H-h-170"

for i, sc in enumerate(spec['scenes']):
    d = sc.get('dur', 3.2)
    n = int(d * fps)
    clip = os.path.join(tmp, f'c{i}.mp4')
    if 'photo' in sc:
        # Slow push-in on the composed frame (Ken Burns).
        vf = PH.format(dx=0) + f",scale=2160:3840,zoompan=z='min(zoom+0.0009,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps={fps}"
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', sc['photo'], '-loop', '1', '-t', str(d), '-i', sc['overlay'],
               '-filter_complex', f"[0:v]{vf}[v];[v][1:v]overlay=0:0,format=yuv420p", '-t', str(d), '-r', str(fps), clip]
    else:
        # Time-lapse: cross-fade between consecutive frames.
        frames = sc['frames']
        seg = d / len(frames)
        inputs, chain = [], ''
        for f in frames:
            inputs += ['-loop', '1', '-t', str(seg + 0.4), '-i', f]
        k = len(frames)
        for j in range(k):
            chain += f"[{j}:v]{sc.get('crop', 'null')},scale=1080:-2,pad=1080:1920:0:oh-ih-330:black,setsar=1,fps={fps}[f{j}];"
        prev = 'f0'
        for j in range(1, k):
            chain += f"[{prev}][f{j}]xfade=transition=fade:duration=0.4:offset={seg * j:.3f}[x{j}];"
            prev = f'x{j}'
        chain += f"[{prev}][{k}:v]overlay=0:0,format=yuv420p"
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-loop', '1', '-i', sc['overlay'],
               '-filter_complex', chain, '-t', str(d), '-r', str(fps), clip]
    subprocess.run(cmd, check=True)
    clips.append((clip, d))

# Chain all clips with cross-fades, add a soft synthesized pad (no music rights involved).
inputs, chain, prev, t = [], '', '0:v', 0
for c, _ in clips:
    inputs += ['-i', c]
for j in range(1, len(clips)):
    t += clips[j - 1][1] - fade
    chain += f"[{prev}][{j}:v]xfade=transition=fade:duration={fade}:offset={t:.3f}[v{j}];"
    prev = f'v{j}'
total = sum(d for _, d in clips) - fade * (len(clips) - 1)
chain += f"[{prev}]fade=t=in:st=0:d=0.4,fade=t=out:st={total - 0.6:.2f}:d=0.6[vout]"
audio = f"aevalsrc='0.06*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.04*sin(2*PI*330*t)+0.03*sin(2*PI*440*t)':s=44100:d={total:.2f},lowpass=f=1200,afade=t=in:d=1,afade=t=out:st={total - 1.2:.2f}:d=1.2"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-f', 'lavfi', '-i', audio,
                '-filter_complex', chain, '-map', '[vout]', '-map', f'{len(clips)}:a',
                '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], check=True)
print('reel', out, f'{total:.1f}s')
