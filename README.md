# ETL - Data Warehouse: Uso de IA y Consumo de Agua

Este proyecto implementa un proceso ETL (Extract, Transform, Load) completo en Python para crear un Data Warehouse que analiza el uso de asistentes de IA en la vida estudiantil y su impacto en el consumo de agua.

## 📋 Descripción

El Data Warehouse integra dos fuentes de datos:
- **AI Assistant Usage in Student Life**: Datos de sesiones de uso de asistentes de IA por estudiantes
- **Global Water Consumption Dataset**: Datos de consumo de agua a nivel global

El ETL crea un modelo dimensional (esquema estrella) con:
- 3 Dimensiones (Tiempo, Geografía, Estudiante)
- 1 Tabla de Hechos con 4 indicadores clave

## 🚀 Requisitos

### Librerías necesarias
```bash
pip install pandas numpy matplotlib
```

## 📁 Estructura del Proyecto

```
ProyectoBD2/
├── config.py                 # Configuración del ETL
├── extract.py                # Módulo de extracción (Extract)
├── transform.py              # Módulo de transformación (Transform)
├── load.py                   # Módulo de carga (Load)
├── visualize.py              # Módulo de visualización
├── run_etl.py                # Script principal de ejecución
├── ModeloConceptual.md       # Documentación del modelo conceptual
├── archive (2)/              # Datos de entrada
│   └── ai_assistant_usage_student_life.csv
├── archive (3)/
│   └── cleaned_global_water_consumption.csv
└── data_warehouse/           # Salidas generadas (se crea automáticamente)
    ├── dimensions/           # Tablas dimensionales
    ├── facts/                # Tabla de hechos
    ├── reports/              # Reportes en texto
    └── visualizations/       # Gráficos generados
```

## 🎯 Indicadores Calculados

1. **Consumo de Agua Estimado**: `TotalPrompts × 0.5 L/prompt`
2. **Cantidad Total de Prompts**: Suma de todos los prompts
3. **Duración Total de las Sesiones**: Suma de minutos de sesión
4. **Número de Sesiones de IA**: Conteo de sesiones únicas

## 📊 Modelo Dimensional

### Dimensiones
- **DIM_TIEMPO**: Fecha, Año, Trimestre, Mes, Semana, Día de Semana
- **DIM_GEOGRAFIA**: País, Nivel de Escasez de Agua
- **DIM_ESTUDIANTE**: Nivel Académico, Disciplina

### Tabla de Hechos
- **FACT_USO_IA_AGUA**: Contiene los 4 indicadores y claves foráneas a las dimensiones

## 🏃‍♂️ Ejecución

### Opción 1: Ejecutar ETL completo
```bash
python run_etl.py
```

Este comando ejecuta:
1. ✅ **Extracción** de datos de los CSV
2. ✅ **Transformación** y limpieza de datos
3. ✅ **Creación** de dimensiones y tabla de hechos
4. ✅ **Carga** de datos en archivos CSV
5. ✅ **Generación** de 8 visualizaciones
6. ✅ **Reporte** resumen en texto

### Opción 2: Ejecutar módulos individualmente

```bash
# Solo extracción
python extract.py

# Solo transformación (requiere haber ejecutado extract)
python transform.py

# Solo carga (requiere haber ejecutado transform)
python load.py

# Solo visualización (requiere haber ejecutado transform)
python visualize.py
```

## 📈 Visualizaciones Generadas

El ETL genera automáticamente 8 gráficos:

1. **01_consumo_agua_por_pais.png** - Top 10 países por consumo de agua estimado
2. **02_uso_por_disciplina.png** - Uso de IA por disciplina académica
3. **03_tendencia_temporal.png** - Tendencia mensual de uso y consumo
4. **04_distribucion_nivel_academico.png** - Distribución por nivel académico
5. **05_escasez_vs_consumo.png** - Consumo vs nivel de escasez hídrica
6. **06_duracion_promedio_trimestre.png** - Duración promedio por trimestre
7. **07_matriz_disciplina_nivel.png** - Heatmap de prompts por disciplina y nivel
8. **08_dashboard_resumen.png** - Dashboard con KPIs principales

## ⚙️ Configuración

Puedes modificar los parámetros en `config.py`:

```python
# Factor de consumo de agua (litros por prompt)
WATER_CONSUMPTION_FACTOR = 0.5

# Formato de salida ('csv' o 'parquet')
OUTPUT_FORMAT = 'csv'

# Tamaño de gráficos
FIGURE_SIZE = (12, 6)
DPI = 100
```

## 📄 Salidas del ETL

### Archivos de Dimensiones (CSV)
- `dim_tiempo.csv` - Dimensión temporal
- `dim_geografia.csv` - Dimensión geográfica
- `dim_estudiante.csv` - Dimensión de estudiante

### Archivo de Hechos (CSV)
- `fact_uso_ia_agua.csv` - Tabla de hechos con todos los indicadores

### Reportes
- `data_warehouse_summary.txt` - Resumen estadístico del DW

### Visualizaciones
- 8 archivos PNG con gráficos de análisis

## 🔍 Análisis Soportados

El Data Warehouse permite realizar análisis como:

- ✅ Consumo de agua por país y región
- ✅ Tendencias temporales de uso de IA
- ✅ Comparación entre niveles académicos
- ✅ Análisis por disciplina de estudio
- ✅ Correlación entre escasez hídrica y uso de IA
- ✅ Patrones de uso por trimestre/mes
- ✅ Duración promedio de sesiones

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**
- **Pandas**: Manipulación y transformación de datos
- **NumPy**: Operaciones numéricas y cálculos
- **Matplotlib**: Generación de visualizaciones

## 📝 Notas

- El dataset de AI Usage no incluye información geográfica, por lo que se asignan países de forma aleatoria (pero reproducible con seed=42) basándose en los países disponibles en el dataset de consumo de agua.
- El factor de consumo de agua (0.5 L/prompt) es hipotético y representa el agua utilizada en la refrigeración de centros de datos.

## 👥 Autor

Proyecto de Base de Datos 2 - UCC

## 📅 Fecha

Octubre 2025
