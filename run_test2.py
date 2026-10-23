import sys
sys.path.insert(0, r'C:\Users\lm-sa\OneDrive\Desktop\race-plan\src')
from PyQt5.QtWidgets import QApplication
import RacePlanGestor

app = QApplication(sys.argv)
g = RacePlanGestor.RacePlanGestor()
g.pdf_path = r'C:\Users\lm-sa\OneDrive\Desktop\race-plan\PDF LECTOR\Cronograma FECHA 1 - Procar4000.pdf'
g.extract_and_parse()
print('EVCOUNT', len(g.all_events))
for k in g.match_keys:
    print('KEY:', k)
sys.exit(0)
