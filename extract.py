"""
Módulo de Extracción de Datos (Extract)
Lee los archivos CSV de las fuentes de datos
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config


def extract_ai_usage_data():
    """
    Extrae datos del archivo de uso de asistente de IA
    
    Returns:
        pd.DataFrame: DataFrame con los datos de uso de IA
    """
    print("📥 Extrayendo datos de AI Assistant Usage...")
    
    try:
        df = pd.read_csv(config.AI_USAGE_FILE)
        print(f"   ✓ {len(df):,} registros extraídos")
        print(f"   ✓ Columnas: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"   ✗ Error: Archivo no encontrado - {config.AI_USAGE_FILE}")
        return pd.DataFrame()
    except Exception as e:
        print(f"   ✗ Error al extraer datos de IA: {e}")
        return pd.DataFrame()


def extract_water_consumption_data():
    """
    Extrae datos del archivo de consumo de agua global
    
    Returns:
        pd.DataFrame: DataFrame con los datos de consumo de agua
    """
    print("📥 Extrayendo datos de Global Water Consumption...")
    
    try:
        df = pd.read_csv(config.WATER_CONSUMPTION_FILE)
        print(f"   ✓ {len(df):,} registros extraídos")
        print(f"   ✓ Columnas: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"   ✗ Error: Archivo no encontrado - {config.WATER_CONSUMPTION_FILE}")
        return pd.DataFrame()
    except Exception as e:
        print(f"   ✗ Error al extraer datos de agua: {e}")
        return pd.DataFrame()


def extract_all_data():
    """
    Extrae todos los datos de las fuentes
    
    Returns:
        tuple: (df_ai_usage, df_water_consumption)
    """
    print("\n" + "="*80)
    print("FASE 1: EXTRACCIÓN DE DATOS (EXTRACT)")
    print("="*80)
    
    df_ai = extract_ai_usage_data()
    df_water = extract_water_consumption_data()
    
    print(f"\n✅ Extracción completada:")
    print(f"   - AI Usage: {len(df_ai):,} registros")
    print(f"   - Water Consumption: {len(df_water):,} registros")
    
    return df_ai, df_water


if __name__ == "__main__":
    # Prueba del módulo
    df_ai, df_water = extract_all_data()
    
    if not df_ai.empty:
        print("\n📊 Vista previa de AI Usage:")
        print(df_ai.head())
        print(f"\nInfo del dataset:")
        print(df_ai.info())
    
    if not df_water.empty:
        print("\n📊 Vista previa de Water Consumption:")
        print(df_water.head())
        print(f"\nInfo del dataset:")
        print(df_water.info())
