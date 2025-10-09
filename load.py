"""
Módulo de Carga de Datos (Load)
Guarda las dimensiones y tabla de hechos en archivos CSV/Parquet
"""

import pandas as pd
import os
import config


def save_dimension(df, dimension_name):
    """
    Guarda una dimensión en archivo
    
    Args:
        df: DataFrame de la dimensión
        dimension_name: Nombre de la dimensión
    """
    filename = f"dim_{dimension_name.lower()}.{config.OUTPUT_FORMAT}"
    filepath = os.path.join(config.DIMENSIONS_DIR, filename)
    
    if config.OUTPUT_FORMAT == 'csv':
        df.to_csv(filepath, index=False, encoding='utf-8')
    elif config.OUTPUT_FORMAT == 'parquet':
        df.to_parquet(filepath, index=False)
    
    print(f"   ✓ {dimension_name}: {filepath}")


def save_fact_table(df, fact_name):
    """
    Guarda la tabla de hechos en archivo
    
    Args:
        df: DataFrame de la tabla de hechos
        fact_name: Nombre de la tabla de hechos
    """
    filename = f"fact_{fact_name.lower()}.{config.OUTPUT_FORMAT}"
    filepath = os.path.join(config.FACTS_DIR, filename)
    
    if config.OUTPUT_FORMAT == 'csv':
        df.to_csv(filepath, index=False, encoding='utf-8')
    elif config.OUTPUT_FORMAT == 'parquet':
        df.to_parquet(filepath, index=False)
    
    print(f"   ✓ {fact_name}: {filepath}")


def generate_summary_report(dim_tiempo, dim_geografia, dim_estudiante, fact_table):
    """
    Genera un reporte resumen del Data Warehouse
    
    Args:
        dim_tiempo: Dimensión Tiempo
        dim_geografia: Dimensión Geografía
        dim_estudiante: Dimensión Estudiante
        fact_table: Tabla de hechos
    """
    report_path = os.path.join(config.REPORTS_DIR, 'data_warehouse_summary.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RESUMEN DEL DATA WAREHOUSE - USO DE IA Y CONSUMO DE AGUA\n")
        f.write("="*80 + "\n\n")
        
        f.write("DIMENSIONES\n")
        f.write("-" * 80 + "\n\n")
        
        # Dimensión Tiempo
        f.write(f"DIM_TIEMPO: {len(dim_tiempo):,} registros\n")
        f.write(f"  - Rango de fechas: {dim_tiempo['Fecha'].min()} a {dim_tiempo['Fecha'].max()}\n")
        f.write(f"  - Años: {sorted(dim_tiempo['Año'].unique())}\n")
        f.write(f"  - Trimestres por año: {dim_tiempo.groupby('Año')['Trimestre'].nunique().to_dict()}\n\n")
        
        # Dimensión Geografía
        f.write(f"DIM_GEOGRAFIA: {len(dim_geografia):,} registros\n")
        f.write(f"  - Países: {len(dim_geografia['Country'].unique())}\n")
        f.write(f"  - Niveles de escasez:\n")
        for level, count in dim_geografia['WaterScarcityLevel'].value_counts().items():
            f.write(f"    * {level}: {count} países\n")
        f.write("\n")
        
        # Dimensión Estudiante
        f.write(f"DIM_ESTUDIANTE: {len(dim_estudiante):,} registros\n")
        f.write(f"  - Niveles académicos:\n")
        for level, count in dim_estudiante['StudentLevel'].value_counts().items():
            f.write(f"    * {level}: {count} combinaciones\n")
        f.write(f"  - Disciplinas: {len(dim_estudiante['Discipline'].unique())} únicas\n")
        f.write(f"    {', '.join(sorted(dim_estudiante['Discipline'].unique()))}\n\n")
        
        # Tabla de Hechos
        f.write("TABLA DE HECHOS\n")
        f.write("-" * 80 + "\n\n")
        f.write(f"FACT_USO_IA_AGUA: {len(fact_table):,} registros\n\n")
        
        f.write("INDICADORES:\n")
        f.write(f"  - Total Prompts: {fact_table['TotalPrompts'].sum():,}\n")
        f.write(f"    * Promedio por sesión: {fact_table['TotalPrompts'].mean():.2f}\n")
        f.write(f"    * Máximo: {fact_table['TotalPrompts'].max()}\n")
        f.write(f"    * Mínimo: {fact_table['TotalPrompts'].min()}\n\n")
        
        f.write(f"  - Duración Total Sesiones: {fact_table['SessionLengthMin'].sum():,.2f} minutos\n")
        f.write(f"    * Promedio por sesión: {fact_table['SessionLengthMin'].mean():.2f} min\n")
        f.write(f"    * Total en horas: {fact_table['SessionLengthMin'].sum() / 60:,.2f} hrs\n\n")
        
        f.write(f"  - Número de Sesiones: {fact_table['NumeroSesiones'].sum():,}\n\n")
        
        f.write(f"  - Consumo de Agua Estimado: {fact_table['ConsumoAguaEstimado'].sum():,.2f} litros\n")
        f.write(f"    * Promedio por sesión: {fact_table['ConsumoAguaEstimado'].mean():.2f} L\n")
        f.write(f"    * Factor de conversión: {config.WATER_CONSUMPTION_FACTOR} L/prompt\n\n")
        
        f.write("="*80 + "\n")
        f.write(f"Reporte generado: {pd.Timestamp.now()}\n")
        f.write("="*80 + "\n")
    
    print(f"   ✓ Reporte resumen: {report_path}")


def load_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table):
    """
    Carga todos los datos del Data Warehouse
    
    Args:
        dim_tiempo: Dimensión Tiempo
        dim_geografia: Dimensión Geografía
        dim_estudiante: Dimensión Estudiante
        fact_table: Tabla de hechos
    """
    print("\n" + "="*80)
    print("FASE 3: CARGA DE DATOS (LOAD)")
    print("="*80)
    
    print("\n💾 Guardando dimensiones...")
    save_dimension(dim_tiempo, "tiempo")
    save_dimension(dim_geografia, "geografia")
    save_dimension(dim_estudiante, "estudiante")
    
    print("\n💾 Guardando tabla de hechos...")
    save_fact_table(fact_table, "uso_ia_agua")
    
    print("\n📄 Generando reporte resumen...")
    generate_summary_report(dim_tiempo, dim_geografia, dim_estudiante, fact_table)
    
    print("\n✅ Carga completada:")
    print(f"   - Formato: {config.OUTPUT_FORMAT.upper()}")
    print(f"   - Ubicación: {config.OUTPUT_DIR}")


if __name__ == "__main__":
    # Prueba del módulo
    from extract import extract_all_data
    from transform import transform_all_data
    
    df_ai, df_water = extract_all_data()
    
    if not df_ai.empty and not df_water.empty:
        dim_tiempo, dim_geografia, dim_estudiante, fact_table = transform_all_data(df_ai, df_water)
        load_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table)
