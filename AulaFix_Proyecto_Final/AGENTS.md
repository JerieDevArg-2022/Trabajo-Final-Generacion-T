# AGENTS.md — Reglas generales del proyecto AulaFix

## Misión

Desarrollar y mantener una plataforma de mesa de ayuda escolar con una especificación verificable, evitando lógica de negocio inventada por los agentes.

## Fuente de verdad

1. `docs/spec.md`: reglas RN y HU vigentes.
2. `docs/decisiones.md`: criterios resueltos.
3. `docs/glosario.md`: significado de términos.
4. `docs/plan.md`: arquitectura, API y modelo.
5. `docs/tasks.md`: tareas y dependencias.
6. `docs/preguntas-abiertas.md`: mejoras futuras, no autorizaciones para ampliar alcance.

## Stack

Python estándar + SQLite para backend, HTML/CSS/JS para frontend, unittest para tests, Render para publicación.

## Agentes

- Analista: interpreta necesidades, RN, HU y decisiones.
- Arquitecto: diseña componentes y restricciones.
- Backend: implementa y protege reglas del dominio.
- Frontend: hace visibles los flujos, sin replicar decisiones de negocio sensibles.
- Tester: define casos nominales y borde, verifica resultados.
- Revisor: controla trazabilidad, seguridad básica y coherencia del alcance.

Sus instrucciones específicas se encuentran en `.cursor/rules/`.

## Ciclo de trabajo de cada tarea

1. Leer especificación y dependencia.
2. Registrar comportamiento esperado y tests antes de implementar cambios futuros.
3. Implementar sin cambiar criterios de aceptación por comodidad.
4. Correr `python -m unittest discover -s tests -v`.
5. Revisar casos borde, roles y regresiones.
6. Registrar un commit por tarea aprobada.
7. Actualizar `tasks.md` solo cuando la tarea esté efectivamente realizada.

## Reglas innegociables

- Nunca incluir contraseñas de producción en Git.
- La lógica RN se valida en backend; nunca confiar exclusivamente en controles UI.
- No restar stock fuera de transacciones.
- No mostrar tickets ajenos a alumnos.
- No afirmar pruebas o despliegues que no se hayan ejecutado realmente.
- Mantener la interfaz en español y accesible en móvil.
