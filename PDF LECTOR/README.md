# Race Plan - Lector de PDF para Salvapantallas

Sistema para leer PDFs de cronogramas, filtrar por clase tal cual aparece en el cronograma y mostrarlo en modo salvapantallas.

## FASE 1 - Instalación

### Requisitos
- Windows 7 / Windows 10
- Python 3.8 - 3.10 (recomendado para mejor compatibilidad con PyQt5 en equipos antiguos)

### Instalación rápida
1. Abrir `PDF LECTOR/`
2. Ejecutar `install.bat`
3. Esperar a que instale todo

### Instalación manual
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

### 1) Extraer y filtrar por clase
```bash
venv\Scripts\activate
python lector.py
```

Pasos:
1. `Seleccionar archivo PDF` - Carga el cronograma
2. Escribir el filtro **tal cual aparece** en el cronograma. Ejemplos:
   - `PROCAR 4000 "CLASE A" (Grupo A)` (para entrenamientos/pruebas con grupo)
   - `PROCAR 4000 "CLASE A"` (para **series y final** sin grupo)
3. `Extraer horarios por filtro` - Muestra preview
4. `Guardar FILTRADO para salvapantallas (horarios_filtrados.json)` - Genera el archivo para el preview

### 2) Previsualizar modo salvapantallas
```bash
venv\Scripts\activate
python screensaver_preview.py
```

**Controles:**
- `ESC` - Salir
- `←` / `-` - -10 minutos
- `→` / `+` / `=` - +10 minutos
- `↑` - +1 hora
- `↓` - -1 hora
- `R` - Volver a hora real

El salvapantallas va a:
- Resaltar en **ROJO** lo que esté en curso
- Resaltar en **AMARILLO** el próximo evento
- Atenuar lo ya pasado
- Mostrar `Salida a pista` junto con hora y descripción tal como lo pediste

## Lógica del filtro

- **Con grupo `(Grupo A)`**: Trae únicamente lo que coincida con ese grupo (entrenamientos, pruebas libres)
- **Sin grupo**: Trae todo lo relacionado a esa clase base (1er/2da/3ra serie, final). Así ves los 3 juntos tal como lo necesitás

## Archivos importantes
- `lector.py` - Interfaz para cargar PDF y filtrar
- `parser_race.py` - Lógica de filtrado por texto exacto
- `screensaver_preview.py` - Preview en pantalla completa con simulador de tiempo
- `horarios_filtrados.json` - Generado al guardar filtrado (usado por el preview)
- `a.json` - Ejemplo con cronograma

## Notas
- Usar JSON local (no MySQL). Más liviano para esas PCs
- El filtro debe ir **exactamente** como está escrito en el PDF para mayor precisión
- Para las series, escribir solo `PROCAR 4000 "CLASE A"` (sin grupo) trae todas las series juntas
