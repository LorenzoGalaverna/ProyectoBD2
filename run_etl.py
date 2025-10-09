"""
Script Principal de Ejecución del ETL
Ejecuta todo el proceso ETL completo: Extract, Transform, Load y Visualize
"""

import sys
import time
from datetime import datetime
import config
from extract import extract_all_data
from transform import transform_all_data
from load import load_all_data
from visualize import visualize_all_data


def print_header():
    """Imprime el encabezado del ETL"""
    print("\n" + "="*80)
    print(" "*20 + "ETL - DATA WAREHOUSE")
    print(" "*10 + "USO DE IA Y CONSUMO DE AGUA")
    print("="*80)
    print(f"\nFecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Factor de consumo de agua: {config.WATER_CONSUMPTION_FACTOR} L/prompt")
    print("="*80)


def print_footer(start_time):
    """Imprime el pie de página con estadísticas de ejecución"""
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("ETL COMPLETADO EXITOSAMENTE ✅")
    print("="*80)
    print(f"\n⏱️ Tiempo total de ejecución: {elapsed_time:.2f} segundos")
    print(f"\n📁 Archivos generados:")
    print(f"   - Dimensiones: {config.DIMENSIONS_DIR}")
    print(f"   - Hechos: {config.FACTS_DIR}")
    print(f"   - Reportes: {config.REPORTS_DIR}")
    print(f"   - Visualizaciones: {config.VISUALIZATIONS_DIR}")
    print("\n" + "="*80)
    print("¡Gracias por usar el ETL de Data Warehouse!")
    print("="*80 + "\n")


def run_etl():
    """
    Ejecuta el proceso ETL completo
    
    Returns:
        bool: True si se ejecutó exitosamente, False en caso contrario
    """
    start_time = time.time()
    
    try:
        # Imprimir encabezado
        print_header()
        
        # FASE 1: EXTRACT
        df_ai, df_water = extract_all_data()
        
        if df_ai.empty or df_water.empty:
            print("\n❌ Error: No se pudieron extraer los datos. Verifica los archivos de entrada.")
            return False
        
        # FASE 2: TRANSFORM
        dim_tiempo, dim_geografia, dim_estudiante, fact_table = transform_all_data(df_ai, df_water)
        
        if any(df.empty for df in [dim_tiempo, dim_geografia, dim_estudiante, fact_table]):
            print("\n❌ Error: No se pudieron transformar los datos.")
            return False
        
        # FASE 3: LOAD
        load_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table)
        
        # FASE 4: VISUALIZE
        visualize_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table)
        
        # Imprimir pie de página
        print_footer(start_time)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución del ETL: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_etl()
    sys.exit(0 if success else 1)
