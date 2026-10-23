import sys
sys.path.insert(0, r'C:\Users\lm-sa\OneDrive\Desktop\race-plan\src')
from RacePlanGestor import RacePlanGestor
g = RacePlanGestor()
g.pdf_path = r'C:\Users\lm-sa\OneDrive\Desktop\race-plan\PDF LECTOR\Cronograma FECHA 1 - Procar4000.pdf'
g.extract_and_parse()
print(len(g.all_events))
for k in g.match_keys:
    print('KEY:', k)
