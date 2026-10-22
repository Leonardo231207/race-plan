import RacePlanGestor, sys, json, os
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)
g = RacePlanGestor.RacePlanGestor()
g.pdf_path = r'C:\Users\Asus\Desktop\race-plan\docs\CARPETA DE PRENSA FECHA 9 2026 OK.pdf'
g.extract_and_parse()
selected = ['PROCAR 4000 "CLASE B" (Grupo A)', 'PROCAR 4000 "CLASE B"']
events_out = []
for ev in g.all_events:
    if ev['match_key'] in selected:
        events_out.append(ev)
events_out.sort(key=lambda x:(x['event_hour'],x['event_min']))
appdata = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~\\AppData\\Local')
target_dir = os.path.join(appdata,'RacePlan')
os.makedirs(target_dir,exist_ok=True)
target = os.path.join(target_dir,'horarios_filtrados.json')
with open(target,'w',encoding='utf-8') as f:
    json.dump(events_out,f,ensure_ascii=False,indent=2)
print(len(events_out))
for e in events_out:
    print(e['fecha_cabecera'] or '', e['raw_time'], e['match_key'], '|', e['descripcion'])
