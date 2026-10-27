# -*- coding: utf-8 -*-
"""Mémoire des lettres de compte : n° de compte (17 chiffres) -> lettre de contrôle (ex. 41102320250014953 -> D).

La lettre qui termine un compte / une déclaration est calculée par BADR (le site ne peut pas la deviner avec certitude) ; mais un même compte revient
dans plusieurs dossiers. Dès qu'une lettre est connue — lue dans une fiche d'imputation, saisie une fois dans DÉCHARGE ou importée d'une liste —
elle est mémorisée (base du site, sauvegardée sur Supabase) et reprise automatiquement ensuite."""

from __future__ import annotations

import re
import time

import database

SCHEMA = """
CREATE TABLE IF NOT EXISTS compte_letters (
    compte TEXT PRIMARY KEY, letter TEXT NOT NULL, source TEXT, email TEXT, ts REAL NOT NULL
);
"""
_READY = {"db": None}


# ----------------------------------------------------------------------------- calcul de la lettre (formule déduite de comptes réels)
ALPHABET = "ABCDEFGHJKLMNPRSTUVWXYZ"           # 23 lettres : ni I, ni O, ni Q


def compute_letter(compte: str) -> str:
    """Lettre de contrôle d'un compte de 17 chiffres (bureau 3 · régime 3 · année 4 · n° d'ordre 7).

    Formule retrouvée sur 13 numéros réels (comptes d'imputation et déclarations, 5 régimes, 2 bureaux, 3 années) :
        lettre = ALPHABET[ (régime × 10⁶ + n° d'ordre) mod 23 ]
    Le bureau et l'année n'interviennent pas. Si BADR donne une lettre différente, la lettre saisie est mémorisée et prime sur le calcul."""
    d = digits(compte)
    if len(d) != 17:
        return ""
    return ALPHABET[(int(d[3:6]) * 10 ** 6 + int(d[10:17])) % 23]


def check_formula(pairs: dict) -> tuple[int, int, list[str]]:
    """Vérifie la formule sur des comptes dont la lettre est connue : (bons, total, comptes en désaccord)."""
    ok, bad = 0, []
    for c, l in pairs.items():
        d = digits(c)
        if len(d) == 17 and l:
            if compute_letter(d) == str(l).upper():
                ok += 1
            else:
                bad.append(d + str(l).upper())
    return ok, ok + len(bad), bad


def digits(compte: str) -> str:
    return re.sub(r"\D", "", str(compte or ""))


def _ensure(con):
    if _READY["db"] != str(database.DB_PATH):
        con.executescript(SCHEMA)
        _READY["db"] = str(database.DB_PATH)


def known(comptes) -> dict[str, str]:
    """{chiffres du compte: lettre} pour les comptes déjà connus."""
    ds = list(dict.fromkeys(d for d in (digits(c) for c in comptes) if d))
    if not ds:
        return {}
    out: dict[str, str] = {}
    try:
        with database.connect() as con:
            _ensure(con)
            for i in range(0, len(ds), 400):
                chunk = ds[i:i + 400]
                rows = con.execute(f"SELECT compte, letter FROM compte_letters WHERE compte IN ({','.join('?' * len(chunk))})", chunk).fetchall()
                out.update({r["compte"]: r["letter"] for r in rows})
    except Exception:  # noqa: BLE001
        pass
    return out


def remember(pairs: dict, source: str = "", email: str = "") -> int:
    """pairs : {compte: lettre}. N'écrit que les paires nouvelles ou modifiées ; renvoie leur nombre."""
    clean = {}
    for c, l in pairs.items():
        d, l = digits(c), str(l or "").strip().upper()
        if len(d) >= 10 and re.fullmatch(r"[A-Z]", l):
            clean[d] = l
    if not clean:
        return 0
    n = 0
    try:
        cur = known(clean)
        with database.connect() as con:
            _ensure(con)
            for d, l in clean.items():
                if cur.get(d) == l:
                    continue
                con.execute("INSERT INTO compte_letters (compte, letter, source, email, ts) VALUES (?,?,?,?,?) "
                            "ON CONFLICT(compte) DO UPDATE SET letter=excluded.letter, source=excluded.source, email=excluded.email, ts=excluded.ts",
                            (d, l, source[:120], (email or "").lower(), time.time()))
                n += 1
    except Exception:  # noqa: BLE001
        return 0
    return n


def parse_pairs(text: str) -> dict[str, str]:
    """Lignes « 411 023 2025 0014953 D » / « 41102320250014953D » / « 41102320250014953;D » -> {chiffres: lettre}."""
    out = {}
    for ln in str(text or "").splitlines():
        m = re.search(r"((?:\d[\s.\-]?){13,17})\s*[;,\t :\-]?\s*([A-Za-z])\b", ln)
        if m:
            out[digits(m.group(1))] = m.group(2).upper()
    return out


def listing(query: str = "", limit: int = 1000) -> list[dict]:
    q, args = "SELECT * FROM compte_letters WHERE 1=1", []
    for w in re.findall(r"\S+", query or ""):
        q += " AND (compte LIKE ? OR letter=? OR source LIKE ?)"
        args += [f"%{digits(w) or w}%", w.upper(), f"%{w}%"]
    q += " ORDER BY ts DESC LIMIT ?"
    args.append(limit)
    with database.connect() as con:
        _ensure(con)
        rows = con.execute(q, args).fetchall()
    return [dict(r) for r in rows]


def remove(compte: str) -> bool:
    with database.connect() as con:
        _ensure(con)
        return con.execute("DELETE FROM compte_letters WHERE compte=?", (digits(compte),)).rowcount > 0


def all_pairs() -> dict[str, str]:
    try:
        with database.connect() as con:
            _ensure(con)
            return {r["compte"]: r["letter"] for r in con.execute("SELECT compte, letter FROM compte_letters").fetchall()}
    except Exception:  # noqa: BLE001
        return {}


def count() -> int:
    with database.connect() as con:
        _ensure(con)
        return con.execute("SELECT COUNT(*) FROM compte_letters").fetchone()[0]
