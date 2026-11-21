# Plan de tareas

Las tareas se diseñaron pequeñas y por dependencia. Cada línea identifica agente, reglas/historias, criterio de terminado y estado. Las tareas de desarrollo y pruebas están completas; las de cuentas del titular son pasos posteriores.

| ID | Tarea | Agente | RN / HU | Depende de | Criterio de terminado | Estado |
|---|---|---|---|---|---|---|
| T01 | Definir problema y usuarios | Analista | HU01–08 | — | Idea y actores claros | [x] |
| T02 | Definir decisiones y reglas | Analista | RN01–14 | T01 | Spec sin huecos | [x] |
| T03 | Construir tablas y restricciones | Arquitecto | RN01,10,12 | T02 | SQLite inicializa | [x] |
| T04 | Implementar creación y plazos | Backend | RN02,03 / HU01 | T03 | Valida alta y plazo | [x] |
| T05 | Implementar asignación y cupo | Backend | RN04,05 / HU03 | T03 | Rechaza sobreasignación | [x] |
| T06 | Implementar transiciones | Backend | RN06–09,14 / HU04,05 | T04,T05 | Estado inválido rechazado | [x] |
| T07 | Implementar repuestos y auditoría | Backend | RN10–13 / HU06,07 | T03,T06 | Descuento atómico y registro | [x] |
| T08 | Construir API y sesión | Backend | RN01 / HU01–08 | T04–07 | Rutas devuelven JSON | [x] |
| T09 | Diseñar panel de acceso | Frontend | RN01 | T08 | Login por perfil | [x] |
| T10 | Crear vistas y formularios | Frontend | HU01–08 | T08,T09 | Tablero, tickets, detalle, inventario | [x] |
| T11 | Elaborar tests unitarios | Tester | RN01–14 | T04–07 | 31 pruebas pasan | [x] |
| T12 | Revisión de usabilidad y documentación | Revisor | HU01–08 | T10,T11 | README y docs presentes | [x] |
| EX01 | Subir a repositorio público de amigo | Titular | — | T12 | URL propia de GitHub | [ ] |
| EX02 | Desplegar Render y probar online | Titular | — | EX01 | URL pública Live comprobada | [ ] |
| EX03 | Entregar enlace en Módulo 5 | Titular | — | EX02 | Enlace enviado al aula | [ ] |

Nota: las últimas tres tareas requieren credenciales y acciones reales del alumno propietario, por eso no se marcan como completadas de manera ficticia.
