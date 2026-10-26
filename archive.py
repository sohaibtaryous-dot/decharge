# -*- coding: utf-8 -*-
"""Journal d'activité + archive des dossiers (recherche par n° de DUM, BL, facture, client…).

  log(email, action, detail)             : une ligne dans le journal (connexion, génération, téléchargement…)
  save(email, module, title, keys, …)    : archive un dossier (fichiers générés) — idempotent grâce à `sig` ; les fichiers générés plus tard
                                           (ventilation, annexe…) s'ajoutent au même dossier
  search(...), file(...), delete(...)    : consultation (un utilisateur ne voit que ses dossiers, l'Admin voit tout)
Tout est dans la base SQLite du site (sauvegardée sur Supabase si configuré) ; les fichiers sont gardés dans data/archive/<id>/ et copiés sur
Supabase en arrière-plan (la génération ne ralentit pas)."""

from __future__ import annotations

import json
import re
import threading
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import database
import persist

SCHEMA = """
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, email TEXT, action TEXT NOT NULL, detail TEXT
);
CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity(ts);
CREATE TABLE IF NOT EXISTS archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, email TEXT, module TEXT, title TEXT,
    keys TEXT, meta TEXT, files TEXT, sig TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_archive_ts ON archive(ts);
"""
_READY = {"db": None}
MAX_ACTIVITY = 20000
ACTIONS = {"login": "Connexion", "login_failed": "Connexion refusée", "logout": "Déconnexion", "signup": "Inscription",
           "approve": "Compte approuvé", "dispatch": "Dossier attribué", "generate": "Génération", "download": "Téléchargement",
           "archive": "Archivage", "delete": "Suppression"}


def _dir() -> Path:
    return Path(database.DATA_DIR) / "archive"


def _ensure(con):
    if _READY["db"] != str(database.DB_PATH):
        con.executescript(SCHEMA)
        _READY["db"] = str(database.DB_PATH)


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._\- ]", "_", Path(name).name) or "fichier"


def _rel(p: Path) -> str:
    return Path(p).resolve().relative_to(Path(database.DATA_DIR).resolve()).as_posix()


# ----------------------------------------------------------------------------- journal
def log(email: str, action: str, detail: str = ""):
    """Ne doit jamais faire échouer l'application : toute erreur est ignorée."""
    try:
        with database.connect() as con:
            _ensure(con)
            con.execute("INSERT INTO activity (ts, email, action, detail) VALUES (?,?,?,?)",
                        (time.time(), (email or "").lower(), action, (detail or "")[:500]))
            n = con.execute("SELECT COUNT(*) FROM activity").fetchone()[0]
            if n > MAX_ACTIVITY:
                con.execute("DELETE FROM activity WHERE id IN (SELECT id FROM activity ORDER BY id LIMIT ?)", (n - MAX_ACTIVITY,))
    except Exception:  # noqa: BLE001
        pass


def activity(limit: int = 500, email: str = "", action: str = "", since: float | None = None) -> list[dict]:
    q, args = "SELECT * FROM activity WHERE 1=1", []
    if email:
        q += " AND email LIKE ?"
        args.append(f"%{email.lower()}%")
    if action:
        q += " AND action=?"
        args.append(action)
    if since:
        q += " AND ts>=?"
        args.append(since)
    q += " ORDER BY id DESC LIMIT ?"
    args.append(int(limit))
    with database.connect() as con:
        _ensure(con)
        rows = con.execute(q, args).fetchall()
    return [{"Date": datetime.fromtimestamp(r["ts"]).strftime("%d/%m/%Y %H:%M:%S"), "Utilisateur": r["email"],
             "Action": ACTIONS.get(r["action"], r["action"]), "Détail": r["detail"] or "", "_ts": r["ts"], "_action": r["action"]} for r in rows]


# ----------------------------------------------------------------------------- archive
def _row(r) -> dict:
    d = dict(r)
    for k, default in (("keys", []), ("meta", {}), ("files", {})):
        try:
            d[k] = json.loads(d.get(k) or json.dumps(default))
        except json.JSONDecodeError:
            d[k] = default
    d["date"] = datetime.fromtimestamp(d["ts"]).strftime("%d/%m/%Y %H:%M")
    return d


def _upload(items: list[tuple[str, bytes]]):
    def run():
        for key, data in items:
            try:
                persist.put_file(key, data)
            except Exception:  # noqa: BLE001
                pass
    if items and persist.enabled():
        threading.Thread(target=run, daemon=True).start()


def save(email: str, module: str, title: str, keys: list[str], meta: dict, files: dict[str, bytes], sig: str) -> int | None:
    """Archive (ou complète) le dossier identifié par `sig`. Renvoie son id."""
    try:
        keys = [k for k in dict.fromkeys(str(x).strip() for x in keys if str(x).strip())][:400]
        with database.connect() as con:
            _ensure(con)
            r = con.execute("SELECT * FROM archive WHERE sig=?", (sig,)).fetchone()
            if r:
                d = _row(r)
                aid, cur_files, cur_keys, cur_meta = d["id"], d["files"], d["keys"], d["meta"]
            else:
                cur = con.execute("INSERT INTO archive (ts, email, module, title, keys, meta, files, sig) VALUES (?,?,?,?,?,?,?,?)",
                                  (time.time(), (email or "").lower(), module, title, "[]", "{}", "{}", sig))
                aid, cur_files, cur_keys, cur_meta = cur.lastrowid, {}, [], {}
            folder = _dir() / str(aid)
            folder.mkdir(parents=True, exist_ok=True)
            up = []
            for name, data in files.items():
                n = _safe(name)
                p = folder / n
                if n in cur_files and p.is_file() and p.stat().st_size == len(data) and p.read_bytes() == data:
                    continue                                              # déjà archivé, identique
                p.write_bytes(data)
                cur_files[n] = len(data)
                up.append((_rel(p), data))
            merged_keys = list(dict.fromkeys(cur_keys + keys))[:600]
            cur_meta.update(meta or {})
            con.execute("UPDATE archive SET title=?, keys=?, meta=?, files=? WHERE id=?",
                        (title or "", json.dumps(merged_keys, ensure_ascii=False), json.dumps(cur_meta, ensure_ascii=False, default=str),
                         json.dumps(cur_files), aid))
        _upload(up)
        if up:
            log(email, "archive", f"{title if title.startswith(module) else module + ' · ' + title} · {len(up)} fichier(s)")
        return aid
    except Exception:  # noqa: BLE001
        return None


def search(query: str = "", module: str = "", email: str | None = None, limit: int = 200) -> list[dict]:
    """email=None : tous les dossiers (Admin) ; sinon uniquement ceux de cet utilisateur. `query` : mots (tous doivent apparaître)."""
    q, args = "SELECT * FROM archive WHERE 1=1", []
    if email is not None:
        q += " AND email=?"
        args.append(email.lower())
    if module:
        q += " AND module=?"
        args.append(module)
    for w in re.findall(r"\S+", query or ""):
        q += " AND (title LIKE ? OR keys LIKE ? OR email LIKE ? OR module LIKE ?)"
        args += [f"%{w}%"] * 4
    q += " ORDER BY ts DESC LIMIT ?"
    args.append(int(limit))
    with database.connect() as con:
        _ensure(con)
        rows = con.execute(q, args).fetchall()
    return [_row(r) for r in rows]


def get_by_sig(sig: str) -> dict | None:
    with database.connect() as con:
        _ensure(con)
        r = con.execute("SELECT * FROM archive WHERE sig=?", (sig,)).fetchone()
    return _row(r) if r else None


def get(aid: int, email: str | None = None) -> dict | None:
    with database.connect() as con:
        _ensure(con)
        r = con.execute("SELECT * FROM archive WHERE id=?", (int(aid),)).fetchone()
    if not r:
        return None
    d = _row(r)
    if email is not None and (d.get("email") or "") != email.lower():
        return None
    return d


def file(aid: int, name: str, email: str | None = None) -> bytes | None:
    d = get(aid, email)
    if not d or _safe(name) not in d["files"]:
        return None
    p = _dir() / str(int(aid)) / _safe(name)
    if not p.is_file():                                                  # disque effacé : copie Supabase
        data = persist.get_file(_rel(p))
        if data is None:
            return None
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return p.read_bytes()


def delete(aid: int, email: str | None = None) -> bool:
    d = get(aid, email)
    if not d:
        return False
    for n in d["files"]:
        p = _dir() / str(int(aid)) / n
        try:
            persist.delete_file(_rel(p))
            p.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
    try:
        (_dir() / str(int(aid))).rmdir()
    except OSError:
        pass
    with database.connect() as con:
        _ensure(con)
        con.execute("DELETE FROM archive WHERE id=?", (int(aid),))
    return True


# ----------------------------------------------------------------------------- statistiques (tableau de bord)
def stats(days: int = 180) -> dict:
    since = time.time() - days * 86400
    with database.connect() as con:
        _ensure(con)
        arch = [_row(r) for r in con.execute("SELECT * FROM archive WHERE ts>=? ORDER BY ts", (since,)).fetchall()]
        acts = con.execute("SELECT ts, email, action FROM activity WHERE ts>=?", (since,)).fetchall()
    by_month, by_module, by_user, value = Counter(), Counter(), Counter(), Counter()
    for a in arch:
        m = datetime.fromtimestamp(a["ts"]).strftime("%Y-%m")
        by_month[m] += 1
        by_module[a["module"]] += 1
        by_user[a["email"]] += 1
        v = a["meta"].get("valeur")
        if isinstance(v, (int, float)):
            value[m] += float(v)
    logins = Counter(datetime.fromtimestamp(r["ts"]).strftime("%Y-%m-%d") for r in acts if r["action"] == "login")
    failed = sum(1 for r in acts if r["action"] == "login_failed")
    return {"dossiers": len(arch), "by_month": dict(sorted(by_month.items())), "by_module": dict(by_module), "by_user": dict(by_user.most_common(10)),
            "value_by_month": dict(sorted(value.items())), "logins_by_day": dict(sorted(logins.items())), "login_failed": failed,
            "active_users": len({r["email"] for r in acts if r["action"] == "login"})}
