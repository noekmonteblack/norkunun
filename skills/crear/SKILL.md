---
name: crear
description: Redacta un issue de Jira nuevo, listo para pasar la auditoría, a partir de un correo, mensaje de WhatsApp/Teams o notas que pega el usuario. Pregunta lo que falte y arma título, tipo, descripción en formato wiki, cuadro ITIL y plan de trabajo. Usar cuando el usuario quiera crear o redactar un issue nuevo.
argument-hint: "[pega el correo o describe la solicitud]"
allowed-tools:
  - Read
  - AskUserQuestion
---

# /norkunun:crear

Ayuda al usuario a redactar un issue **nuevo** que pase la auditoría desde el primer día.
Norkunun no crea issues en Jira: tú redactas y el usuario lo crea y pega el texto.

## Regla de oro
**No inventes datos.** Lo que no venga en el material ni te diga el usuario va como
`[COMPLETAR: ...]` y queda en la lista de pendientes.

## Flujo

1. Lee `${CLAUDE_PLUGIN_ROOT}/reference/criterios.md`.
2. **Material**: si `$ARGUMENTS` está vacío, pide que pegue el correo, el chat o una descripción
   de la solicitud.
3. **Extrae** del material todo lo que puedas: solicitante (nombre, área, correo), medio,
   número de ticket del cliente, qué se pide, para qué, plazos y a quién afecta.
4. **Pregunta lo que falte**, de a 1 a 3 preguntas por turno, con el mismo orden y el mismo
   estilo que `/norkunun:mejorar` (solicitante → medio → detalle → objetivo → ITIL).
   - **Tipo**: propón Incidente, Requerimiento o Tarea y explica en una frase por qué.
   - **ITIL**: preguntas concretas de impacto y urgencia, propuesta según la matriz y
     confirmación.
   - **Proyecto** de Jira: pregunta en cuál se crea, si no es obvio.
   - **Plan de trabajo**: si el trabajo empieza pronto, ofrece dejarlo desde ya.
5. **Entrega**:
   - Título (verbo + objeto + sistema/cliente), tipo y proyecto.
   - Descripción completa en un bloque de código, con la plantilla de los criterios.
   - Checklist proyectado: lo que queda ✓, y lo que aún no aplica (plan, desarrollo, horas)
     con la nota de que se exige cuando pase a En curso.
   - Pendientes: los `[COMPLETAR]` y los adjuntos sugeridos (por ejemplo, el correo original).
6. Ofrece: "Cuando lo crees en Jira, pásame la clave y lo audito con `/norkunun:auditar`".
