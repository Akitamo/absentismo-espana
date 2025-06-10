# INSTALACIÓN RÁPIDA 🚀

## Windows

1. **Clonar repositorio:**
   ```cmd
   git clone https://github.com/tu-usuario/absentismoespana.git
   cd absentismoespana
   ```

2. **Ejecutar instalador:**
   ```cmd
   install_windows.bat
   ```

3. **¡Listo!** El instalador hará todo automáticamente.

---

## Linux/Mac

1. **Clonar repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/absentismoespana.git
   cd absentismoespana
   ```

2. **Ejecutar setup:**
   ```bash
   python3 setup_project.py
   ```

3. **Activar entorno:**
   ```bash
   source venv/bin/activate
   ```

---

## Instalación Manual

Si prefieres hacerlo paso a paso:

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/absentismoespana.git
cd absentismoespana

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar
python fix_paths.py
```

---

## Verificar Instalación

```python
python -c "import pandas; print('✅ Pandas OK')"
python -c "import numpy; print('✅ NumPy OK')"
python -c "import requests; print('✅ Requests OK')"
```

Si todo muestra ✅, ¡está listo para usar!
