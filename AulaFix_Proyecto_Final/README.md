# AulaFix · Proyecto final Generación T

**Sistema de incidencias y reparaciones de tecnología escolar.** Es un producto diferente de BiblioLab y ReservaClub: permite que alumnos reporten fallas y que el equipo TIC las administre con reglas de prioridad, asignación, vencimientos, repuestos y trazabilidad.

## Funcionalidades

- Acceso por perfiles (alumno, técnico, administrador).
- Registro y seguimiento de incidencias por ubicación, categoría y prioridad.
- Fechas límite calculadas según la prioridad: crítica 4 h, alta 12 h, media 48 h, baja 120 h.
- Asignación exclusiva por administración, solo a técnicos, con cupo de tres trabajos activos.
- Máquina de estados validada, con solución obligatoria antes de resolver.
- Inventario de repuestos con salida transaccional sin stock negativo y alertas por mínimo.
- Historial de auditoría de altas, cambios, asignaciones y consumos.
- Tablero con indicadores y búsquedas; interfaz adaptada a celulares.
- 31 pruebas automáticas de lógica.

## Tecnología

Frontend: HTML5, CSS3, JavaScript sin dependencias. Backend: Python 3 (biblioteca estándar: `http.server`). Base de datos: SQLite. Publicación: Render Blueprint (`render.yaml`). Todo se sirve desde un único servicio web.

## Ejecutar localmente

Requiere Python 3.10 o posterior. Desde la raíz:

```bash
python backend/server.py
```

Abrir `http://localhost:8000`. Para correr pruebas:

```bash
python -m unittest discover -s tests -v
```

## Cuentas de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Alumno | `martina@aulafix.test` | `alumno123` |
| Alumno | `tomas@aulafix.test` | `alumno123` |
| Técnico | `lucia@aulafix.test` | `tecnico123` |
| Técnico | `nicolas@aulafix.test` | `tecnico123` |
| Administrador | `admin@aulafix.test` | valor secreto de `ADMIN_PASSWORD` |

En local, si falta la variable de administrador, se usa `Admin2026!` como contraseña de desarrollo. En producción **es obligatorio** configurar `ADMIN_PASSWORD` con al menos ocho caracteres.

## Publicación en Render

1. Crear un repositorio nuevo de GitHub y subir **todo el contenido** de esta carpeta a la raíz, sin `.env`. Si se utiliza la interfaz web de GitHub, no arrastrar `.git`; para preservar los commits, hacer `git remote add origin URL` y `git push -u origin main` desde una consola.
2. Entrar a Render → New → Blueprint → conectar el repositorio.
3. Al crear el servicio, indicar una contraseña privada para la variable `ADMIN_PASSWORD`.
4. Comprobar que el despliegue diga **Live**, abrir el enlace `https://<servicio>.onrender.com` y probar los flujos de los tres roles.
5. Añadir el enlace público real al README y entregar **el enlace del repositorio** en el Módulo 5.

**Enlace público de la aplicación:** PENDIENTE DE PUBLICACIÓN POR EL TITULAR DEL REPOSITORIO.

### Limitaciones de demostración

Los datos se guardan en SQLite, con archivo en `/tmp` en Render Free. Se pierden al reiniciar o redesplegar el servicio, porque el sistema de archivos gratuito no es persistente. Las cuentas y existencias iniciales se vuelven a crear. **No utilizar información personal real**; es un prototipo educativo, no un producto listo para una institución. Las contraseñas de las cuentas de muestra se incluyen solo para facilitar la evaluación. Para un sistema real deberían usarse hashes de contraseña, sesiones persistentes, rate limiting y almacenamiento persistente.

## Documentación

`docs/idea.md`, `decisiones.md`, `glosario.md`, `preguntas-abiertas.md`, `spec.md`, `plan.md`, `tasks.md`, `informe.md`, `pruebas.txt`; `AGENTS.md` y reglas bajo `.cursor/rules/`.

## API resumida

`GET /api/health`; `POST /api/login`; `POST /api/logout`; `GET /api/session`; `GET/POST /api/tickets`; `GET /api/tickets/:id`; `POST /api/tickets/:id/assign`; `POST /api/tickets/:id/status`; `POST /api/tickets/:id/part`; `GET /api/stock`; `GET /api/staff`; `GET /api/dashboard`.
