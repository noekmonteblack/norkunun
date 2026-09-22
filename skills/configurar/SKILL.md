---
name: configurar
description: Configura o verifica la conexión de Norkunun a Jira (URL, usuario y password del propio usuario). Usar la primera vez que se usa Norkunun, o cuando falle la conexión o las credenciales.
allowed-tools:
  - Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" check)
  - Bash(python "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" check)
---

# /norkunun:configurar

1. Ejecuta `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/norkunun.py" check` (o `python` si
   `python3` no existe).
2. Si responde `"ok": true`, muestra con qué usuario quedó conectado y los proyectos
   configurados. Listo.
3. Si falla con `no_config`, `auth` o `ssl`, el usuario tiene que hacer el login **en su propia
   terminal**, fuera de Claude Code, porque el login pide la password de forma interactiva y
   así nunca pasa por este chat. Dale el comando exacto, con la ruta real (la que aparece en
   `mensaje`, o `${CLAUDE_PLUGIN_ROOT}` ya expandido):

   ```
   python3 "<ruta>/scripts/norkunun.py" login
   ```

   Explica lo que le va a preguntar:
   - **URL de Jira**: la que usa en el navegador, sin `/browse/...`.
   - **Usuario y password de Jira**: los mismos del navegador. La password no se muestra al
     escribirla.
   - **Verificar certificado SSL**: `s`; si da error de certificado, repetir con `n`.
   - **Dominios internos**: el dominio del correo de su empresa, para distinguir clientes de
     colegas.
   - **Proyectos**: las claves de los proyectos que quiere ver en `mis-issues` (Enter = todos).

   Todo queda guardado solo en su equipo, en `~/.config/norkunun/config.json` (legible solo por
   su usuario).
4. **Nunca** pidas ni aceptes la password en el chat. Si el usuario la escribe aquí, dile que no
   hace falta, que la cambie si le preocupa, y que haga el login en la terminal.
5. Cuando diga que terminó, vuelve a ejecutar `check` para confirmar.
