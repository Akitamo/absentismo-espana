#!/usr/bin/env python
"""
Script para comparar snapshots y detectar nuevos periodos de datos del INE
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComparadorSnapshots:
    """Compara snapshots para detectar actualizaciones del INE"""
    
    def __init__(self):
        """Inicializa el comparador"""
        # Usar ruta relativa desde el script
        self.snapshots_dir = Path(__file__).parent.parent.parent / "snapshots"
        self.comparaciones_dir = Path(__file__).parent / "comparaciones"
        self.comparaciones_dir.mkdir(exist_ok=True)
    
    def listar_snapshots_disponibles(self):
        """
        Lista todos los snapshots disponibles
        
        Returns:
            list: Lista de fechas de snapshots ordenadas
        """
        if not self.snapshots_dir.exists():
            logger.error(f"No existe el directorio de snapshots: {self.snapshots_dir}")
            return []
        
        snapshots = []
        for carpeta in self.snapshots_dir.iterdir():
            if carpeta.is_dir():
                try:
                    # Verificar que es una fecha válida
                    datetime.strptime(carpeta.name, "%Y-%m-%d")
                    # Verificar que tiene periodos.json
                    if (carpeta / "periodos.json").exists():
                        snapshots.append(carpeta.name)
                except ValueError:
                    continue
        
        return sorted(snapshots)
    
    def cargar_snapshot(self, fecha):
        """
        Carga los datos de un snapshot
        
        Args:
            fecha: Fecha del snapshot (YYYY-MM-DD)
            
        Returns:
            dict: Datos del snapshot o None si hay error
        """
        snapshot_dir = self.snapshots_dir / fecha
        
        # Cargar archivos del snapshot
        snapshot_data = {
            'fecha': fecha,
            'metadata': None,
            'checksums': None,
            'periodos': None
        }
        
        # Cargar metadata
        metadata_path = snapshot_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                snapshot_data['metadata'] = json.load(f)
        
        # Cargar checksums
        checksums_path = snapshot_dir / "checksums.json"
        if checksums_path.exists():
            with open(checksums_path, 'r', encoding='utf-8') as f:
                snapshot_data['checksums'] = json.load(f)
        
        # Cargar periodos (lo más importante)
        periodos_path = snapshot_dir / "periodos.json"
        if periodos_path.exists():
            with open(periodos_path, 'r', encoding='utf-8') as f:
                snapshot_data['periodos'] = json.load(f)
        else:
            logger.warning(f"Snapshot {fecha} no tiene análisis de periodos")
        
        return snapshot_data
    
    def comparar_periodos(self, snapshot1, snapshot2):
        """
        Compara los periodos entre dos snapshots
        
        Args:
            snapshot1: Datos del primer snapshot
            snapshot2: Datos del segundo snapshot
            
        Returns:
            dict: Resultado de la comparación
        """
        comparacion = {
            'fecha1': snapshot1['fecha'],
            'fecha2': snapshot2['fecha'],
            'nuevos_periodos': [],
            'archivos_actualizados': [],
            'archivos_nuevos': [],
            'archivos_eliminados': [],
            'cambios_filas': [],
            'sin_cambios': []
        }
        
        # Si no hay datos de periodos, no podemos comparar
        if not snapshot1.get('periodos') or not snapshot2.get('periodos'):
            comparacion['error'] = "Uno o ambos snapshots no tienen análisis de periodos"
            return comparacion
        
        archivos1 = snapshot1['periodos'].get('archivos', {})
        archivos2 = snapshot2['periodos'].get('archivos', {})
        
        # Detectar archivos nuevos y eliminados
        archivos_set1 = set(archivos1.keys())
        archivos_set2 = set(archivos2.keys())
        
        comparacion['archivos_nuevos'] = list(archivos_set2 - archivos_set1)
        comparacion['archivos_eliminados'] = list(archivos_set1 - archivos_set2)
        
        # Comparar archivos comunes
        archivos_comunes = archivos_set1 & archivos_set2
        
        for archivo in archivos_comunes:
            datos1 = archivos1[archivo]
            datos2 = archivos2[archivo]
            
            # Skip si hay errores
            if 'error' in datos1 or 'error' in datos2:
                continue
            
            # Comparar último periodo
            ultimo1 = datos1.get('ultimo_periodo', {})
            ultimo2 = datos2.get('ultimo_periodo', {})
            
            if ultimo1.get('texto') != ultimo2.get('texto'):
                # Nuevo periodo detectado
                cambio = {
                    'archivo': archivo,
                    'periodo_anterior': ultimo1.get('texto', 'N/A'),
                    'periodo_nuevo': ultimo2.get('texto', 'N/A'),
                    'año_anterior': ultimo1.get('año'),
                    'año_nuevo': ultimo2.get('año'),
                    'trimestre_anterior': ultimo1.get('trimestre'),
                    'trimestre_nuevo': ultimo2.get('trimestre')
                }
                
                # Determinar si es un nuevo periodo o actualización
                if (ultimo2.get('año', 0) > ultimo1.get('año', 0)) or \
                   (ultimo2.get('año', 0) == ultimo1.get('año', 0) and 
                    ultimo2.get('trimestre', 0) > ultimo1.get('trimestre', 0)):
                    comparacion['nuevos_periodos'].append(cambio)
                else:
                    comparacion['archivos_actualizados'].append(cambio)
            
            # Comparar total de filas
            if datos1.get('total_filas') != datos2.get('total_filas'):
                cambio_filas = {
                    'archivo': archivo,
                    'filas_antes': datos1.get('total_filas', 0),
                    'filas_despues': datos2.get('total_filas', 0),
                    'diferencia': datos2.get('total_filas', 0) - datos1.get('total_filas', 0),
                    'porcentaje': ((datos2.get('total_filas', 0) - datos1.get('total_filas', 0)) / 
                                  datos1.get('total_filas', 1)) * 100
                }
                comparacion['cambios_filas'].append(cambio_filas)
            else:
                comparacion['sin_cambios'].append(archivo)
        
        return comparacion
    
    def generar_informe_comparacion(self, comparacion):
        """
        Genera un informe formateado de la comparación
        
        Args:
            comparacion: Resultado de la comparación
            
        Returns:
            str: Informe en formato texto
        """
        informe = []
        informe.append("=" * 60)
        informe.append("ANÁLISIS DE ACTUALIZACIÓN INE")
        informe.append("=" * 60)
        informe.append(f"Comparando: {comparacion['fecha1']} vs {comparacion['fecha2']}")
        informe.append("")
        
        # Verificar si hay error
        if 'error' in comparacion:
            informe.append(f"❌ ERROR: {comparacion['error']}")
            return "\n".join(informe)
        
        # Resumen
        total_archivos = (len(comparacion['nuevos_periodos']) + 
                         len(comparacion['archivos_actualizados']) +
                         len(comparacion['cambios_filas']) +
                         len(comparacion['sin_cambios']))
        
        informe.append("📊 RESUMEN:")
        informe.append(f"- Archivos analizados: {total_archivos}")
        informe.append(f"- Archivos con nuevos periodos: {len(comparacion['nuevos_periodos'])}")
        informe.append(f"- Archivos con cambios de filas: {len(comparacion['cambios_filas'])}")
        informe.append(f"- Archivos sin cambios: {len(comparacion['sin_cambios'])}")
        
        # Nuevos periodos
        if comparacion['nuevos_periodos']:
            informe.append("")
            informe.append("🆕 NUEVOS PERIODOS DETECTADOS:")
            
            tabla_periodos = []
            for cambio in comparacion['nuevos_periodos']:
                tabla_periodos.append([
                    cambio['archivo'],
                    cambio['periodo_anterior'],
                    cambio['periodo_nuevo']
                ])
            
            informe.append(tabulate(
                tabla_periodos,
                headers=['Archivo', 'Periodo Anterior', 'Periodo Nuevo'],
                tablefmt='grid'
            ))
        
        # Cambios en filas
        if comparacion['cambios_filas']:
            informe.append("")
            informe.append("📝 CAMBIOS EN NÚMERO DE FILAS:")
            
            tabla_filas = []
            for cambio in comparacion['cambios_filas']:
                tabla_filas.append([
                    cambio['archivo'],
                    f"{cambio['filas_antes']:,}",
                    f"{cambio['filas_despues']:,}",
                    f"{cambio['diferencia']:+,}",
                    f"{cambio['porcentaje']:+.1f}%"
                ])
            
            informe.append(tabulate(
                tabla_filas,
                headers=['Archivo', 'Filas Antes', 'Filas Después', 'Diferencia', '%'],
                tablefmt='grid'
            ))
        
        # Archivos nuevos/eliminados
        if comparacion['archivos_nuevos']:
            informe.append("")
            informe.append("✅ ARCHIVOS NUEVOS:")
            for archivo in comparacion['archivos_nuevos']:
                informe.append(f"  - {archivo}")
        
        if comparacion['archivos_eliminados']:
            informe.append("")
            informe.append("❌ ARCHIVOS ELIMINADOS:")
            for archivo in comparacion['archivos_eliminados']:
                informe.append(f"  - {archivo}")
        
        # Conclusión
        informe.append("")
        if comparacion['nuevos_periodos']:
            periodo_ejemplo = comparacion['nuevos_periodos'][0]
            informe.append(f"✨ NUEVO TRIMESTRE DISPONIBLE: {periodo_ejemplo['periodo_nuevo']}")
            informe.append(f"   El INE ha actualizado los datos con información del {periodo_ejemplo['periodo_nuevo']}")
        elif comparacion['cambios_filas']:
            informe.append("📊 Se detectaron actualizaciones en datos existentes")
            informe.append("   (posibles revisiones de datos provisionales)")
        else:
            informe.append("✅ No se detectaron cambios significativos")
        
        return "\n".join(informe)
    
    def guardar_comparacion(self, comparacion):
        """
        Guarda la comparación en archivos JSON y Markdown
        
        Args:
            comparacion: Resultado de la comparación
        """
        # Nombre base para los archivos
        nombre_base = f"{comparacion['fecha1']}_vs_{comparacion['fecha2']}"
        
        # Guardar JSON
        json_path = self.comparaciones_dir / f"{nombre_base}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparacion, f, ensure_ascii=False, indent=2)
        logger.info(f"Comparación guardada en: {json_path}")
        
        # Guardar informe Markdown
        informe_texto = self.generar_informe_comparacion(comparacion)
        md_path = self.comparaciones_dir / f"{nombre_base}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(informe_texto)
        logger.info(f"Informe guardado en: {md_path}")
    
    def comparar(self, fecha1, fecha2=None, guardar=True, mostrar=True):
        """
        Realiza la comparación entre dos fechas
        
        Args:
            fecha1: Primera fecha
            fecha2: Segunda fecha (None para usar la más reciente)
            guardar: Si guardar los resultados
            mostrar: Si mostrar el informe en consola
            
        Returns:
            dict: Resultado de la comparación
        """
        # Si no se especifica fecha2, usar la más reciente
        if fecha2 is None:
            snapshots = self.listar_snapshots_disponibles()
            if not snapshots:
                logger.error("No hay snapshots disponibles")
                return None
            fecha2 = snapshots[-1]
        
        # Cargar snapshots
        logger.info(f"Cargando snapshot {fecha1}...")
        snapshot1 = self.cargar_snapshot(fecha1)
        if not snapshot1:
            logger.error(f"No se pudo cargar snapshot {fecha1}")
            return None
        
        logger.info(f"Cargando snapshot {fecha2}...")
        snapshot2 = self.cargar_snapshot(fecha2)
        if not snapshot2:
            logger.error(f"No se pudo cargar snapshot {fecha2}")
            return None
        
        # Realizar comparación
        logger.info("Comparando snapshots...")
        comparacion = self.comparar_periodos(snapshot1, snapshot2)
        
        # Guardar resultados
        if guardar:
            self.guardar_comparacion(comparacion)
        
        # Mostrar informe
        if mostrar:
            print("\n" + self.generar_informe_comparacion(comparacion))
        
        return comparacion

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Compara snapshots para detectar nuevos periodos del INE"
    )
    
    parser.add_argument(
        '--fecha1',
        help='Primera fecha (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--fecha2',
        help='Segunda fecha (YYYY-MM-DD). Si no se especifica, usa la más reciente'
    )
    
    parser.add_argument(
        '--ultimo',
        action='store_true',
        help='Compara fecha1 con el snapshot más reciente'
    )
    
    parser.add_argument(
        '--listar',
        action='store_true',
        help='Lista todos los snapshots disponibles'
    )
    
    parser.add_argument(
        '--historico',
        action='store_true',
        help='Muestra el histórico de cambios entre todos los snapshots'
    )
    
    args = parser.parse_args()
    
    comparador = ComparadorSnapshots()
    
    # Listar snapshots disponibles
    if args.listar:
        snapshots = comparador.listar_snapshots_disponibles()
        if snapshots:
            print("\n📸 SNAPSHOTS DISPONIBLES:")
            for fecha in snapshots:
                print(f"  - {fecha}")
        else:
            print("❌ No hay snapshots disponibles")
        return
    
    # Mostrar histórico
    if args.historico:
        snapshots = comparador.listar_snapshots_disponibles()
        if len(snapshots) < 2:
            print("❌ Se necesitan al menos 2 snapshots para ver el histórico")
            return
        
        print("\n📊 HISTÓRICO DE CAMBIOS:")
        print("=" * 60)
        
        for i in range(len(snapshots) - 1):
            fecha1 = snapshots[i]
            fecha2 = snapshots[i + 1]
            
            print(f"\n{fecha1} → {fecha2}:")
            comparacion = comparador.comparar(fecha1, fecha2, guardar=False, mostrar=False)
            
            if comparacion and 'nuevos_periodos' in comparacion:
                if comparacion['nuevos_periodos']:
                    for cambio in comparacion['nuevos_periodos']:
                        print(f"  ✅ Nuevo periodo: {cambio['periodo_nuevo']}")
                else:
                    print("  - Sin nuevos periodos")
        return
    
    # Comparación normal
    if not args.fecha1:
        parser.print_help()
        print("\n❌ Debe especificar al menos --fecha1")
        return
    
    fecha2 = None if args.ultimo else args.fecha2
    comparador.comparar(args.fecha1, fecha2)

if __name__ == "__main__":
    main()
