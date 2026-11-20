"""Rebuild the complete kit using local, vector-native authoring sources."""
from pathlib import Path
import subprocess,sys,shutil
SOURCE=Path(__file__).resolve().parent;ROOT=SOURCE.parent
for folder in ['svg','pdf','eps','png','guide','palette']:(ROOT/folder).mkdir(exist_ok=True)
for script in ['build_core.py','build_campaign.py','build_sweatshirt.py','build_graduates.py',
               'build_forms.py','build_applications.py','export_assets.py','build_brand_board.py']:
    subprocess.run([sys.executable,str(SOURCE/script)],check=True)
for ext in ['pdf','png']:
    command=['inkscape',str(ROOT/'guide/IUS_Brand_Board.svg'),'--export-type='+ext,
             '--export-filename='+str(ROOT/('IUS_Brand_Board.'+ext))]
    if ext=='png':command+=['--export-width=1400']
    subprocess.run(command,check=True)
for script in ['build_manifest.py','build_guide.py','build_northern_n_review.py','build_font_review.py','build_gallery.py','validate_assets.py']:
    subprocess.run([sys.executable,str(SOURCE/script)],check=True)
print('Kit rebuilt in',ROOT)
