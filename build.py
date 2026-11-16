#!/usr/bin/env python3
"""ai-excited-01 round 8 — 'The Ember Wolf That Burned Through Its Frame'.

Deterministic SVG -> PNG (768x768) via cairosvg. All artwork is generated
here from hand-placed paths: a giant ember wolf leaping diagonally from the
bottom-right to the top-left, bursting through a shattered golden frame.
Seeded RNG only; same input bytes -> same output bytes.
v2: leaner lupine anatomy, bigger head, muscular legs, flame mane trailing
    opposite the leap (south-east), irregular shards, embers on the leap path.
"""
import hashlib
import math
import random
import sys

import cairosvg

W = H = 768
SEED = 8
rng = random.Random(SEED)

# ---------------------------------------------------------------- palette
FUR_D = "#171226"
FUR_M = "#2c2140"
FUR_L = "#4a3560"
EMBER = "#ff6a00"
EMBER2 = "#ff9d00"
GOLD = "#ffd23f"
GOLD_D = "#b97f10"
GOLD_L = "#ffe9a8"

# ---------------------------------------------------------------- helpers
def poly(points, **kw):
    pts = " ".join(f"{x},{y}" for x, y in points)
    attrs = " ".join(f'{k}="{v}"' for k, v in kw.items())
    return f'<polygon points="{pts}" {attrs}/>'

def path(d, **kw):
    attrs = " ".join(f'{k}="{v}"' for k, v in kw.items())
    return f'<path d="{d}" {attrs}/>'

def circle(cx, cy, r, **kw):
    attrs = " ".join(f'{k}="{v}"' for k, v in kw.items())
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {attrs}/>'

def flame(x, y, length, angle_deg, w, fill, bend=0.45):
    """One curved flame tongue pointing along angle_deg (0=east, 90=south).
    S-curved: the tip curls sideways so it reads as fire, not a triangle."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    tip = (x + dx * length + px * w * 1.6, y + dy * length + py * w * 1.6)
    b1 = (x + px * w, y + py * w)
    b2 = (x - px * w, y - py * w)
    c1 = (x + dx * length * 0.45 + px * w * 0.9, y + dy * length * 0.45 + py * w * 0.9)
    c2 = (x + dx * length * 0.8 + px * w * 1.4, y + dy * length * 0.8 + py * w * 1.4)
    return path(
        f"M {b1[0]:.1f},{b1[1]:.1f} Q {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
        f"Q {tip[0]:.1f},{tip[1]:.1f} {tip[0]:.1f},{tip[1]:.1f} "
        f"Q {x + dx * length * 0.55 - px * w * 0.7:.1f},{y + dy * length * 0.55 - py * w * 0.7:.1f} "
        f"{b2[0]:.1f},{b2[1]:.1f} Z",
        fill=fill, stroke="none")

def leg2(x1, y1, xm, ym, x2, y2, w1, wm, w2, fill, stroke="#0d0a18"):
    """A bent limb: upper segment (x1,y1)->(xm,ym), lower (xm,ym)->(x2,y2)."""
    return (leg(x1, y1, xm, ym, w1, wm, fill, stroke)
            + leg(xm, ym, x2, y2, wm, w2, fill, stroke))

def paw(x, y, ang_deg, s, fill="url(#fur)"):
    """Small paw with three claws pointing along ang_deg."""
    a = math.radians(ang_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    pts = [(x + px * s * 0.7, y + py * s * 0.7), (x + dx * s * 0.9, y + dy * s * 0.9),
           (x - px * s * 0.7, y - py * s * 0.7), (x - dx * s * 0.5, y - dy * s * 0.5)]
    out = [poly(pts, fill=fill, stroke="#0d0a18", **{"stroke-width": 1.5})]
    for k in (-0.55, 0.0, 0.55):
        cx = x + dx * s * 0.9 + px * s * k
        cy = y + dy * s * 0.9 + py * s * k
        out.append(path(f"M {cx:.1f},{cy:.1f} l {dx * s * 0.9:.1f},{dy * s * 0.9:.1f} "
                        f"l {-px * s * 0.28 + dx * s * 0.1:.1f},{-py * s * 0.28 + dy * s * 0.1:.1f} Z",
                        fill="#e8ecff", opacity="0.95"))
    return "".join(out)

def leg(x1, y1, x2, y2, w1, w2, fill, stroke="#0d0a18"):
    """A tapered limb from (x1,y1) width w1 to (x2,y2) width w2."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    a = (x1 + px * w1 / 2, y1 + py * w1 / 2)
    b = (x2 + px * w2 / 2, y2 + py * w2 / 2)
    c = (x2 - px * w2 / 2, y2 - py * w2 / 2)
    d = (x1 - px * w1 / 2, y1 - py * w1 / 2)
    return path(f"M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f} "
                f"L {c[0]:.1f},{c[1]:.1f} L {d[0]:.1f},{d[1]:.1f} Z",
                fill=fill, stroke=stroke, **{"stroke-width": 1.5})

# ---------------------------------------------------------------- defs
defs = """
<defs>
  <radialGradient id="bg" cx="30%" cy="22%" r="95%">
    <stop offset="0%" stop-color="#16224f"/>
    <stop offset="45%" stop-color="#0b1026"/>
    <stop offset="100%" stop-color="#05070f"/>
  </radialGradient>
  <radialGradient id="haze" cx="82%" cy="88%" r="70%">
    <stop offset="0%" stop-color="#7a2c00" stop-opacity="0.85"/>
    <stop offset="45%" stop-color="#3a1503" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="#3a1503" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="moon" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#f4f6ff"/>
    <stop offset="70%" stop-color="#dfe6ff"/>
    <stop offset="100%" stop-color="#b9c4ef" stop-opacity="0.25"/>
  </radialGradient>
  <linearGradient id="fur" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#4a3560"/>
    <stop offset="45%" stop-color="#2c2140"/>
    <stop offset="100%" stop-color="#171226"/>
  </linearGradient>
  <linearGradient id="furbelly" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#3a2a52"/>
    <stop offset="100%" stop-color="#120d1e"/>
  </linearGradient>
  <linearGradient id="flame" x1="0%" y1="100%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#ff3d00"/>
    <stop offset="45%" stop-color="#ff6a00"/>
    <stop offset="80%" stop-color="#ff9d00"/>
    <stop offset="100%" stop-color="#ffd23f"/>
  </linearGradient>
  <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#ffe9a8"/>
    <stop offset="35%" stop-color="#f6c945"/>
    <stop offset="65%" stop-color="#c98f12"/>
    <stop offset="100%" stop-color="#8a5a00"/>
  </linearGradient>
  <linearGradient id="gold2" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#ffe9a8"/>
    <stop offset="50%" stop-color="#d9a521"/>
    <stop offset="100%" stop-color="#7a4d00"/>
  </linearGradient>
  <radialGradient id="eye" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#fff6c8"/>
    <stop offset="45%" stop-color="#ffd23f"/>
    <stop offset="100%" stop-color="#ff6a00"/>
  </radialGradient>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="3"/>
  </filter>
  <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="7" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="blur2" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="1.6"/>
  </filter>
</defs>
"""

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
parts.append(defs)

# ---------------------------------------------------------------- background
parts.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
parts.append(f'<rect width="{W}" height="{H}" fill="url(#haze)"/>')
for _ in range(60):
    x = rng.uniform(0, 700); y = rng.uniform(0, 420)
    r = rng.uniform(0.7, 2.0); o = rng.uniform(0.25, 0.85)
    parts.append(circle(f"{x:.1f}", f"{y:.1f}", f"{r:.1f}", fill="#ffffff", opacity=f"{o:.2f}"))
# moon, dim, top-left
parts.append(circle(96, 86, 46, fill="url(#moon)", opacity="0.9"))
parts.append(circle(96, 86, 58, fill="none", stroke="#dfe6ff", **{"stroke-width": 1.5, "stroke-opacity": 0.25}))
parts.append(circle(82, 74, 9, fill="#b9c4ef", opacity="0.35"))
parts.append(circle(108, 98, 6, fill="#b9c4ef", opacity="0.3"))

# ---------------------------------------------------------------- golden frame (tilted -18 deg, shattered)
parts.append('<g transform="rotate(-18 384 384)">')
parts.append('<rect x="92" y="172" width="584" height="424" fill="none" stroke="#ff9d00" stroke-width="26" stroke-opacity="0.18" filter="url(#soft)"/>')
parts.append(path("M 92,172 L 330,172 L 330,196 L 92,196 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 470,172 L 676,172 L 676,196 L 470,196 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 92,572 L 676,572 L 676,596 L 92,596 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 520,572 L 528,596 M 560,572 L 552,596", stroke="#7a4d00", **{"stroke-width": 2, "stroke-opacity": 0.7}))
parts.append(path("M 92,196 L 116,196 L 116,300 L 92,300 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 92,420 L 116,420 L 116,572 L 92,572 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 652,196 L 676,196 L 676,380 L 652,380 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 652,500 L 676,500 L 676,572 L 652,572 Z", fill="url(#gold)", stroke="#7a4d00", **{"stroke-width": 1}))
parts.append(path("M 104,184 L 330,184 M 470,184 L 664,184 M 104,584 L 664,584 M 104,208 L 104,300 M 104,420 L 104,560 M 664,208 L 664,380 M 664,500 L 664,560",
                 stroke="#7a4d00", **{"stroke-width": 1.5, "stroke-opacity": 0.55, "fill": "none"}))
for cx, cy in ((104, 184), (664, 584)):
    parts.append(circle(cx, cy, 10, fill="url(#gold2)", stroke="#7a4d00", **{"stroke-width": 1}))
    parts.append(circle(cx, cy, 4, fill="#ffe9a8"))
parts.append('</g>')

# ---------------------------------------------------------------- shards (irregular, few, near the two gaps)
shards = [
    ([(296, 148), (344, 124), (360, 150), (330, 174), (306, 166)], "url(#gold)"),
    ([(244, 118), (288, 96), (308, 124), (270, 142), (250, 132)], "url(#gold2)"),
    ([(388, 128), (424, 114), (436, 138), (406, 154)], "#c98f12"),
    ([(182, 166), (224, 142), (238, 168), (204, 188), (188, 180)], "url(#gold2)"),
    ([(640, 326), (684, 302), (704, 330), (672, 356), (650, 344)], "url(#gold)"),
    ([(658, 420), (700, 402), (714, 430), (678, 448), (664, 436)], "#c98f12"),
    ([(600, 466), (640, 448), (654, 474), (620, 490), (604, 480)], "url(#gold2)"),
    # thin splinters
    ([(420, 96), (470, 76), (476, 85), (428, 104)], "#f6c945"),
    ([(122, 296), (162, 280), (166, 290), (128, 306)], "#f6c945"),
]
for pts, f in shards:
    parts.append(poly(pts, fill=f, stroke="#7a4d00", **{"stroke-width": 1, "stroke-opacity": 0.8}))

# ---------------------------------------------------------------- motion streaks (behind wolf, along diagonal)
for (x1, y1, x2, y2, w, o, col) in [
    (660, 660, 430, 420, 5, 0.32, "#ff9d00"),
    (710, 560, 480, 350, 3, 0.28, "#ffd23f"),
    (680, 710, 500, 510, 4, 0.26, "#ff6a00"),
    (580, 720, 420, 540, 3, 0.22, "#ffd23f"),
    (730, 470, 540, 300, 3, 0.20, "#ff9d00"),
]:
    parts.append(path(f"M {x1},{y1} Q {(x1+x2)//2 + 30},{(y1+y2)//2 - 20} {x2},{y2}",
                     stroke=col, **{"stroke-width": w, "stroke-opacity": o, "fill": "none",
                                     "stroke-linecap": "round", "filter": "url(#blur2)"}))

# ================================================================ THE WOLF
# ---- TAIL: flame ribbon sweeping down-right from the hip
parts.append(path(
    "M 500,420 C 590,460 655,540 690,625 C 702,656 694,690 664,694 "
    "C 634,698 614,668 604,626 C 592,578 556,532 500,508 Z",
    fill="url(#flame)", stroke="#c22e00", **{"stroke-width": 2, "stroke-opacity": 0.6}))
parts.append(path(
    "M 516,438 C 580,480 632,542 656,610 C 666,636 660,662 642,666 "
    "C 624,670 610,640 604,608 C 596,568 562,526 516,498 Z",
    fill="#ffd23f", opacity="0.85"))
for (x, y, ln, ang, w, f) in [
    (648, 648, 66, 55, 15, "#ff9d00"), (672, 672, 50, 70, 12, "#ffd23f"),
    (614, 612, 56, 40, 13, "#ff6a00"), (692, 606, 44, 80, 10, "#ff9d00")]:
    parts.append(flame(x, y, ln, ang, w, f))

# ---- HIND LEGS (push-off, bottom-right), bent at the hock
# far hind leg, darker
parts.append(leg2(466, 466, 530, 540, 588, 602, 44, 28, 18, "#1c142e"))
parts.append(paw(592, 606, 45, 16, "#1c142e"))
# haunch mass
parts.append(path(
    "M 470,400 C 510,396 540,420 544,456 C 546,486 524,508 492,506 "
    "C 462,504 446,478 450,448 C 454,424 458,408 470,400 Z",
    fill="url(#fur)", stroke="#0d0a18", **{"stroke-width": 1.5}))
# near hind leg
parts.append(leg2(500, 462, 566, 540, 632, 606, 50, 30, 19, "url(#fur)"))
parts.append(paw(636, 610, 45, 18))

# ---- BODY (lean torso, diagonal: deep chest, pinched waist, round hip)
parts.append(path(
    "M 300,252 "
    "C 356,232 428,256 474,318 "      # back line shoulder -> mid-back
    "C 502,354 518,388 522,420 "      # to hip
    "C 525,448 512,468 490,472 "      # hip round
    "C 448,462 404,452 370,432 "      # belly rear (flatter)
    "C 332,404 308,378 298,352 "      # belly front rising
    "C 288,318 288,276 300,252 Z",
    fill="url(#fur)", stroke="#0d0a18", **{"stroke-width": 2}))
# belly shadow (thinner)
parts.append(path(
    "M 306,372 C 340,424 404,452 470,452 C 436,470 388,460 348,432 C 324,414 308,394 306,372 Z",
    fill="url(#furbelly)", opacity="0.9"))
# shoulder / chest mass
parts.append(path(
    "M 302,252 C 336,238 368,256 374,292 C 378,326 360,358 328,362 "
    "C 300,364 280,340 282,308 C 284,280 288,262 302,252 Z",
    fill="url(#fur)", stroke="#0d0a18", **{"stroke-width": 1.5}))
# fur texture strokes on flank (more visible)
for (x1, y1, x2, y2) in [(360, 320, 400, 340), (380, 356, 420, 374), (340, 396, 380, 414), (420, 396, 452, 414), (330, 350, 360, 372), (440, 340, 470, 362)]:
    parts.append(path(f"M {x1},{y1} Q {(x1+x2)//2},{(y1+y2)//2 + 8} {x2},{y2}",
                     stroke="#5a4272", **{"stroke-width": 3, "stroke-opacity": 0.75, "fill": "none",
                                           "stroke-linecap": "round"}))

# ---- FLAME MANE trailing south-east (opposite the leap), layered:
# outer orange tongues (long, narrow) + inner yellow tongues (shorter)
mane_outer = [
    (306, 250, 88, 52, 11, "#ff6a00"), (338, 240, 96, 46, 12, "#ff9d00"),
    (372, 244, 102, 40, 12, "#ff6a00"), (406, 258, 96, 34, 12, "#ff9d00"),
    (438, 280, 88, 28, 11, "#ff6a00"), (466, 308, 80, 22, 11, "#ff9d00"),
    (490, 340, 72, 16, 10, "#ff6a00"), (508, 372, 64, 10, 10, "#ff9d00"),
    (520, 402, 56, 4, 9, "#ff9d00"),
]
mane_inner = [
    (322, 246, 58, 48, 8, "#ffd23f"), (356, 242, 64, 42, 8, "#ffd23f"),
    (390, 250, 66, 36, 8, "#ffd23f"), (422, 268, 60, 30, 8, "#ffd23f"),
    (452, 294, 54, 24, 7, "#ffd23f"), (478, 322, 48, 18, 7, "#ffd23f"),
    (500, 354, 42, 12, 7, "#ffd23f"),
]
for (x, y, ln, ang, w, f) in mane_outer + mane_inner:
    parts.append(flame(x, y, ln, ang, w, f))
# ember rim along the back edge
parts.append(path("M 300,252 C 356,232 428,256 474,318 C 502,354 518,388 522,420",
                 stroke="#ff9d00", **{"stroke-width": 4, "stroke-opacity": 0.85, "fill": "none",
                                       "stroke-linecap": "round", "filter": "url(#glow)"}))

# ---- NECK + HEAD (bigger, top-left) — thick neck so the head is anchored
parts.append(path(
    "M 310,250 C 278,222 244,204 214,196 L 246,276 C 268,284 290,290 310,296 Z",
    fill="url(#fur)", stroke="#0d0a18", **{"stroke-width": 1.5}))
# chest flame ruff at the throat
for (x, y, ln, ang, w, f) in [(276, 300, 52, 60, 10, "#ff6a00"), (292, 316, 46, 70, 9, "#ff9d00")]:
    parts.append(flame(x, y, ln, ang, w, f))
# ears first (behind skull): near ear upright, swept back slightly; far ear smaller
parts.append(path("M 228,152 L 268,102 L 262,164 Z", fill="#1c142e", stroke="#0d0a18", **{"stroke-width": 1.5}))
parts.append(path("M 212,148 L 240,108 L 238,156 Z", fill="#241a33", stroke="#0d0a18", **{"stroke-width": 1.5}))
parts.append(path("M 236,148 L 260,114 L 254,152 Z", fill="#ff6a00", opacity="0.5"))
# skull + long snout pointing NW, jaws open
parts.append(path(
    "M 252,158 "                        # back of skull
    "C 240,140 216,132 192,138 "        # crown to forehead
    "C 176,142 164,150 156,162 "        # stop
    "C 148,172 142,182 140,192 "        # bridge to nose
    "C 139,200 144,206 152,208 "        # nose tip
    "C 168,212 190,210 206,202 "        # upper lip back
    "C 224,196 240,186 250,176 "        # cheek to jaw hinge
    "C 256,168 256,164 252,158 Z",
    fill="url(#fur)", stroke="#0d0a18", **{"stroke-width": 2}))
# lower jaw dropped open
parts.append(path(
    "M 204,206 C 190,216 178,230 172,246 C 169,256 175,262 186,260 "
    "C 200,256 214,242 224,226 C 228,216 216,206 204,206 Z",
    fill="#241a33", stroke="#0d0a18", **{"stroke-width": 1.5}))
# mouth interior glow
parts.append(path("M 154,200 C 170,206 190,206 204,198 C 198,214 184,228 170,230 C 160,224 153,212 154,200 Z",
                 fill="#ff3d00", opacity="0.9", filter="url(#glow)"))
# teeth
for (x, y, s) in [(156, 196, 8), (172, 200, 9), (190, 200, 8)]:
    parts.append(poly([(x, y), (x + s, y + 2), (x + 2, y + s + 5)], fill="#fff6e0"))
for (x, y, s) in [(178, 228, 6), (192, 222, 6)]:
    parts.append(poly([(x, y), (x + s, y - 1), (x + 2, y - s - 4)], fill="#fff6e0"))
# glowing eye (bigger, fierce angle)
parts.append(path("M 192,168 Q 210,156 230,166 Q 212,180 192,168 Z", fill="url(#eye)", filter="url(#glow)"))
parts.append(circle(212, 166, 3.6, fill="#1a0d00"))
parts.append(path("M 188,166 L 232,164", stroke="#0d0a18", **{"stroke-width": 2, "stroke-opacity": 0.8}))
# nose
parts.append(path("M 140,192 C 146,182 156,178 164,182 C 160,192 150,200 142,198 C 138,196 138,194 140,192 Z",
                 fill="#0d0a18"))
# forehead flame tuft trailing back
for (x, y, ln, ang, w, f) in [(228, 148, 36, 25, 9, "#ff9d00"), (244, 156, 30, 35, 8, "#ffd23f")]:
    parts.append(flame(x, y, ln, ang, w, f))
# rim light on snout
parts.append(path("M 252,158 C 240,140 216,132 192,138 C 176,142 164,150 156,162 C 148,172 142,182 140,192",
                 stroke="#ffd23f", **{"stroke-width": 2.5, "stroke-opacity": 0.8, "fill": "none",
                                       "stroke-linecap": "round"}))

# ---- FORELEGS reaching NW (through the frame gap), bent at the elbow
# far foreleg (darker, behind)
parts.append(leg2(296, 326, 240, 292, 200, 258, 38, 26, 16, "#1c142e"))
parts.append(paw(196, 254, -135, 15, "#1c142e"))
# near foreleg (extended, claws out)
parts.append(leg2(318, 348, 252, 306, 180, 258, 44, 28, 17, "url(#fur)"))
parts.append(paw(176, 254, -135, 17))

# ---------------------------------------------------------------- EMBERS on the leap path (concentrated band)
for _ in range(55):
    t = rng.uniform(0, 1)
    # diagonal band from head (190,190) to tail tip (690,660)
    cx = 190 + t * 500 + rng.uniform(-55, 55)
    cy = 190 + t * 470 + rng.uniform(-55, 55)
    r = rng.uniform(1.2, 5.0)
    col = rng.choice(["#ffd23f", "#ff9d00", "#ff6a00", "#ff3d00", "#ffe9a8"])
    o = rng.uniform(0.55, 1.0)
    parts.append(circle(f"{cx:.1f}", f"{cy:.1f}", f"{r:.1f}", fill=col, opacity=f"{o:.2f}",
                        filter="url(#glow)" if r > 3.5 else ""))
for (x, y, r) in [(330, 150, 7), (430, 300, 6), (560, 480, 8), (250, 260, 5), (610, 380, 6)]:
    parts.append(circle(x, y, r, fill="#ffd23f", opacity="0.95", filter="url(#glow)"))
    parts.append(circle(x, y, r * 0.45, fill="#fff6c8"))

# ---------------------------------------------------------------- vignette
parts.append('<rect width="768" height="768" fill="none" stroke="#05070f" stroke-width="46" stroke-opacity="0.55" filter="url(#soft)"/>')

parts.append('</svg>')
svg = "\n".join(parts)

out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out, output_width=W, output_height=H)
data = open(out, "rb").read()
print(f"{out}: {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
buf2 = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=W, output_height=H)
print("deterministic:", hashlib.sha256(buf2).hexdigest() == hashlib.sha256(data).hexdigest())
