import sys
import pdfplumber
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QTextEdit, QFileDialog, QLabel, QLineEdit,
                             QHBoxLayout, QMessageBox)
from parser_race import RaceParser


class PdfReaderApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana
        self.setWindowTitle("Race Plan - Lector de PDF con Filtro por Clase")
        self.setGeometry(100, 100, 700, 550)

        # Layout principal
        layout = QVBoxLayout()

        # Botón para seleccionar archivo PDF
        self.select_button = QPushButton("1) Seleccionar archivo PDF")
        self.select_button.clicked.connect(self.select_pdf_file)
        layout.addWidget(self.select_button)

        # Info PDF cargado
        self.pdf_label = QLabel("PDF cargado: (ninguno)")
        layout.addWidget(self.pdf_label)

        # Filtro por texto tal cual aparece en el cronograma
        filter_layout = QVBoxLayout()
        self.filter_label = QLabel('2) Escribir filtro TAL CUAL aparece en el cronograma')
        self.filter_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(self.filter_label)

        self.filter_hint = QLabel('Ej: PROCAR 4000 "CLASE A" (Grupo A)  |  O  PROCAR 4000 "CLASE A"  (para series/finales)')
        self.filter_hint.setStyleSheet("color: gray;")
        filter_layout.addWidget(self.filter_hint)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('PROCAR 4000 "CLASE A" (Grupo A)')
        filter_layout.addWidget(self.filter_input)

        layout.addLayout(filter_layout)

        # Botón para extraer por filtro
        self.extract_filter_button = QPushButton("3) Extraer horarios por filtro")
        self.extract_filter_button.clicked.connect(self.extract_by_filter)
        layout.addWidget(self.extract_filter_button)

        # Área de texto para mostrar preview filtrado
        self.preview_label = QLabel("Vista previa (formato para salvapantallas):")
        self.preview_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.preview_label)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Botones para guardar
        buttons_layout = QHBoxLayout()
        self.save_raw_button = QPushButton("Guardar TODO el PDF (horarios.json)")
        self.save_raw_button.clicked.connect(self.save_raw_to_file)
        buttons_layout.addWidget(self.save_raw_button)

        self.save_filtered_button = QPushButton("Guardar FILTRADO para salvapantallas (horarios_filtrados.json)")
        self.save_filtered_button.clicked.connect(self.save_filtered_to_file)
        buttons_layout.addWidget(self.save_filtered_button)

        layout.addLayout(buttons_layout)

        # Establecer layout
        self.setLayout(layout)

        # Variables
        self.pdf_path = None
        self.raw_pages = []
        self.filtered_events = []

    def select_pdf_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo PDF", "", "Archivos PDF (*.pdf)")
        if file_name:
            self.pdf_path = file_name
            self.pdf_label.setText(f"PDF cargado: {os.path.basename(file_name)}")
            self.extract_raw(file_name)

    def extract_raw(self, pdf_path):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                self.raw_pages = pages
            QMessageBox.information(self, "PDF cargado", f"Se extrajeron {len(pages)} página(s) correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el PDF:\n{e}")

    def extract_by_filter(self):
        if not self.raw_pages:
            QMessageBox.warning(self, "Sin datos", "Primero seleccioná un archivo PDF")
            return

        filter_text = self.filter_input.text().strip()
        if not filter_text:
            QMessageBox.warning(self, "Sin filtro", 'Escribí el filtro tal cual aparece en el cronograma.\nEj: PROCAR 4000 "CLASE A" (Grupo A)')
            return

        try:
            parser = RaceParser(self.raw_pages)
            self.filtered_events = parser.extract_by_filter(filter_text)

            if not self.filtered_events:
                self.text_area.setPlainText("[SIN RESULTADOS]\n\nProbá con otro texto.\nRecordá copiarlo EXACTAMENTE como aparece en el cronograma.")
                QMessageBox.warning(self, "Sin resultados", "No se encontró nada con ese filtro.\nRevisá mayúsculas/minúsculas, comillas, paréntesis.")
                return

            # Mostrar preview
            lines_out = []
            for ev in self.filtered_events:
                lines_out.append(ev['linea_display'])
            self.text_area.setPlainText("\n".join(lines_out))
            QMessageBox.information(self, "Extraído", f"Se encontraron {len(self.filtered_events)} evento(s) para ese filtro.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar:\n{e}")

    def save_raw_to_file(self):
        if not self.raw_pages:
            QMessageBox.warning(self, "Sin datos", "Primero seleccioná un archivo PDF")
            return
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(current_directory, 'horarios.json')
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(self.raw_pages, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Guardado", f"Guardado: {file_name}")
            print(f"Horarios guardados en {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def save_filtered_to_file(self):
        if not self.filtered_events:
            QMessageBox.warning(self, "Sin datos filtrados", "Primero hacé 'Extraer horarios por filtro'")
            return
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(current_directory, 'horarios_filtrados.json')
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(self.filtered_events, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Guardado", f"Guardado: {file_name}\nListo para usar con screensaver_preview.py")
            print(f"Horarios filtrados guardados en {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PdfReaderApp()
    window.show()
    sys.exit(app.exec_())

