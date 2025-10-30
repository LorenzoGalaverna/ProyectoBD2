# FASE 1: ANÁLISIS DE REQUERIMIENTOS

**Proyecto:** Data Warehouse - Huella Hídrica del Uso de IA en Estudiantes
**Metodología:** Hefesto
**Fecha:** Octubre 2025

---

## Objetivo General

Analizar el **impacto ambiental** (específicamente la huella hídrica) del uso de asistentes de IA por parte de estudiantes a nivel global. El objetivo es cruzar datos de uso académico de la IA con datos de consumo y escasez de agua por país para generar conciencia y permitir un análisis estratégico.

---

## a) Identificar Preguntas de Negocio

Se formulan las siguientes preguntas para guiar el análisis:

### Pregunta 1: Consumo Total por Dimensiones
**¿Cuál es el consumo total de agua estimado derivado del uso de asistentes de IA por parte de estudiantes, desglosado por país, disciplina académica y a lo largo del tiempo?**

- **Qué mide:** Consumo de agua en litros
- **Cómo se analiza:** Por país, por disciplina, por tiempo
- **Por qué:** Identificar dónde y cuándo se concentra el mayor impacto hídrico

### Pregunta 2: Comparación Huella vs Escasez
**¿Cómo se compara la huella hídrica de la IA con el nivel de escasez de agua en cada país?**

- **Qué mide:** Relación entre consumo estimado y disponibilidad de agua
- **Cómo se analiza:** Por país y nivel de escasez
- **Por qué:** Identificar zonas críticas donde el uso de IA agrava problemas de agua

### Pregunta 3: Impacto por Tipo de Tarea
**¿Cuál es el promedio de prompts y la duración de las sesiones por tipo de tarea académica, y cuál es su impacto hídrico correspondiente?**

- **Qué mide:** Prompts promedio, duración, consumo de agua
- **Cómo se analiza:** Por disciplina académica
- **Por qué:** Identificar qué áreas académicas tienen mayor impacto

### Pregunta 4: Correlación con Nivel Académico
**¿Existe una correlación entre el nivel académico del estudiante (pregrado, posgrado) y el consumo de agua estimado por el uso de IA?**

- **Qué mide:** Consumo de agua por nivel académico
- **Cómo se analiza:** Por nivel de estudiante
- **Por qué:** Entender patrones de uso entre diferentes niveles educativos

---

## b) Identificar Indicadores y Perspectivas

### Indicadores (Lo que se quiere medir)

| # | Indicador | Descripción | Unidad |
|---|-----------|-------------|--------|
| 1 | **Consumo de Agua Estimado** | Huella hídrica total del uso de IA | Litros |
| 2 | **Cantidad Total de Prompts** | Total de consultas enviadas a la IA | Cantidad |
| 3 | **Duración Total de las Sesiones** | Tiempo total de uso de la IA | Minutos |
| 4 | **Número de Sesiones de IA** | Cantidad de sesiones realizadas | Cantidad |

### Perspectivas (Cómo se quiere analizar)

| # | Perspectiva | Atributos | Fuente |
|---|-------------|-----------|--------|
| 1 | **Geografía** | País, Nivel de Escasez de Agua | Global Water Consumption Dataset |
| 2 | **Estudiante** | Nivel Académico, Disciplina | AI Assistant Usage Dataset |
| 3 | **Tiempo** | Año, Trimestre, Mes | SessionDate (AI Usage Dataset) |
| 4 | **Tipo de Tarea** | Categoría de actividad académica | TaskType (AI Usage Dataset) |

---

## c) Modelo Conceptual

El modelo conceptual representa la relación entre perspectivas e indicadores:

```
┌─────────────────────────────────────────────────────────────────┐
│                   ÁREA DE ESTUDIO                               │
│         HUELLA HÍDRICA DEL USO ACADÉMICO DE IA                  │
└─────────────────────────────────────────────────────────────────┘

PERSPECTIVAS                                          INDICADORES
─────────────                                         ────────────

┌─────────────────┐                                  ┌──────────────────────────┐
│  GEOGRAFÍA      │                                  │ Consumo de Agua Estimado │
│  - País         │─────┐                           │ (Litros)                 │
│  - Nivel Escasez│     │                           └──────────────────────────┘
└─────────────────┘     │
                        │                            ┌──────────────────────────┐
┌─────────────────┐     │    ┌──────────────┐      │ Cantidad Total Prompts   │
│  ESTUDIANTE     │     ├───►│   ANÁLISIS   │◄─────│ (Cantidad)               │
│  - Nivel Académ.│     │    │   HUELLA     │      └──────────────────────────┘
│  - Disciplina   │     │    │   HÍDRICA    │
└─────────────────┘     │    └──────────────┘       ┌──────────────────────────┐
                        │                            │ Duración Total Sesiones  │
┌─────────────────┐     │                           │ (Minutos)                │
│  TIEMPO         │─────┘                           └──────────────────────────┘
│  - Año          │
│  - Trimestre    │                                  ┌──────────────────────────┐
│  - Mes          │                                  │ Número de Sesiones IA    │
└─────────────────┘                                  │ (Cantidad)               │
                                                     └──────────────────────────┘
```

---

## Fuentes de Datos

### Dataset 1: AI Assistant Usage in Student Life
- **Origen:** Kaggle
- **URL:** https://www.kaggle.com/datasets/ayeshasal89/ai-assistant-usage-in-student-life-synthetic
- **Registros:** ~10,000 sesiones de estudiantes
- **Campos clave:**
  - SessionID, SessionDate, TotalPrompts
  - SessionLengthMin, StudentLevel, Discipline, TaskType

### Dataset 2: Global Water Consumption Dataset
- **Origen:** Kaggle
- **URL:** https://www.kaggle.com/datasets/atharvasoundankar/global-water-consumption-dataset-2000-2024
- **Registros:** ~500 registros de consumo por país
- **Campos clave:**
  - Country, Year, Water Scarcity Level

---

## Conclusiones de la Fase 1

✅ Se identificaron **4 preguntas de negocio** específicas
✅ Se definieron **4 indicadores** medibles (métricas)
✅ Se establecieron **3 perspectivas** principales de análisis
✅ Se creó el **modelo conceptual** que relaciona perspectivas e indicadores
✅ Se validaron las **fuentes de datos** necesarias

**Siguiente fase:** Análisis de OLTP para definir cálculos y correspondencias
