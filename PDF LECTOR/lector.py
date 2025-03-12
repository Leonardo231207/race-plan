import sys
import pdfplumber
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
import os

class PdfReaderApp(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana
        self.setWindowTitle("Lector de Horarios PDF")
        self.setGeometry(100, 100, 600, 400)

        # Layout de la interfaz
        layout = QVBoxLayout()

        # Crear botón para seleccionar archivo PDF
        self.select_button = QPushButton("Seleccionar archivo PDF")
        self.select_button.clicked.connect(self.select_pdf_file)
        layout.addWidget(self.select_button)

        # Crear área de texto para mostrar los horarios extraídos
        self.text_area = QTextEdit(self)
        layout.addWidget(self.text_area)

        # Crear botón para guardar los horarios en un archivo
        self.save_button = QPushButton("Guardar Horarios")
        self.save_button.clicked.connect(self.save_to_file)
        layout.addWidget(self.save_button)

        # Establecer el layout en la ventana
        self.setLayout(layout)

        # Variable para almacenar los horarios extraídos
        self.horarios = []

    def select_pdf_file(self):
        """Abrir un cuadro de diálogo para seleccionar un archivo PDF y extraer los horarios"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo PDF", "", "Archivos PDF (*.pdf)")
        if file_name:
            self.extract_horarios(file_name)

    def extract_horarios(self, pdf_path):
        """Extraer los horarios del archivo PDF usando pdfplumber"""
        with pdfplumber.open(pdf_path) as pdf:
            horarios = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Aquí podrías agregar lógica para filtrar o procesar los horarios que necesitas
                    # Por ejemplo, buscando patrones específicos
                    horarios.append(text)  # Simplemente guardamos todo el texto por ahora

            # Mostrar los horarios extraídos en el área de texto
            self.horarios = horarios
            self.text_area.setPlainText("\n".join(horarios))
    def save_to_file(self):
        """Guardar los horarios extraídos en un archivo JSON en la misma carpeta"""
        # Obtener la ruta actual del script
        current_directory = os.getcwd()

        # Construir la ruta del archivo 'horarios.json'
        file_name = os.path.join(current_directory, 'horarios.json')

        # Guardar los horarios en ese archivo
        with open(file_name, 'w') as f:
            json.dump(self.horarios, f)
        print(f"Horarios guardados en {file_name}")



# Ejecutar la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PdfReaderApp()
    window.show()
    sys.exit(app.exec_())
