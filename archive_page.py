# -*- coding: utf-8 -*-
"""Pages : ARCHIVE (dossiers générés, recherche par n° de DUM / BL / facture / client), journal d'activité et tableau de bord (Admin)."""

from __future__ import annotations

import time

import pandas as pd
import streamlit as st

import archive

MODULES = ["Tous", "IMPORT", "EXPORT", "DÉCHARGE"]
MIME = {"xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "zip": "application/zip", "csv": "text/csv", "pdf": "application/pdf"}


def render(user: dict):
    admin = user.get("role") == "admin"
    import ui
    ui.hero_3d(None, badge="TIMAR TANGER · ARCHIVE", title="Archive", highlight="dossiers générés",
               desc="Chaque dossier traité (IMPORT, EXPORT, DÉCHARGE) est gardé ici automatiquement avec ses fichiers Excel. "
                    "Cherchez par n° de facture, BL, DUM, client…"
                    + (" Vous voyez les dossiers de tous les utilisateurs." if admin else " Vous ne voyez que vos dossiers."))
    c1, c2, c3 = st.columns([2.2, 1, 1.4])
    q = c1.text_input("Rechercher", placeholder="Ex. FCM3625 · 803879400 · ALSTOM VALENCIENNES · 0003729", key="arch_q")
    mod = c2.selectbox("Module", MODULES, key="arch_mod")
    who = c3.text_input("Utilisateur", key="arch_who", placeholder="e-mail (Admin)") if admin else ""
    rows = archive.search(q, "" if mod == "Tous" else mod, None if admin else user["email"], limit=200)
    if admin and who.strip():
        rows = [r for r in rows if who.strip().lower() in (r.get("email") or "")]
    if not rows:
        st.info("Aucun dossier archivé" + (" pour cette recherche." if (q or mod != 'Tous') else " pour le moment : générez un dossier (IMPORT / EXPORT / DÉCHARGE), il apparaîtra ici."))
        return
    df = pd.DataFrame([{"Date": r["date"], "Module": r["module"], "Dossier": r["title"], "Utilisateur": r["email"], "Fichiers": len(r["files"]),
                        "Valeur": r["meta"].get("valeur")} for r in rows])
    ev = st.dataframe(df, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", key="arch_tbl",
                      column_config={"Valeur": st.column_config.NumberColumn(format="%.2f")})
    st.caption(f"{len(rows)} dossier(s) — cochez la case à gauche d'une ligne pour voir et télécharger ses fichiers.")
    sel = (ev.selection.rows if ev and getattr(ev, "selection", None) else []) or []
    if not sel:
        return
    r = rows[sel[0]]
    with st.container(border=True):
        st.markdown(f"**{r['title']}**  \n{r['module']} · {r['date']} · {r['email']}")
        m = r["meta"]
        facts = [f"{m[k]:,.0f} {lab}".replace(",", " ") if k in ("net", "brut", "colis") else f"{m[k]:,.2f} {lab}".replace(",", " ")
                 for k, lab in (("valeur", "de valeur"), ("net", "kg net"), ("brut", "kg brut"), ("colis", "colis")) if isinstance(m.get(k), (int, float))]
        if facts:
            st.caption(" · ".join(facts))
        if r["keys"]:
            st.caption("Références : " + " · ".join(r["keys"][:40]) + (" …" if len(r["keys"]) > 40 else ""))
        cols = st.columns(min(3, max(1, len(r["files"]))))
        for i, name in enumerate(r["files"]):
            data = archive.file(r["id"], name, None if admin else user["email"])
            if data is None:
                cols[i % len(cols)].caption(f"{name} : fichier introuvable")
                continue
            ext = name.rsplit(".", 1)[-1].lower()
            cols[i % len(cols)].download_button(name, data=data, file_name=name, mime=MIME.get(ext, "application/octet-stream"), icon=":material/download:",
                                                key=f"arch_dl_{r['id']}_{i}", use_container_width=True,
                                                on_click=lambda n=name: archive.log(user["email"], "download", f"archive #{r['id']} · {n}"))
        if st.button("Supprimer ce dossier de l'archive", icon=":material/delete:", key=f"arch_del_{r['id']}"):
            archive.delete(r["id"], None if admin else user["email"])
            archive.log(user["email"], "delete", f"archive #{r['id']} · {r['title']}")
            st.rerun()


def render_journal():
    st.markdown("#### Journal d'activité")
    c1, c2, c3 = st.columns([1.5, 1, 1])
    who = c1.text_input("Utilisateur (e-mail ou partie)", key="jr_who")
    act = c2.selectbox("Action", ["Toutes"] + list(archive.ACTIONS.values()), key="jr_act")
    per = c3.selectbox("Période", ["24 h", "7 jours", "30 jours", "Tout"], index=1, key="jr_per")
    since = {"24 h": 86400, "7 jours": 7 * 86400, "30 jours": 30 * 86400}.get(per)
    code = next((k for k, v in archive.ACTIONS.items() if v == act), "")
    rows = archive.activity(1000, who.strip(), code, time.time() - since if since else None)
    if not rows:
        st.info("Aucune activité pour ces filtres.")
        return
    df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    st.dataframe(df, use_container_width=True, hide_index=True, height=480)
    st.caption(f"{len(rows)} événement(s) (les 1000 plus récents) — seules les actions faites **dans le site** sont enregistrées.")
    st.download_button("Télécharger le journal (CSV)", data=df.to_csv(sep=";", index=False).encode("utf-8-sig"), file_name="JOURNAL_ACTIVITE.csv",
                       mime="text/csv", icon=":material/download:", key="jr_dl")


def render_dashboard():
    st.markdown("#### Tableau de bord")
    days = st.selectbox("Période", [30, 90, 180, 365], index=2, format_func=lambda d: f"{d} derniers jours", key="db_days")
    s = archive.stats(days)
    c = st.columns(4)
    c[0].metric("Dossiers archivés", s["dossiers"])
    c[1].metric("Utilisateurs actifs", s["active_users"])
    c[2].metric("Connexions refusées", s["login_failed"])
    c[3].metric("Modules", ", ".join(f"{k} {v}" for k, v in s["by_module"].items()) or "—")
    if not s["dossiers"]:
        st.info("Pas encore de dossier archivé sur cette période.")
        return
    a, b = st.columns(2)
    with a:
        st.caption("Dossiers par mois")
        st.bar_chart(pd.Series(s["by_month"], name="dossiers"))
    with b:
        st.caption("Valeur traitée par mois (devise du dossier, tous modules)")
        if s["value_by_month"]:
            st.bar_chart(pd.Series(s["value_by_month"], name="valeur"))
    a, b = st.columns(2)
    with a:
        st.caption("Utilisateurs les plus actifs (dossiers)")
        st.dataframe(pd.DataFrame({"Utilisateur": list(s["by_user"]), "Dossiers": list(s["by_user"].values())}), hide_index=True, use_container_width=True)
    with b:
        st.caption("Connexions par jour")
        if s["logins_by_day"]:
            st.bar_chart(pd.Series(s["logins_by_day"], name="connexions"))
