# -*- coding: utf-8 -*-
"""Colle entre les modules (IMPORT / EXPORT / DÉCHARGE) et archive.py : chaque appel est idempotent et ne peut jamais bloquer l'application.
Un « dossier » = un traitement lancé (identifié par un identifiant de session) ; les modifications / fichiers générés ensuite complètent la même entrée."""

from __future__ import annotations

import hashlib
import uuid

import streamlit as st

import archive


def me() -> str:
    u = st.session_state.get("auth_user") or {}
    return (u.get("email") or "").lower()


def new_run(kind: str) -> str:
    """Nouveau traitement lancé : identifiant du dossier d'archive (3 modules : imp / exp / dch)."""
    run = f"{kind}-{uuid.uuid4().hex[:12]}"
    st.session_state[f"arch_run_{kind}"] = run
    return run


def _run(kind: str) -> str:
    return st.session_state.get(f"arch_run_{kind}") or new_run(kind)


def _sig(files: dict) -> str:
    h = hashlib.sha1()
    for n in sorted(files):
        h.update(n.encode())
        h.update(hashlib.sha1(files[n]).digest())
    return h.hexdigest()


def generated(module: str, detail: str):
    archive.log(me(), "generate", f"{module} · {detail}")


def save(kind: str, module: str, title: str, keys: list, meta: dict, files: dict):
    """Archive si le contenu a changé depuis le dernier appel de cette session (évite d'écrire à chaque rerun)."""
    try:
        files = {n: d for n, d in files.items() if d}
        if not files:
            return
        run = _run(kind)
        seen = st.session_state.setdefault("arch_seen", {})
        s = _sig(files)
        if seen.get(run) == s:
            return
        archive.save(me(), module, title, keys, meta, files, run)
        seen[run] = s
    except Exception:  # noqa: BLE001
        pass


def export_done(fact_df, bl_df, rep: dict | None, files: dict):
    import pandas as pd
    try:
        inv = [str(x) for x in fact_df["Numéro de facture"].dropna()]
        clients = [str(x) for x in fact_df["Nom du fournisseur ou client"].dropna().unique()]
        bls = [str(x) for x in bl_df["BL Number (Bon de Livraison)"].dropna().unique()]
        num = lambda c: float(pd.to_numeric(bl_df[c], errors="coerce").sum())  # noqa: E731
        meta = {"factures": len(inv), "bl": len(bls), "valeur": float(pd.to_numeric(fact_df["Montant en devise"], errors="coerce").sum()),
                "net": num("Total Net Weight of the BL"), "brut": num("Total Gross Weight of the BL"),
                "colis": num("Number of Packages (Nombre de Colis)")}
        title = "EXPORT · " + (", ".join(clients[:2]) or "dossier") + f" · {len(inv)} facture(s)"
        save("exp", "EXPORT", title, inv + bls + clients, meta, files)
    except Exception:  # noqa: BLE001
        pass


def ventilation_done(kind: str, data: dict, dest: str):
    """Fichiers VENTILATION / ANNEXE générés : ajoutés au dossier d'archive en cours (EXPORT « exp », IMPORT « imp »)."""
    try:
        suffix = "IMPORT" if kind == "imp" else "DUM"
        files = {f"VENTILATION_{suffix}.xlsx": data.get("bytes"), f"ANNEXE_{suffix}.xlsx": data.get("annexe")}
        run = _run(kind)
        seen = st.session_state.setdefault("arch_seen_vent", {})
        files = {n: d for n, d in files.items() if d}
        s = _sig(files)
        if not files or seen.get(run) == s:
            return
        arch = archive.get_by_sig(run)
        title = arch["title"] if arch else f"{'IMPORT' if kind == 'imp' else 'EXPORT'} · ventilation"
        archive.save(me(), "IMPORT" if kind == "imp" else "EXPORT", title, [dest, f"DUM {dest}"], {"ventilation": True}, files, run)
        seen[run] = s
    except Exception:  # noqa: BLE001
        pass


def import_done(final_df, files: dict, result: dict | None = None):
    import pandas as pd
    try:
        cl = [str(x) for x in final_df["Client"].dropna().unique()] if "Client" in final_df else []
        inv = [str(x) for x in final_df["N° facture"].dropna().unique()] if "N° facture" in final_df else []
        val = float(pd.to_numeric(final_df["Valeur HT"], errors="coerce").sum()) if "Valeur HT" in final_df else 0.0
        meta = {"clients": len(cl), "factures": len(inv), "lignes": len(final_df), "valeur": val}
        title = "IMPORT · " + (", ".join(cl[:3]) or "dossier") + (f" (+{len(cl) - 3})" if len(cl) > 3 else "")
        save("imp", "IMPORT", title, inv + cl, meta, files)
    except Exception:  # noqa: BLE001
        pass


def decharge_done(title: str, keys: list, meta: dict, files: dict):
    save("dch", "DÉCHARGE", title, keys, meta, files)
