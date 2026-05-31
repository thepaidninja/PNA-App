"""
Icon generator for Pai Nayak & Associates Audit Management Software.
Produces app_icon.ico with sizes: 16, 32, 48, 64, 128, 256.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

# Brand colors matching the app's dark theme
BG_DARK   = (18, 28, 58)    # Deep navy
BG_MID    = (26, 42, 88)    # Mid navy (inner fill)
GOLD      = (196, 160, 72)  # Gold accent
GOLD_LITE = (230, 195, 110) # Lighter gold for highlights
WHITE     = (240, 244, 255) # Near-white text


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_vertical_gradient(draw, x0, y0, x1, y1, top_color, bot_color):
    h = y1 - y0
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(h, 1)
        draw.line([(x0, y), (x1, y)], fill=(*lerp_color(top_color, bot_color, t), 255))


def rounded_rect_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def get_font(size, bold=True):
    candidates = [
        # Windows
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/verdanab.ttf" if bold else "C:/Windows/Fonts/verdana.ttf",
        # macOS
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_balance_scale(draw, cx, cy, size, color, lw):
    """Draw a simplified balance scale (two pans on a beam with a fulcrum)."""
    beam_half = size * 0.38
    beam_y    = cy - size * 0.10
    pole_h    = size * 0.28
    pan_r     = size * 0.09
    chain_len = size * 0.10

    # Vertical pole
    draw.line([(cx, beam_y), (cx, beam_y + pole_h)], fill=color, width=max(1, lw))
    # Base feet
    base_w = size * 0.18
    draw.line([(cx - base_w, beam_y + pole_h), (cx + base_w, beam_y + pole_h)],
              fill=color, width=max(1, lw))
    # Beam
    draw.line([(cx - beam_half, beam_y), (cx + beam_half, beam_y)],
              fill=color, width=max(1, lw))
    # Central pivot dot
    piv = max(2, lw + 1)
    draw.ellipse([(cx - piv, beam_y - piv), (cx + piv, beam_y + piv)], fill=color)
    # Left chain + pan
    lx = cx - beam_half
    draw.line([(lx, beam_y), (lx, beam_y + chain_len)], fill=color, width=max(1, lw))
    draw.ellipse([
        (lx - pan_r, beam_y + chain_len),
        (lx + pan_r, beam_y + chain_len + pan_r * 0.5)
    ], outline=color, width=max(1, lw))
    # Right chain + pan
    rx = cx + beam_half
    draw.line([(rx, beam_y), (rx, beam_y + chain_len)], fill=color, width=max(1, lw))
    draw.ellipse([
        (rx - pan_r, beam_y + chain_len),
        (rx + pan_r, beam_y + chain_len + pan_r * 0.5)
    ], outline=color, width=max(1, lw))


def make_frame(size):
    img   = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd    = ImageDraw.Draw(grad)
    draw_vertical_gradient(gd, 0, 0, size - 1, size - 1, BG_MID, BG_DARK)

    radius = size // 5
    mask   = rounded_rect_mask(size, radius)
    img.paste(grad, mask=mask)

    draw = ImageDraw.Draw(img)

    # Gold border
    bw = max(1, size // 48)
    draw.rounded_rectangle([bw, bw, size - 1 - bw, size - 1 - bw],
                            radius=radius - bw, outline=GOLD, width=bw)

    if size >= 64:
        # Balance scale in upper portion
        scale_size = size * 0.44
        cx = size / 2
        cy = size * 0.38
        lw = max(1, size // 56)
        draw_balance_scale(draw, cx, cy, scale_size, GOLD_LITE, lw)

        # Thin divider line
        pad  = size * 0.16
        div_y = int(size * 0.62)
        draw.line([(pad, div_y), (size - pad, div_y)], fill=GOLD, width=max(1, size // 96))

        # "PNA" text below divider
        font_sz = max(8, int(size * 0.22))
        font    = get_font(font_sz, bold=True)
        text    = "PNA"
        bbox    = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2 - bbox[0]
        ty = div_y + int(size * 0.05) - bbox[1]
        draw.text((tx, ty), text, fill=WHITE, font=font)

    elif size >= 32:
        # Just "PNA" centered — no scale at this size
        font_sz = max(7, int(size * 0.30))
        font    = get_font(font_sz, bold=True)
        text    = "PNA"
        bbox    = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2 - bbox[0]
        ty = (size - th) // 2 - bbox[1]
        draw.text((tx, ty), text, fill=GOLD_LITE, font=font)

    else:
        # 16×16: single letter "P"
        font_sz = max(6, int(size * 0.55))
        font    = get_font(font_sz, bold=True)
        text    = "P"
        bbox    = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2 - bbox[0]
        ty = (size - th) // 2 - bbox[1]
        draw.text((tx, ty), text, fill=GOLD_LITE, font=font)

    return img


def build_ico(out_path="app_icon.ico"):
    sizes   = [256, 128, 64, 48, 32, 16]
    frames  = [make_frame(s) for s in sizes]
    # PIL saves multi-size ICO when append_images is provided
    frames[0].save(
        out_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print(f"Saved {out_path}  ({len(frames)} sizes: {sizes})")


def build_png(out_path="app_icon.png", size=512):
    img = make_frame(size)
    img.save(out_path, format="PNG")
    print(f"Saved {out_path}  ({size}x{size})")


if __name__ == "__main__":
    import sys
    if "--png" in sys.argv:
        build_png()
    else:
        build_ico()
