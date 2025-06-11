# ⚠️ CARPETA NO UTILIZADA

Esta carpeta `scripts/extractors/data/raw/csv/` **NO SE USA** para almacenar los CSVs.

## 📁 UBICACIÓN CORRECTA DE LOS CSVs:
Los archivos CSV descargados del INE se guardan en:
```
C:\Users\%USERPROFILE%\absentismoespana\data\raw\csv\
```

Es decir, en la **RAÍZ del proyecto**, no dentro de scripts/extractors.

## 🔧 Configuración:
El archivo `config_csv.json` usa la ruta relativa correcta:
```json
"datos_raw": "../../data/raw/csv/"
```

Esto significa: desde scripts/extractors/, subir dos niveles y luego ir a data/raw/csv/.

---
Esta carpeta se mantiene vacía y este README sirve como recordatorio.
