"""
FASE 4: INTEGRACIÓN DE DATOS - CARGA INICIAL
Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
Metodología: Hefesto
Autor: Sistema ETL
Fecha: Octubre 2025

Este script realiza la carga inicial completa del Data Warehouse:
1. Extrae datos de las fuentes CSV (OLTP)
2. Transforma y limpia los datos
3. Carga las dimensiones
4. Carga la tabla de hechos con métricas agregadas
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
AI_USAGE_FILE = BASE_DIR / "archive (2)" / "ai_assistant_usage_student_life.csv"
WATER_FILE = BASE_DIR / "archive (3)" / "cleaned_global_water_consumption.csv"
DB_FILE = BASE_DIR / "dw_hefesto_sql" / "database" / "datawarehouse.db"
SQL_DIR = BASE_DIR / "dw_hefesto_sql" / "3_modelo_logico" / "sql"

# Factor de conversión (litros por prompt)
WATER_CONSUMPTION_FACTOR = 0.5

# Seed para reproducibilidad
RANDOM_SEED = 42

print("="*80)
print(" " * 20 + "CARGA INICIAL DEL DATA WAREHOUSE")
print(" " * 15 + "Huella Hídrica del Uso de IA en Estudiantes")
print("="*80)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# ============================================================================
# PASO 0: CREAR BASE DE DATOS Y TABLAS
# ============================================================================

def crear_estructura_database():
    """Crea la base de datos y las tablas usando los scripts SQL"""
    print("\n[PASO 0] CREANDO ESTRUCTURA DE BASE DE DATOS")
    print("-" * 80)

    # Crear directorio si no existe
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Conectar a SQLite (crea el archivo si no existe)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Habilitar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("   ✓ Creando tablas de dimensiones...")

    # Crear DIM_GEOGRAFIA (con Año para mantener variación temporal de escasez)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_GEOGRAFIA (
        idGeografia INTEGER PRIMARY KEY AUTOINCREMENT,
        Pais TEXT NOT NULL,
        Anio INTEGER NOT NULL,
        Nivel_Escasez_Agua TEXT NOT NULL,
        UNIQUE(Pais, Anio),
        CHECK (Nivel_Escasez_Agua IN ('Low', 'Moderate', 'High', 'Extreme'))
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_geografia_pais ON DIM_GEOGRAFIA(Pais);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_geografia_anio ON DIM_GEOGRAFIA(Anio);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_geografia_escasez ON DIM_GEOGRAFIA(Nivel_Escasez_Agua);")

    # Crear DIM_ESTUDIANTE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_ESTUDIANTE (
        idEstudiante INTEGER PRIMARY KEY AUTOINCREMENT,
        Nivel_Academico TEXT NOT NULL,
        Disciplina TEXT NOT NULL,
        UNIQUE(Nivel_Academico, Disciplina),
        CHECK (Nivel_Academico IN ('Undergraduate', 'Graduate', 'High School'))
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_estudiante_nivel ON DIM_ESTUDIANTE(Nivel_Academico);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_estudiante_disciplina ON DIM_ESTUDIANTE(Disciplina);")

    # Crear DIM_TIEMPO
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_TIEMPO (
        idTiempo INTEGER PRIMARY KEY,
        Fecha DATE NOT NULL UNIQUE,
        Anio INTEGER NOT NULL,
        Trimestre INTEGER NOT NULL,
        Mes INTEGER NOT NULL,
        Nombre_Mes TEXT NOT NULL,
        Dia_Semana TEXT NOT NULL,
        CHECK (Trimestre BETWEEN 1 AND 4),
        CHECK (Mes BETWEEN 1 AND 12),
        CHECK (Anio BETWEEN 2000 AND 2100)
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tiempo_fecha ON DIM_TIEMPO(Fecha);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tiempo_anio_mes ON DIM_TIEMPO(Anio, Mes);")

    print("   ✓ Creando tabla de hechos...")

    # Crear HECHOS_HUELLA_HIDRICA_IA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS HECHOS_HUELLA_HIDRICA_IA (
        idGeografia INTEGER NOT NULL,
        idEstudiante INTEGER NOT NULL,
        idTiempo INTEGER NOT NULL,
        Huella_Hidrica REAL NOT NULL CHECK (Huella_Hidrica >= 0),
        Total_Prompts INTEGER NOT NULL CHECK (Total_Prompts >= 0),
        Duracion_Total_Sesiones REAL NOT NULL CHECK (Duracion_Total_Sesiones >= 0),
        Numero_Sesiones INTEGER NOT NULL CHECK (Numero_Sesiones > 0),
        PRIMARY KEY (idGeografia, idEstudiante, idTiempo),
        FOREIGN KEY (idGeografia) REFERENCES DIM_GEOGRAFIA(idGeografia)
            ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY (idEstudiante) REFERENCES DIM_ESTUDIANTE(idEstudiante)
            ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY (idTiempo) REFERENCES DIM_TIEMPO(idTiempo)
            ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hechos_geografia ON HECHOS_HUELLA_HIDRICA_IA(idGeografia);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hechos_estudiante ON HECHOS_HUELLA_HIDRICA_IA(idEstudiante);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hechos_tiempo ON HECHOS_HUELLA_HIDRICA_IA(idTiempo);")

    conn.commit()
    conn.close()

    print(f"   ✓ Base de datos creada: {DB_FILE}")
    print("   ✓ Estructura del DW lista\n")

# ============================================================================
# PASO 1: EXTRACCIÓN DE DATOS (EXTRACT)
# ============================================================================

def extraer_datos():
    """Extrae datos de las fuentes CSV"""
    print("\n[PASO 1] EXTRACCIÓN DE DATOS")
    print("-" * 80)

    # Validar existencia de archivos
    if not AI_USAGE_FILE.exists():
        print(f"   ✗ ERROR: Archivo no encontrado: {AI_USAGE_FILE}")
        sys.exit(1)
    if not WATER_FILE.exists():
        print(f"   ✗ ERROR: Archivo no encontrado: {WATER_FILE}")
        sys.exit(1)

    # Leer AI Usage
    print("   📥 Extrayendo AI Assistant Usage...")
    df_ai = pd.read_csv(AI_USAGE_FILE)
    print(f"      ✓ {len(df_ai):,} registros extraídos")
    print(f"      ✓ Columnas: {', '.join(df_ai.columns.tolist())}")

    # Leer Water Consumption
    print("   📥 Extrayendo Global Water Consumption...")
    df_water = pd.read_csv(WATER_FILE)
    print(f"      ✓ {len(df_water):,} registros extraídos")
    print(f"      ✓ Columnas: {', '.join(df_water.columns.tolist())}")

    return df_ai, df_water

# ============================================================================
# PASO 2: TRANSFORMACIÓN DE DATOS (TRANSFORM)
# ============================================================================

def limpiar_datos(df_ai, df_water):
    """Limpia y valida los datos"""
    print("\n[PASO 2] TRANSFORMACIÓN Y LIMPIEZA DE DATOS")
    print("-" * 80)

    # Limpiar AI Usage
    print("   🧹 Limpiando AI Usage...")
    df_ai_clean = df_ai.copy()
    df_ai_clean['SessionDate'] = pd.to_datetime(df_ai_clean['SessionDate'])

    # Eliminar nulos en campos críticos
    initial_count = len(df_ai_clean)
    df_ai_clean = df_ai_clean.dropna(subset=['SessionID', 'SessionDate', 'TotalPrompts'])
    removed = initial_count - len(df_ai_clean)
    if removed > 0:
        print(f"      ✓ Removidos {removed} registros con valores nulos")

    # Asegurar tipos correctos
    df_ai_clean['TotalPrompts'] = df_ai_clean['TotalPrompts'].astype(int)
    df_ai_clean['SessionLengthMin'] = df_ai_clean['SessionLengthMin'].astype(float)

    # Eliminar duplicados
    initial_count = len(df_ai_clean)
    df_ai_clean = df_ai_clean.drop_duplicates(subset=['SessionID'])
    removed = initial_count - len(df_ai_clean)
    if removed > 0:
        print(f"      ✓ Removidos {removed} registros duplicados")

    print(f"      ✓ {len(df_ai_clean):,} registros limpios de AI Usage")

    # Limpiar Water Consumption
    print("   🧹 Limpiando Water Consumption...")
    df_water_clean = df_water.copy()
    df_water_clean = df_water_clean.dropna(subset=['Country', 'Year', 'Water Scarcity Level'])
    df_water_clean['Country'] = df_water_clean['Country'].str.strip()
    print(f"      ✓ {len(df_water_clean):,} registros limpios de Water Consumption")

    return df_ai_clean, df_water_clean

# ============================================================================
# PASO 3: CARGA DE DIMENSIONES (LOAD DIMENSIONS)
# ============================================================================

def cargar_dim_geografia(df_water, conn):
    """Carga la dimensión Geografía con granularidad anual"""
    print("\n   🌍 Cargando DIM_GEOGRAFIA...")

    # Obtener combinaciones únicas de país, año y nivel de escasez
    geo_data = df_water[['Country', 'Year', 'Water Scarcity Level']].drop_duplicates()

    geo_data.rename(columns={
        'Country': 'Pais',
        'Year': 'Anio',
        'Water Scarcity Level': 'Nivel_Escasez_Agua'
    }, inplace=True)

    # Ordenar por país y año
    geo_data = geo_data.sort_values(['Pais', 'Anio']).reset_index(drop=True)

    # Insertar registros uno por uno para obtener IDs
    cursor = conn.cursor()
    for _, row in geo_data.iterrows():
        cursor.execute("""
            INSERT INTO DIM_GEOGRAFIA (Pais, Anio, Nivel_Escasez_Agua)
            VALUES (?, ?, ?)
        """, (row['Pais'], int(row['Anio']), row['Nivel_Escasez_Agua']))
    conn.commit()

    print(f"      ✓ {len(geo_data):,} combinaciones (país + año) cargadas")
    print(f"      ✓ Países únicos: {geo_data['Pais'].nunique()}")
    print(f"      ✓ Rango de años: {geo_data['Anio'].min()} - {geo_data['Anio'].max()}")
    print(f"      ✓ Niveles de escasez: {sorted(geo_data['Nivel_Escasez_Agua'].unique())}")

    return geo_data

def cargar_dim_estudiante(df_ai, conn):
    """Carga la dimensión Estudiante"""
    print("   🎓 Cargando DIM_ESTUDIANTE...")

    # Obtener combinaciones únicas
    student_data = df_ai[['StudentLevel', 'Discipline']].drop_duplicates()
    student_data = student_data.sort_values(['StudentLevel', 'Discipline']).reset_index(drop=True)

    student_data.rename(columns={
        'StudentLevel': 'Nivel_Academico',
        'Discipline': 'Disciplina'
    }, inplace=True)

    # Insertar registros con SQL
    cursor = conn.cursor()
    for _, row in student_data.iterrows():
        cursor.execute("""
            INSERT INTO DIM_ESTUDIANTE (Nivel_Academico, Disciplina)
            VALUES (?, ?)
        """, (row['Nivel_Academico'], row['Disciplina']))
    conn.commit()

    print(f"      ✓ {len(student_data):,} combinaciones cargadas")
    print(f"      ✓ Niveles: {student_data['Nivel_Academico'].unique()}")
    print(f"      ✓ Disciplinas: {len(student_data['Disciplina'].unique())} únicas")

    return student_data

def cargar_dim_tiempo(df_ai, conn):
    """Carga la dimensión Tiempo"""
    print("   📅 Cargando DIM_TIEMPO...")

    # Extraer fechas únicas
    dates = pd.to_datetime(df_ai['SessionDate']).dt.date.unique()
    dates_df = pd.DataFrame({'Fecha': pd.to_datetime(dates)})

    # Extraer componentes de tiempo
    dates_df['idTiempo'] = dates_df['Fecha'].dt.strftime('%Y%m%d').astype(int)
    dates_df['Anio'] = dates_df['Fecha'].dt.year
    dates_df['Mes'] = dates_df['Fecha'].dt.month
    dates_df['Trimestre'] = dates_df['Fecha'].dt.quarter
    dates_df['Nombre_Mes'] = dates_df['Fecha'].dt.month_name()
    dates_df['Dia_Semana'] = dates_df['Fecha'].dt.day_name()

    # Ordenar y seleccionar columnas
    dates_df = dates_df.sort_values('Fecha')
    dates_df = dates_df[['idTiempo', 'Fecha', 'Anio', 'Trimestre', 'Mes',
                          'Nombre_Mes', 'Dia_Semana']]

    # Insertar registros con SQL
    cursor = conn.cursor()
    for _, row in dates_df.iterrows():
        cursor.execute("""
            INSERT INTO DIM_TIEMPO (idTiempo, Fecha, Anio, Trimestre, Mes, Nombre_Mes, Dia_Semana)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (int(row['idTiempo']), str(row['Fecha'].date()), int(row['Anio']),
              int(row['Trimestre']), int(row['Mes']), row['Nombre_Mes'], row['Dia_Semana']))
    conn.commit()

    print(f"      ✓ {len(dates_df):,} fechas cargadas")
    print(f"      ✓ Rango: {dates_df['Fecha'].min()} a {dates_df['Fecha'].max()}")

    return dates_df

# ============================================================================
# PASO 4: CARGA DE HECHOS (LOAD FACTS)
# ============================================================================

def cargar_hechos(df_ai, conn):
    """Carga la tabla de hechos con datos agregados"""
    print("\n   📊 Cargando HECHOS_HUELLA_HIDRICA_IA...")

    # Obtener dimensiones cargadas
    dim_geografia = pd.read_sql("SELECT * FROM DIM_GEOGRAFIA", conn)
    dim_estudiante = pd.read_sql("SELECT * FROM DIM_ESTUDIANTE", conn)
    dim_tiempo = pd.read_sql("SELECT * FROM DIM_TIEMPO", conn)

    print("      → Asignando países a sesiones (seed=42 para reproducibilidad)...")
    # Asignar países aleatoriamente pero reproducible
    np.random.seed(RANDOM_SEED)
    paises_unicos = dim_geografia['Pais'].unique()
    df_ai['Country'] = np.random.choice(paises_unicos, size=len(df_ai))

    # Preparar datos para join
    df_ai['Fecha'] = pd.to_datetime(df_ai['SessionDate']).dt.date
    df_ai['Anio'] = pd.to_datetime(df_ai['SessionDate']).dt.year
    df_ai['idTiempo'] = pd.to_datetime(df_ai['SessionDate']).dt.strftime('%Y%m%d').astype(int)

    # Renombrar columnas para match
    df_ai_renamed = df_ai.rename(columns={
        'Country': 'Pais',
        'StudentLevel': 'Nivel_Academico',
        'Discipline': 'Disciplina'
    })

    print("      → Uniendo con dimensiones...")
    # JOIN con geografía (considerando País Y Año para obtener nivel de escasez correcto)
    # Para años fuera del rango de dim_geografia, usar el año más cercano disponible

    # Obtener año mínimo y máximo en dim_geografia
    anio_min = dim_geografia['Anio'].min()
    anio_max = dim_geografia['Anio'].max()

    # Ajustar años de sesiones al rango disponible
    df_ai_renamed['Anio_Ajustado'] = df_ai_renamed['Anio'].clip(anio_min, anio_max)

    df_merged = df_ai_renamed.merge(
        dim_geografia[['idGeografia', 'Pais', 'Anio', 'Nivel_Escasez_Agua']],
        left_on=['Pais', 'Anio_Ajustado'],
        right_on=['Pais', 'Anio'],
        how='left'
    )

    # Remover columna temporal
    df_merged = df_merged.drop(columns=['Anio_Ajustado', 'Anio_y'])
    df_merged = df_merged.rename(columns={'Anio_x': 'Anio'})

    # JOIN con estudiante
    df_merged = df_merged.merge(
        dim_estudiante[['idEstudiante', 'Nivel_Academico', 'Disciplina']],
        on=['Nivel_Academico', 'Disciplina'],
        how='left'
    )

    # Verificar si hay NULLs en las claves
    nulls = df_merged[['idGeografia', 'idEstudiante', 'idTiempo']].isnull().sum().sum()
    if nulls > 0:
        print(f"      ⚠️ Advertencia: {nulls} registros con claves nulas, serán removidos")
        df_merged = df_merged.dropna(subset=['idGeografia', 'idEstudiante', 'idTiempo'])

    print("      → Calculando indicadores...")
    # Calcular Huella Hídrica
    df_merged['Huella_Hidrica'] = df_merged['TotalPrompts'] * WATER_CONSUMPTION_FACTOR

    print("      → Agregando datos por (País, Estudiante, Fecha)...")
    # Agrupar por las claves de la tabla de hechos
    hechos = df_merged.groupby(['idGeografia', 'idEstudiante', 'idTiempo']).agg({
        'TotalPrompts': 'sum',
        'SessionLengthMin': 'sum',
        'SessionID': 'count',  # Número de sesiones
        'Huella_Hidrica': 'sum'
    }).reset_index()

    # Renombrar columnas finales
    hechos.rename(columns={
        'TotalPrompts': 'Total_Prompts',
        'SessionLengthMin': 'Duracion_Total_Sesiones',
        'SessionID': 'Numero_Sesiones'
    }, inplace=True)

    # Reordenar columnas
    hechos = hechos[['idGeografia', 'idEstudiante', 'idTiempo',
                     'Huella_Hidrica', 'Total_Prompts',
                     'Duracion_Total_Sesiones', 'Numero_Sesiones']]

    print(f"      → Cargando {len(hechos):,} registros agregados...")
    # Cargar a BD
    hechos.to_sql('HECHOS_HUELLA_HIDRICA_IA', conn, if_exists='append', index=False)

    print(f"      ✓ {len(hechos):,} hechos cargados exitosamente")
    print(f"      ✓ Huella hídrica total: {hechos['Huella_Hidrica'].sum():,.2f} litros")
    print(f"      ✓ Total de prompts: {hechos['Total_Prompts'].sum():,}")
    print(f"      ✓ Total de sesiones: {hechos['Numero_Sesiones'].sum():,}")

    return hechos

# ============================================================================
# MAIN: EJECUTAR CARGA COMPLETA
# ============================================================================

def main():
    """Ejecuta el proceso completo de carga inicial"""
    try:
        # PASO 0: Crear estructura
        crear_estructura_database()

        # PASO 1: Extraer
        df_ai, df_water = extraer_datos()

        # PASO 2: Transformar y limpiar
        df_ai_clean, df_water_clean = limpiar_datos(df_ai, df_water)

        # Conectar a base de datos
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON;")

        print("\n[PASO 3] CARGA DE DIMENSIONES")
        print("-" * 80)

        # PASO 3: Cargar dimensiones
        dim_geografia = cargar_dim_geografia(df_water_clean, conn)
        dim_estudiante = cargar_dim_estudiante(df_ai_clean, conn)
        dim_tiempo = cargar_dim_tiempo(df_ai_clean, conn)

        print("\n[PASO 4] CARGA DE HECHOS")
        print("-" * 80)

        # PASO 4: Cargar hechos
        hechos = cargar_hechos(df_ai_clean, conn)

        # Commit y cerrar
        conn.commit()
        conn.close()

        # Resumen final
        print("\n" + "="*80)
        print(" " * 25 + "✅ CARGA INICIAL COMPLETADA")
        print("="*80)
        print("\nRESUMEN:")
        print(f"   • Dimensiones cargadas: 3")
        print(f"     - DIM_GEOGRAFIA: {len(dim_geografia):,} países")
        print(f"     - DIM_ESTUDIANTE: {len(dim_estudiante):,} combinaciones")
        print(f"     - DIM_TIEMPO: {len(dim_tiempo):,} fechas")
        print(f"   • Hechos cargados: {len(hechos):,} registros agregados")
        print(f"   • Base de datos: {DB_FILE}")
        print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nPRÓXIMOS PASOS:")
        print("   1. Validar datos con: sqlite3 datawarehouse.db")
        print("   2. Ejecutar consultas: 3_modelo_logico/sql/03_consultas_ejemplo.sql")
        print("   3. Conectar Power BI al archivo datawarehouse.db")
        print("="*80)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR EN LA CARGA: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
