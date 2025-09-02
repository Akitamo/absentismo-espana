from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.data_service import DataService

svc = DataService()
print('periods', svc.get_available_periods()[:3])
print('ccaa_count', len(svc.get_ccaa_list()))
print('sectors_count', len(svc.get_sectors_list()))
print('kpis', svc.get_kpis('2024T4'))
print('evo_rows', len(svc.get_evolution_data()))
print('rank_rows', len(svc.get_ranking_ccaa('2024T4')))

