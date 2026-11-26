"""Second free tool in the pipeline (Pillow): adds subtle film grain and a soft
vignette to each rendered PNG, then exports an Instagram-ready JPEG (1080x1350, sRGB)."""
import sys, glob, os, random
from PIL import Image, ImageFilter, ImageChops

src = sys.argv[1]
for png in sorted(glob.glob(os.path.join(src, "*.png"))):
    im = Image.open(png).convert("RGB")
    w, h = im.size
    # soft vignette
    mask = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).ellipse((-w * .25, -h * .2, w * 1.25, h * 1.2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    im = Image.composite(im, Image.blend(im, dark, .28), mask)
    # fine grain
    random.seed(7)
    noise = Image.effect_noise((w, h), 18).convert("RGB")
    im = Image.blend(im, ImageChops.overlay(im, noise), .10)
    out = png[:-4] + ".jpg"
    im.save(out, "JPEG", quality=92, optimize=True, progressive=True)
    os.remove(png)
    print("finished", out)
