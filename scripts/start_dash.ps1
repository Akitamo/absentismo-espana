$ErrorActionPreference = 'Stop'

$env:APP_DB_PATH = "data\analysis.db"
python scripts\tokens_to_css.py | Out-Null

$p = Start-Process -FilePath "python" -ArgumentList "apps/dash/app.py" -PassThru
Write-Output ("PID={0}" -f $p.Id)
Write-Output "URL=http://127.0.0.1:8050"

