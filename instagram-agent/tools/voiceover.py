#!/usr/bin/env python3
"""Merge a voiceover (e.g. from tools/tts.py) onto a reel video. Free: ffmpeg only.

What it handles:
  * length mismatch: if the voice (plus lead-in and tail) is longer than the video,
    the last frame is held (freeze) until the voice ends; if it is shorter, the video
    keeps its length and the voice is padded with silence.
  * music: the reel's own soundtrack (or --music, looped if short) is lowered and
    ducked automatically under the voice (sidechain), then faded out at the end.
  * loudness: the voice is normalised to about -16 LUFS (Instagram-friendly).
  * videos with no audio track and voices of any sample rate.

usage:
  python3 tools/voiceover.py <reel.mp4> <voice.wav> <out.mp4>
          [--delay 0.5] [--tail 0.8] [--music-vol 0.25] [--music track.mp3] [--no-music]
          [--max-extend 6]

  --delay       seconds of video before the voice starts (default 0.5)
  --tail        seconds kept after the voice ends (default 0.8)
  --music-vol   music level under the voice, 0-1 (default 0.25)
  --music       use this track instead of the video's own audio (looped to length)
  --no-music    voice only
  --max-extend  if holding the last frame would add more than this many seconds,
                stop and ask for a shorter script or an extra scene (default 6)
"""
import argparse
import json
import subprocess
import sys


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
         "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    kinds = {s["codec_type"] for s in d.get("streams", [])}
    return float(d["format"]["duration"]), "audio" in kinds


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("voice")
    p.add_argument("out")
    p.add_argument("--delay", type=float, default=0.5)
    p.add_argument("--tail", type=float, default=0.8)
    p.add_argument("--music-vol", type=float, default=0.25)
    p.add_argument("--music")
    p.add_argument("--no-music", action="store_true")
    p.add_argument("--max-extend", type=float, default=6.0)
    a = p.parse_args()

    vdur, vhas_audio = probe(a.video)
    adur, _ = probe(a.voice)
    need = a.delay + adur + a.tail
    extend = max(0.0, need - vdur)
    total = vdur + extend
    if extend > a.max_extend:
        sys.exit(f"الصوت ({adur:.1f}ث) أطول من الريل ({vdur:.1f}ث) بـ {extend:.1f}ث، وتثبيت آخر لقطة كل المدة دي هيبان. "
                 f"اختصر النص أو زوّد مشهد، أو ارفع --max-extend لو مقصود.")

    inputs = ["-i", a.video, "-i", a.voice]
    music = None
    if not a.no_music:
        if a.music:
            inputs = ["-i", a.video, "-i", a.voice, "-stream_loop", "-1", "-i", a.music]
            music = "2:a"
        elif vhas_audio:
            music = "0:a"

    ms = int(a.delay * 1000)
    fade_start = max(0.0, total - 1.5)
    f = []
    # video: hold the last frame if the voice runs longer
    if extend > 0:
        f.append(f"[0:v]tpad=stop_mode=clone:stop_duration={extend:.3f}[v]")
    # voice: normalise, common format, lead-in delay, pad to full length
    f.append(f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,"
             f"adelay={ms}|{ms},apad,atrim=0:{total:.3f}[vo]")
    if music:
        f.append("[vo]asplit=2[vo1][sc]")
        f.append(f"[{music}]aformat=sample_rates=44100:channel_layouts=stereo,volume={a.music_vol},"
                 f"apad,atrim=0:{total:.3f}[m]")
        f.append("[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500[duck]")
        f.append(f"[vo1][duck]amix=inputs=2:duration=first:normalize=0,"
                 f"afade=t=out:st={fade_start:.3f}:d=1.5,alimiter=limit=0.95[a]")
    else:
        f.append(f"[vo]afade=t=out:st={fade_start:.3f}:d=1.5[a]")

    vmap = "[v]" if extend > 0 else "0:v"
    vcodec = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"] if extend > 0 else ["-c:v", "copy"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(f),
           "-map", vmap, "-map", "[a]", *vcodec, "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-t", f"{total:.3f}", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    note = f"تثبيت آخر لقطة {extend:.1f}ث" if extend > 0 else "طول الفيديو كما هو"
    print(f"✓ {a.out}  ({total:.1f}ث، الصوت {adur:.1f}ث، {note})", file=sys.stderr)


if __name__ == "__main__":
    main()
