"""
norkunun_rules.py
-----------------
Reglas deterministas de la auditoría de issues: solicitante, medio/origen, plan de trabajo,
horas y la regla especial de issues de "respaldo".

Trabaja sobre el JSON crudo de la API REST de Jira (`issue["fields"]`), sin dependencias
externas, para que lo puedan usar tanto el bot de auditoría central como el script local de
cada usuario. Los criterios que requieren juicio (detalle, objetivo, ITIL, coherencia,
desarrollo) están descritos en `reference/criterios.md` y los evalúa un LLM.
"""

from __future__ import annotations

import re

CHECK_LABELS = {
    "solicitante": "solicitante",
    "origen": "origen/medio",
    "detalle": "detalle",
    "objetivo": "objetivo",
    "itil": "cuadro ITIL",
    "coherencia": "coherencia",
    "plan": "plan de trabajo",
    "desarrollo": "desarrollo",
    "horas": "horas imputadas",
}
ORDER = tuple(CHECK_LABELS)

REQUIRED_TODO = ("solicitante", "origen", "detalle", "objetivo", "itil", "coherencia")
REQUIRED_IN_PROGRESS = REQUIRED_TODO + ("plan", "desarrollo", "horas")
DETERMINISTIC = ("solicitante", "origen", "plan", "horas")

# Coherencia: % de sub-checks "ok" sobre (ok + no) necesario para aprobar.
COH_MIN = 75

DEFAULT_BOT_AUTHORS = {"Jira Admin"}

_WROTE_RE = re.compile(r"^[ \t]*(?:\d{1,2}/\d{1,2}/\d{2,4}[^\n-]*-\s*)?(?P<name>[^\n]{3,80}?)\s+wrote:", re.M)
_FROM_RE = re.compile(r"^[ \t*]*(?:De|From)\s*:\**\s*(?P<name>[^<\n]{3,80}?)\s*<(?P<email>[^>\n]+)>", re.M | re.I)
_MAIL_HDR_RE = re.compile(r"^[ \t*]*(?:De|From|Enviado|Sent|Asunto|Subject)\s*:", re.M | re.I)
_LABEL_RE = re.compile(r"^[ \t]*(?:solicitante|solicita|cliente|requirente)\s*:\s*(?P<v>.+)$", re.M | re.I)
_EMAIL_RE = re.compile(r"[\w.+-]+@(?P<d>[\w-]+(?:\.[\w-]+)+)")
_TEAM_RE = re.compile(r"(oficina|subdirecci[oó]n|departamento|unidad|gerencia|[aá]rea|divisi[oó]n|equipo)", re.I)
_TICKET_RE = re.compile(r"Ticket\s*#?\s*(\d{8,})", re.I)
_PLAN_FILE_RE = re.compile(r"(plan|trabajo|pdt|cronograma|gantt|carta)", re.I)
_PLAN_TEXT_RE = re.compile(r"(plan de trabajo|\bPDT\b|cronograma|carta gantt)", re.I)
_RESPALDO_RE = re.compile(r"respaldo", re.I)
_BKP_FILE_RE = re.compile(r"(bkp|backup|\.tar(\.gz)?$|\.tgz$|\.gz$)", re.I)
_IMG_FILE_RE = re.compile(r"\.(png|jpe?g|gif|bmp|webp)$", re.I)
_HOST_TABLE_RE = re.compile(r"(host|servidor)[^\n]{0,40}(respaldo|backup|bkp)|(respaldo|backup|bkp)[^\n]{0,40}\bhost\b", re.I)
_FLAG_AUDIT = re.compile(r"\[AUDITAR\]", re.I)
_FLAG_SKIP = re.compile(r"\[NOAUDITAR\]", re.I)


def _all_comments(fields: dict) -> list[dict]:
    return ((fields.get("comment") or {}).get("comments")) or []


def comments(fields: dict, bot_authors: set[str] = DEFAULT_BOT_AUTHORS) -> list[dict]:
    """Comentarios humanos, sin bots ni comentarios que solo llevan flags de auditoría."""
    out = []
    for c in _all_comments(fields):
        author = (c.get("author") or {}).get("displayName", "") or ""
        if author in bot_authors:
            continue
        body = c.get("body") or ""
        if _FLAG_AUDIT.search(body) or _FLAG_SKIP.search(body):
            continue
        out.append({"author": author, "created": (c.get("created") or "")[:10], "body": body})
    return out


def flags(fields: dict) -> tuple[bool, str | None]:
    """(excluido por [NOAUDITAR], fecha del último [AUDITAR])."""
    skip, force = False, None
    for c in _all_comments(fields):
        body = c.get("body") or ""
        if _FLAG_SKIP.search(body):
            skip = True
        if _FLAG_AUDIT.search(body):
            force = max(force or "", (c.get("created") or "")[:19])
    return skip, force


def extract_deterministic(fields: dict, internal_domains: set[str] = frozenset(),
                          bot_authors: set[str] = DEFAULT_BOT_AUTHORS) -> dict:
    desc = fields.get("description") or ""
    summary = fields.get("summary") or ""
    all_text = desc + "\n" + "\n".join(c["body"] for c in comments(fields, bot_authors))
    attachment_names = [a.get("filename", "") for a in (fields.get("attachment") or [])]

    nombre = cliente = equipo = None
    fm = _FROM_RE.search(desc) or _FROM_RE.search(all_text)
    m = None if fm else (_WROTE_RE.search(desc) or _WROTE_RE.search(all_text))
    if fm:
        nombre = fm.group("name").strip(" *")
        dom = fm.group("email").split("@")[-1].strip().lower()
        if dom not in internal_domains:
            cliente = dom
    elif m:
        nombre = m.group("name").strip()
        after = (desc if _WROTE_RE.search(desc) else all_text)[m.end():m.end() + 2500]
        for line in after.splitlines()[:40]:
            if equipo is None and _TEAM_RE.search(line):
                equipo = line.strip(" |")[:80]
            em = _EMAIL_RE.search(line)
            if em and cliente is None and em.group("d") not in internal_domains and "mesadeservicios" not in line:
                cliente = em.group("d")
    else:
        lm = _LABEL_RE.search(all_text)
        if lm:
            nombre = lm.group("v").strip()[:80]

    medios = []
    head = f"{summary}\n{desc}"
    if re.search(r"wrote:|Emisor:|\[Ticket#|Ticket#", head, re.I) or _MAIL_HDR_RE.search(head) or _EMAIL_RE.search(desc):
        medios.append("email")
    if re.search(r"whats\s?app", head, re.I):
        medios.append("whatsapp")
    if re.search(r"\bteams\b", head, re.I):
        medios.append("teams")

    ticket = _TICKET_RE.search(head)

    plan_files = [n for n in attachment_names if _PLAN_FILE_RE.search(n)]
    plan_files += [x for x in re.findall(r"\[\^([^\]]+)\]", all_text) if _PLAN_FILE_RE.search(x)]
    plan_text = bool(_PLAN_TEXT_RE.search(all_text))

    is_respaldo = bool(_RESPALDO_RE.search(summary))
    backup_evidence = False
    if is_respaldo:
        backup_evidence = (
            any(_BKP_FILE_RE.search(n) or _IMG_FILE_RE.search(n) for n in attachment_names)
            or bool(_HOST_TABLE_RE.search(all_text))
        )

    return {
        "solicitante": nombre,
        "cliente": cliente,
        "equipo": equipo,
        "medios": medios,
        "ticket_cliente": ticket.group(1) if ticket else None,
        "plan_files": sorted(set(plan_files)),
        "plan_text": plan_text,
        "is_respaldo": is_respaldo,
        "backup_evidence": backup_evidence,
    }


def is_in_progress(fields: dict) -> bool:
    return ((fields.get("status") or {}).get("statusCategory") or {}).get("key") == "indeterminate"


def required_checks(fields: dict, ext: dict) -> tuple[str, ...]:
    required = REQUIRED_IN_PROGRESS if is_in_progress(fields) else REQUIRED_TODO
    if ext["is_respaldo"]:
        required = tuple(k for k in required if k != "itil")
    return required


def deterministic_checks(fields: dict, ext: dict) -> dict:
    return {
        "solicitante": bool(ext["solicitante"]),
        "origen": bool(ext["medios"]),
        "plan": bool(ext["plan_files"] or ext["plan_text"] or ext["backup_evidence"]),
        "horas": (fields.get("timespent") or 0) > 0,
    }


def coherence_pct(detail: dict) -> int | None:
    """detail = {"titulo": "ok|no|na", "tipo": ..., "trabajo": ..., "estado": ...}"""
    vals = list(detail.values())
    oks, nos = vals.count("ok"), vals.count("no")
    return round(100 * oks / (oks + nos)) if oks + nos else None
