# -*- coding: utf-8 -*-
"""Designs à essayer dans le site (menu « Thème ») et animations à ajouter (menu « Animations »).

- 24 designs : 1-8 « classiques » (couleurs, polices, décor animé en CSS dans l'en-tête), 9-24 « waw » (scène animée en <canvas>
  ou WebGL dans l'en-tête et en fond de la page de connexion). Chaque design a ses formes (cartes, boutons, chiffres de l'en-tête).
- 22 animations (A-V), cumulables, pour n'importe quel design.
Rien ne change dans les calculs : seulement l'apparence. Le choix vaut pour la session de l'utilisateur.
"""

from __future__ import annotations

import html
import json

import streamlit as st

# polices Google : seules celles du design choisi sont chargées
_FONTS = {"Outfit": "Outfit:wght@400;500;600;700;800", "IBM Plex Sans": "IBM+Plex+Sans:wght@400;500;600;700", "IBM Plex Mono": "IBM+Plex+Mono:wght@400;500;600",
          "Big Shoulders Display": "Big+Shoulders+Display:wght@600;800", "Chakra Petch": "Chakra+Petch:wght@500;600;700", "Special Elite": "Special+Elite",
          "Bricolage Grotesque": "Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800", "Marcellus": "Marcellus", "Oswald": "Oswald:wght@500;600;700",
          "Audiowide": "Audiowide", "Syne": "Syne:wght@600;700;800", "Sora": "Sora:wght@400;600;700;800", "JetBrains Mono": "JetBrains+Mono:wght@400;500;700",
          "Unbounded": "Unbounded:wght@500;700;800"}
_EXTRA_FONTS = {4: ("IBM Plex Mono",), 7: ("IBM Plex Mono",), 18: ("Big Shoulders Display",)}


def font_url(*families: str) -> str:
    fams = dict.fromkeys(f for f in (*families, "Outfit", "IBM Plex Mono") if f in _FONTS)
    return "https://fonts.googleapis.com/css2?" + "&".join("family=" + _FONTS[f] for f in fams) + "&display=swap"


FONT_URL = font_url(*_FONTS)

# id, nom, clair ?, palette (fond, surface, surface 2, barre latérale, texte, texte 2, texte 3, accent, accent foncé, accent 2, accent clair),
# polices (titres, texte), décor d'en-tête, scène <canvas> (en-tête + fond de connexion)
SPECS = [
    (1, "Port de Tanger", False, ("#071226", "#0C1C36", "#12284A", "#0A1A33", "#E6EEF8", "#9FB7D6", "#7690B4", "#0EA5E9", "#0284C7", "#38BDF8", "#7DD3FC"), ("Outfit", "Outfit"), "port", None),
    (2, "Aurore", False, ("#050B14", "#0B1A22", "#10242C", "#07141A", "#EAF6F3", "#A7C7C0", "#7FA39B", "#14B8A6", "#0D9488", "#5EEAD4", "#99F6E4"), ("Outfit", "Outfit"), "aurora", None),
    (3, "Blanc Corporate Pro", True, ("#F6F8FB", "#FFFFFF", "#F1F5F9", "#FFFFFF", "#0F172A", "#475569", "#64748B", "#1D4ED8", "#1E40AF", "#2563EB", "#1D4ED8"), ("IBM Plex Sans", "IBM Plex Sans"), "lines", None),
    (4, "Conteneurs", False, ("#17191C", "#1F2226", "#2B2F35", "#101214", "#F1F3F5", "#ADB5BD", "#868E96", "#E8590C", "#C2410C", "#FD7E14", "#FFA94D"), ("Big Shoulders Display", "IBM Plex Sans"), "boxes", None),
    (5, "Routes ALSTOM", False, ("#060D1A", "#0B1628", "#13233C", "#08111F", "#E2E8F0", "#A0AEC0", "#7C8BA3", "#F59E0B", "#D97706", "#FBBF24", "#FCD34D"), ("Outfit", "Outfit"), "routes", None),
    (6, "Néon Scanner", False, ("#04050B", "#070914", "#0D1022", "#070914", "#E0F2FE", "#93C5D8", "#6B8FA6", "#22D3EE", "#0891B2", "#E879F9", "#67E8F9"), ("Chakra Petch", "Chakra Petch"), "neon", None),
    (7, "Tampon Douane", True, ("#E6ECE6", "#F6F8F5", "#E1E9E2", "#EEF2EC", "#1C2A22", "#4B5E52", "#6B7F72", "#1F3A2C", "#14281E", "#7A1F3D", "#7A1F3D"), ("Special Elite", "IBM Plex Sans"), "stamp", None),
    (8, "Graphite", True, ("#FAFAF9", "#FFFFFF", "#F0EFED", "#F5F5F4", "#0C0A09", "#44403C", "#78716C", "#2F4FD8", "#1E3A8A", "#2F4FD8", "#2F4FD8"), ("Bricolage Grotesque", "IBM Plex Sans"), None, None),
    (9, "Phare du Cap Spartel", False, ("#070A1C", "#0E1430", "#151D42", "#0A0F26", "#EEF0FA", "#A9B0D0", "#7F88AE", "#F0A35E", "#D9823A", "#FDE68A", "#FCD9A8"), ("Bricolage Grotesque", "IBM Plex Sans"), None, "phare"),
    (10, "Usine à ventilation", False, ("#0A101C", "#101A2B", "#17243A", "#0C1422", "#E5ECF6", "#9DB0C8", "#7489A6", "#2563EB", "#1D4ED8", "#22C55E", "#86EFAC"), ("Bricolage Grotesque", "IBM Plex Sans"), None, "usine"),
    (11, "Train à grande vitesse", False, ("#0D0B1E", "#16132E", "#1F1A3D", "#100E24", "#F3EEF8", "#B9AFCF", "#8E84A8", "#F97316", "#EA580C", "#FDBA74", "#FED7AA"), ("Outfit", "Outfit"), None, "train"),
    (12, "Globe du détroit", False, ("#030712", "#0A1222", "#111C31", "#060C18", "#E2E8F0", "#9AA8BF", "#73839E", "#FBBF24", "#D97706", "#7DD3FC", "#FDE68A"), ("Outfit", "Outfit"), None, "globe"),
    (13, "Particules TIMAR", False, ("#040710", "#0B1020", "#121A30", "#070B18", "#EEF2FF", "#A5B0D6", "#7C86AE", "#6366F1", "#4F46E5", "#F472B6", "#C4B5FD"), ("Bricolage Grotesque", "IBM Plex Sans"), None, "particules"),
    (14, "Fluide lumineux", False, ("#04070F", "#0A1426", "#0F1D33", "#060D1A", "#ECFEFF", "#A5C9D3", "#7AA0AD", "#06B6D4", "#0891B2", "#FBBF24", "#A5F3FC"), ("Outfit", "Outfit"), None, "fluide"),
    (15, "Hologramme 3D", False, ("#02060E", "#071526", "#0B1E35", "#04101E", "#E0F7FF", "#9CCFE0", "#6FA3B8", "#22D3EE", "#0891B2", "#F0ABFC", "#A5F3FC"), ("Outfit", "Outfit"), "holo", None),
    (16, "Port Tanger Med", False, ("#040814", "#0B1530", "#12203F", "#071026", "#E6EEF8", "#A1B4D0", "#7890B0", "#EAB308", "#CA8A04", "#F43F5E", "#FDE047"), ("Outfit", "Outfit"), None, "port3d"),
    (17, "Tanger la nuit", False, ("#0A0B1E", "#121433", "#1A1D45", "#0C0E27", "#F2F0FA", "#B5B2D3", "#8784A8", "#F2C14E", "#D9A43A", "#2DD4BF", "#FDE7A9"), ("Marcellus", "IBM Plex Sans"), None, "tanger"),
    (18, "Terminal 3D", False, ("#0B0D10", "#15181D", "#1E232A", "#0E1013", "#F3F4F6", "#A8AFB9", "#7F8792", "#FF7A1A", "#E35F00", "#2BB0ED", "#FFB37A"), ("Oswald", "IBM Plex Sans"), None, "terminal"),
    (19, "Survol néon", False, ("#0D0221", "#170736", "#220B4A", "#12042B", "#FCE7FF", "#C9A9E0", "#9A7BB5", "#FF2E97", "#D6177A", "#00F0FF", "#FF9DE2"), ("Audiowide", "Outfit"), None, "synth"),
    (20, "Galaxie", False, ("#03020A", "#0B0920", "#13102E", "#070516", "#EDE9FE", "#B4ABD8", "#857CAA", "#A78BFA", "#7C3AED", "#F0ABFC", "#DDD6FE"), ("Syne", "Outfit"), None, "galaxie"),
    (21, "Avions de papier", True, ("#EEF5FB", "#FFFFFF", "#E7F0F8", "#F7FBFE", "#0E2238", "#4A6178", "#6F8499", "#0F6FDE", "#0A55AD", "#FF8A3D", "#0F6FDE"), ("Sora", "IBM Plex Sans"), None, "avions"),
    (22, "Code douane", False, ("#020604", "#071009", "#0B1A0F", "#040A06", "#D1FAE5", "#86C9A4", "#5E9C7A", "#22C55E", "#15803D", "#FBBF24", "#86EFAC"), ("JetBrains Mono", "IBM Plex Sans"), None, "codes"),
    (23, "Chrome liquide", False, ("#0A0A0C", "#141418", "#1C1C22", "#0E0E11", "#F4F4F5", "#B4B4BD", "#8A8A95", "#E2E8F0", "#94A3B8", "#F0ABFC", "#FFFFFF"), ("Unbounded", "Outfit"), None, "chrome"),
    (24, "Lignes de flux", False, ("#061018", "#0C1A24", "#12242F", "#08141C", "#E6F4F1", "#9DBDB6", "#6F938B", "#2DD4BF", "#0D9488", "#F5B841", "#99F6E4"), ("Bricolage Grotesque", "IBM Plex Sans"), None, "flux"),
]
HEAVY = {"particules", "fluide", "port3d", "galaxie", "chrome", "flux"}
NAMES = {i: f"{i} · {n}" for i, n, *_ in SPECS}
BY_NAME = {f"{i} · {n}": (i, n, light, pal, fonts, art, scene) for i, n, light, pal, fonts, art, scene in SPECS}

ANIMS = {
    "A": "A · Camion sur la barre de chargement", "B": "B · Tampon « PRÊT ✓ » au succès", "C": "C · Chiffres de l'en-tête qui défilent",
    "D": "D · Scanner sur les fichiers déposés", "E": "E · Zone de dépôt vivante", "F": "F · Coche + confettis au téléchargement",
    "G": "G · Bateau dans l'en-tête", "H": "H · Carte des routes dans l'en-tête", "I": "I · Passage doux entre modules",
    "J": "J · Cartes en relief (3D)", "K": "K · Intro à l'ouverture", "L": "L · Projecteur sous la souris",
    "M": "M · Boutons magnétiques", "N": "N · Couleurs selon l'heure de Tanger",
    "O": "O · Comète qui suit la souris", "P": "P · Onde au clic", "Q": "Q · Titre qui se décode",
    "R": "R · Bordure néon qui tourne autour des cartes", "S": "S · Étoiles filantes en fond", "T": "T · Conteneurs qui tombent au succès",
    "U": "U · Lumière qui suit la souris sur les cartes", "V": "V · Fond qui respire",
}
ENGINE_ANIMS = {"C", "F", "J", "K", "L", "M", "N", "O", "P", "Q", "S", "T", "U", "V"}

# animations choisies automatiquement pour chaque design (déclenchées dès qu'on choisit le thème, modifiables ensuite)
DEFAULT_ANIMS: dict[int, list[str]] = {
    1: ["J", "M"], 2: ["U"], 3: ["I"], 4: ["A", "T"], 5: ["G"], 6: ["D", "R"], 7: ["B"], 8: ["I"],
    9: ["L", "K"], 10: ["J", "E"], 11: ["O", "M"], 12: ["N", "U"], 13: ["O"], 14: ["V"], 15: ["J", "R"], 16: ["R", "T"],
    17: ["S", "K"], 18: ["J", "M"], 19: ["Q", "R"], 20: ["O", "S"], 21: ["P", "I"], 22: ["Q"], 23: ["U"], 24: ["V", "U"],
}
# idem pour « Bleu Port », « Bleu Port (classique) » et les anciens thèmes (pas de design « N · Nom » ci-dessus)
LEGACY_DEFAULT_ANIMS: dict[str, list[str]] = {
    "Émeraude": ["I"], "Violet Aurore": ["U"], "Or & Noir": ["R"], "Rouge Cargo": ["A"],
    "Vice Sunset (style GTA)": ["Q"], "Lunea Café (luxe)": ["U"], "Aurora Glass": ["V"], "Blanc Corporate": ["I"],
}


def default_anims(theme: str) -> list[str]:
    """Animations à activer automatiquement quand on choisit ce thème (sans rien cocher soi-même)."""
    s = spec(theme)
    return list(DEFAULT_ANIMS.get(s[0], [])) if s else list(LEGACY_DEFAULT_ANIMS.get(theme, []))


def _rgb(hexv: str) -> str:
    h = hexv.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"


def _darker(hexv: str, f: float = .62) -> str:
    h = hexv.lstrip("#")
    return "".join(f"{max(0, min(255, round(int(h[i:i + 2], 16) * f))):02X}" for i in (0, 2, 4))


def _on_accent(hexv: str) -> str:
    """Texte des boutons principaux : blanc si assez lisible sur l'accent (contraste ≥ 3), sinon presque noir."""
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
    return "#FFFFFF" if 1.05 / (lum(hexv) + .05) >= 3 else "#0B0F19"


def theme_entry(light: bool, pal: tuple) -> dict:
    """Correspondance couleurs « Bleu Port » -> couleurs du design (même mécanisme que les thèmes existants : ui.skin)."""
    bg, sf, sf2, side, ink, ink2, ink3, ac, acd, ac2, acl = (p.lstrip("#").upper() for p in pal)
    hexm = {"3B82F6": ac, "2563EB": acd, "1D4ED8": acd, "38BDF8": ac2, "93C5FD": acl, "60A5FA": acl, "1E3A8A": _darker(acd), "BFDBFE": acl,
            "070D1C": bg, "0A1226": bg, "08101F": bg, "0A1020": bg, "0C1426": side, "0F1B33": sf2, "0C1528": sf, "0B1A2C": sf,
            "101A2E": sf, "15213A": sf2, "E6EBF5": ink, "A3AEC4": ink2, "6B7895": ink3}
    rgbm = {"59,130,246": _rgb(ac), "37,99,235": _rgb(acd), "14,165,233": _rgb(ac2), "30,64,175": _rgb(acd), "56,189,248": _rgb(ac2), "96,165,250": _rgb(acl)}
    e = {"hex": hexm, "rgb": rgbm, "design": True}
    if light:
        e["css"] = "LIGHT"
        e["raw"] = {"color:#fff;font-variant": f"color:#{ink};font-variant"}
    return e


def register(themes: dict) -> dict:
    """Thèmes du menu : « Bleu Port », puis les 16 designs, puis les anciens thèmes."""
    out = {"Bleu Port": themes.get("Bleu Port")}
    for name, (_i, _n, light, pal, *_r) in BY_NAME.items():
        out[name] = theme_entry(light, pal)
    for k, v in themes.items():
        out.setdefault(k, v)
    return out


def spec(theme: str):
    return BY_NAME.get(theme)


def is_light(theme: str) -> bool:
    s = spec(theme)
    return bool(s and s[2])


def anims() -> list[str]:
    return [a for a in (st.session_state.get("anims") or []) if a in ANIMS]


# =============================================================================
# CSS : polices, touches propres à chaque design, décors d'en-tête, animations CSS (A B D E I N R U V)
# =============================================================================

ART_CSS = """
.ph.has-art { position: relative; overflow: hidden; min-height: 196px; padding: 24px 26px 20px !important; border: 1px solid var(--brd) !important;
  border-radius: 18px; background: var(--surface); align-items: flex-end; }
.ph.has-art > .ph-l, .ph.has-art > .ph-stats { position: relative; z-index: 2; }
.ph.has-art { flex-direction: column; align-items: flex-start !important; justify-content: flex-end; gap: 12px; }
.ph.has-art > .ph-l { max-width: 58%; }
@media (max-width: 760px) { .ph.has-art > .ph-l { max-width: 100%; } }
.ph-art { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.ph-art.right { left: 46%; }
.ph-veil { position: absolute; inset: 0; z-index: 1; pointer-events: none; background: linear-gradient(90deg, var(--bg) 0%, rgba(0,0,0,0) 62%); opacity: .92; }
.ph.has-art .ph-stat { backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }
.scene-slot { position: absolute; inset: 0; }
.scene-slot > canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.scene-bg { position: fixed !important; inset: 0; z-index: -1; pointer-events: none; }
.block-container { position: relative; z-index: 1; }
/* 1 port */
.tz-sky { position: absolute; inset: 0; background: linear-gradient(180deg, #0B2447 0%, #0E3A6B 62%, #0A2C52 62.5%, #072039 100%); }
.tz-stars { position: absolute; inset: 0 0 45% 0; background-image: radial-gradient(1px 1px at 20% 30%, #fff8, transparent), radial-gradient(1px 1px at 60% 20%, #fff6, transparent), radial-gradient(1.5px 1.5px at 80% 45%, #fff9, transparent), radial-gradient(1px 1px at 40% 60%, #fff5, transparent); }
.tz-cranes { position: absolute; right: 24px; bottom: 37%; width: 220px; height: 66px; }
.tz-sea { position: absolute; left: 0; right: 0; bottom: 0; height: 38%; background: repeating-linear-gradient(90deg, rgba(125,211,252,0) 0 18px, rgba(125,211,252,.2) 18px 30px, rgba(125,211,252,0) 30px 60px);
  background-size: 120px 3px; background-repeat: repeat-x; background-position: 0 30%; animation: tz-sea 3s linear infinite; }
@keyframes tz-sea { to { background-position-x: 120px; } }
.tz-ship { position: absolute; bottom: 24%; left: -180px; width: 160px; animation: tz-ship 18s linear infinite; }
@keyframes tz-ship { to { transform: translateX(1500px); } }
/* 2 aurore */
.tz-aur { position: absolute; inset: -30%; filter: blur(40px); opacity: .9; background: radial-gradient(30% 35% at 30% 30%, #0D9488, transparent 70%), radial-gradient(30% 30% at 70% 60%, #0369A1, transparent 70%), radial-gradient(25% 30% at 55% 20%, #22C55E66, transparent 70%); animation: tz-aur 14s ease-in-out infinite alternate; }
@keyframes tz-aur { 50% { transform: translate(6%, -4%) rotate(8deg) scale(1.06); } 100% { transform: translate(-5%, 5%) rotate(-6deg); } }
/* 3 blanc */
.tz-lines { position: absolute; right: 26px; top: 18px; width: 300px; height: 130px; }
.tz-lines path { stroke-dasharray: 6 7; animation: tz-dash 1.2s linear infinite; }
@keyframes tz-dash { to { stroke-dashoffset: -26; } }
/* 4 conteneurs */
.tz-stack { position: absolute; right: 18px; bottom: 6px; width: 300px; height: 150px; }
.tz-ct { position: absolute; width: 96px; height: 40px; border-radius: 2px; font: 700 9px "Big Shoulders Display", sans-serif; letter-spacing: .08em; color: rgba(255,255,255,.88);
  display: grid; place-items: center; background-image: repeating-linear-gradient(90deg, rgba(0,0,0,.22) 0 2px, transparent 2px 7px); animation: tz-drop 7s cubic-bezier(.3,1.4,.5,1) infinite both; }
@keyframes tz-drop { 0% { transform: translateY(-180px); opacity: 0; } 12% { transform: none; opacity: 1; } 86% { transform: none; opacity: 1; } 100% { transform: none; opacity: 0; } }
/* 5 routes */
.tz-dots { position: absolute; inset: 0; background-image: radial-gradient(rgba(148,163,184,.22) 1px, transparent 1.3px); background-size: 9px 9px; }
.tz-routes { position: absolute; right: 18px; top: 14px; width: 420px; height: 160px; }
.tz-route { fill: none; stroke: #F59E0B; stroke-width: 1.6; stroke-dasharray: 4 5; animation: tz-flow 1.4s linear infinite; }
@keyframes tz-flow { to { stroke-dashoffset: -18; } }
.tz-city { fill: #FDE68A; }
.tz-pulse { fill: none; stroke: #FBBF24; stroke-width: 1.4; transform-box: fill-box; transform-origin: center; animation: tz-pulse 2.2s ease-out infinite; }
@keyframes tz-pulse { from { transform: scale(.4); opacity: 1; } to { transform: scale(3.2); opacity: 0; } }
.tz-lbl { fill: #CBD5E1; font: 600 8px "IBM Plex Mono", monospace; letter-spacing: .06em; }
/* 6 néon */
.tz-grid { position: absolute; left: -10%; right: -10%; bottom: -40px; height: 130px; transform: perspective(240px) rotateX(62deg); transform-origin: bottom;
  background-image: linear-gradient(rgba(232,121,249,.55) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.45) 1px, transparent 1px); background-size: 34px 22px; animation: tz-grid 1.6s linear infinite; }
@keyframes tz-grid { to { background-position: 0 22px; } }
.tz-doc { position: absolute; right: 48px; top: 20px; width: 96px; height: 124px; border: 1px solid rgba(34,211,238,.6); border-radius: 4px; background: rgba(34,211,238,.05);
  background-image: repeating-linear-gradient(180deg, transparent 0 12px, rgba(34,211,238,.35) 12px 13px); overflow: hidden; }
.tz-doc::after { content: ""; position: absolute; left: -6px; right: -6px; height: 3px; background: #22D3EE; box-shadow: 0 0 14px 4px rgba(34,211,238,.7); animation: tz-scan 2s ease-in-out infinite alternate; }
@keyframes tz-scan { from { top: 0; } to { top: calc(100% - 3px); } }
/* 7 tampon */
.tz-form { position: absolute; inset: 0; background-image: linear-gradient(rgba(31,58,44,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(31,58,44,.12) 1px, transparent 1px); background-size: 100% 22px, 120px 100%; }
.tz-stamp { position: absolute; right: 54px; top: 34px; width: 150px; height: 96px; border: 3px solid #8E2449; border-radius: 10px; color: #8E2449; display: grid; place-items: center; text-align: center;
  font: 700 13px/1.2 "IBM Plex Mono", monospace; letter-spacing: .12em; transform: rotate(-9deg); opacity: .85; mix-blend-mode: multiply; animation: tz-hit 4.5s cubic-bezier(.2,1.6,.4,1) infinite; }
@keyframes tz-hit { 0%, 8% { transform: rotate(-9deg) scale(2.2); opacity: 0; } 18% { transform: rotate(-9deg) scale(1); opacity: .85; } 90% { opacity: .85; } 100% { transform: rotate(-9deg) scale(1); opacity: 0; } }
/* 15 hologramme */
.holo { position: absolute; top: 0; bottom: 0; right: 0; left: 60%; perspective: 900px; display: grid; place-items: center; }
.hgrp { position: relative; width: 92%; height: 82%; transform-style: preserve-3d; transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)); }
.hc { position: absolute; border-radius: 12px; padding: 10px 12px; color: #E0F7FF; display: grid; gap: 3px; align-content: start; overflow: hidden;
  background: linear-gradient(160deg, rgba(34,211,238,.16), rgba(30,58,138,.30)); border: 1px solid rgba(165,243,252,.45); box-shadow: 0 0 30px -8px rgba(34,211,238,.55), inset 0 0 22px -10px rgba(165,243,252,.6); }
.hc::after { content: ""; position: absolute; inset: 0; pointer-events: none; mix-blend-mode: screen; background-size: 260% 100%; background-position: var(--sx, 50%) 0;
  background-image: linear-gradient(115deg, transparent 30%, rgba(120,255,240,.32) 44%, rgba(255,140,240,.28) 52%, transparent 64%); }
.hc small { font: 500 9px "IBM Plex Mono", monospace; letter-spacing: .12em; color: #A5F3FC; text-transform: uppercase; }
.hc b { font: 700 22px "Outfit", sans-serif; color: #fff; text-shadow: 0 0 16px rgba(103,232,249,.6); }
.hc1 { left: 0; top: 0; width: 56%; height: 78%; transform: translateZ(-50px); }
.hc2 { right: 0; top: 0; width: 40%; height: 46%; transform: translateZ(40px); }
.hc3 { right: 8%; bottom: 0; width: 46%; height: 44%; transform: translateZ(100px); }
@media (max-width: 760px) { .ph-art.right, .holo { left: 30%; opacity: .55; } .tz-routes, .tz-lines, .tz-stack, .tz-cranes { opacity: .5; } }
"""

CS = "div[class*='st-key-card']:not(.st-key-card_login)"            # cartes du site (la carte de connexion a ses propres formes)
PB = ".stButton > button[kind='primary'], .stDownloadButton > button[kind='primary'], [data-testid^='stBaseButton-primary']"
BTN = ".stButton > button, .stDownloadButton > button, [data-testid^='stBaseButton-secondary'], [data-testid^='stBaseButton-primary']"
INP = "[data-baseweb='input'], [data-baseweb='select'] > div"
_ZELLIGE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'%3E%3Cg fill='none' stroke='%23F2C14E' "
            "stroke-opacity='.09'%3E%3Crect x='16' y='16' width='24' height='24'/%3E%3Crect x='16' y='16' width='24' height='24' transform='rotate(45 28 28)'/%3E%3C/g%3E%3C/svg%3E\")")

# formes propres aux designs 9-24 (cartes, boutons, chiffres de l'en-tête)
SHAPES = {
    9: [f"{CS} {{ border-radius: 18px !important; background: radial-gradient(120% 70% at 100% 0%, rgba(240,163,94,.10), transparent 55%), var(--surface) !important;"
        " border-color: rgba(240,163,94,.18) !important; }",
        ".ph-stat { border-radius: 14px !important; border-color: rgba(240,163,94,.25) !important; }",
        f"{PB} {{ background: linear-gradient(135deg, #F7B97A, #D9823A) !important; border-color: #D9823A !important; }}"],
    10: [f"{CS} {{ border-radius: 10px !important; border: 1px solid #22324D !important; background: radial-gradient(circle at 11px 11px, rgba(148,163,184,.4) 2px, transparent 2.6px),"
         " radial-gradient(circle at calc(100% - 11px) 11px, rgba(148,163,184,.4) 2px, transparent 2.6px), var(--surface) !important; }",
         ".ph-stat { border-radius: 8px !important; border-top: 2px solid #22C55E !important; }",
         f"{PB} {{ border-radius: 8px !important; box-shadow: 0 8px 20px -10px #2563EB !important; }}"],
    11: [f"{CS} {{ border-radius: 22px !important; }}", f"{BTN}, {INP} {{ border-radius: 999px !important; }}",
         ".ph-stat { border-radius: 999px !important; padding-left: 1.05rem !important; padding-right: 1.05rem !important; border-color: rgba(249,115,22,.3) !important; }",
         f"{PB} {{ background: linear-gradient(90deg, #F97316, #FDBA74) !important; }}"],
    12: [f"{CS} {{ border-radius: 24px !important; background: radial-gradient(140% 90% at 100% 0%, rgba(125,211,252,.08), transparent 55%), var(--surface) !important; }}",
         ".ph-stat { border-radius: 18px !important; }", f"{PB} {{ background: linear-gradient(135deg, #FDE68A, #F59E0B) !important; border-radius: 14px !important; }}"],
    13: [f"{CS} {{ border-radius: 16px !important; border: 1px solid rgba(129,140,248,.24) !important; box-shadow: 0 24px 48px -28px rgba(99,102,241,.55) !important; }}",
         ".ph-stat { border-color: rgba(129,140,248,.3) !important; }", f"{PB} {{ background: linear-gradient(135deg, #6366F1, #EC4899) !important; border-color: transparent !important; }}"],
    14: [f"{CS} {{ border-radius: 24px !important; background: linear-gradient(160deg, rgba(255,255,255,.07), rgba(255,255,255,.02)) !important; border-color: rgba(165,243,252,.16) !important;"
         " backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }",
         ".ph-stat { border-radius: 16px !important; background: rgba(255,255,255,.05) !important; }",
         f"{PB} {{ background: linear-gradient(135deg, #67E8F9, #06B6D4) !important; border-radius: 14px !important; }}"],
    15: [f"{CS} {{ border-radius: 12px !important; border: 1px solid rgba(34,211,238,.35) !important; background: repeating-linear-gradient(0deg, rgba(165,243,252,.035) 0 1px, transparent 1px 3px),"
         " linear-gradient(160deg, #0A1D33, #061222) !important; box-shadow: 0 0 26px -16px rgba(34,211,238,.8) !important; }",
         ".ph-stat { border-color: rgba(34,211,238,.4) !important; }", f"{PB} {{ background: linear-gradient(135deg, #A5F3FC, #22D3EE) !important; }}"],
    16: [f"{CS} {{ border-radius: 6px !important; background: repeating-linear-gradient(-45deg, #EAB308 0 9px, #111827 9px 18px) top left / 100% 4px no-repeat, var(--surface) !important; }}",
         f".ph-stat, {BTN}, {INP} {{ border-radius: 4px !important; }}", ".ph-stat { border-left: 3px solid #EAB308 !important; }"],
    17: [f"{CS} {{ border-radius: 16px !important; border: 1px solid rgba(242,193,78,.2) !important; box-shadow: inset 0 2px 0 rgba(242,193,78,.5), 0 18px 40px -26px rgba(0,0,0,.8) !important; }}",
         ".ph-stat { border-radius: 40px 40px 10px 10px !important; border-color: rgba(242,193,78,.32) !important; padding-top: .7rem !important; text-align: center; }",
         f"section[data-testid='stSidebar'] {{ background-image: {_ZELLIGE} !important; }}",
         f"{PB} {{ background: linear-gradient(135deg, #F7D57A, #D9A43A) !important; border-color: #D9A43A !important; }}", ".ph h1 { font-weight: 400 !important; letter-spacing: .01em; }"],
    18: [f"{CS} {{ border-radius: 4px !important; box-shadow: inset 4px 0 0 #FF7A1A, 0 14px 30px -22px rgba(0,0,0,.9) !important; }}",
         f".ph-stat, {BTN}, {INP} {{ border-radius: 3px !important; }}", ".ph-stat { border-left: 3px solid #FF7A1A !important; }",
         ".ph h1, .stApp h2, .stApp h3, .section-h b { text-transform: uppercase; letter-spacing: .02em; }", ".ph h1 { font-weight: 600 !important; }",
         "section[data-testid='stSidebar'] { background-image: repeating-linear-gradient(90deg, rgba(255,255,255,.018) 0 10px, transparent 10px 12px) !important; }"],
    19: [f"{CS} {{ border-radius: 10px !important; border-color: rgba(255,46,151,.28) !important; box-shadow: 0 0 30px -14px rgba(255,46,151,.6) !important; }}",
         ".ph h1 { text-shadow: 0 0 16px rgba(255,46,151,.55); font-weight: 400 !important; }", ".ph-stat { border-color: rgba(0,240,255,.35) !important; }",
         f"{PB} {{ background: linear-gradient(90deg, #FF2E97, #B026FF) !important; border-color: transparent !important; box-shadow: 0 0 22px -6px rgba(255,46,151,.8) !important; }}"],
    20: [f"{CS} {{ border-radius: 22px !important; border: 1px solid rgba(167,139,250,.22) !important;"
         " background: radial-gradient(rgba(255,255,255,.16) .6px, transparent .9px) 0 0 / 22px 22px, linear-gradient(160deg, #100C28, #0A081C) !important; }",
         ".ph-stat { border-radius: 16px !important; border-color: rgba(167,139,250,.3) !important; }",
         f"{PB} {{ background: linear-gradient(135deg, #C4B5FD, #F0ABFC) !important; border-color: transparent !important; }}"],
    21: [".stApp { background: linear-gradient(180deg, #DDEBF8 0, #EEF5FB 360px) !important; }",
         f"{CS} {{ border-radius: 20px !important; border: 1px solid #DCE7F3 !important; box-shadow: 0 18px 40px -26px rgba(15,111,222,.35) !important; }}",
         f"{BTN}, {INP} {{ border-radius: 999px !important; }}", ".ph-stat { border-radius: 16px !important; background: #FFFFFF !important; }"],
    22: [f"{CS} {{ border-radius: 2px !important; border: 1px solid rgba(34,197,94,.3) !important; background: repeating-linear-gradient(0deg, rgba(34,197,94,.03) 0 1px, transparent 1px 3px), var(--surface) !important; }}",
         f".ph-stat, {BTN}, {INP} {{ border-radius: 2px !important; }}", ".ph-stat b, .ph-crumb, .ph p, .stButton > button p, label p { font-family: 'JetBrains Mono', monospace !important; }",
         ".ph h1 { text-shadow: 0 0 12px rgba(34,197,94,.45); font-weight: 700 !important; letter-spacing: -.01em; }",
         ".ph h1::after { content: '▌'; color: #22C55E; margin-left: .12em; animation: tz-caret 1s steps(1) infinite; } @keyframes tz-caret { 50% { opacity: 0; } }",
         f"{PB} {{ background: rgba(34,197,94,.1) !important; color: #4ADE80 !important; border: 1px solid #22C55E !important; box-shadow: 0 0 16px -6px rgba(34,197,94,.7) !important; }}",
         f"{PB} p {{ color: #4ADE80 !important; }}"],
    23: [f"{CS} {{ border-radius: 20px !important; border: 1px solid transparent !important;"
         " background: linear-gradient(160deg, #1A1A20, #111115) padding-box, linear-gradient(135deg, #52525B, #F4F4F5 30%, #71717A 52%, #F0ABFC 72%, #D4D4D8) border-box !important; }",
         ".ph h1 { background: linear-gradient(180deg, #FFFFFF 15%, #A1A1AA 55%, #F4F4F5 85%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }",
         ".ph h1 em.hl { -webkit-text-fill-color: #F0ABFC !important; }", ".ph-stat { border-radius: 14px !important; }",
         f"{PB} {{ background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 45%, #94A3B8 55%, #E2E8F0 100%) !important; border-color: #CBD5E1 !important;"
         " box-shadow: inset 0 1px 0 #fff, 0 8px 20px -10px rgba(240,171,252,.55) !important; }"],
    24: [f"{CS} {{ border-radius: 16px !important; border: 1px solid rgba(45,212,191,.16) !important;"
         " background: linear-gradient(90deg, transparent, rgba(45,212,191,.6), rgba(245,184,65,.5), transparent) bottom / 100% 1px no-repeat, var(--surface) !important; }",
         ".ph-stat { border-top: 2px solid #2DD4BF !important; }", f"{PB} {{ background: linear-gradient(135deg, #5EEAD4, #2DD4BF) !important; }}"],
}


def _design_css(theme: str) -> str:
    s = spec(theme)
    if not s:
        return ""
    i, _n, light, pal, (fd, fb), art, scene = s
    bg, sf, sf2, side, ink, ink2, ink3, ac, acd, ac2, acl = pal
    css = [f"@import url('{font_url(fd, fb, *_EXTRA_FONTS.get(i, ()))}');",
           f":root {{ --bg:{bg}; --surface:{sf}; --surface2:{sf2}; --ink:{ink}; --ink2:{ink2}; --ink3:{ink3}; --accent:{ac}; --accent2:{ac2};"
           f" --brd:{'rgba(15,23,42,.13)' if light else 'rgba(148,163,184,.16)'}; --f-display:'{fd}', 'IBM Plex Sans', system-ui, sans-serif; --f-body:'{fb}', system-ui, sans-serif; }}",
           ".stApp, .stApp p, .stApp label, .stApp li, .stMarkdown, button, input, textarea, select { font-family: var(--f-body) !important; }",
           ".ph h1, .stApp h1, .stApp h2, .stApp h3, .card-title b, .section-h b, .side-brand b, .ph-stat b { font-family: var(--f-display) !important; }",
           f".stApp {{ background: {bg} !important; }}",
           f"section[data-testid='stSidebar'] {{ background: {side} !important; }}",
           f".ph h1 em.hl {{ color: {acl} !important; }}",
           f"{PB} {{ background: {ac} !important; border-color: {acd} !important; color: {_on_accent(ac)} !important; }} {PB} p {{ color: {_on_accent(ac)} !important; }}",
           f"[data-baseweb='tag'] {{ background: {ac}2E !important; border-color: {ac}66 !important; }} [data-baseweb='tag'] span, [data-baseweb='tag'] svg {{ color: {ink} !important; fill: {ink} !important; }}"]
    if light:
        css += [f".stApp h1, .stApp h2, .stApp h3, .section-h {{ background: none !important; -webkit-text-fill-color: {ink} !important; color: {ink} !important; }}",
                f".ph h1, .ph h1 * {{ -webkit-text-fill-color: {ink} !important; }} .ph h1 em.hl {{ -webkit-text-fill-color: {acl} !important; }}",
                f"section[data-testid='stSidebar'] * {{ color: {ink}; }}",
                f"[data-testid='stMultiSelect'] [data-baseweb='select'] > div, [data-testid='stMultiSelect'] [data-baseweb='select'] > div > div {{ background: {sf2} !important; }}",
                f"[data-testid='stNumberInputContainer'], [data-testid='stNumberInputContainer'] > div {{ background: {sf2} !important; }}",
                f"[data-testid='stNumberInputField'], [data-testid='stNumberInput'] input {{ color: {ink} !important; -webkit-text-fill-color: {ink} !important; background: transparent !important; }}",
                f"[data-testid='stNumberInput'] button {{ color: {ink2} !important; }}",
                f".stRadio label:has(input:not(:checked)) > div:first-child, .stCheckbox label:has(input:not(:checked)) > span:first-child {{ background: {sf} !important; border: 1.5px solid {ink3} !important; }}",
                # Streamlit 1.66 : liste à choix multiples (react-aria), boutons radio et cases à cocher
                f"[data-testid='stMultiSelect'] .react-aria-ComboBox > div {{ background: {sf2} !important; border-color: rgba(15,23,42,.14) !important; }}"
                f" [data-testid='stMultiSelect'] input {{ color: {ink} !important; -webkit-text-fill-color: {ink} !important; }}",
                f"[data-testid='stMultiSelectDropdown'] {{ background: {sf} !important; border: 1px solid rgba(15,23,42,.12) !important; }} [data-testid='stMultiSelectDropdown'] [role='option'] {{ color: {ink} !important; }}",
                f"[data-testid='stRadioOption']:has(input:not(:checked)) > div > div:first-child {{ background: {sf} !important; border: 1.5px solid {ink3} !important; }}",
                f"[data-testid='stCheckbox'] label:has(input:not(:checked)) > div:first-of-type {{ background: {sf} !important; border: 1.5px solid {ink3} !important; }}"]
    if i == 2:
        css += [".stApp::before { content: ''; position: fixed; inset: -20%; z-index: 0; pointer-events: none; filter: blur(70px); opacity: .5;"
                " background: radial-gradient(30% 35% at 30% 30%, #0D9488, transparent 70%), radial-gradient(30% 30% at 70% 60%, #0369A1, transparent 70%);"
                " animation: tz-aur 22s ease-in-out infinite alternate; }",
                f"{CS}, [data-testid='stExpander'], .side-user, .ph-stat {{ background: rgba(255,255,255,.05) !important; border-color: rgba(255,255,255,.14) !important;"
                " backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }"]
    if i == 4:
        css += [f"{CS}, {INP}, .stButton > button, .stDownloadButton > button, [data-testid='stFileUploaderDropzone'],"
                " .ph-stat, .side-user, .ph.has-art, [data-testid='stExpander'] { border-radius: 3px !important; }",
                ".ph h1, .stApp h2, .stApp h3, .section-h b { text-transform: uppercase; letter-spacing: .03em; }",
                f"section[data-testid='stSidebar'] {{ border-right: 4px solid {ac} !important; }}",
                f"div.st-key-module [data-testid='stRadioOption'][data-selected='true'] {{ background: {ac} !important; }} div.st-key-module [data-testid='stRadioOption'][data-selected='true'] p {{ color: #101214 !important; }}"]
    if i == 6:
        css += [f"{CS}, .ph-stat, .ph.has-art {{ border-color: rgba(34,211,238,.28) !important; box-shadow: 0 0 24px -14px rgba(34,211,238,.8) !important; }}",
                ".ph h1 { text-transform: uppercase; letter-spacing: .04em; text-shadow: 0 0 18px rgba(34,211,238,.35); }",
                f"{PB} {{ background: transparent !important; color: #22D3EE !important; border: 1.5px solid #22D3EE !important; box-shadow: 0 0 16px -2px rgba(34,211,238,.6) !important; }} {PB} p {{ color: #22D3EE !important; }}"]
    if i == 7:
        css += [f"{CS}, .ph-stat, .ph.has-art, {INP}, .stButton > button {{ border-radius: 2px !important; }}",
                ".ph-stat b, .ph-crumb, .ph p { font-family: 'IBM Plex Mono', monospace !important; }", ".ph h1 { font-weight: 400 !important; }",
                ".ph.has-art { border-bottom: 2px solid #1F3A2C !important; }"]
    if i == 8:
        css += [f"{CS}, .ph-stat, {INP}, .stButton > button, .stDownloadButton > button, [data-testid='stFileUploaderDropzone'], .side-user, [data-testid='stExpander'] {{ border-radius: 0 !important; }}",
                f"{CS} {{ border: 1px solid #0C0A09 !important; box-shadow: none !important; }}",
                ".ph h1 { font-size: 2.1rem !important; letter-spacing: -.03em; } .ph-stat { border: none !important; border-left: 2px solid #0C0A09 !important; background: transparent !important; }",
                f"{PB} {{ background: #0C0A09 !important; border-color: #0C0A09 !important; color: #FAFAF9 !important; }} {PB} p {{ color: #FAFAF9 !important; }}"]
    if i == 3:
        css += [f"{CS} {{ transition: transform .2s, box-shadow .2s !important; }} {CS}:hover {{ transform: translateY(-2px); box-shadow: 0 10px 24px -14px rgba(15,23,42,.3) !important; }}"]
    css += SHAPES.get(i, [])
    if scene in ("tanger", "terminal", "synth", "galaxie", "avions", "codes", "chrome", "flux"):
        css.append(".ph.has-art { min-height: 214px; }")
    return "\n".join(css)


_TRUCK_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 30'%3E%3Crect x='0' y='4' width='40' height='18' rx='2' fill='%23E8590C'/%3E"
              "%3Cpath d='M40 9 H52 L60 16 V22 H40 Z' fill='%23475569'/%3E%3Ccircle cx='10' cy='24' r='4.5' fill='%230F172A'/%3E%3Ccircle cx='30' cy='24' r='4.5' fill='%230F172A'/%3E"
              "%3Ccircle cx='52' cy='24' r='4.5' fill='%230F172A'/%3E%3C/svg%3E")
BASE_CSS = ".block-container { position: relative; z-index: 1; }"


def _anim_css(a: list[str]) -> str:
    css = []
    if "A" in a:
        css.append(".stProgress > div > div > div > div { position: relative; overflow: visible !important; }"
                   f".stProgress > div > div > div > div::after {{ content: ''; position: absolute; right: -22px; top: -17px; width: 34px; height: 16px; background: url(\"{_TRUCK_URI}\") no-repeat center / contain; }}"
                   ".stProgress > div > div > div { overflow: visible !important; margin-top: 14px; }")
    if "B" in a:
        css.append(".status-banner.status-ok, [data-testid='stAlert']:has([data-testid='stAlertContentSuccess']) { position: relative; overflow: visible; }"
                   ".status-banner.status-ok::after, [data-testid='stAlert']:has([data-testid='stAlertContentSuccess'])::after { content: 'PRÊT ✓'; position: absolute; right: 18px; top: 50%;"
                   " border: 3px solid #16A34A; color: #16A34A; font: 700 15px 'IBM Plex Mono', monospace; padding: 5px 12px; border-radius: 8px; letter-spacing: .12em; pointer-events: none;"
                   " transform: translateY(-50%) rotate(-8deg); animation: tz-stamp .9s cubic-bezier(.2,1.6,.4,1) both; background: rgba(22,163,74,.08); }"
                   "@keyframes tz-stamp { 0% { transform: translateY(-50%) rotate(-8deg) scale(2.4); opacity: 0; } 100% { transform: translateY(-50%) rotate(-8deg) scale(1); opacity: 1; } }")
    if "D" in a:
        css.append("[data-testid='stFileUploaderFile'] { position: relative; overflow: hidden; }"
                   "[data-testid='stFileUploaderFile']::after { content: ''; position: absolute; left: 0; right: 0; height: 22px; top: -22px; pointer-events: none;"
                   " background: linear-gradient(180deg, transparent, rgba(56,189,248,.5)); border-bottom: 2px solid #38BDF8; animation: tz-fscan 1.1s ease-in-out 3; }"
                   "@keyframes tz-fscan { 0% { top: -22px; } 100% { top: 100%; } }")
    if "E" in a:
        css.append("[data-testid='stFileUploaderDropzone'] { animation: tz-breathe 2.6s ease-in-out infinite; }"
                   "[data-testid='stFileUploaderDropzone'] button svg, [data-testid='stFileUploaderDropzone'] button span[data-testid='stIconMaterial'] { animation: tz-bob 2.6s ease-in-out infinite; }"
                   "@keyframes tz-breathe { 50% { border-color: var(--accent) !important; background: rgba(59,130,246,.08) !important; box-shadow: 0 0 0 4px rgba(59,130,246,.08); } }"
                   "@keyframes tz-bob { 50% { transform: translateY(-3px); } }")
    if "I" in a:
        css.append("section.stMain [data-testid='stMainBlockContainer'] > div > [data-testid='stVerticalBlock'] > [data-testid='stElementContainer'],"
                   " section.stMain [data-testid='stMainBlockContainer'] > div > [data-testid='stVerticalBlock'] > [data-testid='stLayoutWrapper'],"
                   " section.stMain [data-testid='stMainBlockContainer'] > div > [data-testid='stVerticalBlock'] > [data-testid='stHorizontalBlock'] { animation: tz-in .45s ease-out both; }"
                   "@keyframes tz-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }")
    if "N" in a:
        css.append(".stApp::after { content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none; background: var(--tz-tint, transparent); transition: background 1s; }"
                   "html.tz-matin { --tz-tint: linear-gradient(180deg, rgba(253,230,138,.07), transparent 40%); } html.tz-soir { --tz-tint: linear-gradient(180deg, rgba(249,115,22,.10), rgba(124,58,237,.06) 60%, transparent); }"
                   "html.tz-nuit { --tz-tint: linear-gradient(180deg, rgba(30,27,75,.18), transparent 60%); }"
                   "#tz-clock { position: fixed; right: 16px; bottom: 14px; z-index: 50; font: 600 11px 'IBM Plex Mono', monospace; padding: 6px 10px; border-radius: 999px;"
                   " background: rgba(10,16,32,.7); color: #E2E8F0; border: 1px solid rgba(148,163,184,.3); pointer-events: none; }")
    if "R" in a or "U" in a:
        css.append(f"{CS} {{ position: relative; isolation: isolate; }}")
    if "R" in a:
        css.append("@property --tz-ang { syntax: '<angle>'; inherits: false; initial-value: 0deg; }"
                   f"{CS}::before {{ content: ''; position: absolute; inset: -1px; border-radius: inherit; padding: 1.5px; pointer-events: none; z-index: 2;"
                   " background: conic-gradient(from var(--tz-ang), transparent 0 55%, var(--accent) 70%, var(--accent2) 80%, transparent 92%);"
                   " -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor;"
                   " mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0); animation: tz-ang 6s linear infinite; }"
                   "@keyframes tz-ang { to { --tz-ang: 360deg; } }"
                   f"@media (prefers-reduced-motion: reduce) {{ {CS}::before {{ animation: none; }} }}")
    if "U" in a:
        css.append(f"{CS}::after {{ content: ''; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; z-index: -1;"
                   " background: radial-gradient(320px circle at var(--mx, 50%) var(--my, 50%), color-mix(in srgb, var(--accent) 17%, transparent), transparent 70%);"
                   " opacity: var(--tz-u, 0); transition: opacity .35s; }")
    if "V" in a:
        css.append("#tz-breathe { position: fixed; inset: -12%; z-index: 0; pointer-events: none;"
                   " background: radial-gradient(38% 46% at 22% 28%, color-mix(in srgb, var(--accent) 20%, transparent), transparent 70%),"
                   " radial-gradient(34% 42% at 78% 72%, color-mix(in srgb, var(--accent2) 16%, transparent), transparent 70%);"
                   " animation: tz-breath 10s ease-in-out infinite alternate; will-change: transform, opacity; }"
                   "@keyframes tz-breath { from { transform: scale(1); opacity: .5; } to { transform: scale(1.14) translate(1.5%, -1.5%); opacity: 1; } }"
                   "@media (prefers-reduced-motion: reduce) { #tz-breathe { animation: none; } }")
    return "\n".join(css)


def css(theme: str) -> str:
    """Bloc <style> du design + des animations CSS (vide pour « Bleu Port » sans animation)."""
    body = _design_css(theme)
    a = anims()
    need_art = bool(spec(theme)) or "G" in a or "H" in a
    out = (BASE_CSS if (body or a) else "") + "\n" + (ART_CSS if need_art else "") + "\n" + body + "\n" + _anim_css(a)
    return f"<style>{out}</style>" if out.strip() else ""


# =============================================================================
# DÉCORS D'EN-TÊTE (HTML)
# =============================================================================

_SHIP = ('<svg viewBox="0 0 190 60" class="tz-ship" aria-hidden="true"><rect x="44" y="12" width="20" height="14" fill="#E8590C"/><rect x="64" y="12" width="20" height="14" fill="#1C7ED6"/>'
         '<rect x="84" y="12" width="20" height="14" fill="#2F9E44"/><rect x="104" y="12" width="20" height="14" fill="#E8590C"/><rect x="54" y="0" width="20" height="12" fill="#F59F00"/>'
         '<rect x="74" y="0" width="20" height="12" fill="#E8590C"/><rect x="94" y="0" width="20" height="12" fill="#1C7ED6"/><rect x="128" y="2" width="22" height="24" fill="#E9ECEF"/>'
         '<path d="M8 26 H182 L166 50 H24 Z" fill="#1E293B"/><path d="M8 26 H182 L178 32 H12 Z" fill="#C92A2A"/></svg>')
_CRANES = ('<svg viewBox="0 0 230 70" class="tz-cranes" aria-hidden="true" fill="none" stroke="#5B8BC9" stroke-width="2"><path d="M20 70 V18 H90 M20 18 L40 2 M60 18 V40 M110 70 V22 H190 M110 22 L130 6 M160 22 V46"/>'
           '<path d="M14 70 H40 M104 70 H130" stroke-width="3"/></svg>')
_CITIES = [("TANGER", -5.8, 35.77), ("VALENCIA", -.38, 39.47), ("BARCELONA", 2.17, 41.39), ("LA ROCHELLE", -1.15, 46.16), ("VALENCIENNES", 3.52, 50.36), ("REICHSHOFFEN", 7.66, 48.93)]


def _routes_svg() -> str:
    P = lambda lo, la: (((lo + 10) / 19) * 470, ((51.5 - la) / 17) * 172)  # noqa: E731
    tx, ty = P(_CITIES[0][1], _CITIES[0][2])
    s = '<svg class="tz-routes" viewBox="0 0 470 172" aria-hidden="true">'
    for _n, lo, la in _CITIES[1:]:
        x, y = P(lo, la)
        s += f'<path class="tz-route" d="M{tx:.1f} {ty:.1f} Q{(tx + x) / 2:.1f} {min(ty, y) - 34:.1f} {x:.1f} {y:.1f}"/>'
    for k, (n, lo, la) in enumerate(_CITIES):
        x, y = P(lo, la)
        s += (f'<circle class="tz-pulse" cx="{x:.1f}" cy="{y:.1f}" r="3" style="animation-delay:{k * .35}s"/><circle class="tz-city" cx="{x:.1f}" cy="{y:.1f}" r="{3.6 if k == 0 else 2.4}"/>'
              f'<text class="tz-lbl" x="{x + 6:.1f}" y="{y + 3:.1f}">{n}</text>')
    return s + "</svg>"


def _stack() -> str:
    items = [("TIMU 803890 7", "#E8590C", 0, 104, 0), ("ALSU 153220 9", "#1C7ED6", 98, 104, .4), ("MSCU 401070 3", "#2F9E44", 196, 104, .8),
             ("CMAU 1532408", "#1C7ED6", 49, 62, 1.2), ("TGHU 3444 A", "#E8590C", 147, 62, 1.6), ("SEGU 175 KG", "#F59F00", 98, 20, 2.0)]
    return '<div class="tz-stack">' + "".join(f'<div class="tz-ct" style="left:{x}px;top:{y}px;background-color:{c};animation-delay:{d}s">{t}</div>' for t, c, x, y, d in items) + "</div>"


def header_art(theme: str, stats: dict | None, badge: str, title: str) -> str:
    """Décor de l'en-tête de page pour le design choisi (+ G bateau / H routes si cochés). Vide = en-tête simple."""
    s = spec(theme)
    a = anims()
    parts = []
    art = s[5] if s else None
    scene = s[6] if s else None
    if scene and st.session_state.pop("_tz_bg_login", False):          # page de connexion : la scène est déjà en fond, l'en-tête reste sobre
        scene = None
        veil = "rgba(255,255,255,.6)" if s[2] else "rgba(4,7,16,.35)"
        parts.append(f'<div class="ph-art" style="background:{veil};backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)"></div>')
    if scene:
        parts.append(f'<div class="ph-art"><div class="scene-slot scene-{scene}"></div></div>')
    elif art == "port":
        parts.append(f'<div class="ph-art right"><div class="tz-sky"></div><div class="tz-stars"></div>{_CRANES}<div class="tz-sea"></div>{_SHIP}</div>')
    elif art == "aurora":
        parts.append('<div class="ph-art"><div class="tz-aur"></div></div>')
    elif art == "lines":
        parts.append('<div class="ph-art"><svg class="tz-lines" viewBox="0 0 300 130" fill="none" aria-hidden="true"><path d="M10 110 C80 110 90 36 160 36 S260 70 290 22" stroke="#93C5FD" stroke-width="2"/>'
                     '<circle cx="10" cy="110" r="4" fill="#1D4ED8"/><circle cx="290" cy="22" r="4" fill="#1D4ED8"/><text x="0" y="128" font-size="10" fill="#64748B" font-family="IBM Plex Mono">TANGER</text>'
                     '<text x="214" y="12" font-size="10" fill="#64748B" font-family="IBM Plex Mono">LA ROCHELLE</text></svg></div>')
    elif art == "boxes":
        parts.append(f'<div class="ph-art">{_stack()}</div>')
    elif art == "routes":
        parts.append(f'<div class="ph-art"><div class="tz-dots"></div>{_routes_svg()}</div>')
    elif art == "neon":
        parts.append('<div class="ph-art"><div class="tz-grid"></div><div class="tz-doc"></div></div>')
    elif art == "stamp":
        parts.append('<div class="ph-art"><div class="tz-form"></div><div class="tz-stamp">DÉDOUANÉ<br><small>TANGER · 401</small></div></div>')
    elif art == "holo":
        kv = list((stats or {}).items())
        k1 = kv[0] if kv else ("dossier", "TIMAR")
        k2 = kv[1] if len(kv) > 1 else ("module", "Tanger")
        parts.append('<div class="ph-art"><div class="scene-slot scene-holo"><div class="holo"><div class="hgrp">'
                     f'<div class="hc hc1"><small>{html.escape(badge)}</small><b>{html.escape(title)}</b></div>'
                     f'<div class="hc hc2"><small>{html.escape(str(k1[0]))}</small><b>{html.escape(str(k1[1]))}</b></div>'
                     f'<div class="hc hc3"><small>{html.escape(str(k2[0]))}</small><b>{html.escape(str(k2[1]))}</b></div></div></div></div></div>')
    if "H" in a and art != "routes":
        parts.append(f'<div class="ph-art right" style="opacity:.9"><div class="tz-dots"></div>{_routes_svg()}</div>')
    if "G" in a and art != "port":
        parts.append(f'<div class="ph-art">{_SHIP}</div>')
    if not parts:
        return ""
    return "".join(parts) + ('<div class="ph-veil"></div>' if (scene or art in ("port", "aurora", "boxes", "routes", "neon")) else "")


def login_background(theme: str):
    """Page de connexion des designs « waw » : la scène animée occupe tout le fond."""
    s = spec(theme)
    if s and s[6]:
        st.session_state["_tz_bg_login"] = True
        st.markdown(f'<div class="scene-slot scene-bg scene-{s[6]}"></div>', unsafe_allow_html=True)


# =============================================================================
# MOTEUR JS (scènes <canvas>/WebGL + animations C F J K L M N O P Q S T U V), injecté une fois dans la page
# =============================================================================

ENGINE = r"""
(function () {
var W = window.__timarHost || window, doc = W.document;
if (W.__timarConfigure) return;
var RM = W.matchMedia("(prefers-reduced-motion: reduce)").matches;
var cfg = { anims: [], heavy: [] };
var mouse = { x: -1e4, y: -1e4 };
var D = Math.PI / 180;
function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function ease(x) { return x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x); }
function poly(c, p, f) { c.beginPath(); c.moveTo(p[0][0], p[0][1]); for (var i = 1; i < p.length; i++) c.lineTo(p[i][0], p[i][1]); c.closePath(); if (f) { c.fillStyle = f; c.fill(); } }
function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
function shade(hex, f) { var n = parseInt(hex.slice(1), 16); function k(v) { return Math.max(0, Math.min(255, Math.round(v * f))); } return "rgb(" + k(n >> 16) + "," + k(n >> 8 & 255) + "," + k(n & 255) + ")"; }
function wide(o) { return o.w / o.h > 2.6; }

var S = {};
S.phare = { init: function (o) { var r = rng(7); o.st = []; for (var i = 0; i < 170; i++) o.st.push({ x: r(), y: r() * .6, a: r() * 6.3, s: r() * 1.3 + .4 }); },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, hz = h * .66, g, i;
    g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, "#050817"); g.addColorStop(.5, "#13214D"); g.addColorStop(.82, "#4E3466"); g.addColorStop(1, "#E0875F"); c.fillStyle = g; c.fillRect(0, 0, w, hz + 1);
    c.fillStyle = "#fff"; for (i = 0; i < o.st.length; i++) { var s = o.st[i], al = (.25 + .75 * Math.abs(Math.sin(t * .9 + s.a))) * (1 - s.y * 1.25); if (al > 0) { c.globalAlpha = al; c.fillRect(s.x * w, s.y * h, s.s, s.s); } } c.globalAlpha = 1;
    var mx = w * .2, my = h * .17, mr = Math.max(8, h * .034); c.fillStyle = "#F8F1DC"; c.beginPath(); c.arc(mx, my, mr, 0, 7); c.fill(); c.fillStyle = "#0B1434"; c.beginPath(); c.arc(mx + mr * .45, my - mr * .15, mr * .92, 0, 7); c.fill();
    c.fillStyle = "#241C46"; c.beginPath(); c.moveTo(0, hz); for (var x = 0; x <= w * .62; x += 6) c.lineTo(x, hz - 3 - h * .022 * (1 + Math.sin(x * .011 + 1)) - h * .01 * Math.sin(x * .037)); c.lineTo(w * .62, hz); c.closePath(); c.fill();
    g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, "#3A2E5C"); g.addColorStop(.18, "#121B3F"); g.addColorStop(1, "#04070F"); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
    for (i = 0; i < 90; i++) { var k = i / 90, y = hz + 3 + k * k * (h - hz), len = (10 + (i * 37) % 40) * (.4 + k), xx = ((i * 211.7 + t * (8 + (i % 5) * 4)) % (w + 160)) - 80;
      c.globalAlpha = (.06 + .14 * (.5 + .5 * Math.sin(t * 2.2 + i * 1.7))) * (1 - k * .6); c.fillStyle = i % 3 ? "#E89A70" : "#9FB4FF"; c.fillRect(xx, y, len, 1 + k * 1.5); } c.globalAlpha = 1;
    var sx = w * 1.05 - ((t * 16) % (w * 1.3)); c.fillStyle = "#0B0F22"; c.fillRect(sx, hz - 6, 46, 5); c.fillRect(sx + 30, hz - 11, 10, 5); c.fillStyle = "#FDE68A"; [4, 10, 16, 22, 34].forEach(function (d) { c.fillRect(sx + d, hz - 4, 1.6, 1.6); });
    c.fillStyle = "#080A16"; c.beginPath(); c.moveTo(w * .56, h); c.lineTo(w * .63, hz + 18); c.lineTo(w * .7, hz - 10); c.lineTo(w * .8, hz - h * .06); c.lineTo(w * .92, hz - h * .07); c.lineTo(w, hz - h * .05); c.lineTo(w, h); c.closePath(); c.fill();
    var th = Math.min(h * .33, 170), tw = th * .2, lx = w * .84, base = hz - h * .065;
    c.fillStyle = "#BCA884"; c.fillRect(lx - tw * 1.7, base - th * .17, tw * 3.4, th * .17);
    poly(c, [[lx - tw * .62, base], [lx + tw * .62, base], [lx + tw * .48, base - th], [lx - tw * .48, base - th]], "#D8C7A4"); poly(c, [[lx, base], [lx + tw * .62, base], [lx + tw * .48, base - th], [lx, base - th]], "#B39F7B");
    var ly = base - th - tw * .45; c.fillStyle = "#2B2F3A"; c.fillRect(lx - tw * .72, base - th - 2, tw * 1.44, 4); c.fillStyle = "#FFF3C4"; c.fillRect(lx - tw * .32, ly - tw * .3, tw * .64, tw * .62);
    poly(c, [[lx - tw * .42, ly - tw * .3], [lx + tw * .42, ly - tw * .3], [lx, ly - tw * .78]], "#2B2F3A");
    var a = t * 1.1, dx = Math.cos(a), dz = Math.sin(a), side = dx < 0 ? -1 : 1, L = Math.abs(dx) * w * 1.15, sp = th * .08 + th * .22 * (1 - Math.abs(dx));
    c.globalCompositeOperation = "lighter"; g = c.createLinearGradient(lx, ly, lx + side * L, ly); g.addColorStop(0, "rgba(255,240,190,.55)"); g.addColorStop(1, "rgba(255,240,190,0)");
    poly(c, [[lx, ly - tw * .15], [lx + side * L, ly - sp * 1.4], [lx + side * L, ly + sp * 1.4], [lx, ly + tw * .15]], g);
    var rad = tw * (1.2 + 9 * Math.pow(Math.max(0, dz), 6)); g = c.createRadialGradient(lx, ly, 0, lx, ly, rad); g.addColorStop(0, "rgba(255,247,214,.95)"); g.addColorStop(1, "rgba(255,247,214,0)"); c.fillStyle = g; c.beginPath(); c.arc(lx, ly, rad, 0, 7); c.fill();
    c.globalCompositeOperation = "source-over"; } };

function gear(c, x, y, r, n, rot, col) { c.save(); c.translate(x, y); c.rotate(rot); c.fillStyle = col; c.beginPath();
  for (var i = 0; i < n; i++) { var a = i * 2 * Math.PI / n, b = a + Math.PI / n; c.lineTo(Math.cos(a - .12) * r, Math.sin(a - .12) * r); c.lineTo(Math.cos(a + .28) * r, Math.sin(a + .28) * r); c.lineTo(Math.cos(b) * r * .76, Math.sin(b) * r * .76); c.lineTo(Math.cos(b + .35) * r * .76, Math.sin(b + .35) * r * .76); }
  c.closePath(); c.fill(); c.fillStyle = "#0B1220"; c.beginPath(); c.arc(0, 0, r * .3, 0, 7); c.fill(); c.restore(); }
function docIcon(c, x, y, w, h, kind) { var xl = kind === "XLSX", i;
  poly(c, [[x, y], [x + w * .7, y], [x + w, y + h * .22], [x + w, y + h], [x, y + h]], xl ? "#ECFDF5" : "#F8FAFC"); poly(c, [[x + w * .7, y], [x + w * .7, y + h * .22], [x + w, y + h * .22]], xl ? "#A7F3D0" : "#CBD5E1");
  if (xl) { c.strokeStyle = "#6EE7B7"; c.lineWidth = 1; for (i = 1; i < 4; i++) { c.beginPath(); c.moveTo(x + w * .12, y + h * (.3 + i * .15)); c.lineTo(x + w * .88, y + h * (.3 + i * .15)); c.stroke(); } }
  else { c.fillStyle = "#CBD5E1"; for (i = 0; i < 4; i++) c.fillRect(x + w * .14, y + h * (.36 + i * .13), w * (i % 2 ? .5 : .66), Math.max(1, h * .04)); }
  c.fillStyle = xl ? "#16A34A" : "#DC2626"; c.fillRect(x - w * .08, y + h * .06, w * .66, h * .2); c.fillStyle = "#fff"; c.font = "700 " + Math.max(6, h * .15) + "px 'IBM Plex Mono', monospace"; c.textBaseline = "middle"; c.fillText(xl ? "XLSX" : kind, x - w * .02, y + h * .165); c.textBaseline = "alphabetic"; }
S.usine = { frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, wd = wide(o), k, x;
    c.fillStyle = "#0A101C"; c.fillRect(0, 0, w, h); c.fillStyle = "rgba(148,163,184,.10)"; for (x = 12; x < w; x += 24) for (var y = 12; y < h; y += 24) c.fillRect(x, y, 1.5, 1.5);
    var by = h * .76, m0 = wd ? w * .74 : w * .43, m1 = wd ? w * .85 : w * .63, mh = h * .5, mt = by - mh, v = Math.max(45, w * .05), sp = Math.max(70, h * .55), dw = Math.max(20, h * .1), dh = dw * 1.3, bh = h * .035;
    [[wd ? w * .6 : 0, m0], [m1, w]].forEach(function (ab) { var a = ab[0], b = ab[1]; c.fillStyle = "#1E293B"; c.fillRect(a, by, b - a, bh); c.fillStyle = "#334155"; var off = (t * v) % 18; for (var xx = a - off; xx < b; xx += 18) if (xx >= a) c.fillRect(xx, by + 2, 8, bh - 4); });
    var base = Math.floor(t * v / sp), off = (t * v) % sp, a0 = wd ? w * .6 : 0;
    for (k = 0; k < 20; k++) { x = a0 + off + (k - 1) * sp - dw; if (x > m0 - dw * .4 || x < a0 - dw * .2) continue; docIcon(c, x, by - dh - 1, dw, dh, (base - k) % 2 ? "BL" : "FC"); }
    for (k = 0; k < 20; k++) { x = m1 + off + (k - 1) * sp; if (x < m1 || x > w) continue; docIcon(c, x, by - dh - 1, dw, dh, "XLSX"); }
    var g = c.createLinearGradient(0, mt, 0, by); g.addColorStop(0, "#1D4ED8"); g.addColorStop(1, "#172554"); c.fillStyle = g; rr(c, m0, mt, m1 - m0, mh + bh, 10); c.fill(); c.strokeStyle = "rgba(147,197,253,.5)"; c.lineWidth = 1.5; c.stroke(); c.lineWidth = 1;
    gear(c, m0 + (m1 - m0) * .3, mt - 2, h * .07, 10, t * 1.4, "#64748B"); gear(c, m0 + (m1 - m0) * .3 + h * .118, mt - h * .035, h * .05, 7, -t * 2, "#94A3B8");
    var wx = m0 + (m1 - m0) * .12, wy = mt + mh * .34, ww = (m1 - m0) * .76, wh = mh * .38; c.fillStyle = "#0B1220"; rr(c, wx, wy, ww, wh, 6); c.fill();
    var sy = wy + 2 + (.5 + .5 * Math.sin(t * 3)) * (wh - 6); g = c.createLinearGradient(0, sy - 14, 0, sy + 2); g.addColorStop(0, "rgba(56,189,248,0)"); g.addColorStop(1, "rgba(56,189,248,.85)"); c.fillStyle = g; c.fillRect(wx + 2, sy - 14, ww - 4, 16);
    c.textAlign = "center"; c.fillStyle = "#DBEAFE"; c.font = "800 " + Math.max(10, h * .07) + "px 'Bricolage Grotesque', sans-serif"; c.fillText("TIMAR", (m0 + m1) / 2, mt + mh * .22); c.textAlign = "left"; } };

S.train = { init: function (o) { var r = rng(3), i; o.p1 = []; o.p2 = []; for (i = 0; i < 6; i++) { o.p1.push([r() * 6.28, .5 + r() * 2]); o.p2.push([r() * 6.28, 1 + r() * 3]); } },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, g, x, k, j;
    g = c.createLinearGradient(0, 0, 0, h * .74); g.addColorStop(0, "#0E1A3A"); g.addColorStop(.55, "#4B3270"); g.addColorStop(.85, "#E07B53"); g.addColorStop(1, "#F6B26B"); c.fillStyle = g; c.fillRect(0, 0, w, h);
    var sx = w * .7, sy = h * .58, sr = h * .1; g = c.createRadialGradient(sx, sy, 0, sx, sy, sr * 3.2); g.addColorStop(0, "rgba(255,214,150,.85)"); g.addColorStop(1, "rgba(255,160,90,0)"); c.fillStyle = g; c.fillRect(0, 0, w, h); c.fillStyle = "#FFD9A0"; c.beginPath(); c.arc(sx, sy, sr, 0, 7); c.fill();
    function ridge(xx, ps) { var s = 0; for (var q = 0; q < ps.length; q++) s += Math.sin(xx * .004 * ps[q][1] + ps[q][0]) / ps[q][1]; return s; }
    c.fillStyle = "#3B2A5C"; c.beginPath(); c.moveTo(0, h); for (x = 0; x <= w + 6; x += 6) c.lineTo(x, h * .62 - (ridge(x + t * 14, o.p1) * .5 + .6) * h * .13); c.lineTo(w, h); c.closePath(); c.fill();
    c.fillStyle = "#24193F"; c.beginPath(); c.moveTo(0, h); for (x = 0; x <= w + 6; x += 6) c.lineTo(x, h * .71 - (ridge(x + t * 80, o.p2) * .5 + .5) * h * .08); c.lineTo(w, h); c.closePath(); c.fill();
    c.fillStyle = "#120E22"; c.fillRect(0, h * .79, w, h * .21);
    var ps = Math.max(170, h * 1.1), po = (t * 900) % ps, topY = h * .37, railY = h * .885; c.strokeStyle = "#0A0814"; c.lineWidth = Math.max(2, h * .008);
    for (x = -po; x < w + ps; x += ps) { c.beginPath(); c.moveTo(x, h * .81); c.lineTo(x, topY); c.lineTo(x + ps * .14, topY + 7); c.stroke(); }
    c.lineWidth = 1.2; c.beginPath(); for (x = -po; x < w + ps; x += ps) { c.moveTo(x + ps * .14, topY + 7); c.quadraticCurveTo(x + ps * .64, topY + 24, x + ps * 1.14, topY + 7); } c.stroke();
    var vib = Math.sin(t * 40) * .5, ty = h * .6 + vib, tb = h * .845 + vib, x0 = wide(o) ? w * .58 : -w * .06, x1 = wide(o) ? w * .86 : w * .8, cars = wide(o) ? 2 : 4, cw = (x1 - x0) / cars, H = tb - ty;
    g = c.createLinearGradient(0, ty, 0, tb); g.addColorStop(0, "#F1F5F9"); g.addColorStop(.62, "#CBD5E1"); g.addColorStop(1, "#64748B"); c.fillStyle = g;
    c.beginPath(); c.moveTo(x0, ty); c.lineTo(x1, ty); c.bezierCurveTo(x1 + cw * .28, ty, x1 + cw * .46, tb - H * .38, x1 + cw * .5, tb); c.lineTo(x0, tb); c.closePath(); c.fill();
    c.fillStyle = "#1D4ED8"; c.beginPath(); c.moveTo(x0, ty + H * .62); c.lineTo(x1 + cw * .38, ty + H * .62); c.lineTo(x1 + cw * .46, ty + H * .74); c.lineTo(x0, ty + H * .74); c.closePath(); c.fill();
    c.fillStyle = "#E11D48"; c.fillRect(x0, ty + H * .75, x1 + cw * .44 - x0, H * .035);
    for (k = 0; k < cars; k++) { var cx0 = x0 + k * cw; for (j = 0; j < 7; j++) { var wx = cx0 + cw * .08 + j * (cw * .84 / 7); c.fillStyle = "#1E293B"; rr(c, wx, ty + H * .18, cw * .84 / 7 * .74, H * .3, 3); c.fill(); c.fillStyle = "rgba(253,230,138,.55)"; rr(c, wx + 1.5, ty + H * .18 + 1.5, cw * .84 / 7 * .74 - 3, H * .3 - 3, 2); c.fill(); } if (k) { c.fillStyle = "#334155"; c.fillRect(cx0 - 1.5, ty + 2, 3, H - 4); } }
    poly(c, [[x1 + cw * .02, ty + H * .1], [x1 + cw * .22, ty + H * .14], [x1 + cw * .36, ty + H * .44], [x1 + cw * .02, ty + H * .44]], "#0F172A");
    c.strokeStyle = "#475569"; c.lineWidth = 2; c.beginPath(); c.moveTo(0, railY); c.lineTo(w, railY); c.stroke(); c.lineWidth = 1; c.fillStyle = "#2A2338"; var so = (t * 900) % 26; for (x = -so; x < w; x += 26) c.fillRect(x, railY + 3, 13, 4); } };

var CITY = [["Tanger", 35.77, -5.8], ["Valencia", 39.47, -.38], ["Barcelona", 41.39, 2.17], ["La Rochelle", 46.16, -1.15], ["Valenciennes", 50.36, 3.52], ["Reichshoffen", 48.93, 7.66]];
var LBL = [[-14, 16, "right"], [16, 10, "left"], [18, -4, "left"], [-18, -6, "right"], [-14, -18, "right"], [16, -14, "left"]];
function vec(la, lo) { var p = la * D, l = lo * D; return [Math.cos(p) * Math.cos(l), Math.cos(p) * Math.sin(l), Math.sin(p)]; }
S.globe = { init: function (o) { o.pts = []; for (var la = -84; la <= 84; la += 4) { var n = Math.max(8, Math.round(90 * Math.cos(la * D))); for (var i = 0; i < n; i++) o.pts.push(vec(la, i * 360 / n - 180)); } },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, i; c.fillStyle = "#030712"; c.fillRect(0, 0, w, h);
    var R = Math.min(h * .95, w * .5), cx = wide(o) ? w * .8 : w * .62, cy = h * .64, l0 = (1 + 10 * Math.sin(t * .12)) * D, p0 = 44 * D, cl = Math.cos(l0), sl = Math.sin(l0), cp = Math.cos(p0), spn = Math.sin(p0);
    function proj(v) { var x1 = v[0] * cl + v[1] * sl, y1 = -v[0] * sl + v[1] * cl, z1 = v[2]; return [cx + y1 * R, cy - (-x1 * spn + z1 * cp) * R, x1 * cp + z1 * spn]; }
    var g = c.createRadialGradient(cx, cy, R * .92, cx, cy, R * 1.3); g.addColorStop(0, "rgba(56,189,248,.3)"); g.addColorStop(1, "rgba(56,189,248,0)"); c.fillStyle = g; c.beginPath(); c.arc(cx, cy, R * 1.3, 0, 7); c.fill();
    g = c.createRadialGradient(cx - R * .3, cy - R * .35, R * .1, cx, cy, R); g.addColorStop(0, "#0C2D50"); g.addColorStop(1, "#040A18"); c.fillStyle = g; c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
    c.fillStyle = "#7DD3FC"; for (i = 0; i < o.pts.length; i++) { var q = proj(o.pts[i]); if (q[2] <= 0) continue; c.globalAlpha = .12 + .7 * q[2]; c.fillRect(q[0], q[1], 1.4, 1.4); } c.globalAlpha = 1;
    var T = vec(CITY[0][1], CITY[0][2]);
    for (i = 1; i < CITY.length; i++) { var B = vec(CITY[i][1], CITY[i][2]), om = Math.acos(T[0] * B[0] + T[1] * B[1] + T[2] * B[2]), pts = [];
      for (var j = 0; j <= 40; j++) { var s = j / 40, a = Math.sin((1 - s) * om) / Math.sin(om), b = Math.sin(s * om) / Math.sin(om), k = 1 + .16 * Math.sin(Math.PI * s); pts.push(proj([(a * T[0] + b * B[0]) * k, (a * T[1] + b * B[1]) * k, (a * T[2] + b * B[2]) * k])); }
      c.strokeStyle = "rgba(251,191,36,.28)"; c.beginPath(); pts.forEach(function (p, jj) { jj ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]); }); c.stroke();
      var head = (t * .4 + i * .21) % 1.3, j0 = Math.floor(Math.max(0, head - .35) * 40), j1 = Math.floor(Math.min(1, head) * 40);
      if (j1 > j0) { c.strokeStyle = "#FBBF24"; c.lineWidth = 2.2; c.shadowColor = "#F59E0B"; c.shadowBlur = 10; c.beginPath(); for (j = j0; j <= j1; j++) j === j0 ? c.moveTo(pts[j][0], pts[j][1]) : c.lineTo(pts[j][0], pts[j][1]); c.stroke(); c.shadowBlur = 0; c.lineWidth = 1; } }
    c.font = "600 " + Math.max(8, Math.min(12, R * .03)) + "px 'IBM Plex Mono', monospace";
    for (i = 0; i < CITY.length; i++) { var p = proj(vec(CITY[i][1], CITY[i][2])); if (p[2] <= 0) continue; var pr = (t * .8 + i * .3) % 1;
      c.strokeStyle = "rgba(251,191,36," + (1 - pr) + ")"; c.beginPath(); c.arc(p[0], p[1], 3 + pr * 12, 0, 7); c.stroke(); c.fillStyle = i ? "#FDE68A" : "#FB923C"; c.beginPath(); c.arc(p[0], p[1], i ? 2.6 : 4.2, 0, 7); c.fill();
      c.textAlign = LBL[i][2]; c.fillStyle = "#E2E8F0"; c.fillText(CITY[i][0].toUpperCase(), p[0] + LBL[i][0], p[1] + LBL[i][1] + 3); c.textAlign = "left"; } } };

var WORDS = ["TIMAR", "TANGER", "175 KG", "DUM ✓"], PCOL = ["#38BDF8", "#3B82F6", "#6366F1", "#A78BFA", "#F472B6", "#FB923C", "#FBBF24", "#FDE68A"];
S.particules = { init: function (o) { var r = rng(5); o.r = r; o.N = Math.min(1500, Math.max(400, Math.round(o.w * o.h / 170))); o.P = []; for (var i = 0; i < o.N; i++) o.P.push({ x: r() * o.w, y: r() * o.h, vx: 0, vy: 0, tx: r() * o.w, ty: r() * o.h, d: true }); o.wi = -1; o.next = 0; },
  targets: function (o, word) { var cv = doc.createElement("canvas"); cv.width = Math.max(1, Math.round(o.w)); cv.height = Math.max(1, Math.round(o.h)); var c = cv.getContext("2d"), wd = wide(o), cx = wd ? o.w * .8 : o.w / 2, maxW = wd ? o.w * .34 : o.w * .88;
    var fs = Math.min(o.h * .5, maxW * 1.6 / Math.max(4, word.length)); c.font = "800 " + fs + "px 'Bricolage Grotesque', 'IBM Plex Sans', sans-serif"; var mw = c.measureText(word).width; if (mw > maxW) { fs *= maxW / mw; c.font = "800 " + fs + "px 'Bricolage Grotesque', 'IBM Plex Sans', sans-serif"; }
    c.textAlign = "center"; c.textBaseline = "middle"; c.fillStyle = "#fff"; c.fillText(word, cx, o.h * .5);
    var d = c.getImageData(0, 0, cv.width, cv.height).data, st = Math.max(3, Math.round(Math.sqrt(o.w * o.h * .1 / o.N))), out = [];
    for (var y = 0; y < cv.height; y += st) for (var x = 0; x < cv.width; x += st) if (d[(y * cv.width + x) * 4 + 3] > 128) out.push([x, y]);
    for (var i = out.length - 1; i > 0; i--) { var j = Math.floor(o.r() * (i + 1)), tmp = out[i]; out[i] = out[j]; out[j] = tmp; } return out; },
  frame: function (o, t, dt) { var c = o.ctx, w = o.w, h = o.h;
    if (t > o.next) { o.wi = (o.wi + 1) % WORDS.length; var T = S.particules.targets(o, WORDS[o.wi]); o.P.forEach(function (p, i) { if (i < T.length) { p.tx = T[i][0]; p.ty = T[i][1]; p.d = false; } else { p.tx = o.r() * w; p.ty = o.r() * h; p.d = true; } p.vx += (o.r() - .5) * 9; p.vy += (o.r() - .5) * 9; }); o.next = t + 4.4; }
    c.fillStyle = dt ? "rgba(4,7,16,.34)" : "#040710"; c.fillRect(0, 0, w, h);
    for (var i = 0; i < o.P.length; i++) { var p = o.P[i];
      if (!dt) { p.x = p.tx; p.y = p.ty; } else { var dx = p.x - o.mx, dy = p.y - o.my, d2 = dx * dx + dy * dy; if (d2 < 9500) { var dd = Math.sqrt(d2) || 1, f = (1 - dd / 97) * 3.4; p.vx += dx / dd * f; p.vy += dy / dd * f; }
        p.vx = (p.vx + (p.tx - p.x) * .018) * .87; p.vy = (p.vy + (p.ty - p.y) * .018) * .87; p.x += p.vx; p.y += p.vy; }
      c.globalAlpha = p.d ? .22 : 1; c.fillStyle = PCOL[Math.max(0, Math.min(7, Math.floor(p.x / w * 8)))]; c.fillRect(p.x, p.y, p.d ? 1.2 : 2, p.d ? 1.2 : 2); } c.globalAlpha = 1; } };

var VS = "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}";
var FS = "precision mediump float;uniform vec2 r;uniform float t;uniform vec2 m;" +
  "float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}" +
  "float n(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),u.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),u.x),u.y);}" +
  "float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*n(p);p=p*2.02+vec2(1.7,9.2);a*=.5;}return v;}" +
  "void main(){vec2 uv=gl_FragCoord.xy/r;float as=r.x/r.y;vec2 p=uv*vec2(as,1.)*2.2;vec2 mm=(m-.5)*.9;" +
  "vec2 q=vec2(fbm(p+t*.05),fbm(p+vec2(5.2,1.3)-t*.04));vec2 w=vec2(fbm(p+3.*q+vec2(1.7,9.2)+mm+t*.06),fbm(p+3.*q+vec2(8.3,2.8)-mm));float f=fbm(p+3.*w);" +
  "vec3 c=mix(vec3(.02,.04,.10),vec3(.05,.20,.46),clamp(f*1.6,0.,1.));c=mix(c,vec3(.05,.55,.62),clamp(length(q)*.9-.35,0.,1.));c=mix(c,vec3(.98,.64,.27),clamp(w.x*w.x*1.3-.38,0.,1.)*.6);" +
  "c*=.72+.5*f;c+=vec3(.10,.20,.28)*smoothstep(.45,0.,distance(uv*vec2(as,1.),m*vec2(as,1.)));gl_FragColor=vec4(c,1.);}";
S.fluide = { gl: true, dprCap: 1,
  init: function (o) { if (o.fail) return; if (!o.g) { var gl = o.cv.getContext("webgl", { antialias: false }); if (!gl) { o.fail = true; return; }
      function sh(ty, src) { var x = gl.createShader(ty); gl.shaderSource(x, src); gl.compileShader(x); return x; }
      var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { o.fail = true; return; }
      gl.useProgram(pr); var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      var loc = gl.getAttribLocation(pr, "a"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      o.g = gl; o.u = { r: gl.getUniformLocation(pr, "r"), t: gl.getUniformLocation(pr, "t"), m: gl.getUniformLocation(pr, "m") }; o.sm = [.5, .5]; }
    o.g.viewport(0, 0, o.cv.width, o.cv.height); },
  frame: function (o, t) { if (o.fail || !o.g) return; var gl = o.g, tm = o.mx > -1e3 ? [o.mx / o.w, 1 - o.my / o.h] : [.5 + .28 * Math.sin(t * .3), .5 + .22 * Math.cos(t * .23)];
    o.sm[0] += (tm[0] - o.sm[0]) * .05; o.sm[1] += (tm[1] - o.sm[1]) * .05; gl.uniform2f(o.u.r, o.cv.width, o.cv.height); gl.uniform1f(o.u.t, t); gl.uniform2f(o.u.m, o.sm[0], o.sm[1]); gl.drawArrays(gl.TRIANGLES, 0, 3); } };

S.holo = { noCanvas: true, init: function (o) { o.g = o.slot.querySelector(".hgrp"); o.rx = 0; o.ry = 0; },
  frame: function (o, t) { if (!o.g || !doc.contains(o.g)) o.g = o.slot.querySelector(".hgrp"); if (!o.g) return; var tx, ty; if (o.mx > -1e3) { ty = (o.mx / o.w - .5) * 36; tx = -(o.my / o.h - .5) * 24; } else { ty = 17 * Math.sin(t * .55); tx = 7 * Math.cos(t * .42); }
    o.rx += (tx - o.rx) * .08; o.ry += (ty - o.ry) * .08; o.g.style.setProperty("--rx", o.rx.toFixed(2) + "deg"); o.g.style.setProperty("--ry", o.ry.toFixed(2) + "deg"); o.g.style.setProperty("--sx", (50 + o.ry * 4).toFixed(1) + "%"); } };

var PAL = ["#C2410C", "#1D4ED8", "#15803D", "#B91C1C", "#0E7490", "#A16207", "#6D28D9"];
function isoBox(c, P, x, y, z, w, d, h, col, ribs) { poly(c, [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(col, 1.18)); poly(c, [P(x, y + d, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x, y + d, z + h)], shade(col, .86));
  poly(c, [P(x + w, y, z), P(x + w, y + d, z), P(x + w, y + d, z + h), P(x + w, y, z + h)], shade(col, .64));
  if (ribs) { c.strokeStyle = "rgba(0,0,0,.18)"; c.lineWidth = 1; c.beginPath(); for (var i = 1; i < ribs; i++) { var a = P(x + w * i / ribs, y + d, z), b = P(x + w * i / ribs, y + d, z + h); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); } c.stroke(); } }
S.port3d = { init: function (o) { var r = rng(11), i, j, n, z; o.stk = []; for (var row = 0; row < 2; row++) for (i = 0; i < 4; i++) { n = 1 + Math.floor(r() * 3); for (z = 0; z < n; z++) o.stk.push([-2 + i * 2.7, 3.2 + row * 1.15, z, PAL[Math.floor(r() * PAL.length)]]); }
    o.deck = []; for (i = 0; i < 4; i++) for (j = 0; j < 3; j++) { n = 1 + Math.floor(r() * 2); for (z = 0; z < n; z++) o.deck.push([1.6 + i * 2.5, -6.5 + j * 1.15, 1.2 + z, PAL[Math.floor(r() * PAL.length)]]); }
    function so(a, b) { return (a[0] + a[1]) - (b[0] + b[1]) || a[2] - b[2]; } o.deck.sort(so); o.stk.sort(so); },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, s = Math.min(w / 31, h / 17.5), ox = (wide(o) ? w * .8 : w * .5) - 8 * s * .866, oy = h * .56 - 3 * s, i;
    function P(x, y, z) { return [ox + (x - y) * s * .866, oy + (x + y) * s * .5 - z * s]; }
    var g = c.createLinearGradient(0, 0, 0, h); g.addColorStop(0, "#040814"); g.addColorStop(1, "#0B1530"); c.fillStyle = g; c.fillRect(0, 0, w, h);
    poly(c, [P(-40, -16, 0), P(40, -16, 0), P(40, -.6, 0), P(-40, -.6, 0)], "#0A2340");
    c.strokeStyle = "rgba(125,211,252,.25)"; c.lineWidth = 1; c.beginPath(); for (i = 0; i < 38; i++) { var yy = -15 + (i % 13) * 1.1, xx = -20 + ((i * 7.3 + t * .8 * (1 + i % 3)) % 50), a = P(xx, yy, 0), b = P(xx + 1.2, yy, 0); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); } c.stroke();
    var bob = Math.sin(t * .8) * .05; isoBox(c, P, 0, -7.2, -.5 + bob, 15.5, 4.4, 1.7, "#1F2937"); isoBox(c, P, .2, -6.9, 1.2 + bob, 1.5, 3.8, 2.8, "#E5E7EB", 0);
    for (i = 0; i < o.deck.length; i++) { var q = o.deck[i]; isoBox(c, P, q[0], q[1], q[2] + bob, 2.4, 1, 1, q[3], 6); }
    var tc = t % 12, CX = 12.9, yS = -4.4, yTk = .6, yT, zs, att = false, ship = true, onT = false;
    if (tc < 2) { yT = yTk + (yS - yTk) * ease(tc / 2); zs = 6; } else if (tc < 3.2) { yT = yS; zs = 6 + (2.2 - 6) * ease((tc - 2) / 1.2); }
    else if (tc < 4.4) { yT = yS; zs = 2.2 + (5.5 - 2.2) * ease((tc - 3.2) / 1.2); att = true; ship = false; } else if (tc < 6.4) { yT = yS + (yTk - yS) * ease((tc - 4.4) / 2); zs = 5.5; att = true; ship = false; }
    else if (tc < 7.6) { yT = yTk; zs = 5.5 + (1.55 - 5.5) * ease((tc - 6.4) / 1.2); att = true; ship = false; } else { yT = yTk; zs = 1.55 + (6 - 1.55) * ease((tc - 7.6) / .8); ship = false; onT = true; }
    if (ship) isoBox(c, P, CX - 1.2, yS - .5, 1.2 + bob, 2.4, 1, 1, "#F59E0B", 6);
    poly(c, [P(-40, -.6, 0), P(40, -.6, 0), P(40, 20, 0), P(-40, 20, 0)], "#2B313D"); poly(c, [P(-40, -.2, 0), P(40, -.2, 0), P(40, 1.5, 0), P(-40, 1.5, 0)], "#232833");
    function leg(x, y) { var p1 = P(x, y, 0), p2 = P(x, y, 7.6); c.strokeStyle = "#E11D48"; c.lineWidth = Math.max(2, s * .22); c.beginPath(); c.moveTo(p1[0], p1[1]); c.lineTo(p2[0], p2[1]); c.stroke(); }
    function truck(x, load) { isoBox(c, P, x, .1, .25, 3, 1, .3, "#334155"); isoBox(c, P, x + 3, .1, .25, .9, 1, 1.1, "#E2E8F0"); if (load) isoBox(c, P, x + .3, .1, .55, 2.4, 1, 1, "#F59E0B", 6); }
    leg(CX - 1.5, -.6); leg(CX + 1.5, -.6);
    if (tc < 8.4) truck(CX - 1.5, onT); else { var k = ease((tc - 8.4) / 3.6); truck(CX - 1.5 + k * 24, true); truck(-18 + k * (CX - 1.5 + 18), false); }
    for (i = 0; i < o.stk.length; i++) { var q2 = o.stk[i]; isoBox(c, P, q2[0], q2[1], q2[2], 2.4, 1, 1, q2[3], 6); }
    leg(CX - 1.5, 1.8); leg(CX + 1.5, 1.8);
    [CX - 1.5, CX + 1.5].forEach(function (x) { var p1 = P(x, 3.2, 7.6), p2 = P(x, -9, 7.6); c.strokeStyle = "#F43F5E"; c.lineWidth = Math.max(2, s * .2); c.beginPath(); c.moveTo(p1[0], p1[1]); c.lineTo(p2[0], p2[1]); c.stroke(); });
    [3.2, -.6, 1.8, -9].forEach(function (yy) { var p1 = P(CX - 1.5, yy, 7.6), p2 = P(CX + 1.5, yy, 7.6); c.strokeStyle = "#BE123C"; c.lineWidth = Math.max(1.5, s * .14); c.beginPath(); c.moveTo(p1[0], p1[1]); c.lineTo(p2[0], p2[1]); c.stroke(); });
    var cab = P(CX, yT, 7.6), sp = P(CX, yT, zs + .15); c.strokeStyle = "#CBD5E1"; c.lineWidth = 1; c.beginPath(); c.moveTo(cab[0] - 3, cab[1]); c.lineTo(sp[0] - 3, sp[1]); c.moveTo(cab[0] + 3, cab[1]); c.lineTo(sp[0] + 3, sp[1]); c.stroke();
    isoBox(c, P, CX - .6, yT - .4, 7.4, 1.2, .8, .5, "#FBBF24"); if (att) isoBox(c, P, CX - 1.2, yT - .5, zs - 1, 2.4, 1, 1, "#F59E0B", 6); isoBox(c, P, CX - 1.25, yT - .55, zs, 2.5, 1.1, .14, "#EAB308");
    c.globalCompositeOperation = "lighter"; [[-4, 2.4], [4, 2.4], [20, 2.4], [8, 9]].forEach(function (l) { var tp = P(l[0], l[1], 4.2); g = c.createRadialGradient(tp[0], tp[1], 0, tp[0], tp[1], s * 3.2); g.addColorStop(0, "rgba(253,224,160,.55)"); g.addColorStop(1, "rgba(253,224,160,0)"); c.fillStyle = g; c.beginPath(); c.arc(tp[0], tp[1], s * 3.2, 0, 7); c.fill(); });
    c.globalCompositeOperation = "source-over"; } };

S.tanger = { init: function (o) { var r = rng(17), w = o.w, h = o.h, i, wd = wide(o);
    o.st = []; for (i = 0; i < 150; i++) o.st.push([r(), r() * .55, r() * 6.3, r() * 1.1 + .3]);
    var x0 = wd ? w * .44 : 0, cw = wd ? w * .56 : w * .8, hz = h * (wd ? .72 : .68), cxh = x0 + cw * .4;
    o.hz = hz; o.x0 = x0; o.cw = cw;
    o.hill = function (x) { var u = (x - cxh) / (cw * .3), v = (x - (x0 + cw * .82)) / (cw * .22), f = Math.min(1, Math.max(0, (x - x0) / (cw * .14))); return (Math.exp(-u * u) * h * .3 + Math.exp(-v * v) * h * .1) * f * f * (3 - 2 * f); };
    o.hs = []; var n = Math.round(cw / 2.6);
    for (i = 0; i < n; i++) { var x = x0 + r() * cw, top = hz - o.hill(x), y = top + Math.pow(r(), 1.4) * (hz - top) * .92, hs, hs = Math.min(1.6, Math.max(.9, h / 400 + .5)), bw = (4 + r() * 8) * hs, bh = (3 + r() * 6) * hs;
      o.hs.push({ x: x, y: y, w: bw, h: bh, lit: r() < .5, on: r() * 4, ph: r() * 6.3, wx: r(), sh: .5 + r() * .32 }); }
    o.hs.sort(function (a, b) { return a.y - b.y; });
    o.mins = [[x0 + cw * .36, 1], [x0 + cw * .58, .78]]; o.t0 = -1; },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, hz = o.hz, x0 = o.x0, cw = o.cw, i, g, x;
    if (o.t0 < 0) o.t0 = t; var el = t - o.t0;
    g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, "#04051A"); g.addColorStop(.6, "#1A1B4B"); g.addColorStop(.88, "#45306A"); g.addColorStop(1, "#7A4470"); c.fillStyle = g; c.fillRect(0, 0, w, hz + 1);
    c.fillStyle = "#fff"; for (i = 0; i < o.st.length; i++) { var s = o.st[i], a = (.3 + .7 * Math.abs(Math.sin(t * .7 + s[2]))) * (1 - s[1]); if (a > 0) { c.globalAlpha = a; c.fillRect(s[0] * w, s[1] * h, s[3], s[3]); } } c.globalAlpha = 1;
    var mx = x0 + cw * .9, my = h * .16, mr = Math.max(7, h * .035); g = c.createRadialGradient(mx, my, mr * .5, mx, my, mr * 5); g.addColorStop(0, "rgba(255,245,214,.35)"); g.addColorStop(1, "rgba(255,245,214,0)"); c.fillStyle = g; c.fillRect(mx - mr * 5, my - mr * 5, mr * 10, mr * 10);
    c.fillStyle = "#FFF5D6"; c.beginPath(); c.arc(mx, my, mr, 0, 7); c.fill(); c.fillStyle = "#0E0F33"; c.beginPath(); c.arc(mx + mr * .42, my - mr * .2, mr * .9, 0, 7); c.fill();
    c.fillStyle = "#0B0C26"; c.beginPath(); c.moveTo(x0, hz); for (x = x0; x <= x0 + cw + 4; x += 4) c.lineTo(x, hz - o.hill(x) - 3); c.lineTo(x0 + cw, hz); c.closePath(); c.fill();
    var k1 = x0 + cw * .27, k2 = x0 + cw * .52; c.fillStyle = "#A8936F";
    for (x = k1; x < k2; x += 3) { var yy = hz - o.hill(x) - 8; c.fillRect(x, yy, 3, 9); if (Math.floor((x - k1) / 6) % 2 === 0) c.fillRect(x, yy - 3, 3, 3); }
    for (i = 0; i < o.mins.length; i++) { var mm = o.mins[i], bx = mm[0], sc = mm[1] * h / 300, by = hz - o.hill(bx) - 4, tw = 7 * sc, th = 52 * sc;
      c.fillStyle = "#D8CFBC"; c.fillRect(bx - tw / 2, by - th, tw, th); c.fillStyle = "#B9AE97"; c.fillRect(bx, by - th, tw / 2, th);
      c.fillStyle = "#D8CFBC"; c.fillRect(bx - tw * .35, by - th - 9 * sc, tw * .7, 9 * sc);
      var ga = .6 + .4 * Math.sin(t * 2 + i); g = c.createRadialGradient(bx, by - th - 11 * sc, 0, bx, by - th - 11 * sc, 14 * sc); g.addColorStop(0, "rgba(52,211,153," + ga + ")"); g.addColorStop(1, "rgba(52,211,153,0)");
      c.fillStyle = g; c.beginPath(); c.arc(bx, by - th - 11 * sc, 14 * sc, 0, 7); c.fill(); }
    for (i = 0; i < o.hs.length; i++) { var hh = o.hs[i];
      c.fillStyle = "rgb(" + Math.round(205 * hh.sh) + "," + Math.round(208 * hh.sh) + "," + Math.round(232 * hh.sh) + ")"; c.fillRect(hh.x, hh.y, hh.w, hh.h);
      c.fillStyle = "rgba(0,0,0,.22)"; c.fillRect(hh.x + hh.w * .62, hh.y, hh.w * .38, hh.h);
      if (hh.lit && el > hh.on) { c.fillStyle = "rgba(255,208,122," + (.75 + .25 * Math.sin(t * 3 + hh.ph)).toFixed(2) + ")"; c.fillRect(hh.x + hh.w * hh.wx * .5, hh.y + hh.h * .3, Math.max(2, hh.w * .2), Math.max(2.5, hh.h * .32)); } }
    g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, "#151744"); g.addColorStop(.3, "#0B0E30"); g.addColorStop(1, "#03040E"); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
    for (i = 0; i < o.hs.length; i += 3) { var q = o.hs[i]; if (!q.lit || el < q.on) continue;
      for (var k = 0; k < 5; k++) { c.fillStyle = "rgba(255,208,122," + ((.35 - k * .06) * (.6 + .4 * Math.sin(t * 2.5 + q.ph + k))).toFixed(3) + ")"; c.fillRect(q.x + Math.sin(t * 2 + k + q.ph) * 1.5, hz + 3 + k * (h - hz) * .1, 1.6, (h - hz) * .05); } }
    for (k = 0; k < 9; k++) { c.fillStyle = "rgba(255,245,214," + (.25 - k * .025).toFixed(3) + ")"; c.fillRect(mx - 6 + Math.sin(t * 2 + k) * 3, hz + 4 + k * (h - hz) * .09, 12 - k, 2); }
    var fy = hz + (h - hz) * .32, fx = x0 + cw + 120 - ((el * 12) % (cw + 260)), fl = Math.max(46, h * .16), fh = fl * .22;
    c.fillStyle = "#E5E7EB"; c.fillRect(fx + fl * .18, fy - fh * 1.5, fl * .5, fh * .8); c.fillStyle = "#F3F4F6"; c.beginPath(); c.moveTo(fx, fy - fh * .7); c.lineTo(fx + fl, fy - fh * .7); c.lineTo(fx + fl * .92, fy); c.lineTo(fx + fl * .06, fy); c.closePath(); c.fill();
    c.fillStyle = "#1F3A8A"; c.fillRect(fx + fl * .04, fy - fh * .35, fl * .9, fh * .14);
    c.fillStyle = "#FFD27A"; for (k = 0; k < 9; k++) c.fillRect(fx + fl * (.1 + k * .09), fy - fh * .62, 2, 2);
    for (k = 0; k < 5; k++) { c.fillStyle = "rgba(255,210,122," + (.25 - k * .04).toFixed(2) + ")"; c.fillRect(fx + fl * .1, fy + 3 + k * 4, fl * .7, 1.5); }
    var lx = x0 + cw * .98, ly = hz - 2; c.fillStyle = "#1F2937"; c.fillRect(lx - cw * .14, ly, cw * .14, 3); c.fillStyle = "#E5E7EB"; c.fillRect(lx - 3, ly - h * .05, 6, h * .05);
    var fa = Math.max(0, Math.sin(t * 1.8)); g = c.createRadialGradient(lx, ly - h * .055, 0, lx, ly - h * .055, h * .08); g.addColorStop(0, "rgba(255,247,214," + fa + ")"); g.addColorStop(1, "rgba(255,247,214,0)"); c.fillStyle = g; c.beginPath(); c.arc(lx, ly - h * .055, h * .08, 0, 7); c.fill(); } };
S.terminal = { init: function (o) { var r = rng(18); o.seg = []; for (var i = 0; i < 64; i++) o.seg.push([1 + Math.floor(r() * 4), 1 + Math.floor(r() * 4), PAL[Math.floor(r() * PAL.length)], PAL[Math.floor(r() * PAL.length)], PAL[Math.floor(r() * PAL.length)], PAL[Math.floor(r() * PAL.length)], r() < .22]); },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, wd = wide(o), cx = wd ? w * .72 : w * .5, cy = h * .46, f = wd ? h * 1.15 : Math.min(w, h * 1.4) * .7;
    var g = c.createLinearGradient(0, 0, 0, h); g.addColorStop(0, "#05070B"); g.addColorStop(.40, "#160C07"); g.addColorStop(.46, "#3A1A06"); g.addColorStop(.5, "#0B0D10"); g.addColorStop(1, "#0B0D10"); c.fillStyle = g; c.fillRect(0, 0, w, h);
    var hg = c.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * .45); hg.addColorStop(0, "rgba(255,122,26,.35)"); hg.addColorStop(1, "rgba(255,122,26,0)"); c.fillStyle = hg; c.fillRect(0, 0, w, h);
    var spd = 7, L = 4.2, base = t * spd, k0 = Math.floor(base / L), off = base - k0 * L, N = 16, k, z;
    function P(x, y, zz) { return [cx + x * f / zz, cy - y * f / zz]; }
    c.strokeStyle = "rgba(250,204,21,.55)"; c.lineWidth = 2; c.beginPath();
    for (k = N; k >= 0; k--) { z = k * L - off + 1.2; if (z < .8) continue; var a = P(0, -1.6, z), b = P(0, -1.6, z + L * .45); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); } c.stroke();
    for (k = N; k >= 0; k--) { z = k * L - off + 1.2; if (z < .55) continue; var sg = o.seg[(k0 + k) % 64]; c.globalAlpha = Math.max(0, Math.min(1, 1.3 - z / (N * L * .8)));
      for (var sd = -1; sd <= 1; sd += 2) { var n = sd < 0 ? sg[0] : sg[1];
        for (var j = 0; j < n; j++) { var col = sg[2 + ((j + (sd > 0 ? 1 : 0)) % 4)], xi = sd * 2.3, xo = sd * 4.9, y0 = -1.6 + j * 1.05, y1 = y0 + 1, z1 = z + L * .92;
          poly(c, [P(xi, y0, z), P(xi, y0, z1), P(xi, y1, z1), P(xi, y1, z)], shade(col, .95));
          poly(c, [P(xi, y0, z), P(xo, y0, z), P(xo, y1, z), P(xi, y1, z)], shade(col, .66));
          c.strokeStyle = "rgba(0,0,0,.25)"; c.lineWidth = 1; c.beginPath(); for (var q = 1; q < 6; q++) { var zz = z + (z1 - z) * q / 6, a1 = P(xi, y0, zz), b1 = P(xi, y1, zz); c.moveTo(a1[0], a1[1]); c.lineTo(b1[0], b1[1]); } c.stroke(); } }
      if (sg[6]) { c.strokeStyle = "#C2410C"; c.lineWidth = Math.max(1.5, f / z * .2); var l1 = P(-5.6, -1.6, z), l2 = P(-5.6, 4.8, z), r1 = P(5.6, -1.6, z), r2 = P(5.6, 4.8, z);
        c.beginPath(); c.moveTo(l1[0], l1[1]); c.lineTo(l2[0], l2[1]); c.lineTo(r2[0], r2[1]); c.lineTo(r1[0], r1[1]); c.stroke(); }
      if ((k0 + k) % 2 === 0) { var lp = P(0, 3.4, z + L * .5), rad = Math.max(2, f / z * 1.3), lg = c.createRadialGradient(lp[0], lp[1], 0, lp[0], lp[1], rad);
        lg.addColorStop(0, "rgba(255,186,90,.9)"); lg.addColorStop(1, "rgba(255,140,40,0)"); c.fillStyle = lg; c.beginPath(); c.arc(lp[0], lp[1], rad, 0, 7); c.fill(); } }
    c.globalAlpha = 1; } };
S.synth = { init: function (o) { var r = rng(19); o.st = []; for (var i = 0; i < 110; i++) o.st.push([r(), r() * .5, r() * 6.3]);
    var R = Math.max(20, Math.round(Math.min(o.h * .3, o.w * .2))); o.R = R; var sc = doc.createElement("canvas"); sc.width = R * 2; sc.height = R * 2; var s = sc.getContext("2d");
    var g = s.createLinearGradient(0, 0, 0, R * 2); g.addColorStop(0, "#FFE66D"); g.addColorStop(.55, "#FF8AC8"); g.addColorStop(1, "#FF2E97"); s.fillStyle = g; s.beginPath(); s.arc(R, R, R, 0, 7); s.fill();
    s.globalCompositeOperation = "destination-out"; for (var k = 0; k < 7; k++) s.fillRect(0, R * (1.02 + k * .14), R * 2, R * (.02 + k * .013)); o.sun = sc; o.hs = [r() * 10, r() * 10]; },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, wd = wide(o), hz = h * .56, cx = wd ? w * .72 : w * .5, i;
    var g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, "#0D0221"); g.addColorStop(.5, "#2B0B4F"); g.addColorStop(.86, "#7A1E6E"); g.addColorStop(1, "#FF2E97"); c.fillStyle = g; c.fillRect(0, 0, w, hz + 1);
    c.fillStyle = "#fff"; for (i = 0; i < o.st.length; i++) { var s = o.st[i]; c.globalAlpha = .3 + .7 * Math.abs(Math.sin(t * .8 + s[2])); c.fillRect(s[0] * w, s[1] * h, 1.3, 1.3); } c.globalAlpha = 1;
    var R = o.R, sy = hz - R * .5, gl = c.createRadialGradient(cx, sy, R * .6, cx, sy, R * 2.2); gl.addColorStop(0, "rgba(255,46,151,.45)"); gl.addColorStop(1, "rgba(255,46,151,0)"); c.fillStyle = gl; c.fillRect(0, 0, w, hz);
    c.drawImage(o.sun, cx - R, sy - R); c.fillStyle = "#0E0322"; c.fillRect(0, hz, w, h - hz);
    var rows = 26, dz = .55, spd = 2.2, ti = Math.floor(t * spd / dz), off = (t * spd) % dz, f = h * .95, camY = .62, prev = null;
    function Hf(xw, zw, z) { var ax = Math.abs(xw); if (ax < 1.3) return 0; var k = Math.min(1, Math.max(0, (z - 1.6) / 4)); return Math.min(ax - 1.3, 2.6) * .42 * k * (.7 + .3 * Math.sin(xw * 1.7 + zw * .9 + o.hs[0]) + .2 * Math.sin(zw * 2.3 - xw * .7 + o.hs[1])); }
    for (var j = rows; j >= 0; j--) { var z = 1 + j * dz - off, zw = (j + ti) * dz, pts = [];
      for (var xw = -9; xw <= 9.01; xw += .45) pts.push([cx + xw * f / z, hz + (camY - Hf(xw, zw, z)) * f / z * .9]);
      var a = 1 - j / rows;
      c.beginPath(); c.moveTo(pts[0][0], h); pts.forEach(function (p) { c.lineTo(p[0], p[1]); }); c.lineTo(pts[pts.length - 1][0], h); c.closePath(); c.fillStyle = "#0E0322"; c.fill();
      c.strokeStyle = "rgba(255,46,151," + (.15 + .75 * a).toFixed(2) + ")"; c.lineWidth = 1 + a; c.beginPath(); pts.forEach(function (p, q) { q ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]); }); c.stroke();
      if (prev) { c.strokeStyle = "rgba(0,240,255," + (.08 + .45 * a).toFixed(2) + ")"; c.lineWidth = 1; c.beginPath(); for (var q = 0; q < pts.length; q += 2) { c.moveTo(prev[q][0], prev[q][1]); c.lineTo(pts[q][0], pts[q][1]); } c.stroke(); }
      prev = pts; } } };
S.galaxie = { init: function (o) { var r = rng(20), N = Math.min(3200, Math.max(1200, Math.round(o.w * o.h / 110))); o.P = [];
    for (var i = 0; i < N; i++) { var arm = i % 3, d = Math.pow(r(), 1.7), sp = (r() - .5) * .55 * (1.15 - d), ang = arm * 2.094 + d * 5.8 + sp, y = (r() - .5) * .08 * (1.1 - d) + (r() - .5) * .02;
      o.P.push([Math.cos(ang) * d, y, Math.sin(ang) * d, d, r()]); }
    o.cols = ["#FFF7E0", "#FDE68A", "#F9A8D4", "#C4B5FD", "#A78BFA", "#818CF8", "#60A5FA"]; o.ry = o.ry || 0; o.rx = 1.1;
    o.neb = []; for (i = 0; i < 9; i++) { var d2 = .25 + r() * .6, a2 = (i % 3) * 2.094 + d2 * 5.8; o.neb.push([Math.cos(a2) * d2, Math.sin(a2) * d2, .18 + r() * .2, i % 2 ? "167,139,250" : "240,171,252"]); } },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, wd = wide(o), cx = wd ? w * .74 : w * .5, cy = h * .5, R = wd ? h * 1.1 : Math.min(w, h) * .55;
    c.fillStyle = "#03020A"; c.fillRect(0, 0, w, h);
    var tx = o.mx > -1e3 ? (o.mx / w - .5) : 0, ty = o.my > -1e3 ? (o.my / h - .5) * .7 : 0; o.ry += .0018 + tx * .012; o.rx += ((1.1 + ty) - o.rx) * .05;
    var cr = Math.cos(o.ry), sr = Math.sin(o.ry), ct = Math.cos(o.rx), stt = Math.sin(o.rx);
    var g = c.createRadialGradient(cx, cy, 0, cx, cy, R * .38); g.addColorStop(0, "rgba(255,240,210,.6)"); g.addColorStop(.4, "rgba(196,181,253,.2)"); g.addColorStop(1, "rgba(124,58,237,0)"); c.fillStyle = g; c.fillRect(0, 0, w, h);
    c.globalCompositeOperation = "lighter";
    o.neb.forEach(function (q) { var x = q[0] * cr - q[1] * sr, z = q[0] * sr + q[1] * cr, y = -z * stt, zz = z * ct, s = 1 / (1.6 + zz * .9), X = cx + x * R * s * 1.6, Y = cy + y * R * s * 1.6, rad = q[2] * R * s * 1.6;
      var ng = c.createRadialGradient(X, Y, 0, X, Y, rad); ng.addColorStop(0, "rgba(" + q[3] + ",.16)"); ng.addColorStop(1, "rgba(" + q[3] + ",0)"); c.fillStyle = ng; c.beginPath(); c.arc(X, Y, rad, 0, 7); c.fill(); });
    for (var i = 0; i < o.P.length; i++) { var p = o.P[i], x = p[0] * cr - p[2] * sr, z = p[0] * sr + p[2] * cr, y = p[1] * ct - z * stt, zz = p[1] * stt + z * ct, s = 1 / (1.6 + zz * .9);
      var X = cx + x * R * s * 1.6, Y = cy + y * R * s * 1.6; if (X < -4 || X > w + 4 || Y < -4 || Y > h + 4) continue;
      c.globalAlpha = Math.min(1, .25 + (1 - p[3]) * .6 + p[4] * .2); c.fillStyle = o.cols[Math.min(6, Math.floor(p[3] * 7))]; var sz = (1.2 + (1 - p[3]) * 1.4) * s * 1.35; c.fillRect(X, Y, sz, sz); }
    c.globalAlpha = 1; c.globalCompositeOperation = "source-over"; } };
S.avions = { init: function (o) { var r = rng(21), i; o.pl = []; for (i = 0; i < 6; i++) o.pl.push({ a: .26 + r() * .18, b: .12 + r() * .14, s: .16 + r() * .12, ph: r() * 6.3, z: .55 + r() * .6, cy: .32 + r() * .36, tr: [] });
    o.cl = []; for (i = 0; i < 7; i++) o.cl.push([r(), .08 + r() * .7, .6 + r() * .9, .2 + r() * .5]); },
  frame: function (o, t) { var c = o.ctx, w = o.w, h = o.h, wd = wide(o), x0 = wd ? w * .42 : 0, cw = w - x0, i;
    var g = c.createLinearGradient(0, 0, 0, h); g.addColorStop(0, "#CFE3F7"); g.addColorStop(1, "#F4F9FE"); c.fillStyle = g; c.fillRect(0, 0, w, h);
    var sg = c.createRadialGradient(w * .86, h * .1, 0, w * .86, h * .1, Math.max(w, h) * .5); sg.addColorStop(0, "rgba(255,232,194,.8)"); sg.addColorStop(1, "rgba(255,232,194,0)"); c.fillStyle = sg; c.fillRect(0, 0, w, h);
    for (i = 0; i < o.cl.length; i++) { var cl = o.cl[i], ccx = ((cl[0] * (w + 300) + t * 9 * cl[3]) % (w + 300)) - 150, ccy = cl[1] * h, sc = cl[2] * Math.min(h, 400) * .12;
      c.fillStyle = "rgba(255,255,255,.88)"; [[0, 0, 1], [.85, .18, .75], [-.85, .22, .7], [.3, -.38, .66]].forEach(function (q) { c.beginPath(); c.arc(ccx + q[0] * sc, ccy + q[1] * sc, sc * q[2], 0, 7); c.fill(); }); }
    for (i = 0; i < o.pl.length; i++) { var p = o.pl[i], u = t * p.s + p.ph, X = x0 + cw * (.5 + p.a * Math.sin(u)), Y = h * (p.cy + p.b * Math.sin(2 * u)), dX = cw * p.a * Math.cos(u), dY = h * p.b * 2 * Math.cos(2 * u), ang = Math.atan2(dY, dX), S2 = p.z * Math.min(h * .14, 34) * (1 + .15 * Math.sin(u * 3));
      p.tr.push([X, Y]); if (p.tr.length > 46) p.tr.shift();
      c.strokeStyle = "rgba(15,111,222,.3)"; c.setLineDash([3, 5]); c.lineWidth = 1.4; c.beginPath(); p.tr.forEach(function (q, k) { k ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]); }); c.stroke(); c.setLineDash([]);
      c.save(); c.translate(X, Y); c.rotate(ang); c.scale(S2 / 30, S2 / 30);
      c.shadowColor = "rgba(14,34,56,.25)"; c.shadowBlur = 8; c.shadowOffsetY = 6; poly(c, [[-30, -14], [30, 0], [-14, 1]], "#FFFFFF"); c.shadowColor = "transparent";
      poly(c, [[-14, 1], [30, 0], [-24, 14]], "#E2E8F0"); poly(c, [[-14, 1], [-24, 14], [-10, 7]], "#CBD5E1");
      c.strokeStyle = "rgba(100,116,139,.6)"; c.lineWidth = 1; c.beginPath(); c.moveTo(-30, -14); c.lineTo(30, 0); c.lineTo(-24, 14); c.stroke(); c.restore(); } } };
S.codes = { init: function (o) { var r = rng(22), fs = Math.max(11, Math.round(Math.min(o.h / 16, 15))); o.fs = fs; o.cols = [];
    o.src = "8544499090 8537100090 3926909290 401-070-3444-A 803890972 1532209 175KG DUM BL NGP TANGER 7326909990 8538900090 ";
    var n = Math.ceil(o.w / (fs * .9)); for (var i = 0; i < n; i++) o.cols.push({ y: -r() * o.h, v: (34 + r() * 70) * (fs / 13), k: Math.floor(r() * o.src.length), L: r() < .12 ? 2 : (r() < .5 ? 1 : 0) }); o.clear = true; },
  frame: function (o, t, dt) { var c = o.ctx, w = o.w, h = o.h, fs = o.fs, i;
    c.font = "600 " + fs + "px 'JetBrains Mono', 'IBM Plex Mono', monospace"; c.textBaseline = "top";
    if (o.clear || !dt) { c.fillStyle = "#020604"; c.fillRect(0, 0, w, h); o.clear = false;
      if (!dt) { for (i = 0; i < o.cols.length; i++) for (var yy = 0; yy < h; yy += fs) { c.fillStyle = Math.random() < .08 ? "rgba(251,191,36,.6)" : "rgba(34,197,94," + (.15 + Math.random() * .45).toFixed(2) + ")"; c.fillText(o.src[(i * 7 + yy) % o.src.length], i * fs * .9, yy); } return; } }
    c.fillStyle = "rgba(2,6,4,.07)"; c.fillRect(0, 0, w, h);
    for (i = 0; i < o.cols.length; i++) { var cl = o.cols[i], x = i * fs * .9, ny = cl.y + cl.v * dt;
      if (Math.floor(ny / fs) > Math.floor(cl.y / fs)) { var yv = Math.floor(ny / fs) * fs; c.fillStyle = cl.L === 2 ? "#FDE68A" : "#D1FAE5"; c.fillText(o.src[cl.k % o.src.length], x, yv);
        c.fillStyle = cl.L === 2 ? "rgba(251,191,36,.8)" : (cl.L ? "rgba(34,197,94,.9)" : "rgba(21,128,61,.75)"); c.fillText(o.src[(cl.k + o.src.length - 1) % o.src.length], x, yv - fs); cl.k++; }
      cl.y = ny; if (cl.y > h + fs * 3) { cl.y = -Math.random() * h * .5; cl.L = Math.random() < .12 ? 2 : (Math.random() < .5 ? 1 : 0); } } } };
var VS2 = "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}";
var FS2 = "precision mediump float;uniform vec2 r;uniform float t;uniform vec2 m;" +
  "float fld(vec2 p){float as=r.x/r.y;vec2 c0=vec2((as>2.6?.74:.5)*as,.5);float sx=min(.85,as*.3);float k=min(1.,as*1.25);float f=0.;for(int i=0;i<7;i++){float fi=float(i);" +
  "vec2 c=c0+vec2(sx*sin(t*.31*(1.+fi*.17)+fi*1.9),.26/k*cos(t*.27*(1.+fi*.13)+fi*2.7));float rd=(.15+.04*sin(fi*3.1+t*.6))*k;vec2 q=p-c;f+=exp(-dot(q,q)/(rd*rd));}" +
  "vec2 mq=p-vec2(m.x*as,m.y);f+=.9*exp(-dot(mq,mq)/.005);return f;}" +
  "float hgt(vec2 p){return sqrt(max(fld(p)-.45,0.));}" +
  "void main(){vec2 uv=gl_FragCoord.xy/r;float as=r.x/r.y;vec2 p=vec2(uv.x*as,uv.y);float f=fld(p);float h=sqrt(max(f-.45,0.));float e=.003;" +
  "vec2 g=vec2(hgt(p+vec2(e,0.))-hgt(p-vec2(e,0.)),hgt(p+vec2(0.,e))-hgt(p-vec2(0.,e)))/(2.*e);vec3 n=normalize(vec3(-g*.22,1.));vec3 rf=reflect(vec3(0.,0.,-1.),n);" +
  "float sky=rf.y*.5+.5;vec3 env=mix(vec3(.05,.05,.07),vec3(.97,.98,1.),smoothstep(.35,.9,sky));env=mix(env,vec3(.14,.14,.18),smoothstep(.55,.45,sky)*.75);" +
  "env=mix(env,vec3(.82,.84,.9),pow(max(rf.z,0.),5.)*.55);env+=vec3(1.,.45,.85)*pow(max(0.,rf.x),3.)*.5+vec3(.3,.75,1.)*pow(max(0.,-rf.x),3.)*.5;" +
  "float ins=smoothstep(0.,.035,h);vec3 bg=mix(vec3(.035,.035,.045),vec3(.075,.07,.09),uv.y);bg+=vec3(.9,.5,1.)*.05*exp(-8.*dot(uv-vec2(.74,.2),uv-vec2(.74,.2)));" +
  "vec3 col=mix(bg,env,ins);col+=vec3(.75,.6,1.)*.16*smoothstep(.12,.45,f)*(1.-ins);gl_FragColor=vec4(col,1.);}";
S.chrome = { gl: true, dprCap: .75,
  init: function (o) { if (o.fail) return; if (!o.g) { var gl = o.cv.getContext("webgl", { antialias: false }); if (!gl) { o.fail = true; return; }
      function sh(ty, src) { var x = gl.createShader(ty); gl.shaderSource(x, src); gl.compileShader(x); return x; }
      var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS2)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS2)); gl.linkProgram(pr); if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { o.fail = true; return; }
      gl.useProgram(pr); var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      var loc = gl.getAttribLocation(pr, "a"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      o.g = gl; o.u = { r: gl.getUniformLocation(pr, "r"), t: gl.getUniformLocation(pr, "t"), m: gl.getUniformLocation(pr, "m") }; o.sm = [.5, .5]; }
    o.g.viewport(0, 0, o.cv.width, o.cv.height); },
  frame: function (o, t) { if (o.fail || !o.g) return; var gl = o.g, tm = o.mx > -1e3 ? [o.mx / o.w, 1 - o.my / o.h] : [-5, -5];
    o.sm[0] += (tm[0] - o.sm[0]) * .08; o.sm[1] += (tm[1] - o.sm[1]) * .08; gl.uniform2f(o.u.r, o.cv.width, o.cv.height); gl.uniform1f(o.u.t, t); gl.uniform2f(o.u.m, o.sm[0], o.sm[1]); gl.drawArrays(gl.TRIANGLES, 0, 3); } };
S.flux = { init: function (o) { var r = rng(24), N = Math.min(1800, Math.max(500, Math.round(o.w * o.h / 260))); o.P = []; for (var i = 0; i < N; i++) o.P.push([r() * o.w, r() * o.h, r() * 200]); o.r = r; o.clear = true; },
  frame: function (o, t, dt) { var c = o.ctx, w = o.w, h = o.h, i;
    if (o.clear || !dt) { c.fillStyle = "#061018"; c.fillRect(0, 0, w, h); o.clear = false; }
    c.fillStyle = "rgba(6,16,24,.05)"; c.fillRect(0, 0, w, h);
    var sc = .0035 * (900 / Math.max(500, w)), steps = dt ? 1 : 60, A = new Path2D(), B = new Path2D();
    for (var st = 0; st < steps; st++) for (i = 0; i < o.P.length; i++) { var p = o.P[i], x = p[0], y = p[1];
      var a = Math.sin(x * sc + t * .12) * 2.2 + Math.cos(y * sc * 1.3 - t * .1) * 2.2 + Math.sin((x + y) * sc * .6) * 1.4;
      if (o.mx > -1e3) { var dx = x - o.mx, dy = y - o.my, d2 = dx * dx + dy * dy; if (d2 < 22000) a += (1 - d2 / 22000) * 2.4; }
      var nx = x + Math.cos(a) * 1.4, ny = y + Math.sin(a) * 1.4, P2 = Math.sin(a * 1.7) > -.45 ? A : B; P2.moveTo(x, y); P2.lineTo(nx, ny);
      p[0] = nx; p[1] = ny; p[2] -= 1; if (p[2] < 0 || nx < 0 || nx > w || ny < 0 || ny > h) { p[0] = o.r() * w; p[1] = o.r() * h; p[2] = 80 + o.r() * 200; } }
    c.lineWidth = 1; c.strokeStyle = "rgba(45,212,191,.6)"; c.stroke(A); c.strokeStyle = "rgba(245,184,65,.55)"; c.stroke(B); } };
/* ---------- montage des scènes ---------- */
var scenes = [];
function unmount(slot) { for (var i = scenes.length - 1; i >= 0; i--) if (scenes[i].slot === slot) { var o = scenes[i]; o.ro.disconnect(); o.io.disconnect(); if (o.cv) o.cv.remove(); scenes.splice(i, 1); } }
function mount() {
  doc.querySelectorAll(".scene-slot").forEach(function (slot) {
    var name = null; slot.className.split(/\s+/).forEach(function (k) { if (k.indexOf("scene-") === 0 && S[k.slice(6)]) name = k.slice(6); });
    var cur = slot.getAttribute("data-m");
    if (cur === name) return;
    if (cur) unmount(slot);                                       /* Streamlit a réutilisé l'élément pour un autre design */
    if (!name) { slot.removeAttribute("data-m"); return; }
    slot.setAttribute("data-m", name);
    var s = S[name], o = { slot: slot, s: s, name: name, vis: true, w: 0, h: 0, mx: -1e4, my: -1e4 };
    o.static = RM || (cfg.heavy.indexOf(name) >= 0 && W.innerWidth < 760);
    if (!s.noCanvas) { o.cv = doc.createElement("canvas"); slot.prepend(o.cv); if (!s.gl) o.ctx = o.cv.getContext("2d"); }
    function rs() { var r = slot.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return; o.w = r.width; o.h = r.height;
      if (o.cv) { var dpr = Math.min(s.dprCap || 1.5, W.devicePixelRatio || 1); o.cv.width = Math.round(o.w * dpr); o.cv.height = Math.round(o.h * dpr); if (o.ctx) o.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
      if (s.init) s.init(o); if (o.static) s.frame(o, 7.3, 0); }
    o.ro = new W.ResizeObserver(rs); o.ro.observe(slot);
    o.io = new W.IntersectionObserver(function (es) { es.forEach(function (e) { o.vis = e.isIntersecting; }); }, { rootMargin: "80px" }); o.io.observe(slot);
    scenes.push(o);
  });
}
var last = W.performance.now();
function loop(now) { var t = now / 1000, dt = Math.min(.05, (now - last) / 1000); last = now;
  if (!doc.hidden) { for (var i = scenes.length - 1; i >= 0; i--) { var o = scenes[i];
      if (!doc.contains(o.slot)) { o.ro.disconnect(); o.io.disconnect(); scenes.splice(i, 1); continue; }
      if (o.vis && !o.static && o.w > 0) { var r = o.slot.getBoundingClientRect(); o.mx = mouse.x - r.left; o.my = mouse.y - r.top; if (o.mx < 0 || o.my < 0 || o.mx > o.w || o.my > o.h) { o.mx = -1e4; o.my = -1e4; } o.s.frame(o, t, dt); } }
    if (comet) cometDraw(now); if (sky) starsDraw(t, dt);
    if (spot && !spotIn) { spot.style.setProperty("--x", (50 + 35 * Math.sin(t * .5)) + "%"); spot.style.setProperty("--y", (50 + 30 * Math.sin(t * .7)) + "%"); } }
  W.requestAnimationFrame(loop); }

/* ---------- animations ---------- */
function on(k) { return cfg.anims.indexOf(k) >= 0; }
function counters() { if (!on("C")) return;
  doc.querySelectorAll(".ph-stat b:not([data-c])").forEach(function (el) { el.setAttribute("data-c", "1"); var txt = el.textContent, m = txt.match(/^([\d\s  ]+)(?:,(\d+))?(.*)$/); if (!m) return;
    var to = parseFloat(m[1].replace(/[\s  ]/g, "") + (m[2] ? "." + m[2] : "")), dec = m[2] ? m[2].length : 0, rest = m[3], t0 = W.performance.now(); if (!isFinite(to)) return;
    (function stp(now) { var p = Math.min(1, (now - t0) / 1100), e = 1 - Math.pow(1 - p, 3); el.textContent = (to * e).toLocaleString("fr-FR", { minimumFractionDigits: dec, maximumFractionDigits: dec }) + rest; if (p < 1) W.requestAnimationFrame(stp); else el.textContent = txt; })(t0); }); }
function burst(x, y) { var box = doc.createElement("div"); box.style.cssText = "position:fixed;left:0;top:0;width:0;height:0;z-index:99999;pointer-events:none";
  var cols = ["#3B82F6", "#F59E0B", "#22C55E", "#E879F9", "#38BDF8", "#F97316"];
  box.innerHTML = '<svg width="56" height="56" viewBox="0 0 66 66" style="position:fixed;left:' + (x - 28) + 'px;top:' + (y - 72) + 'px"><circle cx="33" cy="33" r="30" fill="rgba(10,16,32,.85)" stroke="#22C55E" stroke-width="4" stroke-dasharray="190" stroke-dashoffset="190"><animate attributeName="stroke-dashoffset" to="0" dur=".45s" fill="freeze"/></circle><path d="M20 34 l9 9 l17 -19" fill="none" stroke="#22C55E" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="50" stroke-dashoffset="50"><animate attributeName="stroke-dashoffset" to="0" begin=".35s" dur=".3s" fill="freeze"/></path></svg>';
  for (var i = 0; i < 26; i++) { var p = doc.createElement("i"), a = Math.random() * 6.28, d = 60 + Math.random() * 90; p.style.cssText = "position:fixed;left:" + x + "px;top:" + y + "px;width:7px;height:11px;border-radius:2px;background:" + cols[i % 6] + ";transition:transform 1s cubic-bezier(.15,.7,.3,1),opacity 1s;opacity:1"; box.appendChild(p);
    (function (p, a, d) { W.requestAnimationFrame(function () { W.requestAnimationFrame(function () { p.style.transform = "translate(" + Math.cos(a) * d + "px," + (Math.sin(a) * d - 40) + "px) rotate(" + (Math.random() * 540) + "deg)"; p.style.opacity = "0"; }); }); })(p, a, d); }
  doc.body.appendChild(box); W.setTimeout(function () { box.remove(); }, 1400); }
doc.addEventListener("click", function (e) { if (!on("F")) return; var b = e.target.closest && e.target.closest('[data-testid="stDownloadButton"] button'); if (b) burst(e.clientX, e.clientY); }, true);
var tiltEl = null;
function onMove(e) {
  if (on("J")) { var el = e.target.closest && e.target.closest(".ph-stat, div[class*='st-key-card']"); if (tiltEl && tiltEl !== el) { tiltEl.style.transform = ""; tiltEl = null; }
    if (el) { var r = el.getBoundingClientRect(), mx = (e.clientX - r.left) / r.width - .5, my = (e.clientY - r.top) / r.height - .5, k = el.classList.contains("ph-stat") ? 14 : 3;
      el.style.transition = "transform .12s"; el.style.transform = "perspective(800px) rotateX(" + (-my * k).toFixed(2) + "deg) rotateY(" + (mx * k).toFixed(2) + "deg)"; tiltEl = el; } }
  if (on("M")) { doc.querySelectorAll('[data-testid^="stBaseButton-primary"], .stDownloadButton button').forEach(function (b) { var r = b.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2, dx = e.clientX - cx, dy = e.clientY - cy, d = Math.hypot(dx, dy), lim = Math.max(r.width, r.height) * .7 + 40;
      b.style.transition = "transform .25s cubic-bezier(.2,.8,.2,1)"; b.style.transform = d < lim ? "translate(" + Math.max(-10, Math.min(10, dx * .18)).toFixed(1) + "px," + Math.max(-8, Math.min(8, dy * .25)).toFixed(1) + "px)" : ""; }); }
  if (spot) { spotIn = true; spot.style.setProperty("--x", e.clientX + "px"); spot.style.setProperty("--y", e.clientY + "px"); W.clearTimeout(spotT); spotT = W.setTimeout(function () { spotIn = false; }, 2500); }
}
W.addEventListener("pointermove", function (e) { mouse.x = e.clientX; mouse.y = e.clientY; onMove(e); cardLight(e);
  if (comet) { cpts.push({ x: e.clientX, y: e.clientY, t: W.performance.now() }); if (cpts.length > 40) cpts.shift(); } }, { passive: true });
doc.addEventListener("pointerout", function (e) { if (!e.relatedTarget && uEl) { uEl.style.removeProperty("--tz-u"); uEl = null; } });
var spot = null, spotIn = false, spotT = 0;
function spotlight() { if (on("L") && !spot) { spot = doc.createElement("div"); spot.id = "tz-spot";
    spot.style.cssText = "position:fixed;inset:0;z-index:2;pointer-events:none;background-image:radial-gradient(rgba(125,211,252,.55) 1.1px,transparent 1.5px);background-size:16px 16px;" +
      "-webkit-mask-image:radial-gradient(150px 150px at var(--x,50%) var(--y,50%),#000 10%,transparent 100%);mask-image:radial-gradient(150px 150px at var(--x,50%) var(--y,50%),#000 10%,transparent 100%);mix-blend-mode:screen";
    doc.body.appendChild(spot); }
  if (!on("L") && spot) { spot.remove(); spot = null; } }
function clock() { var el = doc.getElementById("tz-clock"), html = doc.documentElement; ["tz-matin", "tz-jour", "tz-soir", "tz-nuit"].forEach(function (k) { html.classList.remove(k); });
  if (!on("N")) { if (el) el.remove(); return; }
  var txt = "", hh = 12; try { txt = new Intl.DateTimeFormat("fr-FR", { timeZone: "Africa/Casablanca", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date()); hh = parseInt(txt, 10); } catch (e) {}
  var p = hh >= 20 || hh < 6 ? ["tz-nuit", "nuit"] : hh >= 17 ? ["tz-soir", "coucher de soleil"] : hh >= 11 ? ["tz-jour", "journée"] : ["tz-matin", "matin"];
  html.classList.add(p[0]); if (!el) { el = doc.createElement("div"); el.id = "tz-clock"; doc.body.appendChild(el); } el.textContent = "Tanger " + txt + " · " + p[1]; }
function intro() { if (!on("K")) return; try { if (W.sessionStorage.getItem("tz-intro")) return; W.sessionStorage.setItem("tz-intro", "1"); } catch (e) {}
  var ov = doc.createElement("div"); ov.style.cssText = "position:fixed;inset:0;z-index:100000;pointer-events:none;display:grid;place-items:center";
  ov.innerHTML = '<div style="position:absolute;inset:0 50% 0 0;background:#05080F;transition:transform .6s cubic-bezier(.7,0,.3,1) 1s"></div><div style="position:absolute;inset:0 0 0 50%;background:#05080F;transition:transform .6s cubic-bezier(.7,0,.3,1) 1s"></div>' +
    '<div style="position:relative;display:flex;gap:12px;align-items:center;color:#fff;font:800 26px Outfit,system-ui,sans-serif;transform:translateX(-160px);opacity:0;transition:transform .7s cubic-bezier(.2,.8,.2,1),opacity .5s">' +
    '<svg viewBox="0 0 64 30" width="64"><rect x="0" y="4" width="40" height="18" rx="2" fill="#E8590C"/><path d="M40 9 H52 L60 16 V22 H40 Z" fill="#3B82F6"/><circle cx="10" cy="24" r="4.5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/><circle cx="30" cy="24" r="4.5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/><circle cx="52" cy="24" r="4.5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/></svg>TIMAR Tanger</div>';
  doc.body.appendChild(ov); var kids = ov.children;
  W.requestAnimationFrame(function () { W.requestAnimationFrame(function () { kids[2].style.transform = "none"; kids[2].style.opacity = "1"; kids[0].style.transform = "translateX(-101%)"; kids[1].style.transform = "translateX(101%)";
    W.setTimeout(function () { kids[2].style.opacity = "0"; }, 950); }); });
  W.setTimeout(function () { ov.remove(); }, 1900); }
/* ---------- animations O à V ---------- */
function accent() { var v = W.getComputedStyle(doc.documentElement).getPropertyValue("--accent").trim(); return v || "#3B82F6"; }
function fullSize(cv) { if (!cv) return; var d = Math.min(2, W.devicePixelRatio || 1); cv.width = Math.round(W.innerWidth * d); cv.height = Math.round(W.innerHeight * d); cv.getContext("2d").setTransform(d, 0, 0, d, 0, 0); }
function layer(id, tag, css, z) { var el = doc.createElement(tag); el.id = id; el.style.cssText = "position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:" + z + ";" + (css || ""); doc.body.appendChild(el); return el; }
W.addEventListener("resize", function () { fullSize(comet); fullSize(sky); });
/* O : comète qui suit la souris */
var comet = null, cpts = [];
function cometToggle() { var want = on("O") && !RM; if (want && !comet) { comet = layer("tz-comet", "canvas", "", 99990); fullSize(comet); } if (!want && comet) { comet.remove(); comet = null; cpts = []; } }
function cometDraw(now) { var c = comet.getContext("2d"), i;
  cpts = cpts.filter(function (p) { return now - p.t < 420; });
  if (cpts.length < 2) { if (comet._d) { c.clearRect(0, 0, W.innerWidth, W.innerHeight); comet._d = false; } return; }
  c.clearRect(0, 0, W.innerWidth, W.innerHeight); comet._d = true; var col = accent();
  c.lineCap = "round"; c.strokeStyle = col; for (i = 1; i < cpts.length; i++) { var a = cpts[i - 1], b = cpts[i], k = i / cpts.length; c.globalAlpha = k * .85; c.lineWidth = .8 + k * 6; c.beginPath(); c.moveTo(a.x, a.y); c.lineTo(b.x, b.y); c.stroke(); }
  var hd = cpts[cpts.length - 1], g = c.createRadialGradient(hd.x, hd.y, 0, hd.x, hd.y, 16); g.addColorStop(0, "rgba(255,255,255,.9)"); g.addColorStop(1, "rgba(255,255,255,0)"); c.globalAlpha = 1; c.fillStyle = g; c.beginPath(); c.arc(hd.x, hd.y, 16, 0, 7); c.fill();
  c.fillStyle = col; for (i = 0; i < 3; i++) { c.globalAlpha = Math.random(); c.fillRect(hd.x + (Math.random() - .5) * 26, hd.y + (Math.random() - .5) * 26, 2, 2); } c.globalAlpha = 1; }
/* P : onde au clic */
doc.addEventListener("pointerdown", function (e) { if (!on("P") || RM) return; var d = doc.createElement("span");
  d.style.cssText = "position:fixed;left:" + e.clientX + "px;top:" + e.clientY + "px;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;border:2px solid " + accent() + ";z-index:99991;pointer-events:none";
  doc.body.appendChild(d); try { d.animate([{ transform: "scale(1)", opacity: .9 }, { transform: "scale(8)", opacity: 0 }], { duration: 650, easing: "cubic-bezier(.2,.8,.2,1)" }).onfinish = function () { d.remove(); }; } catch (x) { d.remove(); } }, true);
/* Q : titre de l'en-tête qui se décode */
var GLY = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789#%&";
function decode() { if (!on("Q")) return;
  doc.querySelectorAll(".ph h1").forEach(function (hh) { if (hh.__tzq) return; var txt = hh.textContent; if (hh.getAttribute("data-q") === txt) return; hh.setAttribute("data-q", txt); if (RM) return;
    var tw = doc.createTreeWalker(hh, 4), nodes = [], n; while ((n = tw.nextNode())) nodes.push([n, n.nodeValue, n.nodeValue]); if (!nodes.length) return; hh.__tzq = true;
    var total = nodes.reduce(function (s, x) { return s + x[1].length; }, 0), t0 = W.performance.now();
    function fin() { nodes.forEach(function (x) { if (x[0].nodeValue === x[2]) x[0].nodeValue = x[1]; }); hh.__tzq = false; hh.setAttribute("data-q", hh.textContent); }
    (function stp(now) { if (nodes.some(function (x) { return x[0].nodeValue !== x[2]; })) { fin(); return; }   /* Streamlit a changé le titre entre-temps */
      var p = Math.min(1, (now - t0) / 900), done = Math.floor(p * total), k = 0;
      nodes.forEach(function (x) { var src = x[1], out = ""; for (var i = 0; i < src.length; i++, k++) out += (k < done || /\s/.test(src[i])) ? src[i] : GLY[Math.floor(Math.random() * GLY.length)]; x[0].nodeValue = out; x[2] = out; });
      if (p < 1) W.requestAnimationFrame(stp); else fin(); })(t0); }); }
/* S : étoiles filantes en fond */
var sky = null, shoot = [], nextShoot = 0;
function starsToggle() { var want = on("S") && !RM; if (want && !sky) { sky = layer("tz-sky", "canvas", "", 0); fullSize(sky); } if (!want && sky) { sky.remove(); sky = null; shoot = []; } }
function starsDraw(t, dt) { var c = sky.getContext("2d"), w = W.innerWidth, h = W.innerHeight, rgb = cfg.light ? "15,111,222" : "255,255,255";
  if (t > nextShoot) { shoot.push({ x: w * (.35 + Math.random() * .75), y: -20 + Math.random() * h * .35, vx: -(380 + Math.random() * 260), vy: 160 + Math.random() * 120, life: 0 }); nextShoot = t + 1.6 + Math.random() * 3; }
  if (!shoot.length && !sky._d) return; c.clearRect(0, 0, w, h); sky._d = shoot.length > 0;
  shoot = shoot.filter(function (s) { return s.life < 1.4; });
  shoot.forEach(function (s) { s.life += dt; s.x += s.vx * dt; s.y += s.vy * dt; var tx = s.x - s.vx * .14, ty = s.y - s.vy * .14, a = Math.max(0, 1 - s.life / 1.4);
    var g = c.createLinearGradient(s.x, s.y, tx, ty); g.addColorStop(0, "rgba(" + rgb + "," + a + ")"); g.addColorStop(1, "rgba(" + rgb + ",0)"); c.strokeStyle = g; c.lineWidth = 2; c.beginPath(); c.moveTo(s.x, s.y); c.lineTo(tx, ty); c.stroke();
    c.fillStyle = "rgba(" + rgb + "," + a + ")"; c.beginPath(); c.arc(s.x, s.y, 1.8, 0, 7); c.fill(); }); }
/* T : conteneurs qui tombent quand un message de succès apparaît */
var CT = ["#E8590C", "#1C7ED6", "#2F9E44", "#F59F00", "#C92A2A", "#0E7490"], okSeen = {};
function successes() { var els = doc.querySelectorAll(".status-banner.status-ok:not([data-t]), [data-testid='stAlertContentSuccess']:not([data-t])"), fresh = false;
  els.forEach(function (el) { el.setAttribute("data-t", "1"); var k = el.textContent.trim().slice(0, 160); if (!okSeen[k]) { okSeen[k] = 1; fresh = true; } });
  if (fresh && on("T") && !RM) dropBoxes(); }
function dropBoxes() { if (doc.getElementById("tz-drop")) return; var box = doc.createElement("div"); box.id = "tz-drop"; box.style.cssText = "position:fixed;right:24px;bottom:0;width:230px;height:110px;z-index:99992;pointer-events:none"; doc.body.appendChild(box);
  var k = 0; for (var row = 0; row < 3; row++) for (var col = 0; col < 3 - row; col++) { var d = doc.createElement("i"), x = col * 74 + row * 37, y = 110 - (row + 1) * 34;
    d.style.cssText = "position:absolute;left:" + x + "px;top:" + y + "px;width:70px;height:32px;border-radius:2px;background:" + CT[k % 6] + " repeating-linear-gradient(90deg,rgba(0,0,0,.2) 0 2px,transparent 2px 7px);box-shadow:0 4px 8px rgba(0,0,0,.35)";
    box.appendChild(d); try { d.animate([{ transform: "translateY(-" + W.innerHeight + "px)" }, { transform: "translateY(0)", offset: .8 }, { transform: "translateY(-10px)", offset: .9 }, { transform: "translateY(0)" }], { duration: 900, delay: k * 120, easing: "cubic-bezier(.5,0,.75,0)", fill: "both" }); } catch (x) {} k++; }
  W.setTimeout(function () { try { box.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 500, fill: "forwards" }); } catch (x) {} }, 2800); W.setTimeout(function () { box.remove(); }, 3400); }
/* U : lumière qui suit la souris sur les cartes */
var uEl = null;
function cardLight(e) { if (!on("U")) { if (uEl) { uEl.style.removeProperty("--tz-u"); uEl = null; } return; }
  var cd = e.target.closest && e.target.closest("div[class*='st-key-card']"); if (uEl && uEl !== cd) { uEl.style.removeProperty("--tz-u"); uEl = null; }
  if (cd) { var rc = cd.getBoundingClientRect(); cd.style.setProperty("--mx", (e.clientX - rc.left).toFixed(0) + "px"); cd.style.setProperty("--my", (e.clientY - rc.top).toFixed(0) + "px"); cd.style.setProperty("--tz-u", "1"); uEl = cd; } }
/* V : fond qui respire */
function breathe() { var el = doc.getElementById("tz-breathe"); if (on("V") && !el) { el = doc.createElement("div"); el.id = "tz-breathe"; doc.body.appendChild(el); } if (!on("V") && el) el.remove(); }
var tmr = 0;
function scan() { W.clearTimeout(tmr); tmr = W.setTimeout(function () { mount(); counters(); decode(); successes(); }, 120); }
new W.MutationObserver(scan).observe(doc.body, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
W.__timarConfigure = function (c) { cfg = c; spotlight(); clock(); intro(); cometToggle(); starsToggle(); breathe(); mount(); counters(); decode(); };
W.requestAnimationFrame(loop);
})();
"""


def engine_html(theme: str) -> str:
    """Iframe invisible qui installe le moteur dans la page (une seule fois) puis lui passe le design et les animations choisis."""
    a = anims()
    cfg = {"theme": theme, "anims": a, "heavy": sorted(HEAVY), "light": is_light(theme)}
    src = json.dumps(ENGINE).replace("</", "<\\/")
    return ("<script>(function(){var P=window.parent,src=" + src + ";try{if(!P.__timarConfigure){var s=P.document.createElement('script');s.textContent=src;P.document.head.appendChild(s);}"
            "}catch(e){}if(!P.__timarConfigure){window.__timarHost=P;try{(new Function(src))();}catch(e){}}"
            "if(P.__timarConfigure)P.__timarConfigure(" + json.dumps(cfg) + ");})();</script>")


def needs_engine(theme: str) -> bool:
    s = spec(theme)
    return bool(s and (s[6] or s[5] == "holo")) or bool(set(anims()) & ENGINE_ANIMS)
