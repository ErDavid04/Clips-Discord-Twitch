# Clips de Twitch → Discord (gratis)

Cada ~5 minutos, GitHub Actions comprueba los clips nuevos de tu canal de Twitch y los publica en tu canal de Discord `#clips` mediante un webhook. Coste: 0 €. No necesitas servidor ni tener el PC encendido.

## 1. Webhook de Discord
1. En tu servidor: clic derecho en `#clips` → **Editar canal** → **Integraciones** → **Webhooks** → **Nuevo webhook**.
2. Ponle nombre (p. ej. "Clips") y avatar si quieres.
3. **Copiar URL del webhook**. Guárdala; es secreta.

## 2. App de Twitch (para leer la API)
1. Entra en https://dev.twitch.tv/console con tu cuenta (necesitas tener la verificación en dos pasos activada).
2. **Registrar tu aplicación**:
   - Nombre: cualquiera único (p. ej. `clips-discord-tunombre`)
   - URL de redirección OAuth: `http://localhost`
   - Categoría: *Other* · Tipo de cliente: *Confidencial*
3. Abre la app → copia el **ID de cliente** y pulsa **Nuevo secreto** para obtener el **Secreto de cliente**.

## 3. Repositorio en GitHub
1. Crea un repositorio **público** (ver nota abajo) y sube estos archivos tal cual, incluida la carpeta `.github/workflows/`.
2. En el repo: **Settings → Secrets and variables → Actions**.
   - Pestaña **Secrets** → *New repository secret*, crea:
     - `TWITCH_CLIENT_ID`
     - `TWITCH_CLIENT_SECRET`
     - `DISCORD_WEBHOOK_URL`
   - Pestaña **Variables** → *New repository variable*:
     - `TWITCH_LOGIN` = tu nombre de usuario de Twitch (el de la URL, p. ej. `twitch.tv/minombre` → `minombre`)
3. **Settings → Actions → General → Workflow permissions** → marca **Read and write permissions** → Save.
4. Pestaña **Actions** → "Clips de Twitch a Discord" → **Run workflow** para probarlo ya.

> La primera ejecución publicará los clips creados en las últimas 24 h. Si no quieres eso, ejecútalo una vez con el webhook apuntando a un canal de pruebas, o simplemente bórralos.

## Notas importantes
- **Repo público = gratis sin límite.** En repos privados GitHub da 2.000 minutos/mes y ejecutar cada 5 min los agota. Los secretos siguen protegidos aunque el repo sea público (nadie puede verlos).
- **Retraso**: GitHub no garantiza puntualidad; el clip puede tardar entre 5 y ~20 min en aparecer.
- **Inactividad**: GitHub desactiva tareas programadas tras 60 días sin actividad en el repo. El script hace un commit al menos una vez por semana para evitarlo. Si alguna vez se desactiva, reactívalo en la pestaña Actions.
- **Seguridad**: si se filtra la URL del webhook, bórralo en Discord y crea otro. Nunca la pongas en el código, solo en Secrets.
- Para cambiar la frecuencia, edita `cron` en `.github/workflows/clips.yml`.
