# Criterios de auditoría de issues

Esta es la fuente de verdad de la auditoría. Los skills de Norkunun la leen antes de auditar,
mejorar o crear un issue.

Hay dos tipos de checks:

- **Deterministas.** Los calcula `scripts/norkunun.py` buscando patrones de texto, y vienen en
  `checks_deterministas`. **No los reinterpretes**: si el script dice `false`, el auditor oficial
  también lo va a marcar como falta, aunque el texto "se entienda".
- **De juicio.** Los evalúas tú (Claude) con los criterios de abajo, y vienen listados en
  `checks_para_llm`. Sé estricto: si no hay evidencia clara en el texto, no cumple. No inventes.

## Qué checks se exigen

| Estado del issue | Checks exigidos |
|---|---|
| Por hacer, Pendiente u otro no iniciado | solicitante, origen, detalle, objetivo, itil, coherencia |
| En curso (`en_curso: true`) | los anteriores + plan, desarrollo, horas |
| Título contiene "respaldo" | no se exige itil; el plan se cumple también con evidencia del respaldo |

Un comentario con `[NOAUDITAR]` excluye el issue de la auditoría y uno con `[AUDITAR]` fuerza una
re-auditoría. Los pone una persona, no tú.

## Checks deterministas: qué busca exactamente el código

### Solicitante (SOL)
Se cumple con **una** de estas formas, dentro de la descripción o de un comentario:
- Una línea de encabezado de correo: `De: Nombre Apellido <correo@dominio>` (o `From:`).
- Una línea de correo citado: `Nombre Apellido wrote:`.
- Una línea que **empiece** con `Solicitante:`, `Solicita:`, `Cliente:` o `Requirente:`,
  seguida del nombre.

La forma recomendada al redactar es `Solicitante: Nombre Apellido`, al inicio de la línea. La
etiqueta puede ir en negrita (`*Solicitante:* Nombre Apellido` o `*Solicitante*: ...`).

### Origen o medio (MED)
Se revisa en el **título y la descripción**, no en los comentarios:
- **Email**: una dirección de correo en la descripción, o encabezados `De:`, `Asunto:`,
  `Enviado:`, o `wrote:` o `Ticket#`. Escribir solo la palabra "correo" **no basta**.
- **WhatsApp**: la palabra `WhatsApp`.
- **Teams**: la palabra `Teams`.

Teléfono, presencial o reunión **no se reconocen**. Si fue por uno de esos medios, avísale al
usuario que MED va a salir en falta y sugiere dejar registro, por ejemplo con un correo de
confirmación que se pega en el issue.

### Plan de trabajo (PLN), solo en curso
- En la descripción o en los comentarios aparece literalmente "plan de trabajo", "PDT",
  "cronograma" o "carta gantt"; **o bien**
- hay un adjunto cuyo nombre contiene plan, trabajo, pdt, cronograma, gantt o carta.
- **Respaldo**: también cumple si hay un adjunto `.tar`, `.tar.gz`, `.tgz` o `.gz`, uno cuyo
  nombre contenga bkp o backup, una imagen, o un texto o tabla que mencione
  host/servidor + respaldo/backup.

### Horas (HRS), solo en curso
Debe haber tiempo imputado en el **worklog** del issue (`horas_imputadas > 0`). Esto no se arregla
con texto: el usuario tiene que registrar horas en Jira.

## Checks de juicio: cómo evaluarlos

### Detalle (DET)
Es **lo que expone el solicitante**: qué pide o qué falla, con sus palabras o citando su correo o
mensaje. Alguien que no leyó el correo original tiene que poder entenderlo: sistema, ambiente y
alcance; en un incidente, los síntomas y desde cuándo ocurre.

### Objetivo (OBJ)
Es **lo que el ingeniero entendió que hay que hacer** para cumplir el detalle, y **el resultado
esperado**: cómo se sabe que quedó listo. Copiar el pedido del solicitante no alcanza; tiene que
verse la interpretación técnica. Lo que diga el correo citado **no cuenta**, aunque use la palabra
"objetivo": tiene que ser texto propio del ingeniero, en la sección `h3. Objetivo`. Ejemplo: "Levantar un lab RHEL 9 con OpenJDK 17 y validar las
cargas Sqoop/Spark/Hive actuales. Queda listo cuando las pruebas corren sin errores y se entrega
el informe de compatibilidad."

### Cuadro ITIL (ITL)
El texto menciona **explícitamente** el impacto y la urgencia. El tipo o la prioridad de Jira no
cuentan. Va en un **comentario propio** (no en la descripción); el auditor lee siempre los
comentarios que mencionan impacto o urgencia, aunque sean antiguos. Si un issue antiguo lo tiene en
la descripción, también cuenta. Formato recomendado:

```
h3. Cuadro ITIL
||Impacto||Urgencia||Prioridad||Justificación||
|Medio|Alta|2 - Alta|Afecta al área de cobranza (15 usuarios); el cierre de mes es el viernes.|
```

Matriz de prioridad (impacto × urgencia):

| Impacto \ Urgencia | Alta | Media | Baja |
|---|---|---|---|
| **Alto** | 1 - Crítica | 2 - Alta | 3 - Media |
| **Medio** | 2 - Alta | 3 - Media | 4 - Baja |
| **Bajo** | 3 - Media | 4 - Baja | 5 - Planificada |

Para definirlos, no le preguntes al usuario "¿cuál es el impacto?". Hazle preguntas concretas:
- **Impacto**: ¿a cuántos usuarios o áreas afecta? ¿Afecta a un cliente final, a la facturación
  o a un proceso crítico? ¿Hay datos o dinero en riesgo?
  Alto = muchos usuarios, un servicio crítico o un cliente final. Medio = un área o un proceso
  secundario. Bajo = una persona o algo cosmético.
- **Urgencia**: ¿hay una fecha límite, un SLA o una multa? ¿Existe una alternativa mientras
  tanto? ¿El daño crece con el tiempo?
  Alta = está detenido o sin alternativa, o hay un plazo cercano. Media = hay una alternativa
  incómoda. Baja = puede esperar.

### Coherencia (COH)
Hay cuatro sub-checks. Cada uno vale `ok`, `no` o `na`, y el issue aprueba si los `ok` son al
menos el 75% de (ok + no).
- **Título**: describe lo que realmente se pide. Nada de títulos genéricos ("Solicitud",
  "Revisión", "Consulta"). Forma sugerida: verbo + objeto + sistema/cliente.
- **Tipo**: corresponde a lo descrito. Una falla o algo que dejó de funcionar es un
  **Incidente**; algo nuevo o un cambio pedido es un **Requerimiento**; el trabajo interno o
  recurrente es una **Tarea**.
- **Trabajo**: los comentarios de avance tratan del tema pedido, sin derivar a otro (`na` si no
  hay comentarios de trabajo).
- **Estado**: consistente con lo ocurrido. Por ejemplo, "En curso" pero detenido, o ya resuelto
  pero sigue abierto, es `no` (`na` si no hay actividad).

### Desarrollo (DES), solo en curso
Se juzga **solo por los comentarios**:
- **completo**: los comentarios muestran el trabajo realizado y entregado o cerrado.
- **parcial (~)**: hay avance concreto, pero sin terminar o sin resultado.
- **ninguno (✗)**: no hay evidencia de trabajo.

Los comentarios de horas, estimaciones o espera ("en espera", "revisando", "se estiman 4h") **no
cuentan**. Un buen comentario de avance dice qué se hizo, el resultado y la evidencia.

## Qué lee el auditor oficial (límites de texto)

Para los checks de juicio, el auditor oficial no lee el issue completo:

- **Descripción**: solo los primeros **2.500 caracteres**. Lo que venga después no existe para
  la auditoría. Por eso Solicitante, Medio, Detalle y Objetivo van **arriba**, y el correo
  original reenviado (firmas, CC, disclaimers) va **al final**.
- **Comentario ITIL**: los comentarios que mencionan impacto o urgencia se leen **siempre** (los 2
  más recientes, hasta 800 caracteres cada uno), estén donde estén.
- **Resto de los comentarios**: solo los **últimos 8**, y de cada uno los primeros **300
  caracteres**. Un comentario de avance tiene que ser corto y decir el resultado en la primera
  frase. Varios comentarios de espera ("en espera", "falta aprobación") seguidos pueden dejar
  fuera los de avance anteriores. El plan de trabajo no tiene este límite: el programa lo busca
  en todos los comentarios.
- **Adjuntos**: solo cuenta el **nombre** del archivo, para el plan o la evidencia de respaldo. El
  contenido no se lee. Si las pruebas o resultados están en un adjunto, hay que resumirlos en un
  comentario de avance que lo mencione por nombre.

## Símbolos del reporte
✓ cumple · ✗ falta · ~ parcial · `·` aún no aplica · ? sin analizar · COH % = coherencia

## Dónde va cada cosa

| Parte | Dónde | Quién la aporta |
|---|---|---|
| Solicitante, Medio | Descripción, arriba | Datos del pedido |
| Detalle | Descripción | Lo que expone el solicitante |
| Objetivo | Descripción | Lo que entendió el ingeniero y el resultado esperado |
| Correo original | Descripción, al final | Cita del pedido |
| Cuadro ITIL | Comentario propio | Ingeniero |
| Plan de trabajo | Comentario propio (o adjunto) | Ingeniero |
| Avances | Un comentario por avance | Ingeniero |

### Plantilla de descripción (formato wiki de Jira Server)

```
Solicitante: Nombre Apellido
Área: Gerencia / Unidad
Medio: Email (nombre.apellido@cliente.cl)

h3. Detalle
Lo que pide el solicitante: qué se solicita o qué falla, sistema, ambiente y alcance.

h3. Objetivo
Lo que se hará para cumplirlo y cómo se sabe que quedó listo.

h3. Correo original
{quote}
De: Nombre Apellido <nombre.apellido@cliente.cl>
...
{quote}
```

### Plantilla del comentario ITIL

```
h3. Cuadro ITIL
||Impacto||Urgencia||Prioridad||Justificación||
|Medio|Alta|2 - Alta|...|
```

### Plantilla del comentario de plan de trabajo

```
h3. Plan de trabajo
# Paso 1 — responsable — fecha
# Paso 2 — ...
```

El plan se exige cuando el issue pasa a En curso, pero conviene dejarlo desde el inicio.
