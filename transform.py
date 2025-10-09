"""
Módulo de Transformación de Datos (Transform)
Limpia, normaliza y transforma los datos para crear las dimensiones y tabla de hechos
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config


def clean_ai_usage_data(df):
    """
    Limpia y prepara los datos de uso de IA
    
    Args:
        df: DataFrame con datos de AI usage
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n🧹 Limpiando datos de AI Usage...")
    
    df_clean = df.copy()
    
    # Convertir SessionDate a datetime
    df_clean['SessionDate'] = pd.to_datetime(df_clean['SessionDate'])
    
    # Eliminar registros con valores nulos en campos críticos
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['SessionID', 'SessionDate', 'TotalPrompts'])
    removed = initial_count - len(df_clean)
    if removed > 0:
        print(f"   ✓ Removidos {removed} registros con valores nulos")
    
    # Asegurar tipos de datos correctos
    df_clean['TotalPrompts'] = df_clean['TotalPrompts'].astype(int)
    df_clean['SessionLengthMin'] = df_clean['SessionLengthMin'].astype(float)
    
    # Eliminar duplicados
    initial_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['SessionID'])
    removed = initial_count - len(df_clean)
    if removed > 0:
        print(f"   ✓ Removidos {removed} registros duplicados")
    
    print(f"   ✓ {len(df_clean):,} registros limpios")
    
    return df_clean


def clean_water_consumption_data(df):
    """
    Limpia y prepara los datos de consumo de agua
    
    Args:
        df: DataFrame con datos de water consumption
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    print("\n🧹 Limpiando datos de Water Consumption...")
    
    df_clean = df.copy()
    
    # Eliminar registros con valores nulos en campos críticos
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['Country', 'Year', 'Water Scarcity Level'])
    removed = initial_count - len(df_clean)
    if removed > 0:
        print(f"   ✓ Removidos {removed} registros con valores nulos")
    
    # Asegurar tipos de datos correctos
    df_clean['Year'] = df_clean['Year'].astype(int)
    
    # Normalizar nombres de países
    df_clean['Country'] = df_clean['Country'].str.strip()
    
    print(f"   ✓ {len(df_clean):,} registros limpios")
    
    return df_clean


def create_dim_tiempo(df_ai):
    """
    Crea la dimensión Tiempo a partir de las fechas de sesión
    
    Args:
        df_ai: DataFrame con datos de AI usage
        
    Returns:
        pd.DataFrame: Dimensión Tiempo
    """
    print("\n📅 Creando Dimensión TIEMPO...")
    
    # Extraer fechas únicas
    dates = pd.to_datetime(df_ai['SessionDate']).unique()
    
    # Crear DataFrame de dimensión
    dim_tiempo = pd.DataFrame({
        'Fecha': pd.to_datetime(dates)
    })
    
    # Extraer componentes de tiempo
    dim_tiempo['Año'] = dim_tiempo['Fecha'].dt.year
    dim_tiempo['Mes'] = dim_tiempo['Fecha'].dt.month
    dim_tiempo['Trimestre'] = dim_tiempo['Fecha'].dt.quarter
    dim_tiempo['Semana'] = dim_tiempo['Fecha'].dt.isocalendar().week
    dim_tiempo['DiaSemana'] = dim_tiempo['Fecha'].dt.day_name()
    dim_tiempo['NombreMes'] = dim_tiempo['Fecha'].dt.month_name()
    
    # Agregar TiempoID
    dim_tiempo = dim_tiempo.sort_values('Fecha').reset_index(drop=True)
    dim_tiempo['TiempoID'] = dim_tiempo.index + 1
    
    # Reordenar columnas
    dim_tiempo = dim_tiempo[['TiempoID', 'Fecha', 'Año', 'Trimestre', 'Mes', 
                             'NombreMes', 'Semana', 'DiaSemana']]
    
    print(f"   ✓ {len(dim_tiempo):,} registros de tiempo creados")
    print(f"   ✓ Rango: {dim_tiempo['Fecha'].min()} a {dim_tiempo['Fecha'].max()}")
    
    return dim_tiempo


def create_dim_geografia(df_water):
    """
    Crea la dimensión Geografía a partir de los datos de consumo de agua
    
    Args:
        df_water: DataFrame con datos de water consumption
        
    Returns:
        pd.DataFrame: Dimensión Geografía
    """
    print("\n🌍 Creando Dimensión GEOGRAFÍA...")
    
    # Obtener combinaciones únicas de país y nivel de escasez
    # Usamos el promedio del nivel de escasez por país
    geo_data = df_water.groupby('Country').agg({
        'Water Scarcity Level': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
    }).reset_index()
    
    # Agregar GeografiaID
    geo_data['GeografiaID'] = range(1, len(geo_data) + 1)
    
    # Renombrar columnas
    dim_geografia = geo_data.rename(columns={
        'Water Scarcity Level': 'WaterScarcityLevel'
    })
    
    # Reordenar columnas
    dim_geografia = dim_geografia[['GeografiaID', 'Country', 'WaterScarcityLevel']]
    
    print(f"   ✓ {len(dim_geografia):,} países registrados")
    print(f"   ✓ Niveles de escasez: {dim_geografia['WaterScarcityLevel'].unique()}")
    
    return dim_geografia


def create_dim_estudiante(df_ai):
    """
    Crea la dimensión Estudiante a partir de los datos de uso de IA
    
    Args:
        df_ai: DataFrame con datos de AI usage
        
    Returns:
        pd.DataFrame: Dimensión Estudiante
    """
    print("\n🎓 Creando Dimensión ESTUDIANTE...")
    
    # Obtener combinaciones únicas de StudentLevel y Discipline
    student_data = df_ai[['StudentLevel', 'Discipline']].drop_duplicates()
    
    # Agregar EstudianteID
    student_data = student_data.sort_values(['StudentLevel', 'Discipline']).reset_index(drop=True)
    student_data['EstudianteID'] = student_data.index + 1
    
    dim_estudiante = student_data[['EstudianteID', 'StudentLevel', 'Discipline']]
    
    print(f"   ✓ {len(dim_estudiante):,} combinaciones de estudiante creadas")
    print(f"   ✓ Niveles: {dim_estudiante['StudentLevel'].unique()}")
    print(f"   ✓ Disciplinas: {len(dim_estudiante['Discipline'].unique())} únicas")
    
    return dim_estudiante


def assign_country_to_sessions(df_ai, dim_geografia):
    """
    Asigna países a las sesiones de IA de forma aleatoria pero consistente
    Esto es necesario porque el dataset de IA no incluye información geográfica
    
    Args:
        df_ai: DataFrame con datos de AI usage
        dim_geografia: DataFrame con dimensión geografía
        
    Returns:
        pd.DataFrame: DataFrame con columna Country agregada
    """
    print("\n🗺️ Asignando países a sesiones de IA...")
    
    df_with_country = df_ai.copy()
    
    # Obtener lista de países
    countries = dim_geografia['Country'].tolist()
    
    # Asignar países de forma aleatoria pero reproducible
    np.random.seed(42)  # Para reproducibilidad
    df_with_country['Country'] = np.random.choice(countries, size=len(df_ai))
    
    print(f"   ✓ Países asignados a {len(df_with_country):,} sesiones")
    
    return df_with_country


def create_fact_table(df_ai, dim_tiempo, dim_geografia, dim_estudiante):
    """
    Crea la tabla de hechos con los indicadores calculados
    
    Args:
        df_ai: DataFrame con datos de AI usage (con Country asignado)
        dim_tiempo: Dimensión Tiempo
        dim_geografia: Dimensión Geografía
        dim_estudiante: Dimensión Estudiante
        
    Returns:
        pd.DataFrame: Tabla de hechos
    """
    print("\n📊 Creando Tabla de HECHOS...")
    
    # Asignar países a las sesiones
    df_ai_with_country = assign_country_to_sessions(df_ai, dim_geografia)
    
    # Crear tabla de hechos base
    fact_table = df_ai_with_country.copy()
    
    # Hacer merge con dimensión tiempo
    fact_table['Fecha'] = pd.to_datetime(fact_table['SessionDate']).dt.date
    fact_table = fact_table.merge(
        dim_tiempo[['TiempoID', 'Fecha']].assign(Fecha=lambda x: x['Fecha'].dt.date),
        on='Fecha',
        how='left'
    )
    
    # Hacer merge con dimensión geografía
    fact_table = fact_table.merge(
        dim_geografia[['GeografiaID', 'Country']],
        on='Country',
        how='left'
    )
    
    # Hacer merge con dimensión estudiante
    fact_table = fact_table.merge(
        dim_estudiante[['EstudianteID', 'StudentLevel', 'Discipline']],
        on=['StudentLevel', 'Discipline'],
        how='left'
    )
    
    # Calcular indicadores
    fact_table['ConsumoAguaEstimado'] = fact_table['TotalPrompts'] * config.WATER_CONSUMPTION_FACTOR
    fact_table['NumeroSesiones'] = 1  # Cada fila es una sesión
    
    # Agregar FactID
    fact_table['FactID'] = range(1, len(fact_table) + 1)
    
    # Seleccionar y ordenar columnas finales
    fact_uso_ia_agua = fact_table[[
        'FactID',
        'GeografiaID',
        'EstudianteID',
        'TiempoID',
        'TotalPrompts',
        'SessionLengthMin',
        'NumeroSesiones',
        'ConsumoAguaEstimado'
    ]]
    
    # Agregar factor de consumo como columna constante
    fact_uso_ia_agua['FactorConsumoLitros'] = config.WATER_CONSUMPTION_FACTOR
    
    print(f"   ✓ {len(fact_uso_ia_agua):,} hechos creados")
    print(f"   ✓ Consumo total de agua estimado: {fact_uso_ia_agua['ConsumoAguaEstimado'].sum():,.2f} litros")
    print(f"   ✓ Total de prompts: {fact_uso_ia_agua['TotalPrompts'].sum():,}")
    
    return fact_uso_ia_agua


def transform_all_data(df_ai, df_water):
    """
    Ejecuta todas las transformaciones y crea el modelo dimensional
    
    Args:
        df_ai: DataFrame con datos de AI usage
        df_water: DataFrame con datos de water consumption
        
    Returns:
        tuple: (dim_tiempo, dim_geografia, dim_estudiante, fact_table)
    """
    print("\n" + "="*80)
    print("FASE 2: TRANSFORMACIÓN DE DATOS (TRANSFORM)")
    print("="*80)
    
    # Limpieza
    df_ai_clean = clean_ai_usage_data(df_ai)
    df_water_clean = clean_water_consumption_data(df_water)
    
    # Crear dimensiones
    dim_tiempo = create_dim_tiempo(df_ai_clean)
    dim_geografia = create_dim_geografia(df_water_clean)
    dim_estudiante = create_dim_estudiante(df_ai_clean)
    
    # Crear tabla de hechos
    fact_table = create_fact_table(df_ai_clean, dim_tiempo, dim_geografia, dim_estudiante)
    
    print("\n✅ Transformación completada:")
    print(f"   - Dimensión Tiempo: {len(dim_tiempo):,} registros")
    print(f"   - Dimensión Geografía: {len(dim_geografia):,} registros")
    print(f"   - Dimensión Estudiante: {len(dim_estudiante):,} registros")
    print(f"   - Tabla de Hechos: {len(fact_table):,} registros")
    
    return dim_tiempo, dim_geografia, dim_estudiante, fact_table


if __name__ == "__main__":
    # Prueba del módulo
    from extract import extract_all_data
    
    df_ai, df_water = extract_all_data()
    
    if not df_ai.empty and not df_water.empty:
        dim_tiempo, dim_geografia, dim_estudiante, fact_table = transform_all_data(df_ai, df_water)
        
        print("\n📊 Vista previa de dimensiones y hechos:")
        print("\nDIM_TIEMPO:")
        print(dim_tiempo.head())
        print("\nDIM_GEOGRAFIA:")
        print(dim_geografia.head())
        print("\nDIM_ESTUDIANTE:")
        print(dim_estudiante.head())
        print("\nFACT_USO_IA_AGUA:")
        print(fact_table.head())
