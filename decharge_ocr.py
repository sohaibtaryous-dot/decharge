# -*- coding: utf-8 -*-
"""DÉCHARGE — lecture d'un tableau Excel reçu en capture d'écran (mail du client) et reconstitution en Excel.

Le tableau du client : titre (destinataire) puis en-tête bleu « COMPTE | NGP | (n°) | QTE NET | QTE BRUT | T/O/N | TX % » et des lignes
encadrées. Lecture sans IA, cellule par cellule :
  1. l'en-tête bleu repère le tableau (plusieurs tableaux par capture possibles, capture d'écran entière acceptée) ;
  2. les traits de la grille (lignes longues) donnent les lignes et les colonnes ;
  3. chaque cellule est recadrée, agrandie puis lue par Tesseract avec la liste de caractères permis de sa colonne ;
  4. contrôle de forme (COMPTE 17 chiffres, NGP 10 chiffres, quantités numériques) : les cellules douteuses sont signalées.
Les captures nettes (≥ 100 % de zoom) sont lues sans erreur ; une cellule douteuse reste corrigeable à l'écran avant l'export."""

from __future__ import annotations

import io
import os
import re

import numpy as np
from PIL import Image, ImageOps

os.environ.setdefault("OMP_THREAD_LIMIT", "1")                  # Tesseract mono-thread : lectures parallèles sans saturer le processeur

COLUMNS7 = ["COMPTE", "NGP", "ORDRE", "QTE NET", "QTE BRUT", "T/O/N", "TX %"]
COLUMNS6 = ["COMPTE", "NGP", "QTE NET", "QTE BRUT", "T/O/N", "TX %"]
WHITELIST = {"COMPTE": "0123456789", "NGP": "0123456789", "ORDRE": "0123456789", "QTE NET": "0123456789",
             "QTE BRUT": "0123456789NA", "T/O/N": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/", "TX %": "0123456789NA%.,"}


def _runs(mask_1d: np.ndarray) -> list[tuple[int, int]]:
    """Séquences de True consécutifs -> [(début, fin incluse)]."""
    if not mask_1d.any():
        return []
    d = np.diff(np.concatenate(([0], mask_1d.astype(np.int8), [0])))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0] - 1))


def _longest_run(mask: np.ndarray, axis: int) -> np.ndarray:
    """Pour chaque ligne (axis=1) ou colonne (axis=0) : longueur de la plus longue séquence de True."""
    m = mask if axis == 1 else mask.T
    out = np.zeros(m.shape[0], dtype=int)
    for i in range(m.shape[0]):
        r = _runs(m[i])
        if r:
            out[i] = max(b - a + 1 for a, b in r)
    return out


def _cluster(idx: np.ndarray, gap: int = 2) -> list[int]:
    """Indices adjacents (trait épais de quelques pixels) -> une position (milieu)."""
    out, cur = [], []
    for i in idx:
        if cur and i - cur[-1] > gap:
            out.append(int(round(sum(cur) / len(cur))))
            cur = []
        cur.append(int(i))
    if cur:
        out.append(int(round(sum(cur) / len(cur))))
    return out


def find_headers(arr: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Bandes d'en-tête bleues (≈ #00619A) : [(x0, y0, x1, y1)]."""
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    mask = (r < 45) & (g > 70) & (g < 125) & (b > 125) & (b < 185)
    rowc = mask.sum(1)
    thr = max(120, int(arr.shape[1] * 0.12))
    bands, cur = [], []
    for y in np.where(rowc >= thr)[0]:
        if cur and y - cur[-1] > 2:
            bands.append((cur[0], cur[-1]))
            cur = []
        cur.append(int(y))
    if cur:
        bands.append((cur[0], cur[-1]))
    out = []
    for y0, y1 in bands:
        if y1 - y0 < 8:
            continue
        cols = np.where(mask[y0:y1 + 1].sum(0) >= max(3, (y1 - y0) // 3))[0]
        if len(cols) < 120:
            continue
        out.append((int(cols.min()), int(y0), int(cols.max()), int(y1)))
    return out


def _grid(arr: np.ndarray, hdr: tuple[int, int, int, int]):
    """(lignes horizontales y[], lignes verticales x[], image claire ?) sous un en-tête."""
    x0, y0, x1, y1 = hdr
    gray = np.asarray(Image.fromarray(arr).convert("L")).astype(int)
    body = gray[y1 + 1: min(gray.shape[0], y1 + 1 + 900), max(0, x0 - 4): x1 + 5]
    dark = float(np.median(body)) < 128
    mask = (body > 175) if dark else (body < 95)
    w = x1 - x0
    hl = _longest_run(mask, 1)
    ys = _cluster(np.where(hl >= 0.8 * w)[0])
    if len(ys) < 2:
        return [], [], dark
    # on s'arrête quand l'écart entre deux traits dépasse nettement la hauteur de ligne du tableau
    gaps = np.diff(ys)
    g0 = int(np.median(gaps[: min(4, len(gaps))])) if len(gaps) else 0
    keep = [ys[0]]
    for yv in ys[1:]:
        if yv - keep[-1] > max(g0 * 1.9, 40):
            break
        keep.append(yv)
    ys = keep
    if len(ys) < 2:
        return [], [], dark
    sub = mask[ys[0]: ys[-1] + 1]
    vl = _longest_run(sub, 0)
    xs = _cluster(np.where(vl >= 0.85 * (ys[-1] - ys[0]))[0])
    ys = [y + y1 + 1 for y in ys]
    xs = [x + max(0, x0 - 4) for x in xs]
    # dernière ligne parfois sans cadre complet (traits partiels) : on l'ajoute si du texte y figure
    rh = int(np.median(np.diff(ys))) if len(ys) > 1 else 0
    for _ in range(3):
        ya, yb = ys[-1] + 3, ys[-1] + rh - 2
        if rh <= 0 or yb >= gray.shape[0] or xs[-1] <= xs[0]:
            break
        reg = gray[ya:yb, xs[0] + 3: xs[-1] - 2]
        ink = float((reg > 150).mean() if dark else (reg < 110).mean())
        if ink > 0.02:
            ys.append(ys[-1] + rh)
        else:
            break
    return ys, xs, dark


def _ocr(img: Image.Image, whitelist: str = "", psm: int = 7, lang: str = "eng") -> str:
    import pytesseract
    cfg = f"--psm {psm}"
    if whitelist:
        cfg += f" -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(img, lang=lang, config=cfg).strip()


def _prep(crop: Image.Image, dark: bool, scale: int = 4) -> Image.Image:
    g = crop.convert("L")
    if dark:
        g = ImageOps.invert(g)
    g = ImageOps.autocontrast(g, cutoff=0)
    g = g.resize((g.width * scale, g.height * scale), Image.LANCZOS)
    return ImageOps.expand(g, border=30, fill=255)


def _title(img: Image.Image, hdr) -> str:
    x0, y0, x1, y1 = hdr
    h = y1 - y0 + 1
    top = max(0, y0 - int(h * 1.7))
    crop = img.crop((x0, top, min(img.width, x0 + int((x1 - x0) * 0.8)), max(top + 4, y0 - 1)))
    arr = np.asarray(crop.convert("L"))
    if arr.size == 0:
        return ""
    # fond du surlignage clair (texte noir) ou foncé (texte blanc) : on teste les 2 lectures
    best = ""
    for inv in (False, True):
        g = ImageOps.invert(crop.convert("L")) if inv else crop.convert("L")
        g = ImageOps.autocontrast(g, cutoff=1).resize((g.width * 4, g.height * 4), Image.LANCZOS)
        txt = _ocr(ImageOps.expand(g, border=16, fill=255), "", 7)
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(re.findall(r"[A-Za-z]", txt)) > len(re.findall(r"[A-Za-z]", best)):
            best = txt
    return best


def _ink_box(gray: np.ndarray, dark: bool):
    """Rectangle du texte (pixels clairs sur fond sombre, sombres sur fond clair) dans l'intérieur d'une cellule."""
    m = (gray > 140) if dark else (gray < 120)
    ys, xs = np.where(m)
    if len(ys) < 6:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _vote(img: Image.Image, box: tuple[int, int, int, int], dark: bool, col: str) -> str:
    """Le texte est isolé (recadrage sur l'encre, sans les traits de la grille), mis à une hauteur constante (≈ 64 px) puis lu plusieurs fois
    (mot isolé, hauteurs 40-90 px) : la valeur majoritaire l'emporte."""
    from collections import Counter
    x0, x1, y0, y1 = box
    inner = img.crop((x0 + 4, y0 + 3, x1 - 3, y1 - 2))      # marge côté traits verticaux : évite que le trait colle au chiffre (« 1 » lu « 4 »)
    if inner.width < 4 or inner.height < 4:
        return ""
    gray = np.asarray(inner.convert("L"))
    bb = _ink_box(gray, dark)
    if bb is None:
        return ""
    bx0, by0, bx1, by1 = bb
    pad = 3
    crop = inner.crop((max(0, bx0 - pad), max(0, by0 - pad), min(inner.width, bx1 + pad), min(inner.height, by1 + pad)))
    th = max(1, by1 - by0)
    wl = WHITELIST.get(col, "")
    reads: list[str] = []
    for k, (target, psm) in enumerate(((48, 7), (40, 7), (56, 7), (64, 7), (48, 8))):   # essais : 48 px / mode « ligne » = le plus fiable
        sc = target / th
        g = crop.convert("L")
        if dark:
            g = ImageOps.invert(g)
        g = ImageOps.autocontrast(g, cutoff=0)
        g = g.resize((max(1, round(g.width * sc)), max(1, round(g.height * sc))), Image.LANCZOS)
        reads.append(_clean(col, _ocr(ImageOps.expand(g, border=30, fill=255), wl, psm)))
        if k == 2 and len(set(reads)) == 1:
            break                                                           # trois lectures identiques : inutile d'insister
    cnt = Counter(r for r in reads if r)
    if not cnt:
        return ""
    top = max(cnt.values())
    return next(r for r in reads if cnt.get(r) == top)


# --------------------------------------------------------------------------- reconnaissance par gabarits (police de la capture)
def _cell_glyphs(img: Image.Image, box, dark: bool):
    """Caractères d'une cellule : liste de tableaux (0 = fond, 1 = encre), séparés par les colonnes vides."""
    x0, x1, y0, y1 = box
    inner = img.crop((x0 + 4, y0 + 3, x1 - 3, y1 - 2))
    if inner.width < 4 or inner.height < 4:
        return []
    g = np.asarray(inner.convert("L")).astype(float)
    bg = float(np.median(g))
    ext = g.max() if dark else g.min()
    if abs(ext - bg) < 40:
        return []
    a = np.clip((g - bg) / (ext - bg), 0, 1)
    ink = a > 0.5
    cols = ink.any(0)
    out = []
    for c0, c1 in _runs(cols):
        sub = a[:, c0:c1 + 1]
        rows = np.where((sub > 0.5).any(1))[0]
        if len(rows) == 0:
            continue
        out.append(sub[rows.min(): rows.max() + 1])
    return out


def _glyph_dist(a: np.ndarray, b: np.ndarray) -> float:
    """Distance moyenne entre deux caractères (alignés en haut à gauche, décalages de ±1 px tolérés)."""
    H, W = max(a.shape[0], b.shape[0]) + 2, max(a.shape[1], b.shape[1]) + 2
    best = 9.0
    for dy in (0, 1):
        for dx in (0, 1, 2):
            pa = np.zeros((H, W)); pa[1 + dy: 1 + dy + a.shape[0], dx: dx + a.shape[1]] = a[: H - 1 - dy, : W - dx]
            for ey in (0, 1):
                for ex in (0, 1, 2):
                    pb = np.zeros((H, W)); pb[1 + ey: 1 + ey + b.shape[0], ex: ex + b.shape[1]] = b[: H - 1 - ey, : W - ex]
                    best = min(best, float(np.abs(pa - pb).mean()))
    return best


def _pad(g: np.ndarray, H: int, W: int) -> np.ndarray:
    out = np.zeros((H, W))
    h, w = min(g.shape[0], H), min(g.shape[1], W - 3)
    out[:h, 1:1 + w] = g[:h, :w]
    return out


def _classify(glyphs, templates: dict) -> tuple[str, float]:
    """Chiffres d'une cellule d'après les gabarits (tous les gabarits comparés d'un coup, décalage horizontal de ±1 px toléré)."""
    keys, mats = [], []
    H = max([g.shape[0] for ts in templates.values() for g in ts] + [g.shape[0] for g in glyphs]) + 1
    W = max([g.shape[1] for ts in templates.values() for g in ts] + [g.shape[1] for g in glyphs]) + 3
    for ch, ts in templates.items():
        for t in ts:
            keys.append(ch)
            mats.append(_pad(t, H, W))
    T = np.stack(mats)
    txt, worst = "", 0.0
    for gl in glyphs:
        g = _pad(gl, H, W)
        best = np.full(len(keys), 9.0)
        for dx in (-1, 0, 1):
            gs = np.roll(g, dx, axis=1)
            best = np.minimum(best, np.abs(T - gs).mean(axis=(1, 2)))
        k = int(best.argmin())
        txt += keys[k]
        worst = max(worst, float(best[k]))
    return txt, worst


def _clean(col: str, raw: str) -> str:
    s = raw.replace("\n", " ").strip()
    if col in ("COMPTE", "NGP", "ORDRE"):
        return re.sub(r"\D", "", s)
    if col in ("QTE BRUT", "T/O/N", "TX %"):
        s = s.upper().replace(" ", "")
        if re.fullmatch(r"N+A*|NA|MA|NA\.|N4|NÀ", s) or s in ("NA", "N", "A"):
            return "NA"
        return s
    return re.sub(r"[^\d.,]", "", s)


def read_table(img: Image.Image, hdr, arr: np.ndarray) -> dict | None:
    ys, xs, dark = _grid(arr, hdr)
    if len(ys) < 2 or len(xs) < 5:
        return None
    ncol = len(xs) - 1
    names = COLUMNS7 if ncol == 7 else (COLUMNS6 if ncol == 6 else [f"COL{i + 1}" for i in range(ncol)])
    from concurrent.futures import ThreadPoolExecutor
    cells = [(i, j) for i in range(len(ys) - 1) for j in range(ncol)]
    boxes = {(i, j): (xs[j], xs[j + 1], ys[i], ys[i + 1]) for i, j in cells}
    with ThreadPoolExecutor(max_workers=4) as ex:                                 # Tesseract = sous-processus : lectures en parallèle
        ocr = dict(zip(cells, ex.map(lambda ij: _vote(img, boxes[ij], dark, names[ij[1]]), cells)))
    # gabarits des chiffres : cellules COMPTE / NGP dont le nombre de caractères = nombre de chiffres lus
    templates: dict[str, list] = {}
    for (i, j), txt in ocr.items():
        if names[j] in ("COMPTE", "NGP") and re.fullmatch(r"\d{10,17}", txt or ""):
            gl = _cell_glyphs(img, boxes[(i, j)], dark)
            if len(gl) == len(txt):
                for ch, g in zip(txt, gl):
                    templates.setdefault(ch, []).append(g)
    tmpl_ok = len(templates) >= 8
    fixed = 0
    if tmpl_ok:
        for (i, j), txt in list(ocr.items()):
            if names[j] in ("COMPTE", "NGP", "ORDRE", "QTE NET") and (re.fullmatch(r"\d+", txt or "") or txt == ""):
                gl = _cell_glyphs(img, boxes[(i, j)], dark)
                if not gl:
                    continue
                t2, worst = _classify(gl, templates)
                if worst < 0.2 and t2 != txt:
                    ocr[(i, j)] = t2
                    fixed += 1
    rows = []
    for i in range(len(ys) - 1):
        row = {names[j]: ocr[(i, j)] for j in range(ncol)}
        if any(v for v in row.values()):
            rows.append(row)
    return {"title": _title(img, hdr), "columns": names, "rows": rows}


def read_image(data: bytes) -> list[dict]:
    """Tous les tableaux d'une capture : [{"title", "columns", "rows"}]."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    scale = 1
    if img.width < 900:                                                    # petite capture : agrandie pour une grille et des chiffres plus nets
        scale = 2
        img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    arr = np.asarray(img)
    out = []
    for hdr in find_headers(arr):
        t = read_table(img, hdr, arr)
        if t and t["rows"]:
            out.append(t)
    return out


def validate(table: dict) -> list[str]:
    """Cellules douteuses : [« ligne 3 · COMPTE : 16 chiffres au lieu de 17 »]."""
    issues = []
    for i, r in enumerate(table["rows"], start=1):
        if r.get("COMPTE") is not None and not re.fullmatch(r"\d{17}", str(r.get("COMPTE", ""))):
            issues.append(f"ligne {i} · COMPTE « {r.get('COMPTE', '')} » : 17 chiffres attendus")
        if r.get("NGP") is not None and not re.fullmatch(r"\d{10}", str(r.get("NGP", ""))):
            issues.append(f"ligne {i} · NGP « {r.get('NGP', '')} » : 10 chiffres attendus")
        q = str(r.get("QTE NET", ""))
        if not re.fullmatch(r"\d+(?:[.,]\d+)?", q):
            issues.append(f"ligne {i} · QTE NET « {q} » : nombre attendu")
    return issues
