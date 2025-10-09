"""
Configuración del ETL para el Data Warehouse de Uso de IA y Consumo de Agua
"""

import os

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR

# Archivos de entrada
AI_USAGE_FILE = os.path.join(DATA_DIR, 'archive (2)', 'ai_assistant_usage_student_life.csv')
WATER_CONSUMPTION_FILE = os.path.join(DATA_DIR, 'archive (3)', 'cleaned_global_water_consumption.csv')

# Directorio de salida
OUTPUT_DIR = os.path.join(BASE_DIR, 'data_warehouse')
DIMENSIONS_DIR = os.path.join(OUTPUT_DIR, 'dimensions')
FACTS_DIR = os.path.join(OUTPUT_DIR, 'facts')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
VISUALIZATIONS_DIR = os.path.join(OUTPUT_DIR, 'visualizations')

# Crear directorios si no existen
for directory in [OUTPUT_DIR, DIMENSIONS_DIR, FACTS_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Parámetros del modelo
WATER_CONSUMPTION_FACTOR = 0.5  # Litros por prompt (hipotético)

# Configuración de visualizaciones
FIGURE_SIZE = (12, 6)
DPI = 100
PLOT_STYLE = 'seaborn-v0_8-darkgrid'

# Nivel de logging
LOG_LEVEL = 'INFO'

# Formatos de salida
OUTPUT_FORMAT = 'csv'  # 'csv' o 'parquet'

# Países de interés (vacío = todos)
COUNTRIES_FILTER = []

# Rango de años
YEAR_MIN = 2000
YEAR_MAX = 2025
