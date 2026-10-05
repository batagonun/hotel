#!/usr/bin/env bash
# Turns a finished 1080x1350 post image into a 9-second 1080x1920 Instagram Reel (free: ffmpeg only).
# Slow zoom on the design, blurred fill top/bottom, and a soft synthesized ambient pad (no copyrighted audio).
# Usage: tools/reel.sh in.jpg out.mp4 [seconds]
set -euo pipefail
in="$1"; out="$2"; dur="${3:-9}"; fr=30; n=$((dur*fr))
ffmpeg -y -loglevel error \
  -loop 1 -t "$dur" -i "$in" \
  -i "$in" \
  -f lavfi -t "$dur" -i "aevalsrc='(0.05*sin(2*PI*110*t)+0.05*sin(2*PI*220*t)+0.04*sin(2*PI*261.63*t)+0.035*sin(2*PI*329.63*t)+0.02*sin(2*PI*392*t))*(0.85+0.15*sin(2*PI*0.25*t))':s=44100" \
  -filter_complex "
    [0:v]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.12:saturation=0.9,fps=$fr[bg];
    [1:v]scale=2160:2700,zoompan=z='min(zoom+0.00025,1.07)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$n:s=1080x1350:fps=$fr[fg];
    [bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,fade=t=in:st=0:d=0.4,fade=t=out:st=$(echo "$dur-0.6"|bc):d=0.6,format=yuv420p[v];
    [2:a]lowpass=f=1200,afade=t=in:st=0:d=1.2,afade=t=out:st=$(echo "$dur-1.5"|bc):d=1.5,volume=0.8[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -profile:v high -r $fr \
  -c:a aac -b:a 128k -ar 44100 -movflags +faststart -t "$dur" "$out"
echo "reel $out"
