# Norkunun

Plugin de Claude Code que ayuda a dejar los issues de Jira en condiciones de **pasar la
auditoría de calidad**. Audita tus issues, te pregunta lo que falta y redacta la descripción, el
cuadro ITIL, el plan de trabajo y los comentarios de avance, listos para pegar en Jira.

Norkunun **solo lee** Jira. Nunca escribe: tú decides qué pegar.

## Instalación

Solo necesitas Claude Code. Norkunun usa Python 3.8 o superior (sin librerías extra); si no lo
tienes, `/norkunun:configurar` te explica cómo instalarlo.

1. En Claude Code:
   ```
   /plugin marketplace add noekmonteblack/norkunun
   /plugin install norkunun@norkunun
   ```
   El repo es privado: tu cuenta de GitHub tiene que tener acceso, y git debe poder clonarlo
   (con `gh auth login` o una clave SSH).

2. Conéctalo a Jira **en tu propia terminal**, no dentro de Claude Code. Dentro de Claude,
   `/norkunun:configurar` te muestra el comando exacto con la ruta. Tiene esta forma:
   ```
   python3 ~/.claude/plugins/.../norkunun/scripts/norkunun.py login
   ```
   Te pide la URL de Jira, tu usuario, tu password y los proyectos que se auditan (tu equipo
   te da la lista; Norkunun solo trabaja con issues de esos proyectos), y los guarda solo en tu equipo, en
   `~/.config/norkunun/config.json`, legible solo por tu usuario. La password nunca pasa por el
   chat. La URL de Jira te la da tu equipo.

3. Verifica con `/norkunun:configurar`.

## Comandos

| Comando | Qué hace |
|---|---|
| `/norkunun:mis-issues` | Tus issues abiertos con su estado de auditoría; te ayuda a elegir cuál arreglar. |
| `/norkunun:auditar PROY-123` | Checklist completo de un issue y qué hacer para que pase. |
| `/norkunun:mejorar PROY-123` | Te guía paso a paso y te entrega el texto corregido. |
| `/norkunun:crear` | Pegas un correo o chat y arma un issue nuevo que ya cumple. |
| `/norkunun:configurar` | Verifica o configura la conexión a Jira. |

También puedes pedirlo en palabras normales: "audita PROY-123", "ayúdame a mejorar PROY-123".

## Qué se audita

Solicitante · medio/origen · detalle · objetivo · cuadro ITIL · coherencia, y cuando el issue
está en curso, además: plan de trabajo · desarrollo · horas imputadas. El detalle de cada
criterio está en [`reference/criterios.md`](reference/criterios.md).

¿No usas Claude Code? [`reference/prompt_issue_auditoria.md`](reference/prompt_issue_auditoria.md)
es un prompt que sirve en cualquier LLM (ChatGPT, Gemini, Copilot…).

## Actualizar

```
/plugin marketplace update norkunun
```

## Uso sin plugin

El script se puede usar solo:
```
python3 scripts/norkunun.py login
python3 scripts/norkunun.py check
python3 scripts/norkunun.py issue PROY-123
python3 scripts/norkunun.py mis-issues
```
Las variables de entorno `NORKUNUN_URL`, `NORKUNUN_USER`, `NORKUNUN_PASS`,
`NORKUNUN_PROJECTS` y `NORKUNUN_VERIFY_SSL` tienen prioridad sobre el archivo de configuración.

## Desarrollo

- Las reglas deterministas están en `scripts/norkunun_rules.py`; los criterios de juicio, en
  `reference/criterios.md`. Si cambias una regla, actualiza ambos y también
  `reference/prompt_issue_auditoria.md`.
- **Nunca** subas URLs, dominios, IPs, nombres de usuarios ni claves de proyectos reales; en los
  ejemplos usa `PROY-123` y `cliente.cl`. Activa el hook que lo bloquea:
  ```
  git config core.hooksPath .githooks
  ```
  y pon tus patrones privados en `.git/info/norkunun-blocklist` (uno por línea). Ese archivo no
  se sube.
