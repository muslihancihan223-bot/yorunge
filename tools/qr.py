"""Minimal QR encoder (byte mode, ECC level M or Q, versions 1-10). Nayuki-style.
Usage: python3 qr.py "<text>" out.png [--label "text"]
"""
import sys

# (data codewords per block layout) for ECC M: version -> (ec_per_block, [(blocks, data_cw), ...])
ECC_M = {
    1: (10, [(1, 16)]), 2: (16, [(1, 28)]), 3: (26, [(1, 44)]), 4: (18, [(2, 32)]),
    5: (24, [(2, 43)]), 6: (16, [(4, 27)]), 7: (18, [(4, 31)]), 8: (22, [(2, 38), (2, 39)]),
    9: (22, [(3, 36), (2, 37)]), 10: (26, [(4, 43), (1, 44)]),
}
ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34],
         7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}

# GF(256) arithmetic
EXP = [0] * 512
LOG = [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def rs_generator(deg):
    g = [1]
    for i in range(deg):
        ng = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            ng[j] ^= c
            ng[j + 1] ^= gmul(c, EXP[i])
        g = ng
    return g


def rs_remainder(data, deg):
    gen = rs_generator(deg)
    res = list(data) + [0] * deg
    for i in range(len(data)):
        coef = res[i]
        if coef:
            for j in range(1, len(gen)):
                res[i + j] ^= gmul(gen[j], coef)
    return res[len(data):]


def encode(text):
    data = text.encode("utf-8")
    for ver in range(1, 11):
        ec, groups = ECC_M[ver]
        cap = sum(b * d for b, d in groups)
        ccbits = 8 if ver < 10 else 16
        if 4 + ccbits + 8 * len(data) <= cap * 8:
            break
    else:
        raise ValueError("text too long")
    bits = []

    def put(val, n):
        for i in range(n - 1, -1, -1):
            bits.append((val >> i) & 1)
    put(4, 4)
    put(len(data), ccbits)
    for b in data:
        put(b, 8)
    put(0, min(4, cap * 8 - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    pad = [0xEC, 0x11]
    k = 0
    while len(bits) < cap * 8:
        put(pad[k % 2], 8)
        k += 1
    cws = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    # split into blocks
    blocks, ecblocks = [], []
    idx = 0
    for nb, dc in groups:
        for _ in range(nb):
            blk = cws[idx:idx + dc]
            idx += dc
            blocks.append(blk)
            ecblocks.append(rs_remainder(blk, ec))
    final = []
    for i in range(max(len(b) for b in blocks)):
        for b in blocks:
            if i < len(b):
                final.append(b[i])
    for i in range(ec):
        for b in ecblocks:
            final.append(b[i])
    return ver, final


def build_matrix(ver, codewords):
    size = ver * 4 + 17
    mod = [[None] * size for _ in range(size)]
    func = [[False] * size for _ in range(size)]

    def setf(x, y, v):
        mod[y][x] = v
        func[y][x] = True

    # timing
    for i in range(size):
        setf(6, i, i % 2 == 0)
        setf(i, 6, i % 2 == 0)

    def finder(cx, cy):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    d = max(abs(dx), abs(dy))
                    setf(x, y, d not in (2, 4))
    finder(3, 3)
    finder(size - 4, 3)
    finder(3, size - 4)
    al = ALIGN[ver]
    n = len(al)
    for i in range(n):
        for j in range(n):
            if (i == 0 and j == 0) or (i == 0 and j == n - 1) or (i == n - 1 and j == 0):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    setf(al[i] + dx, al[j] + dy, max(abs(dx), abs(dy)) != 1)
    # reserve format areas (draw dummy)
    draw_format(mod, func, size, 0, setf)
    if ver >= 7:
        draw_version(ver, size, setf)
    # data
    allbits = []
    for cw in codewords:
        for i in range(7, -1, -1):
            allbits.append((cw >> i) & 1)
    i = 0
    right = size - 1
    while right >= 1:
        if right == 6:
            right = 5
        for vert in range(size):
            for j in range(2):
                x = right - j
                upward = ((right + 1) & 2) == 0
                y = size - 1 - vert if upward else vert
                if not func[y][x]:
                    mod[y][x] = bool(allbits[i]) if i < len(allbits) else False
                    i += 1
        right -= 2
    return mod, func, size


def draw_format(mod, func, size, mask, setf):
    data = (0 << 3) | mask  # ECC M = 00
    rem = data
    for _ in range(10):
        rem = (rem << 1) ^ ((rem >> 9) * 0x537)
    bits = ((data << 10) | rem) ^ 0x5412
    g = lambda i: ((bits >> i) & 1) == 1
    for i in range(0, 6):
        setf(8, i, g(i))
    setf(8, 7, g(6))
    setf(8, 8, g(7))
    setf(7, 8, g(8))
    for i in range(9, 15):
        setf(14 - i, 8, g(i))
    for i in range(0, 8):
        setf(size - 1 - i, 8, g(i))
    for i in range(8, 15):
        setf(8, size - 15 + i, g(i))
    setf(8, size - 8, True)


def draw_version(ver, size, setf):
    rem = ver
    for _ in range(12):
        rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
    bits = (ver << 12) | rem
    for i in range(18):
        b = ((bits >> i) & 1) == 1
        a, c = size - 11 + i % 3, i // 3
        setf(a, c, b)
        setf(c, a, b)


MASKS = [
    lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
    lambda x, y: (x + y) % 3 == 0, lambda x, y: (x // 3 + y // 2) % 2 == 0,
    lambda x, y: x * y % 2 + x * y % 3 == 0, lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
    lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
]


def penalty(m, size):
    p = 0
    for rows in (m, [list(c) for c in zip(*m)]):
        for row in rows:
            run, col = 1, row[0]
            for v in row[1:]:
                if v == col:
                    run += 1
                else:
                    if run >= 5:
                        p += run - 2
                    run, col = 1, v
            if run >= 5:
                p += run - 2
            s = "".join("1" if v else "0" for v in row)
            p += 40 * (s.count("10111010000") + s.count("00001011101"))
    for y in range(size - 1):
        for x in range(size - 1):
            if m[y][x] == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                p += 3
    dark = sum(v for row in m for v in row)
    p += abs(dark * 20 - size * size * 10) // (size * size) * 10
    return p


def make(text):
    ver, cws = encode(text)
    base, func, size = build_matrix(ver, cws)
    best = None
    for mk in range(8):
        m = [row[:] for row in base]
        for y in range(size):
            for x in range(size):
                if not func[y][x] and MASKS[mk](x, y):
                    m[y][x] = not m[y][x]

        def setf(x, y, v):
            m[y][x] = v
        draw_format(m, func, size, mk, setf)
        p = penalty(m, size)
        if best is None or p < best[0]:
            best = (p, m)
    return best[1]


def save_png(m, path, scale=16, border=4, label=None):
    from PIL import Image, ImageDraw, ImageFont
    size = len(m)
    w = (size + border * 2) * scale
    extra = 0
    if label:
        extra = scale * 5
    img = Image.new("RGB", (w, w + extra), "white")
    d = ImageDraw.Draw(img)
    for y in range(size):
        for x in range(size):
            if m[y][x]:
                x0, y0 = (x + border) * scale, (y + border) * scale
                d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill="black")
    if label:
        try:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", scale * 2)
        except Exception:
            f = ImageFont.load_default()
        tw = d.textlength(label, font=f)
        d.text(((w - tw) / 2, w - scale), label, fill="black", font=f)
    img.save(path)


if __name__ == "__main__":
    text, out = sys.argv[1], sys.argv[2]
    label = None
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
    save_png(make(text), out, label=label)
    print("saved", out)
