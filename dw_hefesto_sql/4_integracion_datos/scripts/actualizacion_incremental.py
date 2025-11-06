"""
FASE 4: INTEGRACIÓN DE DATOS - ACTUALIZACIÓN INCREMENTAL
Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
Metodología: Hefesto
Autor: Sistema ETL
Fecha: Octubre 2025

Este script realiza actualizaciones periódicas del Data Warehouse:
1. Actualiza dimensiones (carga total para dimensiones pequeñas)
2. Actualiza hechos de los últimos N días (reemplazo de ventana temporal)
3. Mantiene la integridad referencial

POLÍTICA DE ACTUALIZACIÓN (según Hefesto):
- Frecuencia: Diaria (puede ejecutarse a medianoche o manualmente)
- Ventana de actualización: Últimos 30 días
- Dimensiones: Carga total (son pequeñas)
- Hechos: Reemplazo de ventana temporal

MODIFICADO: Adaptado para usar PostgreSQL con psycopg2
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
AI_USAGE_FILE = BASE_DIR / "archive (2)" / "ai_assistant_usage_student_life.csv"
WATER_FILE = BASE_DIR / "archive (3)" / "cleaned_global_water_consumption.csv"

# Parámetros de actualización
VENTANA_DIAS = 30  # Actualizar últimos 30 días
WATER_CONSUMPTION_FACTOR = 0.5
RANDOM_SEED = 42

# Variables de control temporal
FECHA_HASTA = datetime.now().date()
FECHA_DESDE = FECHA_HASTA - timedelta(days=VENTANA_DIAS)

print("="*80)
print(" " * 17 + "ACTUALIZACIÓN INCREMENTAL DEL DATA WAREHOUSE")
print(" " * 15 + "Huella Hídrica del Uso de IA en Estudiantes")
print("="*80)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Ventana de actualización: {FECHA_DESDE} a {FECHA_HASTA} ({VENTANA_DIAS} días)")
print("="*80)

# ============================================================================
# FUNCIONES DE EXTRACCIÓN Y LIMPIEZA (reutilizadas de carga_inicial)
# ============================================================================

def extraer_datos():
    """Extrae datos de las fuentes CSV"""
    print("\n[PASO 1] EXTRACCIÓN DE DATOS")
    print("-" * 80)

    if not AI_USAGE_FILE.exists() or not WATER_FILE.exists():
        print("   ✗ ERROR: Archivos fuente no encontrados")
        sys.exit(1)

    df_ai = pd.read_csv(AI_USAGE_FILE)
    df_water = pd.read_csv(WATER_FILE)

    print(f"   ✓ AI Usage: {len(df_ai):,} registros")
    print(f"   ✓ Water Consumption: {len(df_water):,} registros")

    return df_ai, df_water

def limpiar_datos(df_ai, df_water):
    """Limpia y valida los datos"""
    print("\n[PASO 2] LIMPIEZA DE DATOS")
    print("-" * 80)

    # Limpiar AI Usage
    df_ai_clean = df_ai.copy()
    df_ai_clean['SessionDate'] = pd.to_datetime(df_ai_clean['SessionDate'])
    df_ai_clean = df_ai_clean.dropna(subset=['SessionID', 'SessionDate', 'TotalPrompts'])
    df_ai_clean['TotalPrompts'] = df_ai_clean['TotalPrompts'].astype(int)
    df_ai_clean['SessionLengthMin'] = df_ai_clean['SessionLengthMin'].astype(float)
    df_ai_clean = df_ai_clean.drop_duplicates(subset=['SessionID'])

    # Limpiar Water
    df_water_clean = df_water.copy()
    df_water_clean = df_water_clean.dropna(subset=['Country', 'Year', 'Water Scarcity Level'])
    df_water_clean['Country'] = df_water_clean['Country'].str.strip()

    print(f"   ✓ {len(df_ai_clean):,} registros limpios de AI Usage")
    print(f"   ✓ {len(df_water_clean):,} registros limpios de Water Consumption")

    return df_ai_clean, df_water_clean

def filtrar_por_ventana_temporal(df_ai, fecha_desde, fecha_hasta):
    """Filtra datos dentro de la ventana temporal de actualización"""
    df_filtrado = df_ai[
        (df_ai['SessionDate'].dt.date >= fecha_desde) &
        (df_ai['SessionDate'].dt.date <= fecha_hasta)
    ].copy()

    print(f"   ✓ Datos filtrados: {len(df_filtrado):,} registros en ventana temporal")
    return df_filtrado

# ============================================================================
# ACTUALIZACIÓN DE DIMENSIONES
# ============================================================================

def actualizar_dimensiones(df_ai, df_water, conn):
    """
    Actualiza las dimensiones con carga total.
    Para dimensiones pequeñas, la carga total es más simple que incremental.
    """
    print("\n[PASO 3] ACTUALIZACIÓN DE DIMENSIONES (Carga Total)")
    print("-" * 80)

    cursor = conn.cursor()

    # 1. DIM_GEOGRAFIA (con granularidad año)
    print("   🌍 Actualizando DIM_GEOGRAFIA...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE DIM_GEOGRAFIA;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    geo_data = df_water[['Country', 'Year', 'Water Scarcity Level']].drop_duplicates()
    geo_data.rename(columns={
        'Country': 'Pais',
        'Year': 'Anio',
        'Water Scarcity Level': 'Nivel_Escasez_Agua'
    }, inplace=True)
    geo_data = geo_data.sort_values(['Pais', 'Anio']).reset_index(drop=True)

    for _, row in geo_data.iterrows():
        cursor.execute("""
            INSERT INTO DIM_GEOGRAFIA (Pais, Anio, Nivel_Escasez_Agua)
            VALUES (%s, %s, %s)
        """, (row['Pais'], int(row['Anio']), row['Nivel_Escasez_Agua']))
    conn.commit()
    print(f"      ✓ {len(geo_data):,} combinaciones (país + año) cargadas")

    # 2. DIM_ESTUDIANTE
    print("   🎓 Actualizando DIM_ESTUDIANTE...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE DIM_ESTUDIANTE;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    student_data = df_ai[['StudentLevel', 'Discipline']].drop_duplicates()
    student_data = student_data.sort_values(['StudentLevel', 'Discipline']).reset_index(drop=True)
    student_data.rename(columns={'StudentLevel': 'Nivel_Academico', 'Discipline': 'Disciplina'}, inplace=True)

    for _, row in student_data.iterrows():
        cursor.execute("""
            INSERT INTO DIM_ESTUDIANTE (Nivel_Academico, Disciplina)
            VALUES (%s, %s)
        """, (row['Nivel_Academico'], row['Disciplina']))
    conn.commit()
    print(f"      ✓ {len(student_data):,} combinaciones cargadas")

    # 3. DIM_TIEMPO (incremental: solo fechas nuevas)
    print("   📅 Actualizando DIM_TIEMPO (incremental)...")

    # Obtener última fecha cargada
    cursor.execute("SELECT MAX(Fecha) FROM DIM_TIEMPO;")
    result = cursor.fetchone()
    ultima_fecha = pd.to_datetime(result[0]).date() if result[0] else None

    if ultima_fecha:
        print(f"      → Última fecha en DIM_TIEMPO: {ultima_fecha}")
        # Solo cargar fechas nuevas
        fechas_nuevas = df_ai[df_ai['SessionDate'].dt.date > ultima_fecha]['SessionDate'].dt.date.unique()
    else:
        # Primera carga
        fechas_nuevas = df_ai['SessionDate'].dt.date.unique()

    if len(fechas_nuevas) > 0:
        dates_df = pd.DataFrame({'Fecha': pd.to_datetime(fechas_nuevas)})
        dates_df['idTiempo'] = dates_df['Fecha'].dt.strftime('%Y%m%d').astype(int)
        dates_df['Anio'] = dates_df['Fecha'].dt.year
        dates_df['Mes'] = dates_df['Fecha'].dt.month
        dates_df['Trimestre'] = dates_df['Fecha'].dt.quarter
        dates_df['Nombre_Mes'] = dates_df['Fecha'].dt.month_name()
        dates_df['Dia_Semana'] = dates_df['Fecha'].dt.day_name()
        dates_df = dates_df.sort_values('Fecha')
        dates_df = dates_df[['idTiempo', 'Fecha', 'Anio', 'Trimestre', 'Mes', 'Nombre_Mes', 'Dia_Semana']]

        for _, row in dates_df.iterrows():
            cursor.execute("""
                INSERT INTO DIM_TIEMPO (idTiempo, Fecha, Anio, Trimestre, Mes, Nombre_Mes, Dia_Semana)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (int(row['idTiempo']), str(row['Fecha'].date()), int(row['Anio']),
                  int(row['Trimestre']), int(row['Mes']), row['Nombre_Mes'], row['Dia_Semana']))
        print(f"      ✓ {len(dates_df):,} fechas nuevas agregadas")
    else:
        print("      ✓ No hay fechas nuevas para cargar")

    conn.commit()
    cursor.close()

# ============================================================================
# ACTUALIZACIÓN DE HECHOS
# ============================================================================

def actualizar_hechos(df_ai, fecha_desde, fecha_hasta, conn):
    """
    Actualiza la tabla de hechos:
    1. Elimina registros en la ventana temporal
    2. Recalcula y carga nuevamente esos registros
    """
    print("\n[PASO 4] ACTUALIZACIÓN DE HECHOS (Ventana Temporal)")
    print("-" * 80)

    cursor = conn.cursor()

    # Convertir fechas a formato idTiempo (YYYYMMDD)
    id_tiempo_desde = int(fecha_desde.strftime('%Y%m%d'))
    id_tiempo_hasta = int(fecha_hasta.strftime('%Y%m%d'))

    print(f"   → Eliminando hechos entre idTiempo {id_tiempo_desde} y {id_tiempo_hasta}...")

    # Eliminar hechos en la ventana temporal
    cursor.execute("""
        DELETE FROM HECHOS_HUELLA_HIDRICA_IA
        WHERE idTiempo >= %s AND idTiempo <= %s
    """, (id_tiempo_desde, id_tiempo_hasta))

    registros_eliminados = cursor.rowcount
    print(f"      ✓ {registros_eliminados:,} registros eliminados")

    # Filtrar datos de AI Usage en la ventana temporal
    df_ventana = filtrar_por_ventana_temporal(df_ai, fecha_desde, fecha_hasta)

    if len(df_ventana) == 0:
        print("      ⚠️ No hay datos nuevos en la ventana temporal")
        return

    # Obtener dimensiones
    dim_geografia = pd.read_sql("SELECT * FROM DIM_GEOGRAFIA", conn)
    dim_estudiante = pd.read_sql("SELECT * FROM DIM_ESTUDIANTE", conn)

    print("      → Procesando datos de la ventana temporal...")

    # Asignar países (reproducible)
    np.random.seed(RANDOM_SEED)
    df_ventana['Country'] = np.random.choice(dim_geografia['Pais'].tolist(), size=len(df_ventana))

    # Preparar para joins
    df_ventana['idTiempo'] = pd.to_datetime(df_ventana['SessionDate']).dt.strftime('%Y%m%d').astype(int)
    df_ventana_renamed = df_ventana.rename(columns={
        'Country': 'Pais',
        'StudentLevel': 'Nivel_Academico',
        'Discipline': 'Disciplina'
    })

    # Preparar año para join con geografía
    df_ventana_renamed['Anio'] = pd.to_datetime(df_ventana_renamed['SessionDate']).dt.year
    anio_min = dim_geografia['Anio'].min()
    anio_max = dim_geografia['Anio'].max()
    df_ventana_renamed['Anio_Ajustado'] = df_ventana_renamed['Anio'].clip(anio_min, anio_max)

    # JOINs con dimensiones (incluir Año para geografía)
    df_merged = df_ventana_renamed.merge(
        dim_geografia[['idGeografia', 'Pais', 'Anio']],
        left_on=['Pais', 'Anio_Ajustado'],
        right_on=['Pais', 'Anio'],
        how='left'
    )

    df_merged = df_merged.drop(columns=['Anio_Ajustado', 'Anio_y'])
    df_merged = df_merged.rename(columns={'Anio_x': 'Anio'})

    df_merged = df_merged.merge(
        dim_estudiante[['idEstudiante', 'Nivel_Academico', 'Disciplina']],
        on=['Nivel_Academico', 'Disciplina'],
        how='left'
    )

    # Eliminar registros con claves nulas
    df_merged = df_merged.dropna(subset=['idGeografia', 'idEstudiante', 'idTiempo'])

    # Calcular Huella Hídrica
    df_merged['Huella_Hidrica'] = df_merged['TotalPrompts'] * WATER_CONSUMPTION_FACTOR

    # Agregar por claves
    hechos = df_merged.groupby(['idGeografia', 'idEstudiante', 'idTiempo']).agg({
        'TotalPrompts': 'sum',
        'SessionLengthMin': 'sum',
        'SessionID': 'count',
        'Huella_Hidrica': 'sum'
    }).reset_index()

    hechos.rename(columns={
        'TotalPrompts': 'Total_Prompts',
        'SessionLengthMin': 'Duracion_Total_Sesiones',
        'SessionID': 'Numero_Sesiones'
    }, inplace=True)

    hechos = hechos[['idGeografia', 'idEstudiante', 'idTiempo',
                     'Huella_Hidrica', 'Total_Prompts',
                     'Duracion_Total_Sesiones', 'Numero_Sesiones']]

    print(f"      → Cargando {len(hechos):,} registros nuevos...")

    # Cargar a BD
    hechos.to_sql('HECHOS_HUELLA_HIDRICA_IA', conn, if_exists='append', index=False)

    print(f"      ✓ {len(hechos):,} hechos actualizados")
    print(f"      ✓ Huella hídrica: {hechos['Huella_Hidrica'].sum():,.2f} litros")
    print(f"      ✓ Prompts: {hechos['Total_Prompts'].sum():,}")
    print(f"      ✓ Sesiones: {hechos['Numero_Sesiones'].sum():,}")

    conn.commit()

# ============================================================================
# MAIN: EJECUTAR ACTUALIZACIÓN
# ============================================================================

def main():
    """Ejecuta el proceso completo de actualización incremental"""
    try:
        # Extraer datos
        df_ai, df_water = extraer_datos()

        # Limpiar datos
        df_ai_clean, df_water_clean = limpiar_datos(df_ai, df_water)

        # Conectar a base de datos PostgreSQL
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='dwuser',
            password='dwpass',
            dbname='datawarehouse_db'
        )

        # Actualizar dimensiones
        actualizar_dimensiones(df_ai_clean, df_water_clean, conn)

        # Actualizar hechos
        actualizar_hechos(df_ai_clean, FECHA_DESDE, FECHA_HASTA, conn)

        # Cerrar conexión
        conn.close()

        # Resumen final
        print("\n" + "="*80)
        print(" " * 22 + "✅ ACTUALIZACIÓN COMPLETADA")
        print("="*80)
        print("\nRESUMEN:")
        print(f"   • Ventana actualizada: {FECHA_DESDE} a {FECHA_HASTA}")
        print(f"   • Dimensiones actualizadas: 3 (carga total)")
        print(f"   • Hechos actualizados: últimos {VENTANA_DIAS} días")
        print(f"   • Base de datos: MySQL (datawarehouse_db)")
        print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNOTA: Esta actualización puede ejecutarse diariamente")
        print("      para mantener el Data Warehouse sincronizado.")
        print("="*80)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR EN LA ACTUALIZACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
