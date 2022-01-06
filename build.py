import shutil
from pathlib import Path
from subprocess import run

dir = Path(__file__).parent
bin_dir = dir / "bin"

# Clean
try:
    shutil.rmtree(bin_dir)
except FileNotFoundError:
    pass
bin_dir.mkdir(parents=True, exist_ok=True)

# Build
run(["pyinstaller", dir / "freeze.spec", "--distpath", bin_dir], check=True)
shutil.copy(dir / "data/vswhere.exe", bin_dir / "vswhere.exe")
