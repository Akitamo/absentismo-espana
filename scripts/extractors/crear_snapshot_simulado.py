import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Añadir el directorio al path
sys.path.append(str(Path(__file__).parent))

os.chdir(Path(__file__).parent)

# Importar módulos
from extractor_csv_ine import ExtractorCSV_INE
from analizar_periodos import AnalizadorPeriodos

# Inicializar extractor
extractor = ExtractorCSV_INE("config_csv.json")
extractor.cargar_urls_etcl("../../urls_etcl_completo.json")

# Forzar una fecha diferente para el snapshot
fecha_nueva = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
print(f"📸 Creando snapshot para fecha simulada: {fecha_nueva}")

# Modificar temporalmente el método para usar nuestra fecha
original_method = extractor.generar_snapshot

def generar_snapshot_custom():
    # Crear directorio con fecha personalizada
    snapshot_dir = Path(extractor.base_dir) / "snapshots" / fecha_nueva
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar método original temporalmente
    extractor.snapshot_dir = snapshot_dir
    
    # Llamar al método original pero modificando la ruta
    import json
    from datetime import datetime
    
    # Generar metadata
    metadata = {
        "fecha_snapshot": fecha_nueva,
        "hora_snapshot": datetime.now().strftime("%H:%M:%S"),
        "total_archivos": 35,
        "fuente": "INE - Encuesta Trimestral de Coste Laboral",
        "version": "2.0"
    }
    
    with open(snapshot_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Copiar checksums del snapshot anterior
    snapshot_anterior = Path(extractor.base_dir) / "snapshots" / "2025-06-10"
    if (snapshot_anterior / "checksums.json").exists():
        import shutil
        shutil.copy2(snapshot_anterior / "checksums.json", snapshot_dir / "checksums.json")
        shutil.copy2(snapshot_anterior / "summary.json", snapshot_dir / "summary.json")
    
    print(f"✅ Snapshot base creado en: {snapshot_dir}")
    
    # Ahora generar análisis de periodos
    print("🔍 Analizando periodos...")
    analizador = AnalizadorPeriodos()
    analisis = analizador.analizar_todos_los_csv()
    
    if analisis:
        analizador.guardar_analisis(analisis, snapshot_dir / "periodos.json")
        resumen = analizador.generar_resumen(analisis)
        print(f"✅ Análisis de periodos completado: {resumen['archivos_procesados']} archivos")
    
    return True

# Ejecutar
if generar_snapshot_custom():
    print(f"\n✅ Nuevo snapshot creado exitosamente para: {fecha_nueva}")
    print("\n🎯 Ahora puedes comparar los snapshots:")
    print(f"   python comparar_periodos.py --fecha1 2025-06-10 --fecha2 {fecha_nueva}")
else:
    print("❌ Error creando snapshot")
