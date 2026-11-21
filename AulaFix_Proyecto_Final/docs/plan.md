# Plan técnico — AulaFix

## Arquitectura

Aplicación monolítica ligera: cliente HTML/CSS/JS (`frontend/`) servido por Python (`backend/server.py`) desde el mismo origen. JSON sobre HTTP bajo `/api`. Lógica de dominio y persistencia en `backend/core.py`. SQLite local mantiene tablas, restricciones e historial.

```text
Navegador
  ├── GET / → frontend/index.html / styles.css / app.js
  └── /api/... → backend/server.py
                       └── backend/core.py
                             └── SQLite
```

## Modelo de datos

- **users**: id, name, email, role, password (cuentas educativas).
- **tickets**: id, reporter_id, title, category, description, priority, location, status, assignee_id, created_at, updated_at, due_at, resolution.
- **stock**: id, name, quantity, minimum.
- **usage**: id, ticket_id, stock_id, quantity, created_at.
- **history**: id, ticket_id, actor_id, action, detail, at.

Relaciones: users 1:N tickets solicitados; users 1:N tickets asignados; tickets 1:N history; tickets 1:N usage; stock 1:N usage. Las claves foráneas evitan referencias huérfanas.

## API

| Método y ruta | Rol | Acción |
|---|---|---|
| GET `/api/health` | Público | Estado del servidor |
| POST `/api/login` | Público | Abre sesión |
| POST `/api/logout` | Todos | Cierra sesión |
| GET `/api/session` | Público | Usuario actual, si existe |
| GET `/api/tickets` | Autenticado | Lista filtrada por rol |
| POST `/api/tickets` | Alumno | Registra reporte |
| GET `/api/tickets/:id` | Autenticado con acceso | Caso, eventos y repuestos |
| POST `/api/tickets/:id/assign` | Admin | Asigna técnico |
| POST `/api/tickets/:id/status` | Rol autorizado | Cambia estado |
| POST `/api/tickets/:id/part` | Admin o técnico asignado | Consume repuesto |
| GET `/api/stock` | Técnico o admin | Inventario |
| GET `/api/staff` | Admin | Técnicos disponibles |
| GET `/api/dashboard` | Autenticado | Indicadores generales (no datos privados de reportes) |

## Reglas y sus capas

- Validación HTTP, sesión y rutas: `server.py`.
- Validaciones RN01–RN14, autorizaciones por rol, estados, stock, auditoría y plazos: `core.py`.
- Visualización, filtros y formularios: `app.js`.
- Restricciones de integridad: esquema SQLite en `core.py`.

## Consistencia

Las escrituras se ejecutan mediante `BEGIN IMMEDIATE`, commit y rollback. Los descuentos de inventario requieren `quantity >= consumo` en la misma sentencia; un fallo de disponibilidad no descuenta stock ni registra consumo. `CHECK(quantity >= 0)` es una segunda barrera.

## Publicación

Archivo `render.yaml` define un servicio Python Free con `python backend/server.py`, salud `/api/health`, `APP_ENV=production`, `DB_PATH=/tmp/aulafix.sqlite3` y secreto `ADMIN_PASSWORD` solicitado al instalar. Se sirve UI + API desde la misma URL, por lo cual no hace falta CORS entre dominios.

## Decisiones técnicas y justificación

- Python estándar: no requiere instalar dependencias, facilita correr y evaluar.
- SQLite: permite demostrar transacciones sin cuenta de base externa.
- Un origen: simplifica el despliegue y elimina configuración CORS.
- Datos y credenciales educativas: no se cargan datos personales reales.

## Restricciones y pasos posteriores

El uso de SQLite en el almacenamiento efímero de Render Free pierde datos al reiniciar. Para producción real se migraría a PostgreSQL administrado, credenciales con hash y autenticación robusta, HTTPS obligatorio en todas las sesiones, observabilidad y tests de carga. El prototipo no afirma resolver esos requisitos de producción.

## Preguntas al analista

Se resolvieron antes de codificar las preguntas sobre roles, cupos, plazos, estados, repuestos, límites de texto y cierre. No hay bloqueantes abiertos en el alcance declarado.
