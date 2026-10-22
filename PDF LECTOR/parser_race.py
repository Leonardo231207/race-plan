import re
from datetime import datetime
from typing import List, Dict, Any


class RaceParser:
    def __init__(self, raw_pages: List[str]):
        self.raw_pages = raw_pages
        self.full_text = "\n".join(raw_pages)
        self.lines = self.full_text.splitlines()

    def extract_by_filter(self, filter_text: str) -> List[Dict[str, Any]]:
        if not filter_text or not filter_text.strip():
            return []

        filter_clean = filter_text.strip()
        results = []

        # Regex para buscar horarios: HH:MM A HH:MM
        time_pattern = re.compile(r'^\s*(\d{1,2}):(\d{2})\s+[Aa]\s+(\d{1,2}):(\d{2})\s+(.+)$')
        # Regex para cabeceras con fecha/dia
        date_pattern = re.compile(r'(LUNES|MARTES|MI[EÉ]RCOLES|JUEVES|VIERNES|S[ÁA]BADO|DOMINGO)\s+\d{1,2}\s+DE\s+[A-ZÁÉÍÓÚ]+', re.IGNORECASE)

        # Detectar si el filtro pide un grupo en específico
        has_group = re.search(r'\(Grupo\s+[A-Z]\)', filter_clean, re.IGNORECASE)
        group_match = re.search(r'\(Grupo\s+([A-Z])\)', filter_clean, re.IGNORECASE)
        group_letter = group_match.group(1).upper() if group_match else None

        # Clase base sin el (Grupo X)
        base_class = re.sub(r'\s*\(Grupo\s+[A-Z]\)', '', filter_clean).strip()

        current_date_header = None

        for line in self.lines:
            # Detectar cabecera de fecha/dia
            dm = date_pattern.search(line)
            if dm and not time_pattern.match(line):
                current_date_header = line.strip()
                continue

            m = time_pattern.match(line)
            if not m:
                continue

            start_h, start_m, end_h, end_m = m.group(1), m.group(2), m.group(3), m.group(4)
            rest = m.group(5).strip()

            if has_group and group_letter:
                line_up = line.upper()
                if filter_clean.upper() in line_up:
                    results.append(self._build_event(start_h, start_m, end_h, end_m, rest, line, current_date_header))
                    continue
                if base_class.upper() in line_up and f'GRUPO {group_letter}' in line_up:
                    results.append(self._build_event(start_h, start_m, end_h, end_m, rest, line, current_date_header))
                    continue
            else:
                if base_class.upper() in line.upper():
                    results.append(self._build_event(start_h, start_m, end_h, end_m, rest, line, current_date_header))
                    continue

        # Ordenar por hora de inicio (y mantener orden de aparicion si misma hora poco comun)
        results.sort(key=lambda x: (int(x['time_start'].split(':')[0]), int(x['time_start'].split(':')[1])))
        return results

    def _build_event(self, sh, sm, eh, em, rest, full_line, date_header):
        desc = rest
        upper = desc.upper()
        tipo = 'OTRO'

        if '1ER' in upper and 'SERIE' in upper:
            tipo = 'SERIE'
        elif '2DA' in upper and 'SERIE' in upper:
            tipo = 'SERIE'
        elif '3ER' in upper and 'SERIE' in upper:
            tipo = 'SERIE'
        elif re.search(r'\b\d+[A-Zªº]?\s+SERIE\b', upper):
            tipo = 'SERIE'
        elif 'SERIE' in upper and 'PRUEBA' not in upper:
            tipo = 'SERIE'
        elif 'FINAL' in upper:
            tipo = 'FINAL'
        elif 'ENTRENAMIENTO' in upper:
            tipo = 'ENTRENAMIENTO'
        elif 'CLASIFICACION' in upper or 'CLASSIFICACION' in upper:
            tipo = 'CLASIFICACION'
        elif 'PRUEBAS LIBRES' in upper:
            tipo = 'LIBRES'

        now_year = datetime.now().year
        try:
            ev_dt = datetime(now_year, datetime.now().month, datetime.now().day, int(sh), int(sm))
        except Exception:
            ev_dt = None

        return {
            "time_start": f"{sh}:{sm}",
            "time_end": f"{eh}:{em}",
            "raw_time": f"{sh}:{sm} A {eh}:{em}",
            "descripcion": desc,
            "tipo": tipo,
            "full_line": full_line.strip(),
            "salida_pista": "Salida a pista",
            "linea_display": f"{sh}:{sm} A {eh}:{em} | Salida a pista | {desc}",
            "fecha_cabecera": date_header if date_header else "",
            "event_hour": int(sh),
            "event_min": int(sm),
            "event_datetime_iso": ev_dt.isoformat() if ev_dt else None
        }

