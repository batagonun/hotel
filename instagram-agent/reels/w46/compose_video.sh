#!/bin/bash
# compose_video.sh <out.mp4> <overlay_dir> <total_secs> clip1:start:dur clip2:start:dur ...
# Crops each real clip to 1080x1920, cross-fades (0.5s), overlays the transparent text frames, adds a soft pad.
set -e
out=$1; ov=$2; total=$3; shift 3
inputs=(); filt=""; i=0; offs=0; prev=""
for c in "$@"; do IFS=: read f s d <<< "$c"
  inputs+=(-ss "$s" -t "$d" -i "$f")
  filt+="[$i:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,setsar=1,format=yuv420p[v$i];"
  if [ $i -eq 0 ]; then prev="v0"; offs=$d; else
    o=$(echo "$offs-0.5" | bc); filt+="[$prev][v$i]xfade=transition=fade:duration=0.5:offset=$o[x$i];"; prev="x$i"; offs=$(echo "$offs+$d-0.5" | bc); fi
  i=$((i+1)); done
n=$i
filt+="[$n:v]format=rgba[ov];[$prev][ov]overlay=0:0:shortest=1,format=yuv420p[v]"
audio="aevalsrc='0.06*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.04*sin(2*PI*330*t)+0.03*sin(2*PI*440*t)':s=44100:d=$total,lowpass=f=1200,afade=t=in:d=1,afade=t=out:st=$(echo "$total-1.2"|bc):d=1.2"
ffmpeg -loglevel error -y "${inputs[@]}" -framerate 25 -i "$ov/f%05d.png" -f lavfi -i "$audio" \
  -filter_complex "$filt" -map "[v]" -map $((n+1)):a -t "$total" -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$out"
echo composed "$out"
