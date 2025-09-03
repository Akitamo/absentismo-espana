from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import importlib
import apps.dash.app  # ensures Dash app is instantiated with use_pages
mod = importlib.import_module('apps.dash.pages.dashboard')
layout = getattr(mod, 'layout')
update_dashboard = getattr(mod, 'update_dashboard')

print('layout type:', type(layout()).__name__)

res = update_dashboard('2024T4', 'Total Nacional', 'Todos')
print('update_dashboard returned items:', len(res))
fig = res[1]
print('figure traces:', len(fig.data))
print('ranking rows:', len(res[2]))
