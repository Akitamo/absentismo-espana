"""
Ejecutor Maestro - Análisis Completo de Factibilidad
Ejecuta todo el pipeline de análisis: estructura + detección + informe visual
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

class EjecutorMaestroAnalisis:
    """
    Ejecutor que coordina todo el proceso de análisis de factibilidad
    """
    
    def __init__(self):
        """Inicializa el ejecutor maestro"""
        self.logger = self._configurar_logging()
        self.directorio_base = Path(__file__).parent
        self.directorio_informes = self.directorio_base / "../../informes"
        
        # Asegurar que existe el directorio de informes
        self.directorio_informes.mkdir(parents=True, exist_ok=True)
        
        self.resultados = {
            'inicio': datetime.now().isoformat(),
            'pasos_completados': [],
            'errores': [],
            'archivos_generados': [],
            'tiempo_total': 0
        }
        
    def _configurar_logging(self) -> logging.Logger:
        """Configura el logging"""
        logger = logging.getLogger('EjecutorMaestro')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def ejecutar_paso(self, script_name: str, descripcion: str) -> bool:
        """
        Ejecuta un paso individual del análisis
        
        Args:
            script_name: Nombre del script a ejecutar
            descripcion: Descripción del paso
            
        Returns:
            True si el paso se ejecutó correctamente
        """
        self.logger.info(f"🚀 Ejecutando: {descripcion}")
        print(f"\n{'='*60}")
        print(f"🚀 PASO: {descripcion}")
        print(f"{'='*60}")
        
        inicio_paso = datetime.now()
        
        try:
            # Ejecutar script
            resultado = subprocess.run([
                sys.executable, script_name
            ], capture_output=True, text=True, cwd=self.directorio_base)
            
            if resultado.returncode == 0:
                tiempo_paso = (datetime.now() - inicio_paso).total_seconds()
                self.logger.info(f"✅ {descripcion} completado en {tiempo_paso:.1f}s")
                
                self.resultados['pasos_completados'].append({
                    'paso': descripcion,
                    'script': script_name,
                    'tiempo_segundos': tiempo_paso,
                    'completado': datetime.now().isoformat()
                })
                
                # Mostrar salida si hay
                if resultado.stdout:
                    print(resultado.stdout)
                
                return True
            else:
                error_msg = f"Error en {descripcion}: {resultado.stderr}"
                self.logger.error(error_msg)
                self.resultados['errores'].append({
                    'paso': descripcion,
                    'error': resultado.stderr,
                    'stdout': resultado.stdout
                })
                print(f"❌ ERROR: {resultado.stderr}")
                return False
                
        except Exception as e:
            error_msg = f"Excepción ejecutando {descripcion}: {str(e)}"
            self.logger.error(error_msg)
            self.resultados['errores'].append({
                'paso': descripcion,
                'error': str(e)
            })
            print(f"❌ EXCEPCIÓN: {str(e)}")
            return False
    
    def verificar_archivos_csv(self) -> bool:
        """Verifica que existan archivos CSV para analizar"""
        data_dir = self.directorio_base / "../../data/raw/csv"
        archivos_csv = list(data_dir.glob("*.csv"))
        
        if len(archivos_csv) < 10:
            self.logger.error(f"Insuficientes archivos CSV: {len(archivos_csv)} encontrados")
            return False
        
        self.logger.info(f"✅ {len(archivos_csv)} archivos CSV encontrados")
        return True
    
    def verificar_archivos_generados(self) -> None:
        """Verifica qué archivos se generaron durante el proceso"""
        archivos_esperados = [
            "../../informes/analisis_estructura_robusto.json",
            "../../informes/deteccion_absentismo_detallada.json", 
            "../../informes/factibilidad_absentismo.html"
        ]
        
        for archivo in archivos_esperados:
            ruta = self.directorio_base / archivo
            if ruta.exists():
                tamaño_kb = ruta.stat().st_size / 1024
                self.resultados['archivos_generados'].append({
                    'archivo': str(ruta),
                    'tamaño_kb': round(tamaño_kb, 1),
                    'existe': True
                })
                self.logger.info(f"✅ Generado: {ruta.name} ({tamaño_kb:.1f} KB)")
            else:
                self.resultados['archivos_generados'].append({
                    'archivo': str(ruta),
                    'existe': False
                })
                self.logger.warning(f"⚠️  No encontrado: {ruta.name}")
    
    def generar_resumen_final(self) -> Dict:
        """Genera resumen final del proceso"""
        tiempo_total = (datetime.now() - datetime.fromisoformat(self.resultados['inicio'])).total_seconds()
        self.resultados['tiempo_total'] = tiempo_total
        self.resultados['fin'] = datetime.now().isoformat()
        
        resumen = {
            'exito': len(self.resultados['errores']) == 0,
            'pasos_completados': len(self.resultados['pasos_completados']),
            'total_pasos': 3,
            'tiempo_total_minutos': round(tiempo_total / 60, 1),
            'archivos_generados': len([a for a in self.resultados['archivos_generados'] if a['existe']]),
            'errores': len(self.resultados['errores'])
        }
        
        return resumen
    
    def ejecutar_analisis_completo(self) -> bool:
        """
        Ejecuta el análisis completo de factibilidad
        
        Returns:
            True si todo el proceso se completó exitosamente
        """
        print("🎯 INICIANDO ANÁLISIS COMPLETO DE FACTIBILIDAD")
        print("="*80)
        print("Este proceso analizará las 35 tablas CSV descargadas para determinar")
        print("la factibilidad del análisis de absentismo laboral en España")
        print("="*80)
        
        # Verificar prerequisitos
        if not self.verificar_archivos_csv():
            print("❌ PREREQUISITOS NO CUMPLIDOS: Archivos CSV insuficientes")
            return False
        
        # Pipeline de análisis con parser robusto
        pasos = [
            ("analisis_estructura_robusto.py", "Análisis Robusto de Estructura de 35 Tablas"),
            ("detector_absentismo.py", "Detección Específica de Datos de Absentismo"),
            ("generar_informe_factibilidad.py", "Generación de Informe Visual HTML")
        ]
        
        # Ejecutar cada paso
        exitos = 0
        for script, descripcion in pasos:
            if self.ejecutar_paso(script, descripcion):
                exitos += 1
            else:
                print(f"\n❌ PROCESO INTERRUMPIDO en: {descripcion}")
                break
        
        # Verificar archivos generados
        self.verificar_archivos_generados()
        
        # Generar resumen final
        resumen = self.generar_resumen_final()
        
        # Mostrar resultados finales
        self._mostrar_resumen_final(resumen)
        
        # Guardar log del proceso
        self._guardar_log_proceso()
        
        return resumen['exito']
    
    def _mostrar_resumen_final(self, resumen: Dict) -> None:
        """Muestra el resumen final del proceso"""
        print("\n" + "="*80)
        print("🏁 ANÁLISIS COMPLETO DE FACTIBILIDAD FINALIZADO")
        print("="*80)
        
        if resumen['exito']:
            print("✅ ESTADO: COMPLETADO EXITOSAMENTE")
        else:
            print("❌ ESTADO: COMPLETADO CON ERRORES")
        
        print(f"📊 Pasos completados: {resumen['pasos_completados']}/{resumen['total_pasos']}")
        print(f"⏱️  Tiempo total: {resumen['tiempo_total_minutos']} minutos")
        print(f"📁 Archivos generados: {resumen['archivos_generados']}")
        
        if resumen['errores'] > 0:
            print(f"⚠️  Errores encontrados: {resumen['errores']}")
        
        # Mostrar archivos generados
        print(f"\n📂 ARCHIVOS GENERADOS:")
        for archivo in self.resultados['archivos_generados']:
            if archivo['existe']:
                print(f"   ✅ {Path(archivo['archivo']).name} ({archivo['tamaño_kb']} KB)")
            else:
                print(f"   ❌ {Path(archivo['archivo']).name} (no generado)")
        
        # Mostrar próximos pasos
        if resumen['exito']:
            print(f"\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE!")
            print(f"📋 PRÓXIMOS PASOS RECOMENDADOS:")
            print(f"   1. Revisar informe HTML: informes/factibilidad_absentismo.html")
            print(f"   2. Validar datos de estructura: informes/analisis_estructura_35_tablas.json")
            print(f"   3. Revisar detección absentismo: informes/deteccion_absentismo_detallada.json")
            print(f"   4. Implementar base de datos según recomendaciones")
            print(f"   5. Desarrollar aplicación de análisis")
        else:
            print(f"\n⚠️  PROCESO INCOMPLETO")
            print(f"💡 RECOMENDACIONES:")
            print(f"   1. Revisar logs de errores")
            print(f"   2. Verificar archivos CSV en data/raw/csv/")
            print(f"   3. Ejecutar pasos individuales para diagnóstico")
    
    def _guardar_log_proceso(self) -> None:
        """Guarda log detallado del proceso"""
        try:
            log_path = self.directorio_informes / f"log_analisis_factibilidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📝 Log del proceso guardado: {log_path}")
            
        except Exception as e:
            self.logger.error(f"Error guardando log: {e}")

def main():
    """Función principal"""
    ejecutor = EjecutorMaestroAnalisis()
    
    try:
        exito = ejecutor.ejecutar_analisis_completo()
        
        if exito:
            print(f"\n🎉 ¡ANÁLISIS DE FACTIBILIDAD COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            print(f"\n💥 Análisis completado con errores")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
