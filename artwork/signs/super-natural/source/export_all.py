from pathlib import Path
import subprocess, sys

root=Path(__file__).resolve().parent
subprocess.run(['node',str(root/'build-sign.mjs')],check=True)
master=root/'output/BC_Super_Natural_Welcome_Sign.svg'
subprocess.run(['inkscape',str(master),'--export-filename='+str(master.with_suffix('.png')),'--export-width=1200'],check=True)
subprocess.run(['inkscape',str(master),'--export-filename='+str(master.with_suffix('.pdf')),'--export-type=pdf'],check=True)
subprocess.run([sys.executable,str(root/'compare.py')],check=True)
subprocess.run([sys.executable,str(root/'finish.py')],check=True)
