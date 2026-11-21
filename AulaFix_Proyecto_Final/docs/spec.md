# Especificación funcional — AulaFix

## Objetivo y alcance

Plataforma de seguimiento de fallas tecnológicas escolares con roles alumno, técnico y administrador. Incluye reportes, asignación, gestión de estados, repuestos, historial y publicación web. Excluye emails, adjuntos y compras.

## Reglas de negocio

- **RN01 — Identificación y permisos.** Solo usuarios autenticados acceden a las operaciones. Un alumno ve únicamente sus propias incidencias. Solo los técnicos ven inventario; solo administración puede asignar responsables.
- **RN02 — Alta validada.** Solo un alumno crea un reporte, con título de 5 a 100 caracteres, descripción de 10 a 1000, ubicación de 2 a 100, categoría `hardware`, `software`, `red` u `otro` y prioridad válida.
- **RN03 — Fecha límite.** Desde la fecha de creación se asignan 4 h a crítica, 12 h a alta, 48 h a media y 120 h a baja. Son horas corridas UTC.
- **RN04 — Asignación.** Solo administración asigna un técnico existente. No se puede asignar a un alumno ni a una incidencia cerrada o cancelada.
- **RN05 — Cupo técnico.** Cada técnico puede tener como máximo tres incidencias en `en_proceso` y `en_espera` simultáneamente (no se cuentan las `abierto`).
- **RN06 — Estados.** `abierto→en_proceso/cancelado`; `en_proceso→en_espera/resuelto/cancelado`; `en_espera→en_proceso/cancelado`; `resuelto→cerrado/en_proceso`; `cerrado` y `cancelado` son terminales.
- **RN07 — Inicio de atención.** Solo puede pasar a `en_proceso` si ya tiene un técnico asignado.
- **RN08 — Resolución.** Para pasar a `resuelto` debe cargarse una descripción de solución de mínimo 10 caracteres.
- **RN09 — Permisos de transición.** El alumno únicamente cancela reportes propios `abierto`. El técnico solamente cambia estados de sus reportes y no puede cerrarlos ni cancelarlos. Administración puede realizar transiciones permitidas.
- **RN10 — Stock.** Solo se descuentan cantidades enteras positivas; el saldo no puede quedar negativo. Descuentos concurrentes se serializan por una transacción.
- **RN11 — Uso de repuestos.** Solo puede descontarse stock en una incidencia `en_proceso`; administración o el técnico asignado registra la salida.
- **RN12 — Auditoría.** Altas, asignaciones, cambios de estado y consumos generan entradas de historial con fecha y autor.
- **RN13 — Alerta de inventario.** Un repuesto presenta alerta cuando `cantidad <= mínimo`.
- **RN14 — Cierre final.** Solo administración cierra una incidencia resuelta; no es posible reabrir una cerrada.

## Historias de usuario y criterios de aceptación

### HU01 — Reportar una falla (RN01, RN02, RN03)
**Como** alumno **quiero** registrar una falla **para** solicitar asistencia.
- Dado que inicié sesión como alumno, cuando completo datos válidos, entonces se crea un reporte abierto con plazo calculado.
- Dado que ingreso una descripción de menos de 10 caracteres, cuando envío, entonces recibo error y no se registra el reporte.

### HU02 — Ver mis casos (RN01)
**Como** alumno **quiero** revisar mis incidencias **para** conocer su avance.
- Dado que hay reportes de otros alumnos, cuando consulto, entonces solo veo los propios.

### HU03 — Asignar responsable (RN04, RN05)
**Como** administrador **quiero** asignar técnicos **para** distribuir el trabajo.
- Dado que selecciono un usuario técnico y un caso abierto, cuando asigno, entonces queda visible el responsable.
- Dado que un técnico ya tiene tres casos en atención, cuando intento una cuarta asignación, entonces el sistema la rechaza.

### HU04 — Avanzar estado (RN06, RN07, RN09, RN14)
**Como** técnico **quiero** actualizar el estado **para** registrar la intervención.
- Dado que un caso no está asignado, cuando intento iniciarlo, entonces se rechaza.
- Dado que el técnico intenta cerrar un caso, cuando solicita el cierre, entonces se rechaza.

### HU05 — Documentar reparación (RN08)
**Como** técnico **quiero** escribir el diagnóstico final **para** registrar lo realizado.
- Dado que no escribí al menos 10 caracteres, cuando intento resolver, entonces no cambia el estado.

### HU06 — Registrar repuestos (RN10, RN11, RN13)
**Como** técnico **quiero** registrar los repuestos usados **para** actualizar el inventario.
- Dado que quedan dos unidades, cuando intento gastar tres, entonces el saldo no cambia.
- Dado que el caso está en proceso, cuando consumo una unidad disponible, entonces queda descontada y registrada.

### HU07 — Consultar trazabilidad (RN12)
**Como** administrador **quiero** ver el historial **para** auditar acciones.
- Dado que hay cambios de estado y asignación, cuando consulto el detalle, entonces aparece cada evento en orden descendente.

### HU08 — Cancelar un reporte (RN09)
**Como** alumno **quiero** cancelar un reporte propio abierto **para** indicar que ya no necesito asistencia.
- Dado que mi incidencia está abierta, cuando la cancelo, entonces el estado es cancelado.
- Dado que es una incidencia ajena, cuando intento cancelarla, entonces se rechaza.

## Casos borde

- Doble consumo del último repuesto: solo una operación lo descuenta.
- Asignación a usuario inexistente: error.
- Estado fuera de grafo: error sin cambios.
- Cantidad negativa, cero o texto: error.
- Sesión no autenticada: HTTP 401.
- Incidencia ajena consultada por alumno: error.
- Técnicos sin caso asignado: no pueden intervenir.

## Pendientes de especificación

**Ninguno para el alcance de esta entrega.** Las posibles mejoras futuras se enumeran por separado en `preguntas-abiertas.md`.
