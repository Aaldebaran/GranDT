# Gran DT — Mundial 2026 (versión gratis)

Juego tipo Gran DT para el Mundial 2026, para jugar entre amigos. Corre solo, gratis,
con datos de football-data.org. Esta es la versión "modelo gratis" (goles + resultados + valla).

## Qué hace cada parte
- `index.html` — tabla y puntos (lo que ven los jugadores). Incluye las reglas.
- `armar.html` — armador de equipo; genera un **código** que cada amigo te manda.
- `scripts/build_pool.py` — baja los planteles de las 48 selecciones → `data/players.json` (se corre **una vez**).
- `scripts/daily.py` — baja resultados + goleadores y calcula puntos → `data/standings.json` (corre **solo, 1 vez por día**).
- `data/teams.json` — acá pegás el código de equipo de cada amigo.

## Puesta en marcha (una sola vez)
1. **Creá un repo nuevo** en GitHub (público) y subí todos estos archivos (Add file → Upload files).
2. **Cargá el token como secreto:** Settings → Secrets and variables → Actions → New repository secret.
   - Name: `FOOTBALL_DATA_TOKEN`  · Value: tu token de football-data.org
3. **Generá el pool de jugadores:** pestaña Actions → "Construir pool de jugadores (manual)" → Run workflow.
   - Esto crea `data/players.json` con las 48 selecciones. (Conviene correrlo cuando estén las listas de 26 definitivas.)
4. **Activá la página web:** Settings → Pages → Source: "Deploy from a branch" → Branch: `main` / `/root` → Save.
   - En 1-2 minutos tu app queda en `https://aaldebaran.github.io/NOMBRE-DEL-REPO/`
5. **Pasales a tus amigos** el link `.../armar.html`. Cada uno arma su equipo y te manda su código.
6. Pegá cada código en `data/teams.json` (campo de la ronda, ej. `"R1"`).

## Durante el torneo
- No hacés nada en el día a día: la tarea "Actualizar puntos (diario)" corre sola y refresca la tabla.
- En cada ventana de transferencias, pegás los códigos nuevos en `data/teams.json` (3 cambios máx. por ronda; quien no cambia, no toca nada).

## Notas
- **Precios:** el modelo gratis no trae datos para ponerlos solos. En `data/players.json` arrancan con un valor por defecto + algunos curados. Editalos a mano (sobre todo los ~50 nombres que la gente va a elegir).
- **Datos que no hay gratis:** minutos, tarjetas, asistencias, minuto del gol. Por eso los puntos de victoria/valla van a tus jugadores de ese equipo jugaran o no.
- Para correr a mano cuando quieras: Actions → "Actualizar puntos (diario)" → Run workflow.
