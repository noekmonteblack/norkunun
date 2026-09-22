# Norkunun: contexto de desarrollo

Proyecto hijo del bot de auditoría central (Likan). Antes se llamaba jmc; se renombró el
2026-09-22. Lleva la auditoría de issues al Claude Code de cada persona, para que cada uno
corrija sus issues antes del reporte diario.

## Decisiones (2026-09-22)

- **Plugin de Claude Code** en un repo GitHub privado. El repo es a la vez marketplace
  (`.claude-plugin/marketplace.json`, con `source: "./"`) y plugin
  (`.claude-plugin/plugin.json`).
- **Skills**: auditar, mejorar, crear, mis-issues y configurar. Lo interactivo lo hace Claude
  guiado por los skills; el script solo trae datos.
- **Script de solo lectura** (`scripts/norkunun.py`), sin dependencias, con salida JSON. Norkunun
  no escribe en Jira; eso podría venir más adelante, con confirmación.
- **Login con usuario y password** (basic auth, sin tokens personales), por decisión del
  usuario. `norkunun.py login` se corre en la terminal propia, fuera de Claude, porque el Bash
  de Claude no es interactivo y así la password no entra al contexto. Se guarda en
  `~/.config/norkunun/config.json` con permisos 600.
- **Nada interno en el repo**: la URL de Jira, los dominios y los proyectos se piden en el login.
  El hook `.githooks/pre-commit` bloquea IPs y los patrones de `.git/info/norkunun-blocklist`,
  que es local y no se versiona.
- **Una sola fuente de reglas**: `scripts/norkunun_rules.py` trabaja sobre el JSON crudo de la
  API REST. La idea es que el auditor central también lo importe (usando `issue.raw`), en lugar
  de mantener una copia propia de las regex. Todavía no está hecho.
- **El auditor central sigue siendo el juez oficial.** Norkunun es para autoevaluarse.

## Verificado
- 2026-09-22: `check`, `issue` y `mis-issues` probados contra el Jira real. Los checks
  deterministas y los checks requeridos coinciden 1:1 con el auditor central en 7 issues,
  incluida la regla de respaldo.

## Pendiente
- Que el auditor central importe `norkunun_rules.py`.
- Probar la instalación del plugin desde GitHub en una máquina de usuario.
