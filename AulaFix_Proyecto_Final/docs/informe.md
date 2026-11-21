# Informe final de proyecto — AulaFix

**Curso:** Generación T — Bootcamp IA-First, Módulos 4 y 5  
**Trabajo:** Proyecto integrador — Sistema de incidencias y reparación de equipamiento escolar  
**Modalidad:** Individual o grupal, a completar por el titular que entregue  
**Fecha:** Noviembre de 2026

## 1. Presentación

AulaFix nació a partir de un problema frecuente: cuando un equipo de una escuela falla, el aviso suele quedar en un mensaje o conversación y nadie sabe exactamente quién lo está resolviendo, cuál es su urgencia o qué repuesto se gastó. Para organizar ese proceso se construyó un sistema web de mesa de ayuda que permite reportar, asignar, reparar, resolver y cerrar incidencias.

La idea fue elegir una temática propia y concentrar el esfuerzo en reglas de negocio que tengan sentido en una institución, no solamente en un formulario para agregar y eliminar registros.

## 2. Usuarios y funcionamiento

Se definieron tres roles. El alumno puede registrar reportes, ver solo sus incidencias y cancelar aquellas que siguen abiertas. El administrador tiene la vista general, asigna técnicos y valida cierres. El técnico puede atender únicamente los trabajos asignados, registrar consumos de repuestos y explicar el arreglo realizado.

El flujo principal es: creación → asignación → inicio → posible espera → resolución → cierre. Cada acción importante queda en un historial con fecha y autor.

## 3. Reglas que aportan complejidad

El proyecto incluye prioridades con plazos concretos de 4, 12, 48 y 120 horas. También impide que un técnico supere tres trabajos activos, valida cambios entre estados permitidos, exige describir la solución antes de resolver y registra repuestos descontándolos en una transacción que no permite saldo negativo. Estas reglas se comprueban en el servidor aunque se modifique el navegador.

## 4. Metodología y justificación del orden

Primero se definió la idea, los términos y las decisiones del negocio, porque sin esa base podían aparecer reglas contradictorias. Después se diseñó la base y se programaron las reglas críticas: creación, asignación, estados y stock. Se priorizó el stock y la asignación porque son los casos que más requieren integridad y control de concurrencia. Una vez estabilizadas las operaciones se construyeron las rutas HTTP y la interfaz. Finalmente se elaboraron y ejecutaron las pruebas unitarias y se revisó la documentación.

Las tareas, sus dependencias y responsables están registradas en `docs/tasks.md`. El objetivo fue trabajar con una especificación central, separando análisis, arquitectura, backend, frontend, pruebas y revisión.

## 5. Arquitectura y plan técnico

El frontend está realizado en HTML, CSS y JavaScript; el backend, en Python 3 sin librerías de terceros, y la persistencia, en SQLite. Las operaciones se exponen como API JSON. Un mismo servidor ofrece la página y el backend, simplificando el despliegue. El modelo incluye usuarios, tickets, inventario, consumos e historial. Más detalles en `docs/plan.md`.

## 6. Pruebas realizadas

Se ejecutó la suite con `python -m unittest discover -s tests -v` y se obtuvieron **31 tests correctos**. Entre los casos cubiertos están: acceso por rol, credenciales incorrectas, creación válida e inválida, cálculo de vencimientos, asignación a un técnico, bloqueo de cuarto trabajo activo, prohibición de cambios de estado, imposibilidad de resolver sin explicación, no consumir stock negativo, impedir que otro técnico use repuestos y acceso privado a incidencias.

El detalle completo de la ejecución se adjunta como `docs/pruebas.txt`. Las pruebas unitarias de lógica no reemplazan la comprobación manual del funcionamiento una vez que la página esté publicada.

## 7. Publicación y entrega

Se proporciona `render.yaml` para publicar el servicio en Render desde el repositorio GitHub y solicitar de forma segura `ADMIN_PASSWORD`. El enlace definitivo debe agregarse al README por el titular luego de desplegar. No se incluyen enlaces ficticios ni se presenta como realizado un despliegue que requiere conectar la cuenta del alumno.

## 8. Limitaciones y mejoras

En el plan gratuito de Render, `/tmp` es almacenamiento efímero, de modo que SQLite sirve para demostrar el sistema pero no conserva los datos de forma garantizada al reiniciar. Una implementación institucional requeriría almacenamiento persistente, contraseñas con hash, recuperación de acceso, notificaciones y más monitoreo. Se mantiene el alcance limitado para priorizar la corrección de las reglas implementadas.

## 9. Conclusión

AulaFix demuestra cómo transformar una idea concreta en reglas verificables, luego en especificación, arquitectura, código, pruebas y una aplicación web lista para ser publicada. La dificultad principal no fue dibujar pantallas sino diseñar las condiciones de asignación, trazabilidad y consumo seguro de repuestos.
