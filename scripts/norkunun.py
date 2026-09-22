#!/usr/bin/env python3
"""
norkunun.py — trae issues de Jira (solo lectura) y calcula los checks deterministas de la
auditoría. Salida en JSON para que la consuma Claude Code.

Uso:
  python3 norkunun.py login            # interactivo, correr en TU terminal (no dentro de Claude)
  python3 norkunun.py check            # verifica configuración y conexión
  python3 norkunun.py issue CLAVE-123  # issue completo + checks deterministas
  python3 norkunun.py mis-issues       # issues abiertos asignados a ti, con checks deterministas

Credenciales: ~/.config/norkunun/config.json (permisos 600). También se pueden pasar por
variables de entorno NORKUNUN_URL, NORKUNUN_USER y NORKUNUN_PASS, que tienen prioridad.
Sin dependencias externas: solo biblioteca estándar de Python 3.8+.
"""

from __future__ import annotations

import base64
import getpass
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import norkunun_rules as rules  # noqa: E402

CONFIG_DIR = Path(os.environ.get("NORKUNUN_CONFIG_DIR", Path.home() / ".config" / "norkunun"))
CONFIG_PATH = CONFIG_DIR / "config.json"
FIELDS = ("summary,description,status,issuetype,priority,assignee,reporter,comment,"
          "attachment,project,created,updated,timespent,timeoriginalestimate")


class NorkununError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- config

def load_config() -> dict:
    cfg = {}
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for key, env in (("url", "NORKUNUN_URL"), ("user", "NORKUNUN_USER"), ("password", "NORKUNUN_PASS")):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    if os.environ.get("NORKUNUN_VERIFY_SSL"):
        cfg["verify_ssl"] = os.environ["NORKUNUN_VERIFY_SSL"].lower() in ("1", "true", "si", "yes")
    missing = [k for k in ("url", "user", "password") if not cfg.get(k)]
    if missing:
        raise NorkununError("no_config", "Falta configurar credenciales ({}). Ejecuta en tu propia terminal: "
                            "python3 {} login".format(", ".join(missing), Path(__file__).resolve()))
    cfg["url"] = cfg["url"].rstrip("/")
    cfg.setdefault("verify_ssl", True)
    cfg.setdefault("internal_domains", [])
    cfg.setdefault("projects", [])
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(CONFIG_DIR, 0o700)
    except OSError:
        pass
    fd = os.open(str(CONFIG_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass


# --------------------------------------------------------------------------- http

def api_get(cfg: dict, path: str, params: dict | None = None):
    url = cfg["url"] + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    token = base64.b64encode(f"{cfg['user']}:{cfg['password']}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}", "Accept": "application/json"})
    ctx = None
    if not cfg.get("verify_ssl", True):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise NorkununError("auth", f"Jira rechazó las credenciales (HTTP {e.code}). Repite el login. "
                                "Si fallaste varias veces, Jira puede pedir CAPTCHA: entra una vez por el navegador.")
        if e.code == 404:
            raise NorkununError("not_found", "No existe o no tienes permiso para verlo.")
        body = e.read().decode("utf-8", "replace")[:300]
        raise NorkununError("http", f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLError):
            raise NorkununError("ssl", f"Error de certificado SSL: {e.reason}. Si tu Jira usa un certificado "
                                "interno, repite el login y responde 'n' a verificar SSL.")
        raise NorkununError("network", f"No se pudo conectar a Jira: {e.reason}")


# --------------------------------------------------------------------------- comandos

def cmd_login() -> dict:
    if not sys.stdin.isatty():
        raise NorkununError("not_tty", "El login es interactivo: ejecútalo en tu propia terminal, no dentro de "
                            f"Claude Code:  python3 {Path(__file__).resolve()} login")
    old = {}
    if CONFIG_PATH.exists():
        old = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def ask(label: str, default: str = "") -> str:
        v = input(f"{label}{f' [{default}]' if default else ''}: ").strip()
        return v or default

    print("Configuración de Norkunun (se guarda solo en este equipo, en %s)\n" % CONFIG_PATH)
    cfg = {
        "url": ask("URL de Jira (ej: https://jira.miempresa.com)", old.get("url", "")).rstrip("/"),
        "user": ask("Usuario de Jira", old.get("user", "")),
    }
    pw = getpass.getpass("Password de Jira (no se muestra; Enter = mantener la actual): ")
    cfg["password"] = pw or old.get("password", "")
    cfg["verify_ssl"] = ask("¿Verificar certificado SSL? (s/n)", "s" if old.get("verify_ssl", True) else "n").lower().startswith("s")
    doms = ask("Dominios de correo internos de tu empresa, separados por coma (para distinguir clientes)",
               ",".join(old.get("internal_domains", [])))
    cfg["internal_domains"] = [d.strip().lower() for d in doms.split(",") if d.strip()]
    projs = ask("Proyectos a revisar en mis-issues, separados por coma (Enter = todos)",
                ",".join(old.get("projects", [])))
    cfg["projects"] = [p.strip().upper() for p in projs.split(",") if p.strip()]

    if not cfg["url"] or not cfg["user"] or not cfg["password"]:
        raise NorkununError("no_config", "URL, usuario y password son obligatorios.")
    me = api_get(cfg, "/rest/api/2/myself")
    save_config(cfg)
    return {"ok": True, "usuario": me.get("displayName") or me.get("name"), "config": str(CONFIG_PATH)}


def cmd_check() -> dict:
    cfg = load_config()
    me = api_get(cfg, "/rest/api/2/myself")
    return {"ok": True, "usuario": me.get("displayName") or me.get("name"), "login": me.get("name"),
            "proyectos": cfg["projects"] or "todos", "dominios_internos": cfg["internal_domains"]}


def _summarize(issue: dict, cfg: dict, full: bool) -> dict:
    f = issue["fields"]
    ext = rules.extract_deterministic(f, set(cfg["internal_domains"]))
    required = rules.required_checks(f, ext)
    det = rules.deterministic_checks(f, ext)
    skip, _ = rules.flags(f)
    status = f.get("status") or {}
    out = {
        "key": issue["key"],
        "url": f"{cfg['url']}/browse/{issue['key']}",
        "summary": f.get("summary"),
        "tipo": (f.get("issuetype") or {}).get("name"),
        "estado": status.get("name"),
        "en_curso": rules.is_in_progress(f),
        "asignado": (f.get("assignee") or {}).get("displayName") or "Sin asignar",
        "horas_imputadas": round((f.get("timespent") or 0) / 3600, 2),
        "horas_estimadas": round((f.get("timeoriginalestimate") or 0) / 3600, 2),
        "excluido_noauditar": skip,
        "es_respaldo": ext["is_respaldo"],
        "checks_requeridos": list(required),
        "checks_deterministas": {k: v for k, v in det.items() if k in required},
        "checks_para_llm": [k for k in required if k not in rules.DETERMINISTIC],
        "extraido": ext,
    }
    if full:
        out.update({
            "prioridad": (f.get("priority") or {}).get("name"),
            "reporter": (f.get("reporter") or {}).get("displayName"),
            "creado": (f.get("created") or "")[:10],
            "actualizado": (f.get("updated") or "")[:10],
            "descripcion": f.get("description") or "",
            "comentarios": rules.comments(f),
            "adjuntos": [a.get("filename") for a in (f.get("attachment") or [])],
        })
    return out


def cmd_issue(key: str) -> dict:
    cfg = load_config()
    issue = api_get(cfg, f"/rest/api/2/issue/{urllib.parse.quote(key.upper())}", {"fields": FIELDS})
    return _summarize(issue, cfg, full=True)


def cmd_mis_issues() -> dict:
    cfg = load_config()
    jql = "assignee = currentUser() AND statusCategory != Done"
    if cfg["projects"]:
        jql += " AND project in ({})".format(", ".join(cfg["projects"]))
    jql += " ORDER BY updated DESC"
    data = api_get(cfg, "/rest/api/2/search", {"jql": jql, "fields": FIELDS, "maxResults": 100})
    issues = [_summarize(i, cfg, full=False) for i in data.get("issues", [])]
    return {"total": data.get("total", len(issues)), "jql": jql, "issues": issues}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, args = argv[0], argv[1:]
    try:
        if cmd == "login":
            result = cmd_login()
        elif cmd == "check":
            result = cmd_check()
        elif cmd == "issue" and len(args) == 1:
            result = cmd_issue(args[0])
        elif cmd == "mis-issues":
            result = cmd_mis_issues()
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except NorkununError as e:
        print(json.dumps({"ok": False, "error": e.code, "mensaje": str(e)}, ensure_ascii=False, indent=2))
        return 1
    except KeyboardInterrupt:
        return 130
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
