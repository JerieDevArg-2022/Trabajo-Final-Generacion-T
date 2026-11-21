# Decisiones tomadas

| Pregunta | Decisión | Motivo |
|---|---|---|
| ¿Quién puede reportar? | Solo alumnos. | Evita entradas no identificadas. |
| ¿Qué información se exige? | Título (5–100 caracteres), descripción (10–1000), ubicación (2–100), categoría y prioridad. | Datos suficientes para diagnóstico. |
| ¿Cómo se fija la urgencia? | Crítica 4 horas, alta 12, media 48 y baja 120. | Criterio simple y medible. |
| ¿Quién asigna? | Administración. | Centraliza carga de trabajo. |
| ¿A quién se asigna? | Solo usuarios técnicos. | Respeta funciones. |
| ¿Cuántas intervenciones simultáneas puede tener un técnico? | Tres en proceso o espera. | Evita sobreasignación. |
| ¿Se saltean estados? | No; se usa un grafo de transiciones explícito. | Permite auditoría clara. |
| ¿Se permite resolver sin explicación? | No; mínimo 10 caracteres. | Exige registro de solución. |
| ¿Cuándo se usan repuestos? | Solo mientras el caso esté en proceso. | Vincula stock con intervención real. |
| ¿Qué pasa si dos consumen el último repuesto? | Transacción `BEGIN IMMEDIATE` y `UPDATE` condicionado por stock. | No queda saldo negativo. |
| ¿Quién cierra? | Administración. | Separación de resolución y verificación. |
| ¿Puede cancelar el alumno? | Solo sus casos abiertos. | Evita borrar trabajo ya iniciado. |
| ¿Qué persistencia se utiliza? | SQLite para prototipo educativo. | Facilita ejecución y pruebas sin servicios externos. |
