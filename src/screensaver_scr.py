import sys
import json
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame
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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(30)

        self.title = QLabel("RACE PLAN")
        self.title.setAlignment(Qt.AlignCenter)
        font_title = QFont("Consolas", 26, QFont.Bold)
        self.title.setFont(font_title)
        self.title.setStyleSheet("color: white;")
        main_layout.addWidget(self.title)

        # Top row: clock + current session
        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(40)
        top_grid.setVerticalSpacing(10)

        clock_frame = QFrame()
        clock_frame.setStyleSheet("QFrame { border: 2px solid #333333; background-color: #050505; }")
        clock_layout = QVBoxLayout(clock_frame)
        clock_layout.setContentsMargins(30, 20, 30, 20)
        clock_layout.setSpacing(5)
        self.clock_header = QLabel("RELOJ")
        self.clock_header.setAlignment(Qt.AlignCenter)
        font_ch = QFont("Consolas", 16, QFont.Bold)
        self.clock_header.setFont(font_ch)
        self.clock_header.setStyleSheet("color: #aaaaaa;")
        clock_layout.addWidget(self.clock_header)
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        font_clock = QFont("Consolas", 90, QFont.Bold)
        self.clock_label.setFont(font_clock)
        self.clock_label.setStyleSheet("color: #00ff88;")
        clock_layout.addWidget(self.clock_label)
        top_grid.addWidget(clock_frame, 0, 0)

        now_frame = QFrame()
        now_frame.setStyleSheet("QFrame { border: 2px solid #333333; background-color: #050505; }")
        now_layout = QVBoxLayout(now_frame)
        now_layout.setContentsMargins(30, 20, 30, 20)
        now_layout.setSpacing(5)
        self.now_header = QLabel("TANDA ACTUAL")
        self.now_header.setAlignment(Qt.AlignCenter)
        font_nh = QFont("Consolas", 16, QFont.Bold)
        self.now_header.setFont(font_nh)
        self.now_header.setStyleSheet("color: #aaaaaa;")
        now_layout.addWidget(self.now_header)
        self.now_label = QLabel("SIN TANDA EN CURSO")
        self.now_label.setAlignment(Qt.AlignCenter)
        font_now = QFont("Consolas", 28, QFont.Bold)
        self.now_label.setFont(font_now)
        self.now_label.setStyleSheet("color: #888888;")
        self.now_label.setWordWrap(True)
        now_layout.addWidget(self.now_label)
        top_grid.addWidget(now_frame, 0, 1)
        top_grid.setColumnStretch(0, 1)
        top_grid.setColumnStretch(1, 1)
        main_layout.addLayout(top_grid)

        # Bottom row: next departure
        next_frame = QFrame()
        next_frame.setStyleSheet("QFrame { border: 2px solid #666600; background-color: #050500; }")
        next_layout = QGridLayout(next_frame)
        next_layout.setHorizontalSpacing(40)
        next_layout.setVerticalSpacing(10)
        next_layout.setContentsMargins(40, 30, 40, 30)

        self.next_left_header = QLabel("FALTA PARA PRÓXIMA\nSALIDA A PISTA")
        self.next_left_header.setAlignment(Qt.AlignCenter)
        font_nlh = QFont("Consolas", 18, QFont.Bold)
        self.next_left_header.setFont(font_nlh)
        self.next_left_header.setStyleSheet("color: #ffff00;")
        self.next_left_header.setWordWrap(True)
        next_layout.addWidget(self.next_left_header, 0, 0)

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        font_cd = QFont("Consolas", 90, QFont.Bold)
        self.countdown_label.setFont(font_cd)
        self.countdown_label.setStyleSheet("color: #ff8800;")
        next_layout.addWidget(self.countdown_label, 1, 0)

        self.next_right_header = QLabel("HORA SIGUIENTE\nSALIDA A PISTA")
        self.next_right_header.setAlignment(Qt.AlignCenter)
        font_nrh = QFont("Consolas", 18, QFont.Bold)
        self.next_right_header.setFont(font_nrh)
        self.next_right_header.setStyleSheet("color: #ffff00;")
        self.next_right_header.setWordWrap(True)
        next_layout.addWidget(self.next_right_header, 0, 1)

        self.next_info_label = QLabel("BUSCANDO...")
        self.next_info_label.setAlignment(Qt.AlignCenter)
        font_ni = QFont("Consolas", 32, QFont.Bold)
        self.next_info_label.setFont(font_ni)
        self.next_info_label.setStyleSheet("color: #ffff00;")
        self.next_info_label.setWordWrap(True)
        next_layout.addWidget(self.next_info_label, 1, 1)

        next_layout.setColumnStretch(0, 1)
        next_layout.setColumnStretch(1, 1)
        main_layout.addWidget(next_frame)

        self.footer = QLabel("MOVER MOUSE O PRESIONAR TECLA PARA SALIR")
        self.footer.setAlignment(Qt.AlignCenter)
        font_footer = QFont("Consolas", 10)
        self.footer.setFont(font_footer)
        self.footer.setStyleSheet("color: #333333;")
        main_layout.addWidget(self.footer)

        self.filtered_events = []
        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        self.update_display()

    def load_data(self):
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.expanduser(os.path.join('~', 'AppData', 'Local'))
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        cwd = os.getcwd()
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else base_dir
        
        self.filtered_events = []
        self.all_events = []
        
        candidates_f = [
            os.path.join(appdata, 'RacePlan', 'horarios_filtrados.json'),
            os.path.join(exe_dir, 'horarios_filtrados.json'),
            os.path.join(cwd, 'horarios_filtrados.json'),
            os.path.join(base_dir, 'horarios_filtrados.json'),
            os.path.join(root_dir, 'horarios_filtrados.json'),
            os.path.join(root_dir, 'PDF LECTOR', 'horarios_filtrados.json'),
        ]
        for p in candidates_f:
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list) and data:
                        self.filtered_events = data
                        # copiar a AppData para próximas veces
                        try:
                            tdir = os.path.join(appdata, 'RacePlan')
                            os.makedirs(tdir, exist_ok=True)
                            with open(os.path.join(tdir, 'horarios_filtrados.json'), 'w', encoding='utf-8') as f2:
                                json.dump(data, f2, ensure_ascii=False, indent=2)
                        except:
                            pass
                        break
                except Exception:
                    continue
        
        candidates_a = [
            os.path.join(appdata, 'RacePlan', 'horarios_todo.json'),
            os.path.join(exe_dir, 'horarios_todo.json'),
            os.path.join(cwd, 'horarios_todo.json'),
            os.path.join(base_dir, 'horarios_todo.json'),
            os.path.join(root_dir, 'horarios_todo.json'),
            os.path.join(root_dir, 'PDF LECTOR', 'horarios_todo.json'),
        ]
        for p in candidates_a:
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        self.all_events = data
                        try:
                            tdir = os.path.join(appdata, 'RacePlan')
                            os.makedirs(tdir, exist_ok=True)
                            with open(os.path.join(tdir, 'horarios_todo.json'), 'w', encoding='utf-8') as f2:
                                json.dump(data, f2, ensure_ascii=False, indent=2)
                        except:
                            pass
                        break
                except Exception:
                    continue

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
            self.now_label.setText("SIN HORARIOS FILTRADOS")
            self.now_label.setStyleSheet("color: #ff3333;")
            appdata = os.environ.get('LOCALAPPDATA') or os.path.expanduser(os.path.join('~','AppData','Local'))
            self.next_info_label.setText(f"GENERAR CON GESTOR EN:\n{os.path.join(appdata,'RacePlan')}")
            self.next_info_label.setStyleSheet("color: #ff3333;")
            self.countdown_label.setText("--:--:--")
            return

        # Buscar en curso (CUALQUIER tanda del cronograma completo que esté corriendo ahora)
        search_all = self.all_events if self.all_events else self.filtered_events
        in_course = None
        for ev in search_all:
            start_dt = self.time_to_dt(ev, now)
            end_dt = self.time_to_dt_end(ev, now)
            if start_dt and end_dt and end_dt < start_dt:
                end_dt = end_dt + timedelta(days=1)
            if start_dt and end_dt:
                if start_dt <= now <= end_dt:
                    in_course = ev
                    break

        if in_course:
            self.now_label.setText(f"{in_course.get('raw_time','')} | {in_course.get('descripcion','')}")
            self.now_label.setStyleSheet("color: #ff3333;")
        else:
            self.now_label.setText("SIN TANDA EN CURSO")
            self.now_label.setStyleSheet("color: #888888;")

        # Buscar MI próxima tanda (la más cercana a arrancar entre las filtradas)
        candidates = []
        for ev in self.filtered_events:
            dt = self.time_to_dt(ev, now)
            if dt is None:
                continue
            if dt < now:  # ya arrancó o pasó
                continue
            candidates.append((dt, ev))

        if not candidates:
            self.next_info_label.setText("NO HAY MÁS SALIDAS A PISTA")
            self.next_info_label.setStyleSheet("color: #888888;")
            self.countdown_label.setText("00:00:00")
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

        next_text = f"{next_ev.get('raw_time','')} | {next_ev.get('descripcion','')}"
        self.next_info_label.setText(next_text)
        self.next_info_label.setStyleSheet("color: #ffff00;")

        if total_seconds <= 0:
            self.countdown_label.setText("00:00:00")
            self.countdown_label.setStyleSheet("color: #ff3333;")
        else:
            self.countdown_label.setText(f"{h_rem:02d}:{m_rem:02d}:{s_rem:02d}")
            self.countdown_label.setStyleSheet("color: #ff8800;")

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

