"""GameDistribution kapak görselleri: gd-assets/{512x384,512x512,200x120,1280x720,1280x550}.jpg"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "gd-assets"); os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
BG, NEON, PINK, GOLD, RED = (7, 7, 26), (61, 242, 255), (255, 61, 242), (255, 200, 60), (255, 50, 90)

def glow(size, draw_fn, blur):
    layer = Image.new("RGBA", size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(layer))
    return Image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)), layer)

def fit_font(text, max_w, max_h):
    s = int(max_h)
    while s > 8:
        f = ImageFont.truetype(FONT, s); b = f.getbbox(text)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h: return f
        s -= 2
    return ImageFont.truetype(FONT, 8)

def make(w, h, subtitle=True):
    random.seed(7); k = min(w, h)
    img = Image.new("RGBA", (w, h), BG + (255,)); d = ImageDraw.Draw(img)
    for _ in range(int(w * h / 900)):  # yıldızlar
        x, y = random.randrange(w), random.randrange(h); c = random.randint(40, 110)
        d.point((x, y), fill=(c, c, c + 30, 255))
    cx, cy, r = w * 0.5, h * 0.46, k * 0.34
    def orbit(dd):
        dd.ellipse((cx - r, cy - r, cx + r, cy + r), outline=NEON + (200,), width=max(2, k // 120))
        dd.ellipse((cx - k*0.05, cy - k*0.05, cx + k*0.05, cy + k*0.05), fill=PINK + (255,))
        a = math.radians(200); dd.line((cx, cy, cx + math.cos(a) * w, cy + math.sin(a) * w), fill=RED + (230,), width=max(3, k // 45))
        for ang, col, rad in ((-50, NEON, 0.055), (25, GOLD, 0.035), (120, GOLD, 0.03)):
            t = math.radians(ang); px, py = cx + math.cos(t) * r, cy + math.sin(t) * r
            dd.ellipse((px - k*rad, py - k*rad, px + k*rad, py + k*rad), fill=col + (255,))
    img = Image.alpha_composite(img, glow((w, h), orbit, k / 40))
    title = "YÖRÜNGE"
    tf = fit_font(title, w * 0.86, h * (0.26 if subtitle else 0.42))
    tb = tf.getbbox(title); tw, th = tb[2] - tb[0], tb[3] - tb[1]
    ty = h * (0.60 if subtitle else 0.5) - th / 2 - tb[1]
    tx = (w - tw) / 2 - tb[0]
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(shade).rectangle((0, ty + tb[1] - h*0.04, w, h), fill=(7, 7, 26, 150))
    img = Image.alpha_composite(img, shade.filter(ImageFilter.GaussianBlur(k / 25)))
    img = Image.alpha_composite(img, glow((w, h), lambda dd: dd.text((tx, ty), title, font=tf, fill=NEON + (255,)), k / 30))
    img = Image.alpha_composite(img, glow((w, h), lambda dd: dd.text((tx, ty), title, font=tf, fill=(235, 255, 255, 255)), 1))
    if subtitle:
        st = "NEON ORBIT"; sf = fit_font(st, w * 0.6, h * 0.09); sb = sf.getbbox(st)
        sx = (w - (sb[2] - sb[0])) / 2 - sb[0]; sy = ty + tb[3] + h * 0.03
        img = Image.alpha_composite(img, glow((w, h), lambda dd: dd.text((sx, sy), st, font=sf, fill=PINK + (255,)), k / 60))
    return img.convert("RGB")

for (w, h, sub) in ((512, 384, True), (512, 512, True), (200, 120, False), (1280, 720, True), (1280, 550, True)):
    make(w, h, sub).save(os.path.join(OUT, f"{w}x{h}.jpg"), quality=72, optimize=True, progressive=True)
print("tamam")
