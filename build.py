import shutil
import os
from pathlib import Path
from subprocess import run

dir = Path(__file__).parent
dist_dir = dir / "dist"

# Clean
try:
    shutil.rmtree(dist_dir)
except FileNotFoundError:
    pass
dist_dir.mkdir()

# Build
os.chdir(dir)
run(["pyinstaller", dir / "freeze.spec", "--distpath", dist_dir], check=True)
