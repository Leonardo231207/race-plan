import json
import re

with open('C:/Users/Asus/Desktop/race-plan/PDF LECTOR/a.json') as f:
    pages = json.load(f)

text = '\n'.join(pages)
time_pattern1 = re.compile(r'^\s*(\d{1,2}):(\d{2})\s+[Aa]\s+(\d{1,2}):(\d{2})\s+(.+)$', re.I)
time_pattern2 = re.compile(r'^\s*(\d{1,2}):(\d{2})\s+[Aa]\s+(\d{1,2}):(\d{2})\s*(?:Hs\.?)?\s*$', re.I)

cats = []
seen = set()
lines = text.splitlines()
for i,line in enumerate(lines):
    m1 = time_pattern1.match(line)
    if m1:
        rest = m1.group(5).strip()
        if rest and not rest.upper().startswith(('SALIDA','1ER','2DA','3RA','1°','2°','CAMARA')):
            rc = re.sub(r'\s+', ' ', rest)
            k = rc.upper()
            if k not in seen and len(rc) > 2:
                seen.add(k)
                cats.append(rc)
        continue
    m2 = time_pattern2.match(line)
    if m2 and i+1 < len(lines):
        nl = lines[i+1].strip()
        if nl and not re.match(r'^\d{1,2}:\d{2}', nl):
            un = nl.upper()
            if un.startswith(('VIERNES','SABADO','DOMINGO','JUEVES','MIERCOLES','MARTES','LUNES','ENTRENAMIENTOS','CLASIFICACIÓN','CLASIFICACION','FINAL','SERIES','SPRINT','INSCRIPTOS','GRUPOS','CIRCUITO','SISTEMA','COPA','CAMPEONATO')):
                continue
            if nl.upper().startswith(('SALIDA','CAMARA')):
                continue
            rc = re.sub(r'\s+', ' ', nl)
            k = rc.upper()
            if k not in seen and len(rc) > 2:
                seen.add(k)
                cats.append(rc)

for c in cats:
    print(c)
print('---TOTAL---')
print(len(cats))
