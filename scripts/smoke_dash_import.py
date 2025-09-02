from pathlib import Path
import sys, importlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
m = importlib.import_module('apps.dash.app')
print('ok', getattr(m, 'app', None) is not None)
