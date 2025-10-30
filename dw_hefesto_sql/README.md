# Data Warehouse - Huella Hídrica del Uso de IA en Estudiantes

**Metodología:** Hefesto
**Base de Datos:** SQLite
**Visualización:** Power BI
**Fecha:** Octubre 2025

---

## 📋 Descripción del Proyecto

Este proyecto implementa un **Data Warehouse** completo siguiendo la **metodología Hefesto** para analizar el impacto ambiental (específicamente la huella hídrica) del uso de asistentes de IA por parte de estudiantes a nivel global.

### Objetivos

- Analizar el consumo de agua estimado derivado del uso de IA académica
- Cruzar datos de uso de IA con niveles de escasez de agua por país
- Generar conciencia sobre el impacto ambiental de la tecnología
- Proporcionar análisis estratégico para toma de decisiones

---

## 🗂️ Estructura del Proyecto

```
dw_hefesto_sql/
│
├── 1_analisis_requerimientos/
│   └── FASE1_ANALISIS_REQUERIMIENTOS.md    # Preguntas de negocio, indicadores, modelo conceptual
│
├── 2_analisis_oltp/
│   └── FASE2_ANALISIS_OLTP.md              # Cálculos, correspondencias, granularidad
│
├── 3_modelo_logico/
│   ├── FASE3_MODELO_LOGICO.md              # Diseño del esquema en estrella
│   └── sql/
│       ├── 01_crear_dimensiones.sql        # CREATE TABLE para dimensiones
│       ├── 02_crear_hechos.sql             # CREATE TABLE para hechos
│       └── 03_consultas_ejemplo.sql        # Queries para análisis y Power BI
│
├── 4_integracion_datos/
│   └── scripts/
│       ├── carga_inicial.py                # ETL: Carga inicial completa
│       └── actualizacion_incremental.py    # ETL: Actualizaciones periódicas
│
├── database/
│   └── datawarehouse.db                    # Base de datos SQLite (generada)
│
└── README.md                               # Este archivo
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Python 3.8+**
- **SQLite** (incluido en Python)
- **Power BI Desktop** (para visualizaciones)

### Instalación

1. **Clonar o ubicarse en el directorio del proyecto:**

```bash
cd /Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql
```

2. **Instalar dependencias de Python:**

```bash
pip install pandas numpy
```

3. **Verificar que existen los archivos fuente CSV:**

```
ProyectoBD2/
├── archive (2)/
│   └── ai_assistant_usage_student_life.csv
└── archive (3)/
    └── cleaned_global_water_consumption.csv
```

---

## 📊 Modelo del Data Warehouse

### Esquema en Estrella

```
          DIM_GEOGRAFIA
                │
                │
    ┌───────────┼───────────┐
    │           │           │
DIM_ESTUDIANTE ─┤  HECHOS   ├─ DIM_TIEMPO
                │   (FACT)  │
                └───────────┘
```

### Tablas

| Tabla | Tipo | Registros | Descripción |
|-------|------|-----------|-------------|
| **DIM_GEOGRAFIA** | Dimensión | ~20 | Países y nivel de escasez de agua |
| **DIM_ESTUDIANTE** | Dimensión | ~21 | Nivel académico + disciplina |
| **DIM_TIEMPO** | Dimensión | ~366 | Fechas con jerarquía temporal |
| **HECHOS_HUELLA_HIDRICA_IA** | Hechos | ~10,000 | Métricas agregadas |

### Indicadores (Métricas)

1. **Huella_Hidrica**: Consumo de agua estimado en litros (TotalPrompts × 0.5 L)
2. **Total_Prompts**: Cantidad total de consultas a la IA
3. **Duracion_Total_Sesiones**: Tiempo total de uso en minutos
4. **Numero_Sesiones**: Conteo de sesiones de IA

---

## ⚙️ Ejecución del ETL

### Paso 1: Carga Inicial

Ejecuta el script de carga inicial para poblar el Data Warehouse por primera vez:

```bash
cd 4_integracion_datos/scripts
python carga_inicial.py
```

**¿Qué hace este script?**
1. Crea la base de datos SQLite (`database/datawarehouse.db`)
2. Crea las tablas de dimensiones y hechos
3. Extrae datos de los CSVs
4. Limpia y transforma los datos
5. Carga las 3 dimensiones
6. Carga la tabla de hechos agregada

**Salida esperada:**
```
================================================================================
                    CARGA INICIAL DEL DATA WAREHOUSE
               Huella Hídrica del Uso de IA en Estudiantes
================================================================================

[PASO 0] CREANDO ESTRUCTURA DE BASE DE DATOS
   ✓ Base de datos creada

[PASO 1] EXTRACCIÓN DE DATOS
   ✓ AI Usage: 10,000 registros
   ✓ Water Consumption: 500 registros

[PASO 2] TRANSFORMACIÓN Y LIMPIEZA
   ✓ Datos limpios

[PASO 3] CARGA DE DIMENSIONES
   ✓ DIM_GEOGRAFIA: 20 países
   ✓ DIM_ESTUDIANTE: 21 combinaciones
   ✓ DIM_TIEMPO: 366 fechas

[PASO 4] CARGA DE HECHOS
   ✓ 10,000 hechos cargados
   ✓ Huella hídrica total: 28,037.50 litros

✅ CARGA INICIAL COMPLETADA
```

### Paso 2: Actualización Incremental (Opcional)

Para actualizar el DW con datos nuevos (ventana de 30 días):

```bash
python actualizacion_incremental.py
```

**Política de actualización:**
- Frecuencia: Diaria
- Ventana: Últimos 30 días
- Dimensiones: Carga total (son pequeñas)
- Hechos: Reemplazo de ventana temporal

---

## 🔍 Consultas y Análisis

### Validar la Carga

Verifica que los datos se cargaron correctamente:

```bash
sqlite3 database/datawarehouse.db
```

```sql
-- Ver totales por tabla
SELECT COUNT(*) AS Total FROM DIM_GEOGRAFIA;    -- Debe ser ~20
SELECT COUNT(*) AS Total FROM DIM_ESTUDIANTE;   -- Debe ser ~21
SELECT COUNT(*) AS Total FROM DIM_TIEMPO;       -- Debe ser ~366
SELECT COUNT(*) AS Total FROM HECHOS_HUELLA_HIDRICA_IA;  -- Debe ser ~10,000

-- Ver resumen de hechos
SELECT * FROM V_RESUMEN_HECHOS;
```

### Consultas de Análisis

Todas las consultas SQL están documentadas en:
```
3_modelo_logico/sql/03_consultas_ejemplo.sql
```

**Ejemplos de consultas incluidas:**

1. **Consumo de agua por país (Top 10)**
2. **Uso por disciplina académica**
3. **Tendencia temporal mensual y trimestral**
4. **Huella hídrica vs escasez de agua**
5. **Matriz disciplina × nivel académico**
6. **KPIs generales del DW**

---

## 📈 Conectar con Power BI

### Opción 1: Importar Consulta Maestra (Recomendado)

1. **Abrir Power BI Desktop**
2. **Obtener datos → Base de datos → SQLite**
3. **Seleccionar archivo:**
   ```
   /Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db
   ```
4. **Seleccionar "Consulta SQL avanzada"**
5. **Copiar y pegar la "CONSULTA MAESTRA"** de `03_consultas_ejemplo.sql`
6. **Cargar datos**

### Opción 2: Importar Tablas Individuales

1. **Obtener datos → SQLite**
2. **Seleccionar todas las tablas:**
   - DIM_GEOGRAFIA
   - DIM_ESTUDIANTE
   - DIM_TIEMPO
   - HECHOS_HUELLA_HIDRICA_IA
3. **Cargar**
4. **Power BI creará las relaciones automáticamente**

### Configurar Relaciones en Power BI

Si importas tablas individuales, verifica las relaciones:

| Desde | Hasta | Campo | Cardinalidad |
|-------|-------|-------|--------------|
| DIM_GEOGRAFIA | HECHOS | idGeografia | 1:* |
| DIM_ESTUDIANTE | HECHOS | idEstudiante | 1:* |
| DIM_TIEMPO | HECHOS | idTiempo | 1:* |

### Medidas DAX Sugeridas

```dax
// KPIs principales
Total Huella Hídrica = SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica])

Total Sesiones = SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])

Total Prompts = SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts])

Litros por Sesión =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )

Prompts por Sesión =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )

Duración Promedio =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Duracion_Total_Sesiones]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )
```

### Visualizaciones Sugeridas

1. **Gráfico de Barras**: Top 10 países por consumo de agua
2. **Gráfico de Líneas**: Tendencia temporal mensual
3. **Matriz**: Disciplina × Nivel Académico (heatmap)
4. **Gráfico de Barras Agrupadas**: Consumo vs Escasez por país
5. **Tarjetas (Cards)**: KPIs principales (Huella Total, Sesiones, Prompts)
6. **Gráfico de Anillos**: Distribución por nivel académico
7. **Tabla**: Detalle de top combinaciones país + disciplina

---

## 📚 Documentación de las Fases Hefesto

Cada fase de la metodología Hefesto está completamente documentada:

### Fase 1: Análisis de Requerimientos
📄 `1_analisis_requerimientos/FASE1_ANALISIS_REQUERIMIENTOS.md`

- Preguntas de negocio
- Identificación de indicadores y perspectivas
- Modelo conceptual

### Fase 2: Análisis de OLTP
📄 `2_analisis_oltp/FASE2_ANALISIS_OLTP.md`

- Cálculo de indicadores (fórmulas)
- Correspondencias con fuentes de datos
- Nivel de granularidad
- Modelo conceptual ampliado

### Fase 3: Modelo Lógico
📄 `3_modelo_logico/FASE3_MODELO_LOGICO.md`

- Diseño del esquema en estrella
- Definición de tablas de dimensiones
- Definición de tabla de hechos
- Diagramas y relaciones
- Scripts SQL completos

### Fase 4: Integración de Datos
📄 Scripts Python en `4_integracion_datos/scripts/`

- Proceso ETL de carga inicial
- Proceso ETL de actualización incremental
- Políticas de actualización

---

## 🔧 Notas Técnicas

### Factor de Consumo de Agua

El proyecto utiliza un **factor hipotético de 0.5 litros/prompt** que representa:
- Energía consumida por el procesamiento de IA
- Agua usada en refrigeración de centros de datos
- Basado en estimaciones de huella de carbono de modelos LLM

⚠️ **Nota:** Este factor es educativo y puede ajustarse según estudios reales.

### Asignación Geográfica

El dataset de AI Usage **NO incluye información geográfica**. Por tanto:
- Se asignan países **aleatoriamente** a las sesiones
- La asignación es **reproducible** (seed=42)
- Permite relacionar ambas fuentes de datos
- Los análisis geográficos son **ilustrativos**

### Optimizaciones

- **Índices creados** en todas las FK y campos de búsqueda frecuente
- **Vistas materializadas** (V_RESUMEN_HECHOS, V_HECHOS_COMPLETO)
- **Agregación previa** en la tabla de hechos por (país, estudiante, fecha)
- **Integridad referencial** con FOREIGN KEYS habilitadas

---

## 🐛 Solución de Problemas

### Error: "Archivos CSV no encontrados"

**Solución:** Verifica que los archivos están en las ubicaciones correctas:
```
ProyectoBD2/archive (2)/ai_assistant_usage_student_life.csv
ProyectoBD2/archive (3)/cleaned_global_water_consumption.csv
```

### Error: "Base de datos bloqueada"

**Solución:** Cierra cualquier conexión abierta:
```bash
# Cerrar sqlite3 si está abierto
.quit

# O eliminar locks
rm database/datawarehouse.db-shm
rm database/datawarehouse.db-wal
```

### Error: "Foreign key constraint failed"

**Solución:** Ejecuta la carga inicial completa desde cero:
```bash
rm database/datawarehouse.db
python carga_inicial.py
```

### Power BI no muestra relaciones

**Solución:** Importa tablas individuales y crea relaciones manualmente en vista de Modelo.

---

## 📊 Resultados Esperados

### KPIs Globales

- **Huella Hídrica Total:** ~28,037.5 litros
- **Total de Prompts:** ~56,075
- **Total de Sesiones:** ~10,000
- **Duración Total:** ~198,464.67 minutos
- **Promedio Litros/Sesión:** ~2.80 L
- **Promedio Prompts/Sesión:** ~5.61

### Dimensiones

- **Países:** 20
- **Combinaciones Estudiante:** 21 (3 niveles × 7 disciplinas)
- **Fechas:** 366 (jun-2024 a jun-2025)

---

## 👥 Créditos

**Proyecto Académico:** Base de Datos 2 - UCC
**Metodología:** Hefesto
**Fuentes de Datos:**
- [AI Assistant Usage in Student Life (Kaggle)](https://www.kaggle.com/datasets/ayeshasal89/ai-assistant-usage-in-student-life-synthetic)
- [Global Water Consumption Dataset (Kaggle)](https://www.kaggle.com/datasets/atharvasoundankar/global-water-consumption-dataset-2000-2024)

---

## 📝 Licencia

Este proyecto es de uso académico y educativo.

---

## 🚀 Próximos Pasos

1. ✅ **Ejecutar carga inicial:** `python carga_inicial.py`
2. ✅ **Validar datos:** `sqlite3 database/datawarehouse.db`
3. ✅ **Ejecutar consultas:** Usar `03_consultas_ejemplo.sql`
4. 📊 **Crear dashboard en Power BI** con visualizaciones sugeridas
5. 📈 **Programar actualización incremental** (cron job o task scheduler)
6. 📄 **Documentar hallazgos** en informe final

---

**¿Preguntas o problemas?** Consulta la documentación en cada carpeta de fase o revisa los comentarios en los scripts SQL y Python.
