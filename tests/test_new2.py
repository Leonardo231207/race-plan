import re
t=open(r'C:\Users\Asus\Desktop\race-plan\docs\CARPETA DE PRENSA FECHA 9 2026 OK.txt','r',encoding='utf-8',errors='ignore').read()
lines=t.splitlines()
cats=[];seen=set()
for line in lines:
    s=line.strip()
    if not s: continue
    su=s.upper()
    if su.startswith(('VIERNES','SABADO','DOMINGO','JUEVES','MIERCOLES','MARTES','LUNES','ENTRENAMIENTOS','CLASIFICACIÓN','CLASIFICACION','FINAL','SERIES','SPRINT','INSCRIPTOS','GRUPOS','CIRCUITO','SISTEMA','COPA','CAMPEONATO','APERTURA','EL CRONOGRAMA','EN CASO','EN LOS','AUTODROMO','FRAD')): continue
    if re.match(r'^\s*\d{1,2}:\d{2}\s+[Aa]\s+\d{1,2}:\d{2}',s): continue
    if su.startswith(('SALIDA','CAMARA')): continue
    if re.search(r'PROCAR|F1|FORMULA|FIAT|SPA',s,re.I):
        if len(s)<120 and not su.startswith(('SE OTORGARÁN','1º','2º','3º','PUNTOS','PARA LA','COPA MASTER')):
            rc=re.sub(r'\s+',' ',s)
            k=rc.upper()
            if k not in seen:
                seen.add(k);cats.append(rc)
for c in cats: print(c)
print('---')
print(len(cats))
