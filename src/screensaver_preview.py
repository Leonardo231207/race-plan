import sys
import json
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame
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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(30)

        self.title = QLabel("RACE PLAN")
        self.title.setAlignment(Qt.AlignCenter)
        font_title = QFont("Consolas", 26, QFont.Bold)
        self.title.setFont(font_title)
        self.title.setStyleSheet("color: white;")
        main_layout.addWidget(self.title)

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

        self.footer = QLabel("PREVIEW | ESC = Salir | ←/- -10m | →/+/= +10m | ↑ +1h | ↓ -1h | R = Hora real")
        self.footer.setAlignment(Qt.AlignCenter)
        font_footer = QFont("Consolas", 10)
        self.footer.setFont(font_footer)
        self.footer.setStyleSheet("color: #333333;")
        main_layout.addWidget(self.footer)

        self.filtered_events = []
        self.all_events = []
        self.sim_offset_minutes = 0
        self.use_real_time = True

        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

        self.update_display()

    def load_data(self):
        self.filtered_events = []
        self.all_events = []
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.expanduser('~\\AppData\\Local')
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Mi filtro
        path = os.path.join(appdata, 'RacePlan', 'horarios_filtrados.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.filtered_events = data
            except Exception as e:
                print(e)
        else:
            for candidate in [
                os.path.join(base_dir, 'horarios_filtrados.json'),
                os.path.join(os.path.dirname(base_dir), 'horarios_filtrados.json'),
            ]:
                if os.path.exists(candidate):
                    try:
                        with open(candidate, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            self.filtered_events = data
                        break
                    except Exception as e:
                        print(e)
                        continue

        # Todo
        path_all = os.path.join(appdata, 'RacePlan', 'horarios_todo.json')
        if os.path.exists(path_all):
            try:
                with open(path_all, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.all_events = data
            except Exception as e:
                print(e)
        else:
            for candidate in [
                os.path.join(base_dir, 'horarios_todo.json'),
                os.path.join(os.path.dirname(base_dir), 'horarios_todo.json'),
            ]:
                if os.path.exists(candidate):
                    try:
                        with open(candidate, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            self.all_events = data
                        break
                    except Exception as e:
                        print(e)
                        continue

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

        # Buscar en curso (CUALQUIER tanda del cronograma completo)
        search_all = self.all_events if self.all_events else self.filtered_events
        in_course = None
        for ev in search_all:
            start_dt = self.time_to_dt(ev)
            end_dt = None
            try:
                eh = int(ev.get('time_end', '0:0').split(':')[0])
                em = int(ev.get('time_end', '0:0').split(':')[1])
                end_dt = now.replace(hour=eh, minute=em, second=0, microsecond=0)
                if end_dt < start_dt:
                    end_dt = end_dt + timedelta(days=1)
            except Exception:
                end_dt = None
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

        if not self.filtered_events:
            self.next_info_label.setText("SIN HORARIOS FILTRADOS")
            self.next_info_label.setStyleSheet("color: #ff3333;")
            self.countdown_label.setText("--:--:--")
            return

        candidates = []
        for ev in self.filtered_events:
            dt = self.time_to_dt(ev)
            if dt is None:
                continue
            if dt < now:
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

        self.next_info_label.setText(f"{next_ev.get('raw_time','')} | {next_ev.get('descripcion','')}")
        self.next_info_label.setStyleSheet("color: #ffff00;")

        if total_seconds <= 0:
            self.countdown_label.setText("00:00:00")
            self.countdown_label.setStyleSheet("color: #ff3333;")
        else:
            self.countdown_label.setText(f"{h_rem:02d}:{m_rem:02d}:{s_rem:02d}")
            self.countdown_label.setStyleSheet("color: #ff8800;")

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

