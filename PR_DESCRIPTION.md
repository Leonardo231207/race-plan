# Implementación del proyecto Race Plan: Gestor, parser multi-categoría, salvapantallas para Windows y compilación .SCR

### Resumen
Este PR implementa el flujo completo solicitado:

- **RacePlan Gestor (`RacePlanGestor.pyw`)**: aplicación de escritorio con carga de PDF, detección automática de categorías, selección múltiple o "Traer TODO", unificación/ordenado por fecha+hora y guardado directo en `AppData\Local\RacePlan\horarios_filtrados.json`.
- **Parser multi-categoría (`parser_race.py`)**: detección de cabeceras de día, extracción por múltiples categorías, opción "sin filtrar", armado con `fecha_cabecera/event_hour/event_min/event_datetime_iso`.
- **Salvapantallas reformado**: `screensaver_scr.py` lee desde AppData con fallback a carpeta local, muestra solo hora actual + siguiente horario importante + cuenta regresiva HH:MM:SS, busca entre varios días con hora actual del sistema, ignora pasados, marca "AHORA / EN MARCHA", salida con mouse/tecla.
- **Previsualización**: `screensaver_preview.py` actualizado para el nuevo flujo.
- **Compilación**: `build_scr.bat` para generar `RacePlan.scr` con pyinstaller (una sola vez).
- **Documentación**: `PLAN_DE_TRABAJO.md` con lista de tareas para seguimiento/tachado.

### Archivos agregados/modificados
- **Agregados**: `RacePlanGestor.pyw`, `build_scr.bat`, `PLAN_DE_TRABAJO.md`
- **Modificados**: `parser_race.py`, `screensaver_scr.py`, `screensaver_preview.py`, `lector.py`, `README.md`

### Cómo probar
1. Instalar dependencias: `PDF LECTOR\install.bat`
2. Abrir gestor: ejecutar `python RacePlanGestor.pyw` o doble clic (sin consola)
3. Cargar PDF → seleccionar categorías o "Traer TODO" → "Generar para Salvapantallas" (guarda en AppData)
4. Probar: `python screensaver_scr.py` o `screensaver_preview.py`
5. Compilar .SCR: `build_scr.bat` → copiar `dist\RacePlan.scr` al lugar deseado

### Notas
- El `.SCR` NO se recompila por cambio de cronograma, solo se sobreescribe el JSON.
- Ruta fija para datos: `%LOCALAPPDATA%\RacePlan\horarios_filtrados.json`
- Multi-categoría soportado tal como se pidió.
