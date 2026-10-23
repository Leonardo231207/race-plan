import sys
import json
import os
import re
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QCheckBox, QScrollArea,
                             QMessageBox, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import pdfplumber


class RacePlanGestor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RacePlan Gestor")
        self.setGeometry(100, 100, 750, 650)
        
        self.pdf_path = None
        self.raw_pages = []
        self.all_events = []  # Todos los eventos parseados con match_key
        self.match_keys = []
        self.category_checkboxes = []
        
        layout = QVBoxLayout()
        
        title = QLabel("RACEPLAN GESTOR")
        title_font = QFont("Arial", 16, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.load_btn = QPushButton("1) Cargar PDF")
        self.load_btn.clicked.connect(self.load_pdf)
        layout.addWidget(self.load_btn)
        
        self.pdf_label = QLabel("PDF: (ninguno)")
        self.pdf_label.setWordWrap(True)
        layout.addWidget(self.pdf_label)
        
        info_label = QLabel("Marcá el grupo con el que salís + el sin grupo para traer TODO lo que te toca")
        info_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()
        self.all_checkbox = QCheckBox("Traer TODO el cronograma sin filtrar")
        self.all_checkbox.stateChanged.connect(self.toggle_all)
        options_layout.addWidget(self.all_checkbox)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        categories_group = QGroupBox("2) Seleccionar clases que vas a salir (marcá grupo + sin grupo)")
        categories_layout = QVBoxLayout()
        self.categories_label = QLabel("Cargá un PDF para detectar")
        categories_layout.addWidget(self.categories_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.scroll_area.setWidget(self.categories_widget)
        categories_layout.addWidget(self.scroll_area)
        
        btns_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Seleccionar todo")
        self.select_all_btn.clicked.connect(self.select_all_cats)
        self.deselect_all_btn = QPushButton("Deseleccionar todo")
        self.deselect_all_btn.clicked.connect(self.deselect_all_cats)
        btns_layout.addWidget(self.select_all_btn)
        btns_layout.addWidget(self.deselect_all_btn)
        categories_layout.addLayout(btns_layout)
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        self.generate_btn = QPushButton("3) Generar para Salvapantallas")
        self.generate_btn.clicked.connect(self.generate_screensaver)
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(self.generate_btn)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        self.all_checkbox.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
    
    def load_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo PDF", "", "Archivos PDF (*.pdf)")
        if file_name:
            self.pdf_path = file_name
            self.pdf_label.setText(f"PDF: {os.path.basename(file_name)}")
            self.extract_and_parse()
    
    def extract_and_parse(self):
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                self.raw_pages = pages
            
            full_text = "\n".join(self.raw_pages)
            self.parse_events(full_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el PDF:\n{e}")
    
    def get_match_key(self, descripcion):
        s = descripcion.upper()
        # PROCAR 4000 con formato "B" o "A" (puede tener guiones, comillas distintas)
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*CLASE\s+([AB])\s*["\u201c\u201d]?\s*[-–]\s*GRUPO\s+([AB])', s)
        if m:
            return f'PROCAR 4000 "CLASE {m.group(1)}" (Grupo {m.group(2)})'
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*([AB])\s*["\u201c\u201d]?\s*[-–]\s*GRUPO\s+([AB])', s)
        if m:
            return f'PROCAR 4000 "{m.group(1)}" (Grupo {m.group(2)})'
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*CLASE\s+([AB])\s*["\u201c\u201d]?\s*\(GRUPO\s+([AB])\)', s)
        if m:
            return f'PROCAR 4000 "CLASE {m.group(1)}" (Grupo {m.group(2)})'
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*([AB])\s*["\u201c\u201d]?\s*\(GRUPO\s+([AB])\)', s)
        if m:
            return f'PROCAR 4000 "{m.group(1)}" (Grupo {m.group(2)})'
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*CLASE\s+([AB])\s*["\u201c\u201d]?', s)
        if m and not re.search(r'GRUPO\s+[AB]', s):
            return f'PROCAR 4000 "CLASE {m.group(1)}"'
        m = re.search(r'PROCAR\s+4000\s+["\u201c\u201d]?\s*([AB])\s*["\u201c\u201d]?', s)
        if m and not re.search(r'GRUPO\s+[AB]', s):
            return f'PROCAR 4000 "{m.group(1)}"'
        if re.search(r'PROCAR\s+2000', s):
            return 'PROCAR 2000'
        m = re.search(r'F[OÓ]RMULA\s*1\s*GRUPO\s+([12])', s)
        if m:
            return f'FÓRMULA 1 (Grupo {m.group(1)})'
        if re.search(r'F1\s*M\.?A\.?|F[OÓ]RMULA\s*1', s):
            return 'FÓRMULA 1'
        m = re.search(r'F[ÓO]RMULA\s*07', s)
        if m:
            m2 = re.search(r'F[ÓO]RMULA\s*07\s*["\u201c\u201d]?([AB])["\u201c\u201d]?', s)
            if m2:
                return f'FORMULA 07 "{m2.group(1)}"'
            return 'FORMULA 07'
        if re.search(r'FIAT\s+UNO\s+ASM', s):
            return 'FIAT UNO ASM'
        m = re.search(r'\bSPA\b.*GRUPO\s+([12])', s)
        if m:
            return f'SPA (Grupo {m.group(1)})'
        if re.search(r'\bSPA\b', s):
            return 'SPA'
        return None
    
    def parse_events(self, full_text):
        lines = full_text.splitlines()
        current_date = None
        events = []
        
        time_pattern = re.compile(r'^\s*(\d{1,2}):(\d{2})\s+[Aa]\s+(\d{1,2}):(\d{2})', re.I)
        date_pattern = re.compile(r'^(VIERNES|SABADO|DOMINGO|JUEVES|MIERCOLES|MARTES|LUNES)\s+\d{1,2}', re.I)
        
        for line in lines:
            s = line.strip()
            if not s:
                continue
            su = s.upper()
            
            if date_pattern.match(s):
                current_date = s
                continue
            
            m_time = time_pattern.match(s)
            if not m_time:
                continue
            
            start_h, start_m = m_time.group(1), m_time.group(2)
            end_h, end_m = m_time.group(3), m_time.group(4)
            
            # Extraer descripción - todo lo que viene después del horario
            # En pdfplumber viene en la misma línea
            rest = s[m_time.end():].strip()
            # Limpiar "Hs." y "Salida a pista" al inicio si aparece
            rest = re.sub(r'^\s*Hs\.?\s*', '', rest, flags=re.I)
            rest = rest.strip()
            
            if not rest or rest.upper().startswith(('SALIDA', 'CAMARA', 'EN VIVO')):
                continue
            
            match_key = self.get_match_key(rest)
            if not match_key:
                continue
            
            events.append({
                "fecha_cabecera": current_date or "",
                "time_start": f"{start_h}:{start_m}",
                "time_end": f"{end_h}:{end_m}",
                "raw_time": f"{start_h}:{start_m} A {end_h}:{end_m}",
                "descripcion": rest,
                "match_key": match_key,
                "salida_pista": "Salida a pista",
                "linea_display": f"{start_h}:{start_m} A {end_h}:{end_m} | Salida a pista | {rest}",
                "event_hour": int(start_h),
                "event_min": int(start_m),
            })
        
        self.all_events = events
        
        # Obtener match_keys únicos manteniendo orden
        seen_keys = set()
        keys_list = []
        for ev in events:
            k = ev['match_key']
            if k not in seen_keys:
                seen_keys.add(k)
                keys_list.append(k)
        self.match_keys = keys_list
        
        # Crear checkboxes
        for cb in self.category_checkboxes:
            self.categories_layout.removeWidget(cb)
            cb.deleteLater()
        self.category_checkboxes = []
        
        if self.match_keys:
            self.categories_label.setText(f"Clases detectadas ({len(self.match_keys)}): Marcá grupo + sin grupo para traer TODO lo que te toca")
            for k in self.match_keys:
                cb = QCheckBox(k)
                self.categories_layout.addWidget(cb)
                self.category_checkboxes.append(cb)
        else:
            self.categories_label.setText("No se detectaron clases")
        
        self.all_checkbox.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)
    
    def toggle_all(self, state):
        if state == Qt.Checked:
            for cb in self.category_checkboxes:
                cb.setChecked(False)
                cb.setEnabled(False)
        else:
            for cb in self.category_checkboxes:
                cb.setEnabled(True)
    
    def select_all_cats(self):
        if self.all_checkbox.isChecked():
            return
        for cb in self.category_checkboxes:
            cb.setChecked(True)
    
    def deselect_all_cats(self):
        if self.all_checkbox.isChecked():
            return
        for cb in self.category_checkboxes:
            cb.setChecked(False)
    
    def generate_screensaver(self):
        if not self.all_events:
            QMessageBox.warning(self, "Sin datos", "Primero cargá un archivo PDF")
            return
        
        events_out = []
        
        if self.all_checkbox.isChecked():
            events_out = list(self.all_events)
        else:
            selected = []
            for cb in self.category_checkboxes:
                if cb.isChecked():
                    selected.append(cb.text())
            
            if not selected:
                QMessageBox.warning(self, "Sin selección", "Seleccioná al menos una clase o marcá 'Traer TODO'")
                return
            
            for ev in self.all_events:
                if ev['match_key'] in selected:
                    events_out.append(ev)
        
        events_out.sort(key=lambda x: (x.get('event_hour', 99), x.get('event_min', 99)))
        all_sorted = list(self.all_events)
        all_sorted.sort(key=lambda x: (x.get('event_hour', 99), x.get('event_min', 99)))
        
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.expanduser('~\\AppData\\Local')
        target_dir = os.path.join(appdata, 'RacePlan')
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, 'horarios_filtrados.json')
        target_file_all = os.path.join(target_dir, 'horarios_todo.json')
        
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(events_out, f, ensure_ascii=False, indent=2)
            with open(target_file_all, 'w', encoding='utf-8') as f:
                json.dump(all_sorted, f, ensure_ascii=False, indent=2)
            self.status_label.setText(f"✓ Guardado en:\n{target_file}\n\n{len(events_out)} evento(s) | Total: {len(all_sorted)}")
            QMessageBox.information(self, "Listo", f"Guardado correctamente!\nMi filtro: {len(events_out)} evento(s)\nCronograma completo: {len(all_sorted)} evento(s)\n\n{target_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RacePlanGestor()
    window.show()
    sys.exit(app.exec_())

