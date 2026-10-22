import sys
import json
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor


class ScreensaverPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Race Plan - Salvapantallas")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.showFullScreen()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(100, 80, 100, 80)
        self.layout.setSpacing(40)

        # Titulo
        self.title = QLabel("RACE PLAN")
        self.title.setAlignment(Qt.AlignCenter)
        font_title = QFont("Consolas", 30, QFont.Bold)
        self.title.setFont(font_title)
        self.title.setStyleSheet("color: white;")
        self.layout.addWidget(self.title)

        # Hora actual del sistema
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        font_clock = QFont("Consolas", 130, QFont.Bold)
        self.clock_label.setFont(font_clock)
        self.clock_label.setStyleSheet("color: #00ff88;")
        self.layout.addWidget(self.clock_label)

        # Siguiente horario importante
        self.next_label = QLabel("BUSCANDO SIGUIENTE HORARIO...")
        self.next_label.setAlignment(Qt.AlignCenter)
        font_next = QFont("Consolas", 42, QFont.Bold)
        self.next_label.setFont(font_next)
        self.next_label.setStyleSheet("color: #ffff00;")
        self.next_label.setWordWrap(True)
        self.layout.addWidget(self.next_label)

        # Tiempo restante
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        font_cd = QFont("Consolas", 72, QFont.Bold)
        self.countdown_label.setFont(font_cd)
        self.countdown_label.setStyleSheet("color: #ff8800;")
        self.layout.addWidget(self.countdown_label)

        # Footer
        self.footer = QLabel("PREVIEW | ESC = Salir | ←/- -10m | →/+/= +10m | ↑ +1h | ↓ -1h | R = Hora real del sistema")
        self.footer.setAlignment(Qt.AlignCenter)
        font_footer = QFont("Consolas", 14)
        self.footer.setFont(font_footer)
        self.footer.setStyleSheet("color: #333333;")
        self.layout.addWidget(self.footer)

        self.filtered_events = []
        self.sim_offset_minutes = 0
        self.use_real_time = True

        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

        self.update_display()

    def load_data(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, 'horarios_filtrados.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.filtered_events = data
            except Exception as e:
                print(e)
                self.filtered_events = []
        else:
            self.filtered_events = []

    def get_current_time(self):
        now = datetime.now()
        if not self.use_real_time:
            now = now + timedelta(minutes=self.sim_offset_minutes)
        return now

    def time_to_dt(self, ev):
        now = self.get_current_time()
        try:
            sh = int(ev.get('event_hour')) if ev.get('event_hour') is not None else int(ev.get('time_start', '0:0').split(':')[0])
            sm = int(ev.get('event_min')) if ev.get('event_min') is not None else int(ev.get('time_start', '0:0').split(':')[1])
            dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            return dt
        except Exception:
            return None

    def update_display(self):
        now = self.get_current_time()
        self.clock_label.setText(now.strftime("%H:%M:%S"))

        if not self.filtered_events:
            self.next_label.setText("SIN HORARIOS FILTRADOS - CARGÁ horarios_filtrados.json")
            self.next_label.setStyleSheet("color: #ff3333;")
            self.countdown_label.setText("")
            return

        # Buscar siguiente evento (por hora del sistema, ignorando dia si no coincide - evaluar siempre con hora actual)
        candidates = []
        for ev in self.filtered_events:
            dt = self.time_to_dt(ev)
            if dt is None:
                continue
            # si ya paso hace mas de 2 horas, lo ignoramos para "siguiente"
            if dt < now - timedelta(hours=2):
                continue
            candidates.append((dt, ev))

        if not candidates:
            # mostrar ultimo del dia o ninguno
            self.next_label.setText("NO HAY MAS HORARIOS A EVALUAR CON HORA ACTUAL")
            self.next_label.setStyleSheet("color: #888888;")
            self.countdown_label.setText("")
            return

        # ordenar por fecha/hora
        candidates.sort(key=lambda x: x[0])
        next_dt, next_ev = candidates[0]

        diff = next_dt - now
        total_seconds = int(diff.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        h_rem = total_seconds // 3600
        m_rem = (total_seconds % 3600) // 60
        s_rem = total_seconds % 60

        if total_seconds <= 0:
            self.next_label.setText(f"AHORA / EN MARCHA | {next_ev.get('raw_time','')} | {next_ev.get('salida_pista','Salida a pista')} | {next_ev.get('descripcion','')}")
            self.next_label.setStyleSheet("color: #ff3333;")
            self.countdown_label.setText("00:00:00")
        else:
            self.next_label.setText(f"SIGUIENTE HORARIO IMPORTANTE | {next_ev.get('raw_time','')} | {next_ev.get('salida_pista','Salida a pista')} | {next_ev.get('descripcion','')}")
            self.next_label.setStyleSheet("color: #ffff00;")
            self.countdown_label.setText(f"FALTAN {h_rem:02d}:{m_rem:02d}:{s_rem:02d}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_Right or key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.use_real_time = False
            self.sim_offset_minutes += 10
            self.update_display()
        elif key == Qt.Key_Left or key == Qt.Key_Minus:
            self.use_real_time = False
            self.sim_offset_minutes -= 10
            self.update_display()
        elif key == Qt.Key_Up:
            self.use_real_time = False
            self.sim_offset_minutes += 60
            self.update_display()
        elif key == Qt.Key_Down:
            self.use_real_time = False
            self.sim_offset_minutes -= 60
            self.update_display()
        elif key == Qt.Key_R:
            self.use_real_time = True
            self.sim_offset_minutes = 0
            self.update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreensaverPreview()
    window.show()
    sys.exit(app.exec_())

