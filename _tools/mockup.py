"""Make protected product mockups: pages fanned on a soft background, low resolution, marked "Preview".

Usage: python _tools/mockup.py
Writes planner-preview.png (Exam Sprint Planner, same URL as before) and
assets/products/*.webp / *.png for each planner.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import fitz  # pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = pathlib.Path(r"F:\Personal Projects\focusflowlab-products")
OUT = ROOT / "assets/products"
OUT.mkdir(parents=True, exist_ok=True)
FONT = None
for f in [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]:
    if pathlib.Path(f).exists():
        FONT = f; break

BG = (226, 244, 239)        # mint wash
PAGE_H = 600                # low on purpose: shows the layout, too small to print well

def mark(page):
    """Soft diagonal 'Preview' marks tiled across the page."""
    w, h = page.size
    big = Image.new("RGBA", (w * 3, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    font = ImageFont.truetype(FONT, int(w * 0.13)) if FONT else ImageFont.load_default()
    step_x, step_y = int(w * 0.75), int(h * 0.22)
    for row, y in enumerate(range(0, h * 3, step_y)):
        for x in range(-w + (row % 2) * step_x // 2, w * 3, step_x):
            d.text((x, y), "Preview", font=font, fill=(20, 33, 61, 30))
    big = big.rotate(28, resample=Image.BICUBIC)
    layer = big.crop((w, h, 2 * w, 2 * h))
    out = page.convert("RGBA"); out.alpha_composite(layer)
    return out

def shrink(page):
    r = PAGE_H / page.height
    return page.resize((int(page.width * r), PAGE_H), Image.LANCZOS)

def compose(pages, size=(1600, 900)):
    canvas = Image.new("RGBA", size, BG + (255,))
    n = len(pages)
    angles = [-9, -3, 3, 9][:n] if n == 4 else [-7, 0, 7][:n]
    spread = 300 if n == 4 else 360
    cx = size[0] // 2
    for i, (pg, ang) in enumerate(zip(pages, angles)):
        pg = mark(shrink(pg))
        rot = pg.rotate(-ang, expand=True, resample=Image.BICUBIC)
        pad = 60
        shadow = Image.new("RGBA", (rot.width + 2 * pad, rot.height + 2 * pad), (0, 0, 0, 0))
        alpha = Image.new("L", shadow.size, 0)
        alpha.paste(rot.split()[3].point(lambda a: 60 if a > 0 else 0), (pad, pad))
        shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(26)))
        shadow = Image.composite(Image.new("RGBA", shadow.size, (20, 40, 60, 255)), shadow, alpha.filter(ImageFilter.GaussianBlur(26)))
        shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(26)))
        x = int(cx + (i - (n - 1) / 2) * spread - rot.width / 2)
        y = int(size[1] / 2 - rot.height / 2 + abs(ang) * 3)
        canvas.alpha_composite(shadow, (x - pad + 8, y - pad + 24))
        canvas.alpha_composite(rot, (x, y))
    return canvas.convert("RGB")

def save(img, name):
    img.save(OUT / f"{name}.webp", quality=80)
    small = img.resize((800, int(800 * img.height / img.width)), Image.LANCZOS)
    small.save(OUT / f"{name}-800.webp", quality=80)
    img.save(OUT / f"{name}.png", optimize=True)
    print("wrote", name)

# Exam Sprint Planner: cut the four pages out of the old flat preview (copy it to %TEMP%/_exam-sprint-source.png from git history first)
src = Image.open(pathlib.Path(__import__("os").environ["TEMP"]) / "_exam-sprint-source.png").convert("RGB")
boxes = [(20, 20, 510, 713), (525, 20, 985, 713), (1015, 20, 1475, 713), (1505, 20, 1965, 713)]
pages = []
for b in boxes:
    pg = Image.new("RGB", (490, 693), "white")
    crop = src.crop(b); pg.paste(crop, (0, 0))
    pages.append(pg)
sprint = compose(pages)
save(sprint, "exam-sprint-planner")
sprint.save(ROOT / "planner-preview.png", optimize=True)   # same URL as before, now the protected mockup

# New planners: render pages 1, 6, 4 from the PDFs at low resolution
for name in ["NCLEX-RN-8-Week-Study-Planner", "MCAT-16-Week-Study-Planner"]:
    doc = fitz.open(PRODUCTS / f"{name}.pdf")
    imgs = []
    for i in (0, 5, 3):
        pix = doc[i].get_pixmap(dpi=70)
        imgs.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    save(compose(imgs), name.lower())
