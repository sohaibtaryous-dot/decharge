# -*- coding: utf-8 -*-
"""Carte de connexion propre à chaque design (menu « Thème ») : à gauche un objet animé qu'on actionne pour faire apparaître
le formulaire (barrière du port, conteneur, passeport, phare…), et une carte aux formes et aux couleurs du design.

concept(theme) -> {"btn": (libellé fermé, libellé ouvert), "hint": …} ou None (design sans carte propre : lampe d'origine)
scene(theme, on) -> HTML de l'objet animé (état fermé / ouvert)
css(theme)       -> <style> de la carte + de l'objet du design
"""

from __future__ import annotations

import math

import ui_designs

# =============================================================================
# CARTE (commun à tous les designs)
# =============================================================================

COMMON_CSS = """
div.st-key-card_login { position: relative; overflow: hidden; padding: 1.4rem 1.6rem 1.2rem !important; border-radius: var(--lgr, 22px) !important;
  background: var(--lg-bg, var(--surface)) !important; border: 1px solid var(--lg-brd, var(--brd)) !important;
  box-shadow: 0 30px 70px -30px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.06) !important; animation: lgx-in .9s cubic-bezier(.2,.8,.2,1) both !important; }
@keyframes lgx-in { from { opacity: 0; transform: translateY(22px) scale(.97); filter: blur(8px); } to { opacity: 1; transform: none; filter: none; } }
div.st-key-card_login h3 { color: var(--ink) !important; font-family: var(--f-display) !important; }
div.st-key-card_login label p, div.st-key-card_login [data-testid="stWidgetLabel"] p { color: var(--ink2) !important; }
div.st-key-card_login [data-baseweb="input"], div.st-key-card_login [data-baseweb="base-input"] { background: var(--lg-field, rgba(255,255,255,.06)) !important;
  border: 1px solid var(--lg-brd, var(--brd)) !important; border-radius: var(--lgf, 12px) !important; }
div.st-key-card_login [data-baseweb="input"]:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 28%, transparent) !important; }
div.st-key-card_login input { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; background: transparent !important; }
div.st-key-card_login [data-testid^="stBaseButton-secondary"] { background: var(--lg-field, rgba(255,255,255,.06)) !important; border: 1px solid var(--lg-brd, var(--brd)) !important;
  border-radius: var(--lgf, 12px) !important; color: var(--ink) !important; transition: box-shadow .2s, border-color .2s; }
div.st-key-card_login [data-testid^="stBaseButton-secondary"]:hover { border-color: var(--accent) !important; box-shadow: 0 0 22px -6px var(--accent) !important; }
div.st-key-card_login [data-testid^="stBaseButton-secondary"] p { color: var(--ink) !important; }
div.st-key-card_login [data-testid^="stBaseButton-primary"] { border-radius: var(--lgf, 12px) !important; box-shadow: 0 10px 26px -12px var(--accent) !important; }
div.st-key-card_login .stTabs [role="tab"][aria-selected="true"] { box-shadow: inset 0 -2px 0 var(--accent) !important; }
.lgx { position: relative; height: 300px; display: grid; place-items: center; user-select: none; }
.lgx svg { overflow: visible; max-width: 100%; }
.lgx .stg { position: relative; width: 240px; height: 300px; }
.lgx-hint { text-align: center; font-size: .82rem; color: var(--ink3) !important; margin-top: .25rem; }
.lgx-ghost { opacity: .2; filter: blur(3px); pointer-events: none; }
.lgx-ghost h3, .lgx-ghost p { color: var(--ink) !important; }
.lgx-form { animation: lgx-form .7s .15s ease-out both; }
@keyframes lgx-form { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes lgx-rot { to { transform: rotate(360deg); } }
@keyframes lgx-float { 50% { transform: translateY(-8px); } }
@keyframes lgx-blink { 50% { opacity: .3; } }
@keyframes lgx-draw { to { stroke-dashoffset: 0; } }
@keyframes lgx-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes lgx-pop { from { opacity: 0; transform: scale(.4); } to { opacity: 1; transform: none; } }
@keyframes lgx-stamp { from { opacity: 0; transform: rotate(-12deg) scale(2.3); } to { opacity: .92; transform: rotate(-12deg) scale(1); } }
@property --lgx-a { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
@keyframes lgx-ang { to { --lgx-a: 360deg; } }
@media (prefers-reduced-motion: reduce) { .lgx *, .lgx *::before, .lgx *::after { animation-duration: .01s !important; animation-iteration-count: 1 !important; } }
"""

# bordure lumineuse qui tourne autour de la carte (designs 13, 19, 20, 24)
SPIN_BORDER = """
div.st-key-card_login::before { content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px; pointer-events: none; z-index: 0;
  background: conic-gradient(from var(--lgx-a), transparent 0 50%, var(--accent) 66%, var(--accent2) 78%, transparent 92%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);
  animation: lgx-ang 5s linear infinite; }
"""

# forme de la carte de chaque design (rayon, fond, motif, bordure)
CARD = {
    1: "--lgr: 22px; --lg-bg: radial-gradient(90% 70% at 15% 0%, rgba(14,165,233,.22), transparent 60%), linear-gradient(160deg, #0C1C36, #071226); --lg-brd: rgba(56,189,248,.32);",
    2: "--lgr: 28px; --lg-bg: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.03)); --lg-brd: rgba(255,255,255,.2);",
    3: "--lgr: 18px; --lg-bg: #FFFFFF; --lg-brd: #E2E8F0; --lg-field: #F8FAFC;",
    4: "--lgr: 3px; --lgf: 3px; --lg-bg: repeating-linear-gradient(90deg, #1F2226 0 22px, #23272C 22px 24px); --lg-brd: #3A3F46;",
    5: "--lgr: 20px; --lg-bg: radial-gradient(rgba(148,163,184,.16) 1px, transparent 1.3px) 0 0 / 10px 10px, linear-gradient(160deg, #0B1628, #060D1A); --lg-brd: rgba(245,158,11,.3);",
    6: "--lgr: 0px; --lgf: 2px; --lg-bg: linear-gradient(160deg, #070914, #04050B); --lg-brd: rgba(34,211,238,.5);",
    7: "--lgr: 4px; --lgf: 2px; --lg-bg: linear-gradient(rgba(31,58,44,.08) 1px, transparent 1px) 0 0 / 100% 26px, #F6F8F5; --lg-brd: #8FA394; --lg-field: #FFFFFF;",
    8: "--lgr: 0px; --lgf: 0px; --lg-bg: #FFFFFF; --lg-brd: #0C0A09; --lg-field: #FAFAF9;",
    9: "--lgr: 24px; --lg-bg: radial-gradient(80% 60% at 90% 0%, rgba(240,163,94,.22), transparent 60%), linear-gradient(170deg, #121A3D, #070A1C); --lg-brd: rgba(240,163,94,.3);",
    10: "--lgr: 12px; --lg-bg: radial-gradient(circle at 12px 12px, #2B4166 3px, transparent 3.5px), radial-gradient(circle at calc(100% - 12px) 12px, #2B4166 3px, transparent 3.5px), linear-gradient(160deg, #13203A, #0A101C); --lg-brd: #2B4166;",
    11: "--lgr: 18px; --lgf: 999px; --lg-bg: linear-gradient(160deg, #1F1A3D, #120F28); --lg-brd: rgba(249,115,22,.35);",
    12: "--lgr: 30px; --lg-bg: radial-gradient(60% 80% at 80% 20%, rgba(56,189,248,.14), transparent 60%), linear-gradient(160deg, #0A1222, #030712); --lg-brd: rgba(251,191,36,.28);",
    13: "--lgr: 20px; --lg-bg: radial-gradient(rgba(255,255,255,.25) .7px, transparent 1px) 0 0 / 23px 23px, linear-gradient(160deg, #0F1430, #040710); --lg-brd: rgba(99,102,241,.25);",
    14: "--lgr: 30px; --lg-bg: radial-gradient(70% 60% at 0% 100%, rgba(6,182,212,.2), transparent 60%), linear-gradient(160deg, rgba(10,24,44,.86), rgba(4,10,22,.8)); --lg-brd: rgba(165,243,252,.24);",
    15: "--lgr: 14px; --lgf: 6px; --lg-bg: repeating-linear-gradient(0deg, rgba(165,243,252,.04) 0 1px, transparent 1px 3px), linear-gradient(160deg, #071526, #02060E); --lg-brd: rgba(34,211,238,.45);",
    16: "--lgr: 6px; --lgf: 4px; --lg-bg: linear-gradient(160deg, #0F1B38, #040814); --lg-brd: rgba(234,179,8,.35);",
    17: "--lgr: 18px; --lg-bg: radial-gradient(70% 60% at 50% 0%, rgba(242,193,78,.16), transparent 60%), linear-gradient(170deg, #161A44, #0A0B1E); --lg-brd: rgba(242,193,78,.4);",
    18: "--lgr: 4px; --lgf: 3px; --lg-bg: linear-gradient(160deg, #1A1E24, #0B0D10); --lg-brd: #2E343C;",
    19: "--lgr: 10px; --lgf: 6px; --lg-bg: linear-gradient(rgba(255,46,151,.08) 1px, transparent 1px) 0 0 / 100% 22px, linear-gradient(90deg, rgba(0,240,255,.06) 1px, transparent 1px) 0 0 / 22px 100%, linear-gradient(170deg, #22094A, #0D0221); --lg-brd: rgba(255,46,151,.35);",
    20: "--lgr: 26px; --lg-bg: radial-gradient(rgba(255,255,255,.35) .7px, transparent 1px) 0 0 / 19px 19px, radial-gradient(80% 70% at 50% 50%, rgba(124,58,237,.22), transparent 70%), #05040F; --lg-brd: rgba(167,139,250,.25);",
    21: "--lgr: 20px; --lg-bg: #FFFFFF; --lg-brd: #D6E4F2; --lg-field: #F4F8FC;",
    22: "--lgr: 4px; --lgf: 2px; --lg-bg: repeating-linear-gradient(0deg, rgba(34,197,94,.05) 0 1px, transparent 1px 3px), #030A05; --lg-brd: rgba(34,197,94,.45);",
    23: "--lgr: 20px; --lg-bg: linear-gradient(160deg, #1C1C22, #0A0A0C); --lg-brd: rgba(226,232,240,.3);",
    24: "--lgr: 16px; --lg-bg: linear-gradient(160deg, #0C1A24, #061018); --lg-brd: rgba(45,212,191,.28);",
}

CARD_EXTRA = {
    14: "div.st-key-card_login { backdrop-filter: blur(18px) saturate(140%); -webkit-backdrop-filter: blur(18px) saturate(140%); }",
    3: "div.st-key-card_login::after { content: ''; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: linear-gradient(90deg, #1D4ED8, #60A5FA); }"
       "div.st-key-card_login { box-shadow: 0 24px 50px -28px rgba(15,23,42,.35) !important; }",
    4: "div.st-key-card_login::after { content: 'TIMU 803890 7 · 45G1 · MAX GROSS 30 480 KG'; position: absolute; right: 14px; top: 8px; font: 700 9px 'IBM Plex Mono', monospace;"
       " letter-spacing: .12em; color: rgba(255,169,77,.55); }",
    6: "div.st-key-card_login { clip-path: polygon(18px 0, calc(100% - 18px) 0, 100% 18px, 100% calc(100% - 18px), calc(100% - 18px) 100%, 18px 100%, 0 calc(100% - 18px), 0 18px);"
       " box-shadow: inset 0 0 0 1px rgba(34,211,238,.55), inset 0 0 40px -18px rgba(34,211,238,.7) !important; }",
    7: "div.st-key-card_login { outline: 1px dashed rgba(31,58,44,.35); outline-offset: -9px; box-shadow: 0 20px 40px -26px rgba(28,42,34,.45) !important; }",
    8: "div.st-key-card_login { box-shadow: 8px 8px 0 #0C0A09 !important; border-width: 2px !important; }",
    11: "div.st-key-card_login { -webkit-mask: radial-gradient(circle 18px at 0 50%, transparent 97%, #000) left / 51% 100% no-repeat, radial-gradient(circle 18px at 100% 50%, transparent 97%, #000) right / 51% 100% no-repeat;"
        " mask: radial-gradient(circle 18px at 0 50%, transparent 97%, #000) left / 51% 100% no-repeat, radial-gradient(circle 18px at 100% 50%, transparent 97%, #000) right / 51% 100% no-repeat; }",
    16: "div.st-key-card_login::after { content: ''; position: absolute; left: 0; right: 0; top: 0; height: 8px; background: repeating-linear-gradient(-45deg, #EAB308 0 12px, #111827 12px 24px); }",
    17: "div.st-key-card_login::after { content: ''; position: absolute; left: 0; right: 0; top: 0; height: 14px; opacity: .9;"
        " background: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='14' viewBox='0 0 28 14'%3E%3Crect width='28' height='14' fill='%230F3D3E'/%3E"
        "%3Cpath d='M14 1 L16.5 5 L21 7 L16.5 9 L14 13 L11.5 9 L7 7 L11.5 5 Z' fill='%23F2C14E'/%3E%3Ccircle cx='0' cy='7' r='3' fill='%231E6F6B'/%3E%3Ccircle cx='28' cy='7' r='3' fill='%231E6F6B'/%3E%3C/svg%3E\") repeat-x; }"
        "div.st-key-card_login { box-shadow: inset 0 0 0 3px rgba(242,193,78,.12), 0 30px 70px -30px rgba(0,0,0,.7) !important; }",
    18: "div.st-key-card_login::after { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #FF7A1A; box-shadow: 0 0 18px #FF7A1A; }",
    19: "div.st-key-card_login { box-shadow: 0 0 0 1px rgba(255,46,151,.35), 0 0 40px -10px rgba(255,46,151,.55), 0 0 80px -30px rgba(0,240,255,.5) !important; }",
    21: "div.st-key-card_login { clip-path: polygon(0 0, calc(100% - 34px) 0, 100% 34px, 100% 100%, 0 100%); box-shadow: 0 26px 50px -30px rgba(14,34,56,.4) !important; }"
        "div.st-key-card_login::after { content: ''; position: absolute; right: 0; top: 0; width: 34px; height: 34px; background: linear-gradient(225deg, transparent 50%, #DCE8F5 50%); box-shadow: -3px 3px 6px rgba(14,34,56,.12); }",
    22: "div.st-key-card_login { box-shadow: inset 0 0 0 1px rgba(34,197,94,.45), 0 0 40px -16px rgba(34,197,94,.6) !important; }"
        "div.st-key-card_login, div.st-key-card_login input, div.st-key-card_login p, div.st-key-card_login h3 { font-family: 'JetBrains Mono', 'IBM Plex Mono', monospace !important; }",
    23: "div.st-key-card_login::before { content: ''; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px; pointer-events: none;"
        " background: conic-gradient(from var(--lgx-a), #6B7280, #F9FAFB, #9CA3AF, #F0ABFC, #E5E7EB, #93C5FD, #6B7280);"
        " -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);"
        " animation: lgx-ang 7s linear infinite; }",
}
for _i in (13, 19, 20, 24):
    CARD_EXTRA[_i] = CARD_EXTRA.get(_i, "") + SPIN_BORDER


# =============================================================================
# OBJETS ANIMÉS (un par design)
# =============================================================================

def _ticks(cx, cy, r1, r2, n, every=0, r3=None, stroke="#7C8BA3"):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = r3 if (every and k % every == 0 and r3) else r1
        out.append(f'<line x1="{cx + rr * math.sin(a):.1f}" y1="{cy - rr * math.cos(a):.1f}" x2="{cx + r2 * math.sin(a):.1f}" y2="{cy - r2 * math.cos(a):.1f}"/>')
    return f'<g stroke="{stroke}" stroke-width="1.2">' + "".join(out) + "</g>"


def _gear(cx, cy, r, n):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        for da, rr in ((-.22, r), (.22, r), (math.pi / n - .1, r * .78), (math.pi / n + .32, r * .78)):
            pts.append(f"{cx + rr * math.cos(a + da):.1f},{cy + rr * math.sin(a + da):.1f}")
    return " ".join(pts)


def _fp_arcs():
    """Empreinte digitale : arcs concentriques ouverts (chacun « pathLength=100 » pour l'animation de tracé)."""
    out = []
    for k in range(10):
        rx, ry = 10 + k * 8.2, 14 + k * 9.4
        a0, a1 = math.radians(200 + (k % 3) * 12), math.radians(520 - (k % 4) * 14)
        x0, y0 = 120 + rx * math.cos(a0), 150 + ry * math.sin(a0)
        x1, y1 = 120 + rx * math.cos(a1), 150 + ry * math.sin(a1)
        large = 1 if (a1 - a0) > math.pi else 0
        out.append(f'<path pathLength="100" d="M{x0:.1f} {y0:.1f} A{rx:.1f} {ry:.1f} 0 {large} 1 {x1:.1f} {y1:.1f}" style="animation-delay:{k * .07:.2f}s"/>')
    return "".join(out)


TRUCK = ('<g class="truck"><rect x="0" y="206" width="58" height="24" rx="2" fill="#E8590C"/><rect x="58" y="212" width="18" height="18" rx="2" fill="#1C7ED6"/>'
         '<rect x="62" y="215" width="9" height="7" fill="#BFDBFE"/><circle cx="12" cy="232" r="5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/>'
         '<circle cx="44" cy="232" r="5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/><circle cx="68" cy="232" r="5" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/></g>')

V = {}

# 1 · barrière du port -------------------------------------------------------------------------------------------------------
V["port"] = (lambda on: f"""<div class="lgx lgx-port{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<defs><linearGradient id="pt-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E3A6B" stop-opacity="0"/><stop offset="1" stop-color="#0E3A6B" stop-opacity=".6"/></linearGradient></defs>
<rect x="0" y="50" width="240" height="186" rx="18" fill="url(#pt-sky)"/>
<g stroke="#2B5C93" stroke-width="2" fill="none" opacity=".85"><path d="M150 236 V118 H226 M150 118 L168 100 M196 118 V150"/><path d="M178 236 V142"/></g>
<circle cx="200" cy="80" r="2" fill="#fff" opacity=".7"/><circle cx="60" cy="70" r="1.5" fill="#fff" opacity=".6"/><circle cx="118" cy="62" r="1.3" fill="#fff" opacity=".5"/>
<rect x="0" y="236" width="240" height="40" fill="#0A1D38"/><line class="road" x1="-24" y1="256" x2="264" y2="256" stroke="#FACC15" stroke-width="3" stroke-dasharray="14 10"/>
<rect x="16" y="150" width="56" height="86" rx="5" fill="#12284A" stroke="#38BDF8" stroke-width="1.5"/><rect class="win" x="24" y="162" width="40" height="28" rx="3" fill="#FDE68A"/>
<rect x="12" y="142" width="64" height="11" rx="3" fill="#0EA5E9"/><text x="44" y="224" text-anchor="middle" font-size="10" font-weight="700" fill="#9FC3EA" font-family="IBM Plex Mono, monospace">PORT</text>
<circle class="sig" cx="44" cy="131" r="7"/>{TRUCK}
<rect x="88" y="192" width="12" height="44" rx="2" fill="#CBD5E1"/>
<g class="arm"><rect x="94" y="191" width="140" height="10" rx="5" fill="#F8FAFC"/><g fill="#DC2626"><rect x="108" y="191" width="12" height="10"/><rect x="132" y="191" width="12" height="10"/>
<rect x="156" y="191" width="12" height="10"/><rect x="180" y="191" width="12" height="10"/><rect x="204" y="191" width="12" height="10"/></g><circle cx="228" cy="196" r="3.5" fill="#F87171"/></g>
<circle cx="94" cy="196" r="7.5" fill="#E2E8F0" stroke="#64748B" stroke-width="2"/></svg></div>""", """
.lgx-port .sig { fill: #EF4444; filter: drop-shadow(0 0 6px #EF4444); animation: lgx-blink 1.4s ease-in-out infinite; }
.lgx-port .arm { transform-box: view-box; transform-origin: 94px 196px; }
.lgx-port .truck { opacity: 0; }
.lgx-port.on .sig { fill: #22C55E; filter: drop-shadow(0 0 9px #22C55E); animation: none; }
.lgx-port.on .arm { animation: lgx-port-up 1s cubic-bezier(.3,1.45,.5,1) forwards; }
.lgx-port.on .truck { opacity: 1; animation: lgx-port-truck 4.5s .9s linear infinite both; }
.lgx-port.on .road { animation: lgx-road .7s linear infinite; }
.lgx-port .win { animation: lgx-blink 4s ease-in-out infinite; }
@keyframes lgx-port-up { to { transform: rotate(-80deg); } }
@keyframes lgx-port-truck { from { transform: translateX(-90px); } to { transform: translateX(270px); } }
@keyframes lgx-road { to { transform: translateX(-24px); } }
""")

# 2 · orbe d'aurore ----------------------------------------------------------------------------------------------------------
V["orb"] = (lambda on: f"""<div class="lgx lgx-orb{on}"><div class="rays"></div><span class="ring a"></span><span class="ring b"></span><span class="ring c"></span>
<div class="orb"><i class="r1"></i><i class="r2"></i><i class="r3"></i><b class="gloss"></b></div></div>""", """
.lgx-orb .orb { position: relative; width: 170px; height: 170px; border-radius: 50%; overflow: hidden; z-index: 2;
  background: radial-gradient(circle at 35% 30%, #134E4A, #042F2E 70%); box-shadow: 0 0 40px -6px rgba(45,212,191,.45), inset 0 -18px 40px rgba(0,0,0,.5); animation: lgx-float 5s ease-in-out infinite; }
.lgx-orb .orb i { position: absolute; inset: -30%; filter: blur(14px); opacity: .5; mix-blend-mode: screen; border-radius: 45%; }
.lgx-orb .r1 { background: radial-gradient(40% 25% at 50% 50%, #2DD4BF, transparent 70%); animation: lgx-rot 9s linear infinite; }
.lgx-orb .r2 { background: radial-gradient(35% 20% at 40% 62%, #38BDF8, transparent 70%); animation: lgx-rot 13s linear infinite reverse; }
.lgx-orb .r3 { background: radial-gradient(30% 18% at 62% 40%, #A3E635, transparent 70%); animation: lgx-rot 17s linear infinite; }
.lgx-orb .gloss { position: absolute; left: 22%; top: 10%; width: 42%; height: 26%; border-radius: 50%; background: linear-gradient(180deg, rgba(255,255,255,.55), rgba(255,255,255,0)); }
.lgx-orb .ring { position: absolute; width: 170px; height: 170px; border-radius: 50%; border: 1.5px solid rgba(94,234,212,.6); opacity: 0; }
.lgx-orb .rays { position: absolute; width: 300px; height: 300px; border-radius: 50%; opacity: 0;
  background: repeating-conic-gradient(from 0deg, rgba(94,234,212,.25) 0 4deg, transparent 4deg 22deg);
  -webkit-mask-image: radial-gradient(circle, transparent 30%, #000 44%, transparent 70%); mask-image: radial-gradient(circle, transparent 30%, #000 44%, transparent 70%); }
.lgx-orb.on .orb i { opacity: 1; filter: blur(9px); }
.lgx-orb.on .orb { box-shadow: 0 0 90px 6px rgba(45,212,191,.6), inset 0 -18px 40px rgba(0,0,0,.3); }
.lgx-orb.on .ring { animation: lgx-ring 2.6s ease-out infinite; } .lgx-orb.on .ring.b { animation-delay: .85s; } .lgx-orb.on .ring.c { animation-delay: 1.7s; }
.lgx-orb.on .rays { opacity: 1; animation: lgx-rot 14s linear infinite; }
@keyframes lgx-ring { from { transform: scale(1); opacity: .9; } to { transform: scale(1.8); opacity: 0; } }
""")

# 3 · badge d'accès ------------------------------------------------------------------------------------------------------------
V["badge"] = (lambda on: f"""<div class="lgx lgx-badge{on}"><svg class="lan" viewBox="0 0 240 96" width="240" height="96"><path d="M90 0 L120 76 L150 0" fill="none" stroke="#1D4ED8" stroke-width="7" stroke-linejoin="round"/>
<rect x="108" y="70" width="24" height="16" rx="3" fill="#94A3B8"/></svg>
<div class="bd"><div class="face fr"><div class="top">TIMAR TANGER</div><div class="ph"></div><b>Badge d'accès</b><i></i><i class="s"></i><div class="bc"></div></div>
<div class="face bk"><svg viewBox="0 0 52 52" width="64" height="64"><circle cx="26" cy="26" r="24" fill="#16A34A"/><path d="M15 27 l7 7 l15 -16" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>
<b>Accès autorisé</b><small>Identité vérifiée</small></div></div></div>""", """
.lgx-badge { perspective: 800px; align-content: start; justify-items: center; }
.lgx-badge .lan { position: absolute; top: 0; left: 50%; transform: translateX(-50%); }
.lgx-badge .bd { position: relative; margin-top: 82px; width: 150px; height: 196px; transform-style: preserve-3d; transform-origin: 50% -12px; animation: lgx-swing 3.2s ease-in-out infinite; }
.lgx-badge .face { position: absolute; inset: 0; border-radius: 14px; backface-visibility: hidden; -webkit-backface-visibility: hidden; display: grid; justify-items: center; align-content: start;
  gap: 8px; padding-bottom: 12px; overflow: hidden; box-shadow: 0 18px 30px -16px rgba(15,23,42,.45); }
.lgx-badge .fr { background: #fff; border: 1px solid #E2E8F0; }
.lgx-badge .fr .top { width: 100%; padding: 9px 0; text-align: center; background: #1D4ED8; color: #fff !important; font: 700 10px 'IBM Plex Sans', sans-serif; letter-spacing: .16em; }
.lgx-badge .fr .ph { width: 54px; height: 54px; border-radius: 50%; margin-top: 6px; background: radial-gradient(circle at 50% 38%, #93C5FD 0 30%, transparent 31%), linear-gradient(180deg, #DBEAFE, #BFDBFE); box-shadow: inset 0 -14px 0 #60A5FA; }
.lgx-badge .fr b { font: 700 13px 'IBM Plex Sans', sans-serif; color: #0F172A !important; }
.lgx-badge .fr i { display: block; width: 96px; height: 7px; border-radius: 4px; background: #E2E8F0; } .lgx-badge .fr i.s { width: 66px; }
.lgx-badge .fr .bc { width: 110px; height: 26px; margin-top: 4px; background: repeating-linear-gradient(90deg, #0F172A 0 2px, transparent 2px 4px, #0F172A 4px 5px, transparent 5px 8px); }
.lgx-badge .bk { transform: rotateY(180deg); background: linear-gradient(160deg, #1D4ED8, #1E3A8A); align-content: center; }
.lgx-badge .bk b { color: #fff !important; font: 700 15px 'IBM Plex Sans', sans-serif; } .lgx-badge .bk small { color: #BFDBFE !important; font-size: 11px; }
.lgx-badge.on .bd { animation: lgx-flip 1s cubic-bezier(.3,1.3,.5,1) forwards; }
@keyframes lgx-swing { 0%, 100% { transform: rotate(-4deg); } 50% { transform: rotate(4deg); } }
@keyframes lgx-flip { from { transform: rotateY(0); } to { transform: rotateY(180deg); } }
""")

# 4 · conteneur ----------------------------------------------------------------------------------------------------------------
V["container"] = (lambda on: f"""<div class="lgx lgx-ct{on}"><div class="sh"></div><div class="box"><div class="in"><span>ACCÈS TIMAR</span><i></i><i></i><i></i></div>
<div class="dr l"><b>TIMU 803890 7</b><small>MAX GROSS 30 480 KG</small></div><div class="dr r"><b>45G1</b><small>TARE 3 820 KG</small></div></div></div>""", """
.lgx-ct { perspective: 700px; }
.lgx-ct .box { position: relative; width: 210px; height: 168px; border: 8px solid #B8460B; border-radius: 3px; background: #1A0D05; transform-style: preserve-3d; box-shadow: 0 22px 30px -18px #000; }
.lgx-ct .in { position: absolute; inset: 0; display: flex; align-items: flex-end; justify-content: center; gap: 6px; padding-bottom: 12px;
  background: radial-gradient(70% 70% at 50% 60%, rgba(255,186,90,.6), #1A0D05 75%); }
.lgx-ct .in i { width: 34px; height: 30px; background: #7C4A1E; border: 1px solid #A0612A; } .lgx-ct .in i:nth-child(3) { height: 46px; }
.lgx-ct .in span { position: absolute; top: 38px; font: 800 15px 'Big Shoulders Display', sans-serif; letter-spacing: .14em; color: #FFE8C2 !important; text-shadow: 0 0 14px rgba(255,186,90,.95); }
.lgx-ct .dr { position: absolute; top: 0; bottom: 0; width: 50%; display: grid; align-content: center; justify-items: center; gap: 4px; backface-visibility: hidden;
  background: repeating-linear-gradient(90deg, #E8590C 0 7px, #C94D0A 7px 9px); border: 1px solid #9A3B07; }
.lgx-ct .dr::before, .lgx-ct .dr::after { content: ""; position: absolute; top: 6px; bottom: 6px; width: 4px; border-radius: 2px; background: linear-gradient(90deg, #8A8F96, #D5D9DE, #8A8F96); }
.lgx-ct .dr.l { left: 0; transform-origin: left center; } .lgx-ct .dr.r { right: 0; transform-origin: right center; }
.lgx-ct .dr.l::before { left: 14px; } .lgx-ct .dr.l::after { left: 70px; } .lgx-ct .dr.r::before { right: 14px; } .lgx-ct .dr.r::after { right: 70px; }
.lgx-ct .dr b { position: relative; z-index: 1; white-space: nowrap; font: 800 12px 'Big Shoulders Display', sans-serif; letter-spacing: .06em; color: #fff !important; background: rgba(0,0,0,.18); padding: 1px 4px; }
.lgx-ct .dr small { position: relative; z-index: 1; font: 600 7px 'IBM Plex Mono', monospace; color: #FFE1CC !important; }
.lgx-ct .sh { position: absolute; bottom: 44px; width: 240px; height: 22px; border-radius: 50%; background: radial-gradient(rgba(0,0,0,.6), transparent 70%); }
.lgx-ct.on .dr.l { animation: lgx-ct-l 1.1s cubic-bezier(.4,.1,.2,1) forwards; } .lgx-ct.on .dr.r { animation: lgx-ct-r 1.1s .12s cubic-bezier(.4,.1,.2,1) forwards; }
.lgx-ct.on .in { animation: lgx-ct-glow 2.4s ease-in-out infinite; }
@keyframes lgx-ct-l { to { transform: rotateY(-112deg); } } @keyframes lgx-ct-r { to { transform: rotateY(112deg); } }
@keyframes lgx-ct-glow { 50% { filter: brightness(1.25); } }
""")

# 5 · boussole -----------------------------------------------------------------------------------------------------------------
V["compass"] = (lambda on: f"""<div class="lgx lgx-cp{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<g class="dial"><circle cx="120" cy="156" r="100" fill="none" stroke="#F59E0B" stroke-opacity=".4" stroke-width="1.5" stroke-dasharray="3 6"/></g>
<circle cx="120" cy="156" r="86" fill="#0B1628" stroke="#24395A" stroke-width="2"/><circle cx="120" cy="156" r="72" fill="none" stroke="#13233C" stroke-width="10"/>
{_ticks(120, 156, 80, 86, 72, 9, 74)}
<g font-family="Outfit, sans-serif" font-weight="700" font-size="14" fill="#E2E8F0" text-anchor="middle"><text x="120" y="102">N</text><text x="181" y="161">E</text><text x="120" y="221">S</text><text x="59" y="161">O</text></g>
<path class="route" pathLength="100" d="M120 156 C 150 146 172 108 198 64" fill="none" stroke="#FBBF24" stroke-width="2.6" stroke-linecap="round"/>
<g class="pin"><circle cx="198" cy="64" r="5.5" fill="#FBBF24"/><circle cx="198" cy="64" r="11" fill="none" stroke="#FBBF24" stroke-opacity=".5"/>
<text x="196" y="44" font-size="9" fill="#FDE68A" font-family="IBM Plex Mono, monospace" text-anchor="middle" font-weight="600">LA ROCHELLE</text></g>
<g class="needle"><polygon points="120,90 129,156 111,156" fill="#F59E0B"/><polygon points="120,222 129,156 111,156" fill="#94A3B8"/><circle cx="120" cy="156" r="7" fill="#FDE68A" stroke="#0B1628" stroke-width="2"/></g>
<text x="120" y="284" text-anchor="middle" font-size="10" fill="#A0AEC0" font-family="IBM Plex Mono, monospace" letter-spacing="2">TANGER · 35°46′N</text></svg></div>""", """
.lgx-cp .needle, .lgx-cp .dial { transform-box: view-box; transform-origin: 120px 156px; }
.lgx-cp .needle { animation: lgx-wobble 3s ease-in-out infinite; } .lgx-cp .dial { animation: lgx-rot 40s linear infinite; }
.lgx-cp .route { stroke-dasharray: 100; stroke-dashoffset: 100; } .lgx-cp .pin { opacity: 0; }
.lgx-cp.on .needle { animation: lgx-cp-spin 1.8s cubic-bezier(.2,.9,.3,1) forwards; }
.lgx-cp.on .route { animation: lgx-draw 1.1s 1.4s ease-out forwards; filter: drop-shadow(0 0 4px #F59E0B); }
.lgx-cp.on .pin { animation: lgx-pin .6s 2.3s cubic-bezier(.3,1.6,.5,1) both; }
@keyframes lgx-wobble { 0%, 100% { transform: rotate(-14deg); } 50% { transform: rotate(10deg); } }
@keyframes lgx-cp-spin { from { transform: rotate(-14deg); } to { transform: rotate(758deg); } }
@keyframes lgx-pin { from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: none; } }
""")

# 6 · empreinte digitale -----------------------------------------------------------------------------------------------------
V["finger"] = (lambda on: f"""<div class="lgx lgx-fp{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<polygon points="40,36 200,36 222,58 222,252 200,274 40,274 18,252 18,58" fill="rgba(34,211,238,.035)" stroke="#22D3EE" stroke-opacity=".7" stroke-width="1.5"/>
<g stroke="#22D3EE" stroke-width="3" fill="none"><path d="M30 80 V48 H62"/><path d="M210 80 V48 H178"/><path d="M30 230 V262 H62"/><path d="M210 230 V262 H178"/></g>
<g class="dim" fill="none" stroke-width="3" stroke-linecap="round">{_fp_arcs()}</g><g class="lit" fill="none" stroke-width="3" stroke-linecap="round">{_fp_arcs()}</g>
<rect class="laser" x="34" y="64" width="172" height="3" fill="#22D3EE"/>
<text class="ok" x="120" y="266" text-anchor="middle" font-size="11" font-weight="700" fill="#E879F9" font-family="Chakra Petch, monospace" letter-spacing="1.5">ACCÈS AUTORISÉ</text></svg></div>""", """
.lgx-fp .dim path { stroke: #164E63; }
.lgx-fp .lit path { stroke: #22D3EE; stroke-dasharray: 100; stroke-dashoffset: 100; }
.lgx-fp .laser { filter: drop-shadow(0 0 6px #22D3EE); animation: lgx-fp-scan 2.4s ease-in-out infinite alternate; }
.lgx-fp .ok { opacity: 0; }
.lgx-fp.on .lit path { animation: lgx-draw .8s ease-out forwards; filter: drop-shadow(0 0 4px #22D3EE); }
.lgx-fp.on .laser { animation: lgx-fp-scan .6s ease-in-out 2 alternate both, lgx-out .2s 1.25s forwards; }
.lgx-fp.on .ok { animation: lgx-glitch .9s 1.2s steps(3) both; filter: drop-shadow(0 0 6px #E879F9); }
@keyframes lgx-fp-scan { from { transform: translateY(0); } to { transform: translateY(168px); } }
@keyframes lgx-out { to { opacity: 0; } }
@keyframes lgx-glitch { 0% { opacity: 0; transform: translateX(-8px); } 30% { opacity: 1; transform: translateX(5px); } 55% { opacity: .5; transform: translateX(-3px); } 100% { opacity: 1; transform: none; } }
""")

# 7 · passeport ----------------------------------------------------------------------------------------------------------------
_CREST = ('<svg viewBox="0 0 40 40" width="46" height="46"><circle cx="20" cy="20" r="18" fill="none" stroke="#D4B26A" stroke-width="1.5"/>'
          '<path d="M20 11 v19 M13 23 q7 9 14 0 M15 15 h10" fill="none" stroke="#D4B26A" stroke-width="2" stroke-linecap="round"/>'
          '<circle cx="20" cy="9" r="2.4" fill="none" stroke="#D4B26A" stroke-width="1.5"/></svg>')
V["passport"] = (lambda on: f"""<div class="lgx lgx-pp{on}"><div class="bk"><div class="pg"><i class="ph"></i><i></i><i></i><i class="s"></i><i></i><i class="s"></i>
<em>TIMAR&lt;&lt;TANGER&lt;&lt;ACCES&lt;&lt;401&lt;&lt;&lt;&lt;</em><div class="stamp">ENTRÉE<small>TANGER · 401</small></div></div>
<div class="cv"><div class="front">{_CREST}<b>PASSEPORT</b><small>TIMAR · TANGER</small></div><div class="inside"></div></div></div></div>""", """
.lgx-pp { perspective: 900px; }
.lgx-pp .bk { position: relative; width: 156px; height: 210px; transform-style: preserve-3d; animation: lgx-float 4s ease-in-out infinite; }
.lgx-pp .pg { position: absolute; inset: 0; border-radius: 6px 12px 12px 6px; padding: 16px 14px; display: grid; align-content: start; gap: 7px;
  background: repeating-radial-gradient(circle at 70% 30%, rgba(31,58,44,.05) 0 2px, transparent 2px 6px), #EEF3EC; box-shadow: 0 16px 26px -14px rgba(0,0,0,.5); }
.lgx-pp .pg i { display: block; height: 6px; border-radius: 3px; background: #C9D6CB; } .lgx-pp .pg i.s { width: 60%; }
.lgx-pp .pg .ph { width: 44px; height: 54px; border-radius: 4px; background: linear-gradient(180deg, #D3DED5, #B7C6BA); }
.lgx-pp .pg em { font: 600 6.5px 'IBM Plex Mono', monospace; color: #4B5E52 !important; font-style: normal; letter-spacing: .06em; margin-top: 6px; word-break: break-all; }
.lgx-pp .stamp { position: absolute; right: 8px; bottom: 40px; border: 3px solid #8E2449; color: #8E2449 !important; border-radius: 8px; padding: 6px 8px; text-align: center;
  font: 700 15px/1.05 'IBM Plex Mono', monospace; letter-spacing: .1em; opacity: 0; transform: rotate(-12deg) scale(2.3); mix-blend-mode: multiply; }
.lgx-pp .stamp small { display: block; font-size: 7px; letter-spacing: .16em; color: #8E2449 !important; margin-top: 3px; }
.lgx-pp .cv { position: absolute; inset: 0; transform-origin: left center; transform-style: preserve-3d; }
.lgx-pp .cv > div { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; }
.lgx-pp .front { border-radius: 6px 12px 12px 6px; display: grid; place-items: center; align-content: center; gap: 10px;
  background: linear-gradient(160deg, #24452F, #14281E); box-shadow: inset 7px 0 10px -6px rgba(0,0,0,.6), 0 16px 26px -14px rgba(0,0,0,.6); }
.lgx-pp .front b { color: #D4B26A !important; font: 700 15px 'Special Elite', 'IBM Plex Mono', monospace; letter-spacing: .2em; }
.lgx-pp .front small { color: #D4B26A !important; font: 600 9px 'IBM Plex Mono', monospace; letter-spacing: .2em; }
.lgx-pp .inside { border-radius: 12px 6px 6px 12px; background: #E1E9E2; transform: rotateY(180deg); }
.lgx-pp.on .bk { animation: lgx-pp-shift 1s ease forwards; }
.lgx-pp.on .cv { animation: lgx-pp-open 1.1s cubic-bezier(.5,.1,.2,1) forwards; }
.lgx-pp.on .stamp { animation: lgx-stamp .5s 1.15s cubic-bezier(.2,1.6,.4,1) forwards; }
@keyframes lgx-pp-open { to { transform: rotateY(-165deg); } }
@keyframes lgx-pp-shift { to { transform: translateX(46px); } }
""")

# 8 · interrupteur -------------------------------------------------------------------------------------------------------------
V["switch"] = (lambda on: f"""<div class="lgx lgx-sw{on}"><div class="wrap"><b class="big">Entrée<span>.</span></b><div class="sw"><i></i><small class="o">OFF</small><small class="n">ON</small></div>
<em>TIMAR — Tanger — Import / Export</em></div></div>""", """
.lgx-sw .wrap { display: grid; gap: 20px; justify-items: start; }
.lgx-sw .big { font: 800 56px/.9 'Bricolage Grotesque', sans-serif; letter-spacing: -.045em; color: #0C0A09 !important; }
.lgx-sw .big span { color: #2F4FD8 !important; }
.lgx-sw .sw { position: relative; width: 150px; height: 58px; border: 2px solid #0C0A09; background: #FAFAF9; }
.lgx-sw .sw i { position: absolute; top: 6px; left: 6px; width: 42px; height: 42px; background: #0C0A09; }
.lgx-sw .sw small { position: absolute; top: 50%; transform: translateY(-50%); font: 700 12px 'IBM Plex Mono', monospace; letter-spacing: .14em; }
.lgx-sw .o { right: 18px; color: #0C0A09 !important; } .lgx-sw .n { left: 18px; color: #FAFAF9 !important; opacity: 0; }
.lgx-sw em { font: 500 11px 'IBM Plex Mono', monospace; color: #78716C !important; font-style: normal; letter-spacing: .06em; }
.lgx-sw.on .sw { animation: lgx-sw-bg .5s .2s both; } .lgx-sw.on .sw i { animation: lgx-sw-k .6s cubic-bezier(.7,0,.2,1) both; }
.lgx-sw.on .o { animation: lgx-out .2s both; } .lgx-sw.on .n { animation: lgx-fade .3s .45s both; }
.lgx-sw.on .big { animation: lgx-sw-t .7s cubic-bezier(.2,.8,.2,1) both; }
@keyframes lgx-sw-k { to { transform: translateX(92px); background: #2F4FD8; } }
@keyframes lgx-sw-bg { to { background: #0C0A09; } }
@keyframes lgx-sw-t { from { letter-spacing: .02em; opacity: .4; } to { letter-spacing: -.045em; opacity: 1; } }
@keyframes lgx-out { to { opacity: 0; } }
""")

# 9 · phare --------------------------------------------------------------------------------------------------------------------
V["lighthouse"] = (lambda on: f"""<div class="lgx lgx-lh{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<defs><linearGradient id="lh-beam" x1="0" x2="1"><stop offset="0" stop-color="#FFF3C4" stop-opacity=".85"/><stop offset="1" stop-color="#FFF3C4" stop-opacity="0"/></linearGradient>
<radialGradient id="lh-glow"><stop offset="0" stop-color="#FFF7D6" stop-opacity=".95"/><stop offset="1" stop-color="#FFF7D6" stop-opacity="0"/></radialGradient><radialGradient id="lh-fg" cx=".5" cy=".35" r=".62"><stop offset=".6" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient><mask id="lh-fade"><rect x="-10" y="226" width="260" height="78" fill="url(#lh-fg)"/></mask></defs>
<g fill="#fff"><circle cx="34" cy="40" r="1.4" opacity=".7"/><circle cx="200" cy="30" r="1.2" opacity=".6"/><circle cx="170" cy="90" r="1" opacity=".5"/><circle cx="60" cy="120" r="1" opacity=".5"/></g>
<g class="beam"><polygon points="128,74 330,30 330,118" fill="url(#lh-beam)"/></g>
<circle class="glow" cx="120" cy="74" r="44" fill="url(#lh-glow)"/>
<path d="M58 252 L76 222 L162 218 L184 252 Z" fill="#0A0D1C"/>
<polygon points="104,222 136,222 130,92 110,92" fill="#EDE6D3"/><polygon points="120,222 136,222 130,92 120,92" fill="#D2C7AC"/>
<polygon points="107,192 133,192 132,172 108,172" fill="#B91C1C"/><polygon points="109,146 131,146 130,128 110,128" fill="#B91C1C"/>
<rect x="117" y="200" width="6" height="10" rx="1" fill="#FCD34D" opacity=".85"/><rect x="117" y="154" width="6" height="9" rx="1" fill="#FCD34D" opacity=".85"/>
<rect x="100" y="86" width="40" height="6" fill="#2B2F3A"/><rect class="lamp" x="111" y="63" width="18" height="23" rx="2"/><polygon points="106,64 134,64 120,46" fill="#2B2F3A"/>
<g mask="url(#lh-fade)"><path class="wave a" d="M-40 252 q20 -8 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 V300 H-40Z" fill="#16204A"/>
<path class="wave b" d="M-40 262 q20 -6 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 V300 H-40Z" fill="#0E1533"/></g></svg></div>""", """
.lgx-lh .lamp { fill: #3A4A6E; } .lgx-lh .beam, .lgx-lh .glow { opacity: 0; }
.lgx-lh .beam, .lgx-lh .glow { transform-box: view-box; transform-origin: 120px 74px; }
.lgx-lh .wave { animation: lgx-wave 3s linear infinite; } .lgx-lh .wave.b { animation-duration: 4.6s; animation-direction: reverse; }
.lgx-lh.on .lamp { fill: #FFF7D6; filter: drop-shadow(0 0 10px #FDE68A); }
.lgx-lh.on .glow { opacity: 1; animation: lgx-lh-flash 4s linear infinite; }
.lgx-lh.on .beam { opacity: 1; animation: lgx-lh-sweep 4s linear infinite; }
@keyframes lgx-lh-sweep { 0% { transform: scaleX(1); } 25% { transform: scaleX(0); } 50% { transform: scaleX(-1); } 75% { transform: scaleX(0); } 100% { transform: scaleX(1); } }
@keyframes lgx-lh-flash { 0%, 50%, 100% { transform: scale(.7); opacity: .7; } 25%, 75% { transform: scale(1.7); opacity: 1; } }
@keyframes lgx-wave { from { transform: translateX(-40px); } to { transform: translateX(0); } }
""")

# 10 · tableau de commande -----------------------------------------------------------------------------------------------------
def _gauge(cx, cy, cls):
    return (f'<path d="M{cx - 34} {cy} A34 34 0 0 1 {cx + 34} {cy}" fill="none" stroke="#24395A" stroke-width="8"/>'
            f'<path d="M{cx - 34} {cy} A34 34 0 0 1 {cx + 10} {cy - 32.5}" fill="none" stroke="#22C55E" stroke-width="4" opacity=".7"/>'
            f'<path d="M{cx + 10} {cy - 32.5} A34 34 0 0 1 {cx + 27} {cy - 20}" fill="none" stroke="#F59E0B" stroke-width="4" opacity=".7"/>'
            f'<path d="M{cx + 27} {cy - 20} A34 34 0 0 1 {cx + 34} {cy}" fill="none" stroke="#EF4444" stroke-width="4" opacity=".7"/>'
            f'<g class="{cls}"><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 30}" stroke="#F8FAFC" stroke-width="2.5" stroke-linecap="round"/></g>'
            f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="#F8FAFC"/>')


V["control"] = (lambda on: f"""<div class="lgx lgx-cl{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<rect x="18" y="34" width="204" height="236" rx="14" fill="#101A2B" stroke="#2B4166" stroke-width="2"/>
<g fill="#2B4166"><circle cx="30" cy="46" r="3"/><circle cx="210" cy="46" r="3"/><circle cx="30" cy="258" r="3"/><circle cx="210" cy="258" r="3"/></g>
<text x="120" y="60" text-anchor="middle" font-size="10" font-weight="700" fill="#93C5FD" font-family="IBM Plex Mono, monospace" letter-spacing="3">TIMAR · VENTILATION</text>
{_gauge(76, 114, "n1")}{_gauge(164, 114, "n2")}
<g font-family="IBM Plex Mono, monospace" font-size="7" fill="#7489A6" text-anchor="middle"><text x="76" y="128">POIDS</text><text x="164" y="128">LIGNES</text></g>
<circle class="lt r" cx="52" cy="160" r="7"/><circle class="lt a" cx="76" cy="160" r="7"/><circle class="lt g" cx="100" cy="160" r="7"/>
<rect x="128" y="150" width="62" height="22" rx="4" fill="#052E16"/><text class="lcd off" x="159" y="165" text-anchor="middle" font-size="10" font-weight="700" fill="#EF4444" font-family="IBM Plex Mono, monospace">ARRÊT</text>
<text class="lcd onx" x="159" y="165" text-anchor="middle" font-size="10" font-weight="700" fill="#4ADE80" font-family="IBM Plex Mono, monospace">PRÊT ✓</text>
<rect x="176" y="186" width="14" height="70" rx="7" fill="#0B1220" stroke="#2B4166"/><g class="lever"><line x1="183" y1="200" x2="160" y2="196" stroke="#94A3B8" stroke-width="4" stroke-linecap="round"/><circle cx="160" cy="196" r="9" fill="#EF4444"/></g>
<polygon class="g1" points="{_gear(66, 226, 22, 10)}" fill="#64748B"/><circle cx="66" cy="226" r="6" fill="#101A2B"/>
<polygon class="g2" points="{_gear(104, 214, 14, 8)}" fill="#94A3B8"/><circle cx="104" cy="214" r="4" fill="#101A2B"/></svg></div>""", """
.lgx-cl .n1, .lgx-cl .n2 { transform-box: view-box; } .lgx-cl .n1 { transform-origin: 76px 114px; } .lgx-cl .n2 { transform-origin: 164px 114px; }
.lgx-cl .n1, .lgx-cl .n2 { transform: rotate(-82deg); animation: lgx-cl-idle 2.2s ease-in-out infinite; }
.lgx-cl .lt { fill: #1E293B; } .lgx-cl .lt.r { fill: #EF4444; filter: drop-shadow(0 0 6px #EF4444); animation: lgx-blink 1.2s infinite; }
.lgx-cl .lcd.onx { opacity: 0; }
.lgx-cl .g1, .lgx-cl .g2 { transform-box: view-box; } .lgx-cl .g1 { transform-origin: 66px 226px; } .lgx-cl .g2 { transform-origin: 104px 214px; }
.lgx-cl .lever { transform-box: view-box; transform-origin: 183px 200px; }
.lgx-cl.on .n1 { animation: lgx-cl-up1 1.4s cubic-bezier(.3,1.4,.5,1) forwards; } .lgx-cl.on .n2 { animation: lgx-cl-up2 1.6s .2s cubic-bezier(.3,1.4,.5,1) forwards; }
.lgx-cl.on .lt.r { fill: #1E293B; filter: none; animation: none; }
.lgx-cl.on .lt.a { animation: lgx-cl-a .4s .3s both; } .lgx-cl.on .lt.g { animation: lgx-cl-g .4s .8s both; }
.lgx-cl.on .lcd.off { opacity: 0; } .lgx-cl.on .lcd.onx { animation: lgx-fade .3s 1.1s both; }
.lgx-cl.on .g1 { animation: lgx-rot 3s linear infinite; } .lgx-cl.on .g2 { animation: lgx-rot 2s linear infinite reverse; }
.lgx-cl.on .lever { animation: lgx-cl-lever .5s cubic-bezier(.3,1.4,.5,1) forwards; }
@keyframes lgx-cl-idle { 50% { transform: rotate(-76deg); } }
@keyframes lgx-cl-up1 { from { transform: rotate(-82deg); } to { transform: rotate(38deg); } }
@keyframes lgx-cl-up2 { from { transform: rotate(-82deg); } to { transform: rotate(62deg); } }
@keyframes lgx-cl-a { to { fill: #F59E0B; filter: drop-shadow(0 0 6px #F59E0B); } }
@keyframes lgx-cl-g { to { fill: #22C55E; filter: drop-shadow(0 0 8px #22C55E); } }
@keyframes lgx-cl-lever { to { transform: translateY(44px); } }
""")

# 11 · billet de train ---------------------------------------------------------------------------------------------------------
V["ticket"] = (lambda on: f"""<div class="lgx lgx-tk{on}"><div class="tk"><div class="l"><small>TIMAR EXPRESS · FRET</small><b>TANGER <span>→</span><br>LA ROCHELLE</b>
<em>Voiture 4 · Place 12</em><div class="bc"></div></div><div class="r"><small>BILLET</small><b>3444</b><em>401-070</em></div><i class="hole"></i><div class="ok">COMPOSTÉ ✓</div></div>
<div class="punch"><i></i></div></div>""", """
.lgx-tk .tk { position: relative; width: 236px; height: 128px; display: grid; grid-template-columns: 1fr 64px; transform: rotate(-6deg); animation: lgx-float 4s ease-in-out infinite;
  background: linear-gradient(180deg, #F97316 0 22px, #FFF7ED 22px); border-radius: 10px; box-shadow: 0 20px 30px -16px rgba(0,0,0,.6);
  -webkit-mask: radial-gradient(circle 9px at 172px 0, transparent 96%, #000) top / 100% 51% no-repeat, radial-gradient(circle 9px at 172px 100%, transparent 96%, #000) bottom / 100% 51% no-repeat;
  mask: radial-gradient(circle 9px at 172px 0, transparent 96%, #000) top / 100% 51% no-repeat, radial-gradient(circle 9px at 172px 100%, transparent 96%, #000) bottom / 100% 51% no-repeat; }
.lgx-tk .l { padding: 5px 10px; display: grid; gap: 3px; align-content: start; border-right: 2px dashed #FDBA74; }
.lgx-tk .l small, .lgx-tk .r small { font: 700 8px 'IBM Plex Mono', monospace; letter-spacing: .14em; color: #FFF7ED !important; }
.lgx-tk .l b { font: 800 15px/1.1 'Outfit', sans-serif; color: #1F1A3D !important; margin-top: 6px; } .lgx-tk .l b span { color: #F97316 !important; }
.lgx-tk .l em, .lgx-tk .r em { font: 500 8.5px 'IBM Plex Mono', monospace; color: #6B5B8A !important; font-style: normal; }
.lgx-tk .bc { height: 16px; width: 120px; background: repeating-linear-gradient(90deg, #1F1A3D 0 2px, transparent 2px 4px, #1F1A3D 4px 5px, transparent 5px 7px); }
.lgx-tk .r { padding: 5px 6px; display: grid; align-content: start; justify-items: center; gap: 6px; }
.lgx-tk .r b { font: 800 16px 'Outfit', sans-serif; color: #1F1A3D !important; margin-top: 10px; }
.lgx-tk .hole { position: absolute; right: 22px; bottom: 26px; width: 18px; height: 18px; border-radius: 50%; background: #120F28; box-shadow: inset 0 2px 3px #000; transform: scale(0); }
.lgx-tk .ok { position: absolute; left: 40px; bottom: 34px; border: 2px solid #16A34A; color: #16A34A !important; font: 800 14px 'IBM Plex Mono', monospace; padding: 3px 8px; border-radius: 6px;
  letter-spacing: .08em; opacity: 0; transform: rotate(-12deg) scale(2.3); background: rgba(255,247,237,.6); }
.lgx-tk .punch { position: absolute; width: 46px; height: 90px; right: 30px; top: -6px; opacity: 0; }
.lgx-tk .punch i { position: absolute; inset: 0; border-radius: 10px 10px 18px 18px; background: linear-gradient(90deg, #64748B, #CBD5E1, #64748B); box-shadow: 0 10px 18px -8px #000; }
.lgx-tk.on .punch { animation: lgx-tk-punch .7s ease both; }
.lgx-tk.on .hole { animation: lgx-pop .25s .45s cubic-bezier(.3,1.6,.5,1) forwards; }
.lgx-tk.on .ok { animation: lgx-stamp .45s .8s cubic-bezier(.2,1.6,.4,1) forwards; }
.lgx-tk.on .tk { animation: lgx-tk-shake .4s .4s ease both; }
@keyframes lgx-tk-punch { 0% { opacity: 0; transform: translateY(-60px); } 40% { opacity: 1; transform: translateY(40px); } 60% { transform: translateY(46px); } 100% { opacity: 0; transform: translateY(-60px); } }
@keyframes lgx-tk-shake { 0%, 100% { transform: rotate(-6deg); } 30% { transform: rotate(-9deg) translateY(4px); } 60% { transform: rotate(-4deg); } }
""")

# 12 · globe -------------------------------------------------------------------------------------------------------------------
_PLANE = ('<svg viewBox="0 0 40 24" width="34" height="20"><path d="M2 12 L14 10 L22 1 L26 1 L21 10 L34 9 L38 4 L40 4 L38 12 L40 20 L38 20 L34 15 L21 14 L26 23 L22 23 L14 14 Z" fill="#FDE68A"/></svg>')
V["globe"] = (lambda on: f"""<div class="lgx lgx-gl{on}"><div class="stg"><div class="g"><div class="tex"></div><div class="shade"></div></div>
<svg class="orb" viewBox="0 0 240 300" width="240" height="300"><ellipse cx="120" cy="150" rx="108" ry="36" fill="none" stroke="#FBBF24" stroke-opacity=".45" stroke-dasharray="3 5" transform="rotate(-16 120 150)"/></svg>
<div class="pl">{_PLANE}</div><div class="pin"><i></i><b>LA ROCHELLE</b></div></div></div>""", """
.lgx-gl .g { position: absolute; left: 40px; top: 70px; width: 160px; height: 160px; border-radius: 50%; overflow: hidden; background: #0C2D50; box-shadow: 0 0 50px -8px rgba(56,189,248,.55); }
.lgx-gl .tex { position: absolute; top: 0; left: 0; width: 640px; height: 160px; animation: lgx-gl-spin 14s linear infinite;
  background: radial-gradient(rgba(125,211,252,.55) 1px, transparent 1.4px) 0 0 / 8px 8px,
    radial-gradient(30px 22px at 60px 60px, rgba(52,211,153,.55), transparent 70%), radial-gradient(40px 30px at 190px 90px, rgba(52,211,153,.5), transparent 70%),
    radial-gradient(26px 34px at 300px 50px, rgba(52,211,153,.5), transparent 70%), radial-gradient(44px 26px at 420px 110px, rgba(52,211,153,.5), transparent 70%),
    radial-gradient(30px 22px at 380px 60px, rgba(52,211,153,.55), transparent 70%), radial-gradient(40px 30px at 510px 90px, rgba(52,211,153,.5), transparent 70%),
    radial-gradient(26px 34px at 620px 50px, rgba(52,211,153,.5), transparent 70%); }
.lgx-gl .shade { position: absolute; inset: 0; border-radius: 50%; background: radial-gradient(circle at 35% 30%, rgba(255,255,255,.18), transparent 40%), radial-gradient(circle at 50% 50%, transparent 55%, rgba(0,0,0,.65) 100%); }
.lgx-gl .orb { position: absolute; inset: 0; }
.lgx-gl .pl { position: absolute; left: 0; top: 0; offset-path: path("M 16 180 A 108 36 -16 1 1 224 120 A 108 36 -16 1 1 16 180"); offset-rotate: auto; animation: lgx-gl-orbit 6s linear infinite; }
.lgx-gl .pin { position: absolute; left: 150px; top: 80px; display: grid; justify-items: center; gap: 2px; opacity: 0; }
.lgx-gl .pin i { width: 12px; height: 12px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: #FBBF24; box-shadow: 0 0 10px #FBBF24; }
.lgx-gl .pin b { font: 700 8px 'IBM Plex Mono', monospace; color: #FDE68A !important; letter-spacing: .1em; }
.lgx-gl.on .pl { offset-path: path("M 20 210 C 60 120 120 40 160 92"); animation: lgx-gl-land 1.8s cubic-bezier(.4,0,.2,1) forwards; }
.lgx-gl.on .pin { animation: lgx-pin .6s 1.7s cubic-bezier(.3,1.6,.5,1) both; }
.lgx-gl.on .tex { animation-duration: 5s; }
@keyframes lgx-gl-spin { to { transform: translateX(-320px); } }
@keyframes lgx-gl-orbit { from { offset-distance: 0%; } to { offset-distance: 100%; } }
@keyframes lgx-gl-land { from { offset-distance: 0%; transform: scale(1); } to { offset-distance: 100%; transform: scale(.55); } }
@keyframes lgx-pin { from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: none; } }
""")

# 13 · constellation -----------------------------------------------------------------------------------------------------------
_KEY_PTS = [(70, 110), (92, 96), (112, 110), (112, 136), (92, 150), (70, 136), (134, 123), (158, 123), (182, 123), (200, 123), (182, 146), (200, 152)]
_KEY_LINES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (3, 6), (6, 7), (7, 8), (8, 9), (8, 10), (9, 11)]
V["constellation"] = (lambda on: """<div class="lgx lgx-cs{on}"><svg viewBox="0 0 240 300" width="240" height="300"><g class="key">
<g class="ln" stroke="#C4B5FD" stroke-width="1.6" stroke-linecap="round">{lines}</g><g class="st">{stars}</g></g>
<g fill="#fff" opacity=".6"><circle cx="30" cy="60" r="1"/><circle cx="210" cy="50" r="1.2"/><circle cx="40" cy="240" r="1"/><circle cx="214" cy="232" r="1.1"/><circle cx="130" cy="40" r=".9"/><circle cx="150" cy="260" r="1"/></g></svg></div>""".format(
    on=on, lines="".join(f'<line pathLength="100" x1="{_KEY_PTS[a][0]}" y1="{_KEY_PTS[a][1] + 30}" x2="{_KEY_PTS[b][0]}" y2="{_KEY_PTS[b][1] + 30}" style="animation-delay:{i * .1:.1f}s"/>'
                                    for i, (a, b) in enumerate(_KEY_LINES)),
    stars="".join(f'<circle cx="{x}" cy="{y + 30}" r="3.2" style="animation-delay:{(k * .37) % 2:.2f}s"/>' for k, (x, y) in enumerate(_KEY_PTS))), """
.lgx-cs .st circle { fill: #EDE9FE; filter: drop-shadow(0 0 4px #A78BFA); animation: lgx-twinkle 2.2s ease-in-out infinite; }
.lgx-cs .ln line { stroke-dasharray: 100; stroke-dashoffset: 100; }
.lgx-cs .key { transform-box: view-box; transform-origin: 135px 153px; }
.lgx-cs.on .ln line { animation: lgx-draw .5s ease-out forwards; filter: drop-shadow(0 0 3px #A78BFA); }
.lgx-cs.on .st circle { animation: lgx-cs-bright .6s ease forwards; }
.lgx-cs.on .key { animation: lgx-cs-turn .9s 1.5s cubic-bezier(.3,1.4,.5,1) forwards; }
@keyframes lgx-twinkle { 50% { opacity: .35; } }
@keyframes lgx-cs-bright { to { fill: #fff; filter: drop-shadow(0 0 8px #F472B6); } }
@keyframes lgx-cs-turn { to { transform: rotate(-90deg) scale(1.08); } }
""")

# 14 · goutte ------------------------------------------------------------------------------------------------------------------
V["drop"] = (lambda on: f"""<div class="lgx lgx-dp{on}"><span class="rp a"></span><span class="rp b"></span><span class="rp c"></span><div class="bl"><b class="hi"></b>
<svg class="ck" viewBox="0 0 52 52" width="58" height="58"><path d="M14 27 l8 8 l16 -18" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="100"/></svg></div></div>""", """
.lgx-dp .bl { position: relative; width: 156px; height: 156px; display: grid; place-items: center; z-index: 2;
  background: linear-gradient(135deg, #06B6D4, #3B82F6 55%, #FBBF24); animation: lgx-morph 7s ease-in-out infinite, lgx-float 5s ease-in-out infinite;
  box-shadow: 0 0 60px -10px rgba(6,182,212,.7), inset 0 -16px 30px rgba(0,0,0,.25); }
.lgx-dp .hi { position: absolute; left: 22%; top: 14%; width: 34%; height: 22%; border-radius: 50%; background: linear-gradient(180deg, rgba(255,255,255,.6), transparent); }
.lgx-dp .ck { opacity: 0; } .lgx-dp .ck path { stroke-dasharray: 100; stroke-dashoffset: 100; }
.lgx-dp .rp { position: absolute; width: 156px; height: 156px; border-radius: 50%; border: 2px solid rgba(165,243,252,.6); opacity: 0; }
.lgx-dp.on .bl { animation: lgx-dp-settle 1.2s cubic-bezier(.3,1.4,.5,1) forwards; }
.lgx-dp.on .ck { opacity: 1; } .lgx-dp.on .ck path { animation: lgx-draw .5s .8s ease-out forwards; }
.lgx-dp.on .rp { animation: lgx-dp-ripple 2.4s ease-out infinite; } .lgx-dp.on .rp.b { animation-delay: .8s; } .lgx-dp.on .rp.c { animation-delay: 1.6s; }
@keyframes lgx-morph { 0%, 100% { border-radius: 42% 58% 62% 38% / 45% 40% 60% 55%; } 33% { border-radius: 60% 40% 38% 62% / 55% 60% 40% 45%; } 66% { border-radius: 38% 62% 55% 45% / 62% 45% 55% 38%; } }
@keyframes lgx-dp-settle { 0% { border-radius: 42% 58% 62% 38% / 45% 40% 60% 55%; transform: scale(1); } 40% { transform: scale(1.12, .9); } 100% { border-radius: 50%; transform: scale(1); } }
@keyframes lgx-dp-ripple { from { transform: scale(1); opacity: .9; } to { transform: scale(1.9); opacity: 0; } }
""")

# 15 · hologramme --------------------------------------------------------------------------------------------------------------
V["holo"] = (lambda on: f"""<div class="lgx lgx-ho{on}"><div class="stg"><div class="cone"></div><div class="cd"><small>BADGE · TIMAR</small><i class="ph"></i><i></i><i class="s"></i><b>ACCÈS</b></div>
<div class="base"></div></div></div>""", """
.lgx-ho .stg { perspective: 700px; }
.lgx-ho .base { position: absolute; left: 50px; bottom: 34px; width: 140px; height: 34px; border-radius: 50%; background: radial-gradient(#0B1E35, #02060E 70%);
  box-shadow: 0 0 0 2px rgba(34,211,238,.5), 0 0 24px rgba(34,211,238,.45); animation: lgx-blink 2.6s ease-in-out infinite; }
.lgx-ho .cone { position: absolute; left: 40px; bottom: 50px; width: 160px; height: 190px; opacity: 0;
  background: linear-gradient(0deg, rgba(34,211,238,.45), rgba(34,211,238,0)); clip-path: polygon(38% 100%, 62% 100%, 100% 0, 0 0); }
.lgx-ho .cd { position: absolute; left: 45px; top: 58px; width: 150px; height: 96px; border-radius: 10px; padding: 8px 10px; display: grid; grid-template-columns: 34px 1fr; gap: 4px 8px; align-content: start;
  border: 1px solid rgba(165,243,252,.8); background: repeating-linear-gradient(0deg, rgba(165,243,252,.12) 0 1px, transparent 1px 3px), rgba(8,51,68,.45);
  box-shadow: 0 0 26px rgba(34,211,238,.55); opacity: 0; transform: scaleY(0); transform-origin: bottom; }
.lgx-ho .cd small { grid-column: 1 / -1; font: 700 8px 'IBM Plex Mono', monospace; letter-spacing: .14em; color: #A5F3FC !important; }
.lgx-ho .cd .ph { grid-row: span 3; width: 34px; height: 40px; border-radius: 6px; background: rgba(165,243,252,.3); }
.lgx-ho .cd i { display: block; height: 6px; border-radius: 3px; background: rgba(165,243,252,.45); } .lgx-ho .cd i.s { width: 60%; }
.lgx-ho .cd b { font: 700 16px 'Outfit', sans-serif; color: #fff !important; text-shadow: 0 0 12px #22D3EE; }
.lgx-ho.on .base { animation: none; box-shadow: 0 0 0 2px rgba(34,211,238,.9), 0 0 40px rgba(34,211,238,.8); }
.lgx-ho.on .cone { animation: lgx-fade .5s ease both, lgx-ho-flick 3s 1s infinite; }
.lgx-ho.on .cd { animation: lgx-ho-rise .8s .3s cubic-bezier(.2,1.2,.4,1) forwards, lgx-ho-spin 6s 1.2s ease-in-out infinite; }
@keyframes lgx-ho-rise { to { opacity: 1; transform: scaleY(1); } }
@keyframes lgx-ho-spin { 0%, 100% { opacity: 1; transform: rotateY(-22deg); } 50% { opacity: 1; transform: rotateY(22deg); } }
@keyframes lgx-ho-flick { 0%, 100% { opacity: 1; } 47% { opacity: 1; } 50% { opacity: .55; } 53% { opacity: 1; } }
""")

# 16 · grue ---------------------------------------------------------------------------------------------------------------------
_LAT = "".join(f"M{48 + 0} {50 + k * 20} L{56} {60 + k * 20} L48 {70 + k * 20} " for k in range(10))
V["crane"] = (lambda on: f"""<div class="lgx lgx-cr{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<rect x="0" y="252" width="240" height="24" fill="#2B313D"/><rect x="0" y="250" width="240" height="4" fill="#FACC15"/>
<rect x="44" y="40" width="16" height="212" fill="#EAB308"/><path d="{_LAT}" fill="none" stroke="#A16207" stroke-width="1.5"/>
<rect x="10" y="38" width="216" height="10" fill="#EAB308"/><path d="M60 38 L84 48 L108 38 L132 48 L156 38 L180 48 L204 38 L226 48" fill="none" stroke="#A16207" stroke-width="1.5"/>
<rect x="12" y="48" width="22" height="18" fill="#475569"/><rect x="60" y="48" width="18" height="15" fill="#1F2937"/><rect x="64" y="51" width="10" height="6" fill="#FDE68A"/>
<path d="M52 38 L52 18 L226 38 M52 18 L10 38" fill="none" stroke="#CA8A04" stroke-width="1.5"/><circle cx="52" cy="16" r="3" fill="#EF4444" class="bea"/>
<g class="trol"><rect x="150" y="48" width="18" height="7" rx="1" fill="#1F2937"/><rect class="cab" x="158" y="55" width="2" height="148" fill="#CBD5E1"/>
<g class="load"><path d="M159 203 v6 a5 5 0 1 1 -5 5" fill="none" stroke="#94A3B8" stroke-width="2.5"/><rect x="124" y="216" width="72" height="34" rx="2" fill="#EF4444"/>
<path d="M132 216 v34 M140 216 v34 M148 216 v34 M156 216 v34 M164 216 v34 M172 216 v34 M180 216 v34 M188 216 v34" stroke="rgba(0,0,0,.18)"/>
<text x="160" y="238" text-anchor="middle" font-size="10" font-weight="800" fill="#fff" font-family="Outfit, sans-serif" letter-spacing="1.5">ACCÈS</text></g></g></svg></div>""", """
.lgx-cr .bea { animation: lgx-blink 1s steps(2) infinite; }
.lgx-cr .cab { transform-box: view-box; transform-origin: 159px 55px; }
.lgx-cr .load { transform-box: view-box; transform-origin: 159px 203px; animation: lgx-cr-sway 3s ease-in-out infinite; }
.lgx-cr.on .load { animation: lgx-cr-lift 1.3s cubic-bezier(.5,0,.3,1) forwards; }
.lgx-cr.on .cab { animation: lgx-cr-cable 1.3s cubic-bezier(.5,0,.3,1) forwards; }
.lgx-cr.on .trol { animation: lgx-cr-move 1.1s 1.3s cubic-bezier(.5,0,.3,1) forwards; }
@keyframes lgx-cr-sway { 0%, 100% { transform: rotate(-1.5deg); } 50% { transform: rotate(1.5deg); } }
@keyframes lgx-cr-lift { to { transform: translateY(-118px); } }
@keyframes lgx-cr-cable { to { transform: scaleY(.2); } }
@keyframes lgx-cr-move { to { transform: translateX(-60px); } }
""")

# 17 · porte de la kasbah ------------------------------------------------------------------------------------------------------
_ZEL = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 22 22'%3E%3Crect width='22' height='22' fill='%230F3D3E'/%3E"
        "%3Cpath d='M11 1.5 L13.3 7.6 L19.5 8.7 L14.9 13 L16.2 19.5 L11 16.2 L5.8 19.5 L7.1 13 L2.5 8.7 L8.7 7.6 Z' fill='%23F2C14E'/%3E%3Ccircle cx='11' cy='11' r='2.4' fill='%231E6F6B'/%3E%3C/svg%3E\")")
V["kasbah"] = (lambda on: f"""<div class="lgx lgx-kb{on}"><div class="fr"></div><div class="ar"><div class="vw"><i class="mn"></i><i class="sea"></i><i class="lt"></i></div>
<div class="dr l"></div><div class="dr r"></div></div><i class="lan a"></i><i class="lan b"></i></div>""", """
.lgx-kb .fr { position: absolute; width: 196px; height: 250px; top: 28px; left: 50%; transform: translateX(-50%); border-radius: 98px 98px 6px 6px / 104px 104px 6px 6px;
  background: """ + _ZEL + """; box-shadow: 0 0 0 3px #F2C14E, 0 24px 40px -20px #000; }
.lgx-kb .ar { position: absolute; width: 156px; height: 218px; top: 52px; left: 50%; transform: translateX(-50%); border-radius: 78px 78px 2px 2px / 86px 86px 2px 2px;
  overflow: hidden; perspective: 600px; box-shadow: 0 0 0 3px #F2C14E; background: #05060F; }
.lgx-kb .vw { position: absolute; inset: 0; background: linear-gradient(180deg, #0A0B1E 0%, #2B2560 55%, #6B3D6E 70%, #0B1030 71%, #04060F 100%); }
.lgx-kb .mn { position: absolute; left: 92px; top: 40px; width: 22px; height: 22px; border-radius: 50%; background: #FFF5D6; box-shadow: 0 0 22px 6px rgba(255,245,214,.5); }
.lgx-kb .sea { position: absolute; left: 0; right: 0; top: 71%; height: 3px; background: repeating-linear-gradient(90deg, rgba(255,230,170,.7) 0 6px, transparent 6px 14px); animation: lgx-kb-sea 2s linear infinite; }
.lgx-kb .lt { position: absolute; inset: 0; background: radial-gradient(60% 50% at 50% 100%, rgba(242,193,78,.55), transparent 70%); }
.lgx-kb .dr { position: absolute; top: 0; bottom: 0; width: 50%; backface-visibility: hidden;
  background: radial-gradient(circle, #D9A43A 1.6px, transparent 2.2px) 7px 9px / 14px 18px, repeating-linear-gradient(90deg, #5B2E12 0 12px, #4A240D 12px 14px); box-shadow: inset 0 0 0 3px #3A1C08; }
.lgx-kb .dr.l { left: 0; transform-origin: left center; } .lgx-kb .dr.r { right: 0; transform-origin: right center; }
.lgx-kb .dr.l::after, .lgx-kb .dr.r::after { content: ""; position: absolute; top: 52%; width: 12px; height: 12px; border-radius: 50%; border: 2.5px solid #D9A43A; }
.lgx-kb .dr.l::after { right: 8px; } .lgx-kb .dr.r::after { left: 8px; }
.lgx-kb .lan { position: absolute; top: 74px; width: 14px; height: 22px; border-radius: 4px 4px 7px 7px; background: linear-gradient(180deg, #F2C14E, #D97706); box-shadow: 0 0 18px 4px rgba(242,193,78,.55);
  animation: lgx-kb-flick 2.4s ease-in-out infinite; }
.lgx-kb .lan::before { content: ""; position: absolute; left: 6px; top: -22px; width: 2px; height: 22px; background: #8A6A2A; }
.lgx-kb .lan.a { left: calc(50% - 116px); } .lgx-kb .lan.b { right: calc(50% - 116px); animation-delay: -1.1s; }
.lgx-kb.on .dr.l { animation: lgx-kb-l 1.3s cubic-bezier(.45,.05,.2,1) forwards; } .lgx-kb.on .dr.r { animation: lgx-kb-r 1.3s .1s cubic-bezier(.45,.05,.2,1) forwards; }
.lgx-kb.on .lt { animation: lgx-kb-glow 2.6s ease-in-out infinite; }
@keyframes lgx-kb-l { to { transform: rotateY(-108deg); } } @keyframes lgx-kb-r { to { transform: rotateY(108deg); } }
@keyframes lgx-kb-flick { 0%, 100% { opacity: 1; } 45% { opacity: .75; } 50% { opacity: .95; } }
@keyframes lgx-kb-sea { to { background-position: 14px 0; } }
@keyframes lgx-kb-glow { 50% { opacity: .65; } }
""")

# 18 · scanner de conteneur ----------------------------------------------------------------------------------------------------
V["scan"] = (lambda on: f"""<div class="lgx lgx-sc{on}"><div class="pl"><b>TIMU 803890 7</b><small>45G1 · MAX 30 480 · TARE 3 820</small><div class="bc"></div>
<i class="c tl"></i><i class="c tr"></i><i class="c bl"></i><i class="c br"></i><i class="lz"></i><div class="ok">✓ VÉRIFIÉ</div></div></div>""", """
.lgx-sc .pl { position: relative; width: 224px; height: 190px; padding: 22px 18px; display: grid; gap: 10px; align-content: start; border-radius: 4px;
  background: repeating-linear-gradient(90deg, #E35F00 0 9px, #C45200 9px 11px); box-shadow: inset 0 0 0 6px #9A4000, 0 22px 30px -18px #000; }
.lgx-sc .pl b { justify-self: start; background: #F3F4F6; color: #111827 !important; font: 800 22px 'Oswald', 'Big Shoulders Display', sans-serif; letter-spacing: .04em; padding: 2px 8px; }
.lgx-sc .pl small { justify-self: start; background: rgba(0,0,0,.35); color: #FFEAD6 !important; font: 600 8px 'IBM Plex Mono', monospace; padding: 2px 6px; letter-spacing: .05em; }
.lgx-sc .bc { height: 54px; margin-top: 4px; background: #F3F4F6 repeating-linear-gradient(90deg, #111827 0 3px, transparent 3px 5px, #111827 5px 6px, transparent 6px 9px, #111827 9px 11px, transparent 11px 14px) content-box; padding: 6px 10px; }
.lgx-sc .c { position: absolute; width: 18px; height: 18px; border-color: #FF7A1A; border-style: solid; border-width: 0; }
.lgx-sc .tl { left: -10px; top: -10px; border-left-width: 3px; border-top-width: 3px; } .lgx-sc .tr { right: -10px; top: -10px; border-right-width: 3px; border-top-width: 3px; }
.lgx-sc .bl { left: -10px; bottom: -10px; border-left-width: 3px; border-bottom-width: 3px; } .lgx-sc .br { right: -10px; bottom: -10px; border-right-width: 3px; border-bottom-width: 3px; }
.lgx-sc .lz { position: absolute; left: -16px; right: -16px; top: 118px; height: 2px; background: #EF4444; box-shadow: 0 0 10px 2px rgba(239,68,68,.8); animation: lgx-sc-lz 1.6s ease-in-out infinite alternate; }
.lgx-sc .ok { position: absolute; right: 14px; bottom: 12px; padding: 4px 10px; border-radius: 999px; background: #16A34A; color: #fff !important; font: 800 12px 'Oswald', sans-serif; letter-spacing: .08em; opacity: 0; }
.lgx-sc.on .lz { background: #22C55E; box-shadow: 0 0 14px 3px rgba(34,197,94,.9); animation: lgx-sc-lz .35s ease-in-out 4 alternate both, lgx-out .2s 1.4s forwards; }
.lgx-sc.on .ok { animation: lgx-pop .4s 1.3s cubic-bezier(.3,1.6,.5,1) both; }
.lgx-sc.on .pl { animation: lgx-sc-flash .5s 1.2s ease both; }
.lgx-sc.on .c { border-color: #22C55E; }
@keyframes lgx-sc-lz { from { transform: translateY(-22px); } to { transform: translateY(26px); } }
@keyframes lgx-sc-flash { 50% { filter: brightness(1.35); } }
@keyframes lgx-out { to { opacity: 0; } }
""")

# 19 · soleil rétro (synthwave) ------------------------------------------------------------------------------------------------
_GRID_V = "".join(f'<line x1="120" y1="190" x2="{120 + k * 34}" y2="300"/>' for k in range(-7, 8))
_GRID_H = "".join(f'<line x1="-60" y1="{190 + (k * k) * 2.2 + k * 4}" x2="300" y2="{190 + (k * k) * 2.2 + k * 4}"/>' for k in range(1, 9))
V["sun"] = (lambda on: f"""<div class="lgx lgx-sn{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<defs><linearGradient id="sn-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0D0221"/><stop offset=".55" stop-color="#3B0F6B"/><stop offset="1" stop-color="#FF2E97"/></linearGradient>
<linearGradient id="sn-sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE66D"/><stop offset=".55" stop-color="#FF8AC8"/><stop offset="1" stop-color="#FF2E97"/></linearGradient>
<mask id="sn-m"><rect x="0" y="0" width="240" height="300" fill="#fff"/><g fill="#000"><rect x="0" y="150" width="240" height="3"/><rect x="0" y="160" width="240" height="4"/><rect x="0" y="171" width="240" height="5"/><rect x="0" y="182" width="240" height="6"/></g></mask>
<clipPath id="sn-c"><rect x="10" y="30" width="220" height="250" rx="14"/></clipPath></defs>
<g clip-path="url(#sn-c)"><rect x="10" y="30" width="220" height="160" fill="url(#sn-sky)"/>
<g fill="#fff" class="stars"><circle cx="40" cy="56" r="1"/><circle cx="196" cy="70" r="1.2"/><circle cx="160" cy="44" r=".9"/><circle cx="70" cy="96" r="1"/><circle cx="210" cy="110" r=".8"/></g>
<g class="sun"><circle cx="120" cy="160" r="58" fill="url(#sn-sun)" mask="url(#sn-m)"/></g>
<polygon points="10,190 40,150 62,170 88,136 112,176 140,146 168,172 196,140 230,180 230,190" fill="#1B0B33" stroke="#FF2E97" stroke-width="1.5"/>
<rect x="10" y="190" width="220" height="90" fill="#12062B"/>
<g class="gv" stroke="#00F0FF" stroke-opacity=".6" stroke-width="1">{_GRID_V}</g><g class="gh" stroke="#FF2E97" stroke-opacity=".7" stroke-width="1">{_GRID_H}</g></g>
<rect x="10" y="30" width="220" height="250" rx="14" fill="none" stroke="#FF2E97" stroke-opacity=".5"/></svg></div>""", """
.lgx-sn .sun { transform: translateY(46px); filter: drop-shadow(0 0 10px rgba(255,46,151,.4)); opacity: .75; }
.lgx-sn .stars circle { animation: lgx-twinkle 2.6s ease-in-out infinite; } .lgx-sn .stars circle:nth-child(2n) { animation-delay: -1.3s; }
.lgx-sn.on .sun { animation: lgx-sn-rise 1.8s cubic-bezier(.2,.8,.2,1) forwards; }
.lgx-sn.on .gh { animation: lgx-sn-grid .9s linear infinite; }
.lgx-sn.on .gv { stroke-opacity: 1; filter: drop-shadow(0 0 3px #00F0FF); }
@keyframes lgx-sn-rise { to { transform: translateY(0); opacity: 1; filter: drop-shadow(0 0 22px rgba(255,46,151,.85)); } }
@keyframes lgx-sn-grid { from { transform: translateY(0); } to { transform: translateY(12px); } }
@keyframes lgx-twinkle { 50% { opacity: .3; } }
""")

# 20 · portail -----------------------------------------------------------------------------------------------------------------
_STREAKS = "".join(f'<line x1="{120 + 30 * math.cos(a):.1f}" y1="{150 + 30 * math.sin(a):.1f}" x2="{120 + 130 * math.cos(a):.1f}" y2="{150 + 130 * math.sin(a):.1f}"/>'
                   for a in [k * math.pi / 12 + .1 for k in range(24)])
V["portal"] = (lambda on: f"""<div class="lgx lgx-po{on}"><svg class="sk" viewBox="0 0 240 300" width="240" height="300"><g stroke="#DDD6FE" stroke-width="1.2" stroke-linecap="round">{_STREAKS}</g></svg>
<div class="p"><i class="r1"></i><i class="r2"></i><i class="r3"></i><i class="r4"></i><b class="core"></b></div></div>""", """
.lgx-po .p { position: relative; width: 190px; height: 190px; transform: scale(.82); }
.lgx-po .p i { position: absolute; inset: 0; border-radius: 50%; -webkit-mask: radial-gradient(circle, transparent 52%, #000 54%, #000 64%, transparent 66%); mask: radial-gradient(circle, transparent 52%, #000 54%, #000 64%, transparent 66%); }
.lgx-po .r1 { background: conic-gradient(#A78BFA, transparent 30%, #F0ABFC 50%, transparent 80%, #A78BFA); animation: lgx-rot 6s linear infinite; }
.lgx-po .r2 { inset: 14% !important; background: conic-gradient(from 90deg, #7C3AED, transparent 25%, #38BDF8 45%, transparent 75%, #7C3AED); animation: lgx-rot 4s linear infinite reverse; }
.lgx-po .r3 { inset: 27% !important; background: conic-gradient(from 45deg, #F0ABFC, transparent 35%, #A78BFA 60%, transparent 90%); animation: lgx-rot 2.6s linear infinite; }
.lgx-po .r4 { inset: -8% !important; opacity: .5; background: conic-gradient(from 200deg, transparent, #7C3AED 20%, transparent 40%, #F0ABFC 70%, transparent); animation: lgx-rot 11s linear infinite reverse; }
.lgx-po .core { position: absolute; inset: 36%; border-radius: 50%; background: radial-gradient(circle, #fff, #C4B5FD 40%, rgba(124,58,237,0) 72%); filter: blur(2px); animation: lgx-po-pulse 2.4s ease-in-out infinite; }
.lgx-po .sk { position: absolute; inset: 0; margin: auto; opacity: 0; }
.lgx-po .sk line { stroke-dasharray: 18 120; }
.lgx-po.on .p { animation: lgx-po-open 1.2s cubic-bezier(.2,1.3,.4,1) forwards; }
.lgx-po.on .p .r1 { animation-duration: 2s; } .lgx-po.on .p .r2 { animation-duration: 1.4s; } .lgx-po.on .p .r3 { animation-duration: 1s; }
.lgx-po.on .sk { opacity: 1; } .lgx-po.on .sk line { animation: lgx-po-streak 1.1s linear infinite; }
@keyframes lgx-po-open { to { transform: scale(1.12); } }
@keyframes lgx-po-pulse { 50% { transform: scale(1.25); opacity: .8; } }
@keyframes lgx-po-streak { from { stroke-dashoffset: 30; } to { stroke-dashoffset: -110; } }
""")

# 21 · avion en papier ---------------------------------------------------------------------------------------------------------
_LOOP = "M 30 238 C 90 150 210 250 196 152 C 184 70 70 92 112 152 C 144 196 214 120 214 52"
_PP = ('<svg viewBox="0 0 60 40" width="58" height="38"><polygon points="0,6 60,20 16,21" fill="#FFFFFF" stroke="#94A3B8" stroke-width=".8"/>'
       '<polygon points="16,21 60,20 6,34" fill="#E2E8F0" stroke="#94A3B8" stroke-width=".8"/><polygon points="16,21 6,34 20,27" fill="#CBD5E1"/></svg>')
V["plane"] = (lambda on: f"""<div class="lgx lgx-pa{on}"><div class="stg"><svg class="tr" viewBox="0 0 240 300" width="240" height="300"><path d="{_LOOP}" pathLength="100" fill="none" stroke="#0F6FDE" stroke-opacity=".45" stroke-width="2" stroke-dasharray="3 4"/></svg>
<div class="cl a"></div><div class="cl b"></div><div class="pp">{_PP}</div></div></div>""", """
.lgx-pa .stg { overflow: visible; }
.lgx-pa .cl { position: absolute; border-radius: 999px; background: #fff; box-shadow: 18px 6px 0 -4px #fff, -14px 8px 0 -6px #fff, 0 10px 20px -12px rgba(14,34,56,.25); }
.lgx-pa .cl.a { left: 24px; top: 60px; width: 60px; height: 20px; animation: lgx-pa-cloud 9s ease-in-out infinite alternate; }
.lgx-pa .cl.b { right: 20px; top: 200px; width: 70px; height: 22px; animation: lgx-pa-cloud 11s ease-in-out infinite alternate-reverse; }
.lgx-pa .tr path { stroke-dasharray: 100; stroke-dashoffset: 100; }
.lgx-pa .pp { position: absolute; left: 0; top: 0; offset-path: path('""" + _LOOP + """'); offset-rotate: auto; offset-distance: 0%; filter: drop-shadow(0 8px 6px rgba(14,34,56,.25)); animation: lgx-pa-bob 2.4s ease-in-out infinite; }
.lgx-pa.on .pp { animation: lgx-pa-fly 2.6s cubic-bezier(.45,.05,.3,1) forwards; }
.lgx-pa.on .tr path { stroke-dasharray: 100; animation: lgx-draw 2.6s cubic-bezier(.45,.05,.3,1) forwards; }
@keyframes lgx-pa-bob { 0%, 100% { offset-distance: 0%; transform: translateY(0); } 50% { offset-distance: 2%; transform: translateY(-6px); } }
@keyframes lgx-pa-fly { from { offset-distance: 0%; } to { offset-distance: 100%; } }
@keyframes lgx-pa-cloud { to { transform: translateX(18px); } }
""")

# 22 · coffre-fort à code ------------------------------------------------------------------------------------------------------
_BOLTS = "".join(f'<rect class="bo" x="{120 + 96 * math.cos(a) - 6:.1f}" y="{150 + 96 * math.sin(a) - 6:.1f}" width="12" height="12" rx="2" fill="#4B5563" '
                 f'style="--dx:{-14 * math.cos(a):.1f}px;--dy:{-14 * math.sin(a):.1f}px"/>' for a in [k * math.pi / 4 for k in range(8)])
_DIAL_NUM = "".join(f'<text x="{120 + 30 * math.sin(math.radians(k * 36)):.1f}" y="{150 - 30 * math.cos(math.radians(k * 36)) + 3:.1f}" text-anchor="middle">{k * 10}</text>' for k in range(10))
V["vault"] = (lambda on: f"""<div class="lgx lgx-vt{on}"><svg viewBox="0 0 240 300" width="240" height="300">
<defs><radialGradient id="vt-st" cx=".35" cy=".3"><stop offset="0" stop-color="#3F4A44"/><stop offset=".7" stop-color="#1B241F"/><stop offset="1" stop-color="#0B120E"/></radialGradient></defs>
<circle cx="120" cy="150" r="112" fill="#020604" stroke="#14532D" stroke-width="3"/><g class="glow"><circle cx="120" cy="150" r="100" fill="#052E16"/>
<text x="120" y="146" text-anchor="middle" font-size="18" font-weight="700" fill="#4ADE80" font-family="JetBrains Mono, IBM Plex Mono, monospace">OUVERT</text>
<text x="120" y="168" text-anchor="middle" font-size="10" fill="#86EFAC" font-family="JetBrains Mono, IBM Plex Mono, monospace">8544 4990 90</text></g>
<g class="door">{_BOLTS}<circle cx="120" cy="150" r="102" fill="url(#vt-st)" stroke="#6B7280" stroke-width="2"/><circle cx="120" cy="150" r="86" fill="none" stroke="#374151" stroke-width="1.5"/>
<g class="hd" stroke="#9CA3AF" stroke-width="5" stroke-linecap="round"><line x1="120" y1="150" x2="120" y2="92"/><line x1="120" y1="150" x2="170" y2="179"/><line x1="120" y1="150" x2="70" y2="179"/></g>
<g class="hd"><circle cx="120" cy="92" r="6" fill="#D1D5DB"/><circle cx="170" cy="179" r="6" fill="#D1D5DB"/><circle cx="70" cy="179" r="6" fill="#D1D5DB"/></g>
<g class="dial"><circle cx="120" cy="150" r="40" fill="#111827" stroke="#22C55E" stroke-opacity=".6" stroke-width="2"/>{_ticks(120, 150, 36, 40, 40, 4, 33, "#22C55E")}
<g font-family="JetBrains Mono, IBM Plex Mono, monospace" font-size="7" fill="#86EFAC">{_DIAL_NUM}</g></g>
<polygon points="114,104 126,104 120,112" fill="#FBBF24"/><circle cx="120" cy="150" r="8" fill="#374151"/></g></svg></div>""", """
.lgx-vt .dial, .lgx-vt .hd, .lgx-vt .door { transform-box: view-box; transform-origin: 120px 150px; }
.lgx-vt .dial { animation: lgx-vt-idle 4s ease-in-out infinite; } .lgx-vt .glow { opacity: 0; }
.lgx-vt.on .dial { animation: lgx-vt-code 1.6s ease-in-out forwards; }
.lgx-vt.on .hd { animation: lgx-vt-hd .5s 1.5s ease forwards; }
.lgx-vt.on .bo { animation: lgx-vt-bolt .3s 1.6s ease forwards; }
.lgx-vt.on .door { transform-origin: 18px 150px; animation: lgx-vt-open 1s 2s cubic-bezier(.5,0,.2,1) forwards; }
.lgx-vt.on .glow { animation: lgx-fade .6s 2.2s both; filter: drop-shadow(0 0 12px #22C55E); }
@keyframes lgx-vt-idle { 50% { transform: rotate(14deg); } }
@keyframes lgx-vt-code { 0% { transform: rotate(0); } 35% { transform: rotate(-216deg); } 70% { transform: rotate(144deg); } 100% { transform: rotate(-36deg); } }
@keyframes lgx-vt-hd { to { transform: rotate(90deg); } }
@keyframes lgx-vt-bolt { to { transform: translate(var(--dx), var(--dy)); } }
@keyframes lgx-vt-open { to { transform: scaleX(.12) translateX(-40px); opacity: .9; } }
""")

# 23 · métal liquide -----------------------------------------------------------------------------------------------------------
V["chrome"] = (lambda on: f"""<div class="lgx lgx-chm{on}"><div class="ring"></div><div class="m"></div><i class="d a"></i><i class="d b"></i><i class="d c"></i></div>""", """
.lgx-chm .m, .lgx-chm .d, .lgx-chm .ring { position: absolute; }
.lgx-chm .m { width: 150px; height: 150px; animation: lgx-morph 6s ease-in-out infinite, lgx-float 5s ease-in-out infinite;
  background: radial-gradient(circle at 32% 26%, #fff 0 7%, transparent 9%), radial-gradient(circle at 68% 76%, rgba(255,255,255,.5) 0 5%, transparent 8%),
    conic-gradient(from 210deg, #6B7280, #F9FAFB, #9CA3AF, #E5E7EB, #4B5563, #D1D5DB, #6B7280);
  box-shadow: 0 30px 40px -24px #000, inset 0 -14px 26px rgba(0,0,0,.45), inset 0 10px 18px rgba(255,255,255,.35); }
.lgx-chm .m::after { content: ""; position: absolute; inset: 0; border-radius: inherit; mix-blend-mode: overlay; opacity: .55;
  background: linear-gradient(120deg, transparent 20%, #F0ABFC 40%, #93C5FD 55%, transparent 75%); background-size: 220% 100%; animation: lgx-chm-sheen 4s linear infinite; }
.lgx-chm .d { width: 26px; height: 26px; border-radius: 50%; opacity: 0; background: radial-gradient(circle at 35% 30%, #fff 0 12%, transparent 16%), conic-gradient(#6B7280, #F9FAFB, #9CA3AF, #E5E7EB, #6B7280); }
.lgx-chm .ring { width: 170px; height: 170px; border-radius: 50%; opacity: 0;
  background: conic-gradient(from 0deg, #6B7280, #F9FAFB, #9CA3AF, #F0ABFC, #E5E7EB, #93C5FD, #6B7280);
  -webkit-mask: radial-gradient(circle, transparent 56%, #000 58%); mask: radial-gradient(circle, transparent 56%, #000 58%); }
.lgx-chm.on .m { animation: lgx-chm-shrink 1.1s cubic-bezier(.5,0,.3,1.3) forwards; }
.lgx-chm.on .d { animation: lgx-chm-orbit 2.4s ease-in-out infinite; } .lgx-chm.on .d.b { animation-delay: -.8s; } .lgx-chm.on .d.c { animation-delay: -1.6s; }
.lgx-chm.on .ring { animation: lgx-pop .8s .6s cubic-bezier(.3,1.5,.5,1) both, lgx-rot 8s 1.4s linear infinite; }
@keyframes lgx-morph { 0%, 100% { border-radius: 42% 58% 62% 38% / 45% 40% 60% 55%; } 33% { border-radius: 60% 40% 38% 62% / 55% 60% 40% 45%; } 66% { border-radius: 38% 62% 55% 45% / 62% 45% 55% 38%; } }
@keyframes lgx-chm-shrink { 0% { transform: scale(1); } 35% { transform: scale(1.18, .82); } 100% { transform: scale(.42); border-radius: 50%; } }
@keyframes lgx-chm-orbit { 0% { opacity: 1; transform: rotate(0deg) translateX(96px) rotate(0deg); } 100% { opacity: 1; transform: rotate(360deg) translateX(96px) rotate(-360deg); } }
@keyframes lgx-chm-sheen { to { background-position: -220% 0; } }
""")

# 24 · signature ---------------------------------------------------------------------------------------------------------------
_SIG = ("M 26 196 C 34 150 58 140 60 162 C 62 188 46 202 44 186 C 42 170 88 150 94 166 C 98 180 90 198 100 190 C 110 180 112 166 118 168 "
        "C 124 172 118 194 128 190 C 138 184 140 166 148 168 C 154 170 148 192 158 188 C 168 182 170 168 178 170 C 186 172 180 192 190 188 C 200 184 206 168 216 176")
_FLOWS = "".join(f'<path d="M -20 {60 + k * 46} C 60 {30 + k * 46} 140 {100 + k * 46} 260 {50 + k * 46}" style="animation-delay:{-k * .9:.1f}s"/>' for k in range(5))
V["sign"] = (lambda on: f"""<div class="lgx lgx-sg{on}"><div class="stg"><svg viewBox="0 0 240 300" width="240" height="300"><g class="fl" fill="none" stroke-width="1.2">{_FLOWS}</g>
<line x1="20" y1="214" x2="220" y2="214" stroke="#9DBDB6" stroke-opacity=".5" stroke-dasharray="2 4"/><text x="20" y="232" font-size="8" fill="#6F938B" font-family="IBM Plex Mono, monospace" letter-spacing="2">SIGNATURE · TIMAR TANGER</text>
<path class="sig" d="{_SIG}" pathLength="100" fill="none" stroke="#F5B841" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<g class="seal"><circle cx="190" cy="96" r="30" fill="#B45309"/><circle cx="190" cy="96" r="24" fill="none" stroke="#FDE68A" stroke-width="1.5" stroke-dasharray="3 3"/>
<text x="190" y="104" text-anchor="middle" font-size="24" font-weight="800" fill="#FDE68A" font-family="Bricolage Grotesque, serif">T</text></g></svg>
<div class="pen"><svg viewBox="0 0 40 12" width="44" height="13"><polygon points="0,6 10,1 38,1 40,6 38,11 10,11" fill="#2DD4BF"/><polygon points="0,6 10,1 10,11" fill="#F5B841"/></svg></div></div></div>""", """
.lgx-sg .fl path { stroke: #2DD4BF; stroke-opacity: .28; stroke-dasharray: 30 200; animation: lgx-sg-flow 4s linear infinite; }
.lgx-sg .sig { stroke-dasharray: 100; stroke-dashoffset: 100; filter: drop-shadow(0 0 4px rgba(245,184,65,.6)); }
.lgx-sg .seal { opacity: 0; transform-box: view-box; transform-origin: 190px 96px; }
.lgx-sg .pen { position: absolute; left: 0; top: 0; offset-path: path('""" + _SIG + """'); offset-rotate: auto 180deg; offset-distance: 0%; animation: lgx-sg-idle 2.4s ease-in-out infinite; }
.lgx-sg.on .sig { animation: lgx-draw 1.9s cubic-bezier(.5,.1,.4,1) forwards; }
.lgx-sg.on .pen { animation: lgx-sg-write 1.9s cubic-bezier(.5,.1,.4,1) forwards, lgx-out .3s 2s forwards; }
.lgx-sg.on .seal { animation: lgx-sg-seal .5s 2s cubic-bezier(.2,1.6,.4,1) forwards; }
@keyframes lgx-sg-flow { from { stroke-dashoffset: 230; } to { stroke-dashoffset: 0; } }
@keyframes lgx-sg-idle { 50% { transform: translateY(-5px); } }
@keyframes lgx-sg-write { from { offset-distance: 0%; } to { offset-distance: 100%; } }
@keyframes lgx-sg-seal { from { opacity: 0; transform: scale(2.2) rotate(-20deg); } to { opacity: 1; transform: scale(1) rotate(-8deg); } }
@keyframes lgx-out { to { opacity: 0; } }
""")

# design n° -> (objet, (bouton fermé, bouton ouvert), consigne)
CONCEPTS = {
    1: ("port", ("Lever la barrière  🚧", "Baisser la barrière"), "Levez la barrière pour entrer au port"),
    2: ("orb", ("Toucher l'aurore  ✨", "Éteindre l'aurore"), "Touchez l'orbe pour vous connecter"),
    3: ("badge", ("Badger  🪪", "Retirer le badge"), "Passez votre badge pour vous connecter"),
    4: ("container", ("Ouvrir le conteneur  🔓", "Fermer le conteneur"), "Ouvrez le conteneur pour vous connecter"),
    5: ("compass", ("Tracer la route  🧭", "Effacer la route"), "Tracez la route pour vous connecter"),
    6: ("finger", ("Scanner l'empreinte  ⌁", "Effacer le scan"), "Scannez votre empreinte pour vous connecter"),
    7: ("passport", ("Tamponner  🛂", "Fermer le passeport"), "Faites tamponner votre passeport pour entrer"),
    8: ("switch", ("Entrer  →", "Sortir"), "Basculez l'interrupteur pour vous connecter"),
    9: ("lighthouse", ("Allumer le phare  🗼", "Éteindre le phare"), "Allumez le phare pour vous connecter"),
    10: ("control", ("Démarrer la machine  ⚙️", "Arrêter la machine"), "Démarrez la machine pour vous connecter"),
    11: ("ticket", ("Composter le billet  🎫", "Rendre le billet"), "Compostez votre billet pour monter à bord"),
    12: ("globe", ("Embarquer  ✈️", "Débarquer"), "Embarquez pour vous connecter"),
    13: ("constellation", ("Relier les étoiles  ✦", "Disperser les étoiles"), "Reliez les étoiles pour former la clé"),
    14: ("drop", ("Toucher la goutte  💧", "Laisser couler"), "Touchez la goutte pour vous connecter"),
    15: ("holo", ("Projeter mon badge  ◈", "Couper la projection"), "Projetez votre badge pour vous connecter"),
    16: ("crane", ("Lever le conteneur  🏗️", "Reposer le conteneur"), "Levez le conteneur pour ouvrir l'accès"),
    17: ("kasbah", ("Ouvrir la porte  🌙", "Fermer la porte"), "Ouvrez la porte de la Kasbah pour entrer"),
    18: ("scan", ("Scanner le conteneur  ⟦⟧", "Réinitialiser"), "Scannez le code du conteneur pour entrer"),
    19: ("sun", ("Lever le soleil  🌅", "Coucher le soleil"), "Levez le soleil pour vous connecter"),
    20: ("portal", ("Ouvrir le portail  🌀", "Fermer le portail"), "Ouvrez le portail pour vous connecter"),
    21: ("plane", ("Lancer l'avion  ✈︎", "Rappeler l'avion"), "Lancez l'avion en papier pour vous connecter"),
    22: ("vault", ("Ouvrir le coffre  🔐", "Refermer le coffre"), "Composez le code pour ouvrir le coffre"),
    23: ("chrome", ("Toucher le métal  ◉", "Figer le métal"), "Touchez le métal liquide pour vous connecter"),
    24: ("sign", ("Signer  ✒️", "Effacer la signature"), "Signez pour vous connecter"),
}


def _id(theme: str):
    s = ui_designs.spec(theme)
    return s[0] if s else None


def concept(theme: str) -> dict | None:
    i = _id(theme)
    if i not in CONCEPTS:
        return None
    key, btn, hint = CONCEPTS[i]
    return {"id": i, "key": key, "btn": btn, "hint": hint}


def scene(theme: str, on: bool) -> str:
    c = concept(theme)
    return V[c["key"]][0](" on" if on else "") if c else ""


def css(theme: str) -> str:
    c = concept(theme)
    if not c:
        return ""
    i = c["id"]
    return ("<style>" + COMMON_CSS + f"div.st-key-card_login {{ {CARD.get(i, '')} }}\n" + CARD_EXTRA.get(i, "") + "\n" + V[c["key"]][1] + "</style>")
