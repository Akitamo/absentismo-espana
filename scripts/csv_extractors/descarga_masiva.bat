@echo off
echo Iniciando descarga masiva de tablas CSV del INE...
cd /d "C:\Users\slunagda\AbsentismoEspana\scripts\csv_extractors"
python extractor_csv_ine.py --activar-todas --urls ../../urls_etcl_completo.json
pause
