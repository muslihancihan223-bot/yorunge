"""QR afişlerini üretir. Her konum için ayrı ?src= kodu olur; hangi afişin kaç oyuncu getirdiği ayrı sayılır.
Kullanım: python3 tools/afis.py [temel_url]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qr import make  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://muslihancihan223-bot.github.io/yorunge/"
OUT = os.path.join(os.path.dirname(__file__), "..", "qr")
os.makedirs(OUT, exist_ok=True)

KONUMLAR = [
    ("durak", "Otobüs mü gecikti?"),
    ("kafe", "Siparişin gelene kadar"),
    ("tuvalet", "Sıkıldın mı?"),
    ("otel", "Lobide beklerken"),
    ("berber", "Sıra sende değil mi?"),
    ("hastane", "Sıra beklerken"),
]

F = "/usr/share/fonts/truetype/dejavu/"
bold = lambda s: ImageFont.truetype(F + "DejaVuSans-Bold.ttf", s)
reg = lambda s: ImageFont.truetype(F + "DejaVuSans.ttf", s)

BG, NEON, PINK, GOLD = (7, 7, 26), (61, 242, 255), (255, 61, 242), (255, 210, 61)


def qr_image(url, px):
    m = make(url)
    n = len(m)
    border = 3
    scale = px // (n + border * 2)
    img = Image.new("RGB", ((n + border * 2) * scale,) * 2, "white")
    d = ImageDraw.Draw(img)
    for y in range(n):
        for x in range(n):
            if m[y][x]:
                x0, y0 = (x + border) * scale, (y + border) * scale
                d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill="black")
    return img


def center(d, y, text, font, fill, W):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)


def glow_text(img, y, text, font, color, W):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    center(ld, y, text, font, color + (255,), W)
    blur = layer.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(blur)
    img.alpha_composite(blur)
    img.alpha_composite(layer)


def poster(src, hook):
    W, H = 1240, 1748  # A6 @ 300dpi (105x148mm)
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    # yörünge süsü
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([W / 2 - 470, 950 - 450, W / 2 + 470, 950 + 430], outline=NEON + (90,), width=6)
    img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(ring)

    center(d, 110, hook, bold(66), (230, 230, 255), W)
    glow_text(img, 210, "YÖRÜNGE", bold(150), NEON, W)
    center(d, 400, "Okut, 30 saniyede oyna", bold(58), GOLD, W)

    q = qr_image(BASE + "?src=" + src, 720)
    q = q.resize((720, 720), Image.NEAREST)
    frame = Image.new("RGBA", (780, 780), PINK + (255,))
    frame_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frame_glow.paste(frame, ((W - 780) // 2, 560))
    img.alpha_composite(frame_glow.filter(ImageFilter.GaussianBlur(20)))
    img.paste(frame.convert("RGB"), ((W - 780) // 2, 560))
    img.paste(q, ((W - 720) // 2, 590))

    d = ImageDraw.Draw(img)
    center(d, 1400, "İndirme yok • Üyelik yok • Ücretsiz", reg(46), (200, 200, 235), W)
    center(d, 1480, "Rekorunu kır, arkadaşına meydan oku", reg(42), (160, 160, 210), W)
    center(d, 1640, BASE.replace("https://", "").rstrip("/"), reg(30), (110, 110, 160), W)
    path = os.path.join(OUT, f"afis-{src}.png")
    img.convert("RGB").save(path, dpi=(300, 300))

    # sade QR (sticker için)
    qr_image(BASE + "?src=" + src, 1000).save(os.path.join(OUT, f"qr-{src}.png"))
    return path


if __name__ == "__main__":
    for src, hook in KONUMLAR:
        print(poster(src, hook))
