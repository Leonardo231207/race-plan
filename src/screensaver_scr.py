import sys
import json
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor


class RaceScreensaver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Race Plan - Screensaver")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(80, 60, 80, 60)
        self.layout.setSpacing(35)

        self.title = QLabel("RACE PLAN")
        self.title.setAlignment(Qt.AlignCenter)
        font_title = QFont("Consolas", 28, QFont.Bold)
        self.title.setFont(font_title)
        self.title.setStyleSheet("color: white;")
        self.layout.addWidget(self.title)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        font_clock = QFont("Consolas", 120, QFont.Bold)
        self.clock_label.setFont(font_clock)
        self.clock_label.setStyleSheet("color: #00ff88;")
        self.layout.addWidget(self.clock_label)

        self.now_label = QLabel("SIN TANDA EN CURSO")
        self.now_label.setAlignment(Qt.AlignCenter)
        font_now = QFont("Consolas", 32, QFont.Bold)
        self.now_label.setFont(font_now)
        self.now_label.setStyleSheet("color: #888888;")
        self.now_label.setWordWrap(True)
        self.layout.addWidget(self.now_label)

        self.next_title = QLabel("PRÓXIMA QUE NOS TOCA")
        self.next_title.setAlignment(Qt.AlignCenter)
        font_nt = QFont("Consolas", 24, QFont.Bold)
        self.next_title.setFont(font_nt)
        self.next_title.setStyleSheet("color: #ffff00;")
        self.layout.addWidget(self.next_title)

        self.next_label = QLabel("BUSCANDO...")
        self.next_label.setAlignment(Qt.AlignCenter)
        font_next = QFont("Consolas", 36, QFont.Bold)
        self.next_label.setFont(font_next)
        self.next_label.setStyleSheet("color: #ffff00;")
        self.next_label.setWordWrap(True)
        self.layout.addWidget(self.next_label)

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        font_cd = QFont("Consolas", 64, QFont.Bold)
        self.countdown_label.setFont(font_cd)
        self.countdown_label.setStyleSheet("color: #ff8800;")
        self.layout.addWidget(self.countdown_label)

        self.footer = QLabel("MOVER MOUSE O PRESIONAR TECLA PARA SALIR")
        self.footer.setAlignment(Qt.AlignCenter)
        font_footer = QFont("Consolas", 12)
        self.footer.setFont(font_footer)
        self.footer.setStyleSheet("color: #333333;")
        self.layout.addWidget(self.footer)

        self.filtered_events = []
        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        self.update_display()

    def load_data(self):
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.expanduser('~\\AppData\\Local')
        path = os.path.join(appdata, 'RacePlan', 'horarios_filtrados.json')
        if not os.path.exists(path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, 'horarios_filtrados.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.filtered_events = data
            except Exception:
                self.filtered_events = []
        else:
            self.filtered_events = []

    def get_current_time(self):
        return datetime.now()

    def time_to_dt(self, ev, now):
        try:
            sh = int(ev.get('event_hour')) if ev.get('event_hour') is not None else int(ev.get('time_start', '0:0').split(':')[0])
            sm = int(ev.get('event_min')) if ev.get('event_min') is not None else int(ev.get('time_start', '0:0').split(':')[1])
            dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            return dt
        except Exception:
            return None

    def time_to_dt_end(self, ev, now):
        try:
            eh = int(ev.get('time_end', '0:0').split(':')[0])
            em = int(ev.get('time_end', '0:0').split(':')[1])
            dt = now.replace(hour=eh, minute=em, second=0, microsecond=0)
            return dt
        except Exception:
            return None

    def update_display(self):
        now = self.get_current_time()
        self.clock_label.setText(now.strftime("%H:%M:%S"))

        if not self.filtered_events:
            self.now_label.setText("SIN HORARIOS FILTRADOS EN AppData\\Local\\RacePlan\\")
            self.now_label.setStyleSheet("color: #ff3333;")
            self.next_label.setText("")
            self.countdown_label.setText("")
            return

        # Buscar en curso
        in_course = None
        for ev in self.filtered_events:
            start_dt = self.time_to_dt(ev, now)
            end_dt = self.time_to_dt_end(ev, now)
            if start_dt and end_dt:
                if start_dt <= now <= end_dt:
                    in_course = ev
                    break

        if in_course:
            self.now_label.setText(f"AHORA / EN CURSO | {in_course.get('raw_time','')} | {in_course.get('descripcion','')}")
            self.now_label.setStyleSheet("color: #ff3333;")
        else:
            self.now_label.setText("SIN TANDA EN CURSO")
            self.now_label.setStyleSheet("color: #888888;")

        # Buscar próximo que nos toca
        candidates = []
        for ev in self.filtered_events:
            dt = self.time_to_dt(ev, now)
            if dt is None:
                continue
            if dt < now - timedelta(hours=2):
                continue
            candidates.append((dt, ev))

        if not candidates:
            self.next_label.setText("NO HAY MÁS TANDAS QUE NOS TOQUEN")
            self.next_label.setStyleSheet("color: #888888;")
            self.countdown_label.setText("")
            return

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
            self.next_label.setText(f"{next_ev.get('raw_time','')} | {next_ev.get('descripcion','')}")
            self.next_label.setStyleSheet("color: #ff3333;")
            self.countdown_label.setText("00:00:00")
        else:
            self.next_label.setText(f"{next_ev.get('raw_time','')} | {next_ev.get('descripcion','')}")
            self.next_label.setStyleSheet("color: #ffff00;")
            self.countdown_label.setText(f"FALTAN {h_rem:02d}:{m_rem:02d}:{s_rem:02d}")

    def mouseMoveEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        self.close()


if __name__ == '__main__':
    args = sys.argv
    app = QApplication(args)
    window = RaceScreensaver()
    window.show()
    sys.exit(app.exec_())

