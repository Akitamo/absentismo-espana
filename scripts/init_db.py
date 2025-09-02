from pathlib import Path
import duckdb

DB_PATH = Path("data") / "analysis.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH))

con.execute(
    """
    CREATE TABLE IF NOT EXISTS observaciones_tiempo_trabajo (
        periodo VARCHAR,
        ambito_territorial VARCHAR,
        ccaa_nombre VARCHAR,
        cnae_nivel VARCHAR,
        cnae_nombre VARCHAR,
        fuente_tabla VARCHAR,
        metrica VARCHAR,
        causa VARCHAR,
        valor DOUBLE
    );
    """
)

# Limpia filas de ejemplo previas
con.execute("DELETE FROM observaciones_tiempo_trabajo WHERE periodo IN ('2024T4','2024T3');")

rows = [
    # Total Nacional (para KPIs y evolución)
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_pactadas",None,1000.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_extraordinarias",None,50.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","vacaciones",80.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","festivos",40.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","razones_tecnicas_economicas",0.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","it_total",30.0),
    ("2024T4","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","otras_bajas",20.0),

    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_pactadas",None,980.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_extraordinarias",None,45.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","vacaciones",70.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","festivos",38.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","razones_tecnicas_economicas",0.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","it_total",28.0),
    ("2024T3","NAC",None,"TOTAL",None,"6042","horas_no_trabajadas","otras_bajas",18.0),

    # CCAA (para ranking en 2024T4)
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_pactadas",None,120.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_extraordinarias",None,5.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_no_trabajadas","vacaciones",10.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_no_trabajadas","festivos",5.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_no_trabajadas","razones_tecnicas_economicas",0.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_no_trabajadas","it_total",3.0),
    ("2024T4","CCAA","Andalucía","TOTAL",None,"6042","horas_no_trabajadas","otras_bajas",2.0),

    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_pactadas",None,110.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_extraordinarias",None,6.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_no_trabajadas","vacaciones",9.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_no_trabajadas","festivos",4.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_no_trabajadas","razones_tecnicas_economicas",0.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_no_trabajadas","it_total",2.0),
    ("2024T4","CCAA","Madrid","TOTAL",None,"6042","horas_no_trabajadas","otras_bajas",1.0),
]

con.executemany(
    """
    INSERT INTO observaciones_tiempo_trabajo
    (periodo, ambito_territorial, ccaa_nombre, cnae_nivel, cnae_nombre, fuente_tabla, metrica, causa, valor)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    rows,
)

con.close()
print(f"OK: inicializado {DB_PATH}")

