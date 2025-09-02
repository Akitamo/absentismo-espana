# CONTEXT.md

**Última actualización:** 02-01-2025 12:10

## 🚨 ESTADO ACTUAL: FASE EXPERIMENTAL (2025-01-02)

**El proyecto está evaluando una solución experimental para cards/visualizaciones**

- **Problema identificado**: Inconsistencias de renderizado con st.container(border=True)
- **Solución en prueba**: Componente React custom (`ui_card`)
- **Páginas de prueba**: 99_Demo_CRM.py (nativo) vs 100_Demo_UI_Card.py (custom)
- **Decisión pendiente**: Continuar con nativo mejorado o adoptar componente custom

⚠️ **NO INTEGRAR** el componente experimental en páginas principales hasta decisión final.

---

## 📊 Estado Actual del Proyecto

### Pipeline de Datos
- ✅ **35 tablas INE** descargadas y procesadas
- ✅ **51 métricas únicas** identificadas y validadas
- ✅ **149,247 registros** en DuckDB
- ✅ **Validación 100%** contra fuentes INE

### Dashboard Streamlit
- **Puerto**: 8505 (ejecutándose)
- **URL**: http://localhost:8505
- **Galería QA**: http://localhost:8505/galeria
- **Versión**: Streamlit 1.30+ con containers nativos

## 🎯 Sprint Completado: Cards y Arquitectura Frontend

### Implementaciones Finales (31-12-2024)
- ✅ **Cards nativos** con `st.container(border=True)` - solución estable sin hacks
- ✅ **CSS mínimo** - un selector estable para Streamlit 1.30+
- ✅ **100% tokens-first** - todos los estilos desde `tokens.json`
- ✅ **Sistema modular de visualizaciones** con registry pattern
- ✅ **Página Galería** para QA visual de componentes
- ✅ **Documentación consolidada** en DESIGN_SYSTEM.md

### Arquitectura de Cards Final
```python
# Solución limpia y estable
@contextmanager
def card(title: str | None = None, subtitle: str | None = None):
    c = st.container(border=True)  # nativo
    with c:
        if title: st.markdown(f"### {title}")
        if subtitle: st.caption(subtitle)
        yield
```

### CSS Estable Aplicado
```css
.stContainer > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    box-shadow: var(--card-shadow);
    padding: var(--spacing-lg);
}
```

## 🚀 Próximos Pasos
1. Conectar visualizaciones con datos reales de DuckDB
2. Implementar filtros dinámicos por periodo/CCAA/sector
3. Crear análisis comparativo entre trimestres
4. Añadir export de datos filtrados

## 📝 Lecciones Aprendidas
- **No-wrapping problem**: Streamlit no permite envolver componentes nativos en HTML custom
- **Solución**: Usar containers nativos con `border=True` + CSS mínimo
- **Tokens-first**: Mantener todos los valores de diseño en `tokens.json`
- **Estabilidad**: Un selector CSS específico es mejor que múltiples alternativas

## 🧪 EXPERIMENTAL: Prueba UI Card Component (2025-01-02)

### Objetivo
Prueba de viabilidad para resolver problemas de renderizado consistente en Streamlit mediante componente custom React.

### Archivos creados (REVERSIBLES)
- `streamlit_app/components/ui_card/` - Componente custom con Vite + TypeScript
- `streamlit_app/pages/100_Demo_UI_Card.py` - Demo página 100
- `streamlit_app/components/card*.py` - Intentos previos con nativos
- `streamlit_app/pages/99_Demo_CRM.py` - Demo página 99
- `streamlit_app/design/tokens_presets/` - Presets de tokens

### Estado
- ✅ Componente compilado y funcional
- ✅ Estilos profesionales tipo Tesla/CRM
- ⏳ Pendiente evaluación de integración con arquitectura actual

### Para revertir
```bash
git rm -r streamlit_app/components/ui_card/
git rm streamlit_app/pages/100_Demo_UI_Card.py
git rm streamlit_app/pages/99_Demo_CRM.py
git rm streamlit_app/components/card*.py
git rm -r streamlit_app/design/tokens_presets/
```