==============
PC CRM to Task
==============

**Autor:** Process Control | https://www.processcontrol.es

Módulo base de área que añade un botón en las oportunidades de CRM para crear
tareas de proyecto, con sistema de valores por defecto a cinco niveles
(ajustes, empresa, equipo CRM, etapa CRM, asistente) y notificaciones
configurables (correo y/o actividad).

Funcionalidades
===============

* Botón **Crear tarea** en el formulario de oportunidad (`crm.lead`).
* Asistente con todos los campos relevantes (proyecto, responsables múltiples,
  etiqueta, etapa, fecha límite, prioridad, descripción).
* Resolución jerárquica de valores por defecto:
  etapa > equipo > empresa > vacío.
* Tres modos de comportamiento configurables:
    - **Siempre asistente** — abre el asistente independientemente de los defaults.
    - **Asistente si faltan datos** — abre el asistente solo si falta proyecto o responsables.
    - **Directo si hay defaults** — crea la tarea sin preguntar cuando los defaults son completos.
* Transferencia configurable del lead a la tarea:
    - Historial de chatter (mensajes).
    - Adjuntos.
    - Seguidores.
* Creación automática de tarea al cambiar la oportunidad a una etapa marcada
  como **Auto-crear tarea**, con dos niveles de kill switch (global + por etapa)
  y opción de evitar duplicados si el lead ya tiene tarea.
* Notificación al asignado configurable (correo + actividad), con plantilla
  por defecto incluida en el módulo y siguiendo la norma gráfica de
  Process Control.
* Botón inteligente **Tareas** en la oportunidad y botón inteligente
  **Oportunidad** en la tarea.
* Filtro de búsqueda **Desde oportunidad** en project.task.

Configuración
=============

1. Ir a *Ajustes > CRM > CRM → Task (Process Control)*.
2. Definir el modo de comportamiento, la estrategia de responsables y los
   valores por defecto a nivel empresa (proyecto, responsables, etapa, etiquetas).
3. (Opcional) En *CRM > Configuración > Equipos*, sobreescribir los defaults
   de empresa para un equipo concreto.
4. (Opcional) En *CRM > Configuración > Etapas*, marcar las etapas que deben
   crear tarea automáticamente al recibir un lead, y elegir el proyecto destino.

Uso
===

* Desde una oportunidad: pulsar **Crear tarea** en la cabecera. Según el modo
  configurado, se abrirá el asistente o se creará la tarea directamente.
* Desde una etapa con creación automática: arrastrar la oportunidad a esa
  etapa en la vista kanban — la tarea se crea sola.

Datos técnicos
==============

**Modelos nuevos:**

* ``crm.lead.to.task.wizard`` — asistente transitorio.

**Modelos extendidos:**

* ``crm.lead`` — botón, smart button, defaults resolution y hook write().
* ``crm.stage`` — campos pc_auto_create_task y pc_auto_task_*.
* ``crm.team`` — defaults de proyecto/responsables/etiquetas a nivel equipo.
* ``project.task`` — campo pc_lead_id y smart button origen.
* ``res.company`` — defaults a nivel empresa.
* ``res.config.settings`` — todos los ajustes globales.

**Plantillas entregadas (noupdate):**

* ``mail.activity.type`` — *Task from opportunity*.
* ``mail.template`` — *CRM → Task: notification to assignees* con norma gráfica
  Process Control.

Créditos
========

**Desarrollado por** `Process Control <https://www.processcontrol.es>`_
