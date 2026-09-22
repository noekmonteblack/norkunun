---
name: mis-issues
description: Lista los issues abiertos asignados al usuario en Jira con su estado de auditoría (✓✗) y le ayuda a decidir cuál corregir primero. Usar cuando el usuario pregunte por sus issues, qué tiene pendiente o cuáles no pasan la auditoría.
allowed-tools:
  - Read
  - AskUserQuestion
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" *)
  - Bash(python "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" *)
---

# /norkunun:mis-issues

Muestra los issues abiertos del usuario y en qué están con la auditoría.

## Pasos

1. Ejecuta `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" mis-issues` (o `python`). Si
   falla, sigue la sección *Errores* de `/norkunun:auditar`.
2. El listado solo trae los **checks deterministas** (SOL, MED, PLN, HRS). Los de juicio
   (detalle, objetivo, ITIL, coherencia, desarrollo) se muestran como `?`, porque evaluarlos
   requiere leer cada issue completo.
3. Muestra una tabla compacta, ordenada con los que tienen más ✗ primero:

   ```
   Issue       Estado        SOL MED PLN HRS  Título
   PROY-259    En curso       ✗   ✗   ✗   ✓   Migrar reportes a ...
   PROY-182    Pendiente      ✗   ✗   ·   ·   Error al generar ...
   PROY-232    En curso       ✓   ✓   ✓   ✓   Actualizar ...
   ```
   Usa `·` para los checks que no aplican en ese estado (no vienen en `checks_deterministas`).
   Marca con `(respaldo)` los que tienen `es_respaldo`.
4. Resume en una línea: cuántos issues hay y cuántos tienen faltas seguras.
5. Pregunta con `AskUserQuestion` cuál quiere trabajar (hasta 3 opciones con los peores, más la
   opción de auditar todos en detalle). Según la respuesta:
   - Un issue: sigue el flujo de `/norkunun:mejorar` con esa clave.
   - Auditar todos: trae cada issue con `issue <CLAVE>`, evalúa los checks de juicio y muestra
     la tabla completa (SOL MED DET OBJ ITL COH PLN DES HRS). Avisa antes si son más de 10.
