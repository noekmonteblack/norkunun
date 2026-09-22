---
name: auditar
description: Audita un issue de Jira contra el checklist de calidad (solicitante, medio, detalle, objetivo, cuadro ITIL, coherencia, plan de trabajo, desarrollo, horas) y explica qué falta y por qué. Usar cuando el usuario pida auditar, revisar o chequear un issue (ej. "audita PROY-123", "¿pasa la auditoría PROY-123?").
argument-hint: "<CLAVE-123>"
allowed-tools:
  - Read
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" *)
  - Bash(python "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" *)
---

# /norkunun:auditar

Audita el issue `$ARGUMENTS` y explica en palabras simples qué cumple y qué falta.

## Pasos

1. Si no te pasaron una clave de issue, pídela.
2. Lee los criterios en `${CLAUDE_PLUGIN_ROOT}/reference/criterios.md`.
3. Trae el issue:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" issue <CLAVE>
   ```
   Si `python3` no existe, usa `python`. Si la respuesta trae `"ok": false`, sigue la sección
   *Errores*.
4. Si `excluido_noauditar` es true, avisa que el issue está excluido con `[NOAUDITAR]` y pregunta
   si igual se quiere revisar.
5. Evalúa:
   - Los checks de `checks_deterministas` se toman **tal cual** del script.
   - Los de `checks_para_llm` los evalúas tú con los criterios, sobre `summary`, `tipo`,
     `estado`, `descripcion` y `comentarios`.
6. Muestra el resultado:

   ```
   PROY-123 — <título>
   Estado: En curso | Tipo: Requerimiento | Horas: 3.5h / 8h

   ✓ solicitante      Juan Pérez (cliente.cl)
   ✗ origen/medio     no se detecta correo, WhatsApp ni Teams
   ✓ detalle          <resumen de 1 línea de lo que se pide>
   ✗ objetivo         no dice para qué se necesita
   ✗ cuadro ITIL      no menciona impacto ni urgencia
   ~ coherencia 50%   tipo: es una falla, debería ser Incidente
   ✓ plan de trabajo
   ~ desarrollo       hay avance pero no se ve resultado
   ✓ horas
   ```
   Los checks que no se exigen en este estado van con `·` y el texto "aún no aplica".
7. Cierra con **"Para pasar la auditoría"**: una lista corta, ordenada por lo más fácil de
   arreglar, con acciones concretas (qué línea agregar y dónde, qué cambiar en Jira). Después
   ofrece: "¿Te ayudo a corregirlo? → `/norkunun:mejorar <CLAVE>`".

Es una autoevaluación. El auditor oficial usa estas mismas reglas, pero su modelo puede juzgar
distinto en los puntos de criterio (detalle, objetivo, ITIL, coherencia, desarrollo). Menciónalo
solo si el usuario pregunta por diferencias.

## Errores
- `no_config`: el usuario no ha hecho login. Dile que ejecute, **en su propia terminal** (fuera
  de Claude Code), el comando que viene en `mensaje`. No le pidas la password en el chat.
- `auth`: las credenciales fallaron; tiene que repetir el login en su terminal. **No reintentes**
  el comando, porque varios fallos seguidos pueden bloquear la cuenta en Jira con CAPTCHA.
- `ssl`: sugiere repetir el login y responder `n` a verificar SSL.
- `not_found`: la clave no existe o el usuario no tiene permiso para verla.
- `network`: no hay conexión a Jira (¿VPN?).
