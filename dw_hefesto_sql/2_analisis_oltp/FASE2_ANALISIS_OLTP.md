# FASE 2: ANÁLISIS DE LOS OLTP

**Proyecto:** Data Warehouse - Huella Hídrica del Uso de IA en Estudiantes
**Metodología:** Hefesto
**Fecha:** Octubre 2025

---

## Objetivo de esta Fase

Establecer la relación entre los indicadores conceptuales y los datos reales disponibles en las fuentes (OLTP), definiendo:
- **Cómo se calculan** los indicadores (fórmulas y funciones)
- **De dónde provienen** los datos (correspondencias)
- **Qué nivel de detalle** se usará (granularidad)

---

## a) Definir el Cálculo de los Indicadores

### Indicador 1: Consumo de Agua Estimado (Huella Hídrica)

**Fórmula:**
```
Consumo_Agua_Estimado = Total_Prompts × Factor_Consumo_Litros_Por_Prompt
```

**Función de Sumarización:** `SUM`

**Detalles:**
- **Campo base:** `TotalPrompts` (del dataset AI Usage)
- **Factor de conversión:** `0.5 litros/prompt` (hipotético)
- **Justificación del factor:** Representa el agua usada en refrigeración de centros de datos por cada consulta procesada
- **Unidad final:** Litros

**Ejemplo de cálculo:**
```
Si una sesión tiene 10 prompts:
Consumo = 10 × 0.5 = 5 litros
```

---

### Indicador 2: Cantidad Total de Prompts

**Fórmula:**
```
Total_Prompts = SUM(TotalPrompts)
```

**Función de Sumarización:** `SUM`

**Detalles:**
- **Campo base:** `TotalPrompts` (del dataset AI Usage)
- **Descripción:** Suma de todas las consultas enviadas al asistente de IA
- **Unidad:** Cantidad (entero)

---

### Indicador 3: Duración Total de las Sesiones

**Fórmula:**
```
Duracion_Total_Sesiones = SUM(SessionLengthMin)
```

**Función de Sumarización:** `SUM`

**Detalles:**
- **Campo base:** `SessionLengthMin` (del dataset AI Usage)
- **Descripción:** Tiempo total de interacción con la IA
- **Unidad:** Minutos

---

### Indicador 4: Número de Sesiones de IA

**Fórmula:**
```
Numero_Sesiones = COUNT(SessionID)
```

**Función de Sumarización:** `COUNT`

**Detalles:**
- **Campo base:** `SessionID` (del dataset AI Usage)
- **Descripción:** Conteo de sesiones únicas de interacción
- **Unidad:** Cantidad (entero)

---

## b) Establecer Correspondencias

Conectamos los elementos conceptuales con los campos reales en las fuentes de datos.

### Correspondencias de Perspectivas

| Perspectiva Conceptual | Campo en OLTP | Fuente de Datos | Transformación |
|------------------------|---------------|-----------------|----------------|
| **Geografía → País** | `Country` | AI Usage + Water Consumption | Asignación aleatoria reproducible (seed) |
| **Geografía → Nivel Escasez** | `Water Scarcity Level` | Water Consumption | Directa |
| **Estudiante → Nivel Académico** | `StudentLevel` | AI Usage | Directa |
| **Estudiante → Disciplina** | `Discipline` | AI Usage | Directa |
| **Tiempo → Año** | `YEAR(SessionDate)` | AI Usage | Extracción de componente temporal |
| **Tiempo → Trimestre** | `QUARTER(SessionDate)` | AI Usage | Cálculo: (Mes-1) DIV 3 + 1 |
| **Tiempo → Mes** | `MONTH(SessionDate)` | AI Usage | Extracción de componente temporal |

### Correspondencias de Indicadores

| Indicador | Campo en OLTP | Fuente | Cálculo |
|-----------|---------------|--------|---------|
| **Consumo Agua Estimado** | `TotalPrompts` | AI Usage | `TotalPrompts × 0.5` |
| **Cantidad Total Prompts** | `TotalPrompts` | AI Usage | `SUM(TotalPrompts)` |
| **Duración Total Sesiones** | `SessionLengthMin` | AI Usage | `SUM(SessionLengthMin)` |
| **Número Sesiones** | `SessionID` | AI Usage | `COUNT(DISTINCT SessionID)` |

---

## c) Nivel de Granularidad

Se seleccionan los campos específicos para cada perspectiva según los requerimientos de análisis.

### Perspectiva GEOGRAFÍA

**Campos seleccionados:**

| Campo | Justificación | Origen |
|-------|---------------|--------|
| **País** (`Country`) | Identificar la ubicación geográfica del consumo | Water Consumption Dataset |
| **Nivel de Escasez de Agua** (`Water Scarcity Level`) | Contextualizar el consumo con disponibilidad hídrica | Water Consumption Dataset |

**Granularidad:** A nivel de **país**

**Nota importante:** El dataset AI Usage NO contiene información geográfica. Se asignará un país aleatorio (pero reproducible con seed=42) a cada sesión, basándose en la distribución de países del dataset de consumo de agua.

---

### Perspectiva ESTUDIANTE

**Campos seleccionados:**

| Campo | Justificación | Origen |
|-------|---------------|--------|
| **Nivel Académico** (`StudentLevel`) | Comparar uso entre pregrado, posgrado, etc. | AI Usage Dataset |
| **Disciplina** (`Discipline`) | Analizar diferencias entre áreas de estudio | AI Usage Dataset |

**Granularidad:** Combinación de **nivel académico + disciplina**

**Valores esperados:**
- StudentLevel: `Undergraduate`, `Graduate`, `High School`
- Discipline: `Computer Science`, `Engineering`, `Business`, `Math`, `Psychology`, `Biology`, `History`

---

### Perspectiva TIEMPO

**Campos seleccionados:**

| Campo | Justificación | Origen |
|-------|---------------|--------|
| **Año** | Análisis de tendencias anuales | Derivado de `SessionDate` |
| **Trimestre** | Análisis estacional/trimestral | Derivado de `SessionDate` |
| **Mes** | Granularidad mensual para patrones detallados | Derivado de `SessionDate` |

**Granularidad:** A nivel de **mes** (la más detallada)

**Rango temporal esperado:**
- Desde: Junio 2024
- Hasta: Junio 2025
- Total: ~12 meses

**Formato de clave:** `idTiempo = YYYYMMDD` (formato numérico para eficiencia)

Ejemplo: `20241015` = 15 de octubre de 2024

---

## d) Modelo Conceptual Ampliado

Modelo enriquecido con las correspondencias, fórmulas y granularidades definidas:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         MODELO CONCEPTUAL AMPLIADO                           ║
║                   HUELLA HÍDRICA DEL USO ACADÉMICO DE IA                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  PERSPECTIVAS (Dimensiones)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ GEOGRAFÍA           ┃
┣━━━━━━━━━━━━━━━━━━━━━┫
┃ • País              ┃ ← [Water Consumption.Country]
┃   (Country)         ┃    + [Asignación aleatoria seed=42]
┃                     ┃
┃ • Nivel Escasez     ┃ ← [Water Consumption.Water Scarcity Level]
┃   (WaterScarcity)   ┃
┗━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ ESTUDIANTE          ┃
┣━━━━━━━━━━━━━━━━━━━━━┫
┃ • Nivel Académico   ┃ ← [AI Usage.StudentLevel]
┃   (StudentLevel)    ┃
┃                     ┃
┃ • Disciplina        ┃ ← [AI Usage.Discipline]
┃   (Discipline)      ┃
┗━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ TIEMPO              ┃
┣━━━━━━━━━━━━━━━━━━━━━┫
┃ • Año               ┃ ← YEAR([AI Usage.SessionDate])
┃ • Trimestre         ┃ ← QUARTER([AI Usage.SessionDate])
┃ • Mes               ┃ ← MONTH([AI Usage.SessionDate])
┗━━━━━━━━━━━━━━━━━━━━━┛

                           ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  INDICADORES (Hechos)                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CONSUMO DE AGUA ESTIMADO (Huella Hídrica)                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Fórmula: [AI Usage.TotalPrompts] × 0.5 litros/prompt                    ┃
┃ Función: SUM                                                             ┃
┃ Unidad: Litros                                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CANTIDAD TOTAL DE PROMPTS                                                ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Campo: [AI Usage.TotalPrompts]                                           ┃
┃ Función: SUM                                                             ┃
┃ Unidad: Cantidad                                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DURACIÓN TOTAL DE SESIONES                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Campo: [AI Usage.SessionLengthMin]                                       ┃
┃ Función: SUM                                                             ┃
┃ Unidad: Minutos                                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ NÚMERO DE SESIONES DE IA                                                 ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Campo: [AI Usage.SessionID]                                              ┃
┃ Función: COUNT(DISTINCT)                                                 ┃
┃ Unidad: Cantidad                                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## Notas Técnicas Importantes

### 1. Asignación Geográfica

⚠️ **Limitación de datos:** El dataset AI Usage NO incluye información de país.

**Solución implementada:**
```python
import numpy as np
np.random.seed(42)  # Reproducibilidad
df['Country'] = np.random.choice(lista_paises, size=len(df))
```

Esta asignación es **artificial pero necesaria** para poder relacionar ambas fuentes de datos.

### 2. Factor de Consumo de Agua

El factor de **0.5 litros/prompt** es hipotético y representa:
- Energía consumida por el procesamiento
- Agua usada en refrigeración de data centers
- Basado en estudios de huella de carbono de IA

**Fuentes de referencia:**
- Estimaciones de consumo energético de modelos LLM
- Estudios de eficiencia de centros de datos

### 3. Agregación Temporal

Los datos se agregarán al nivel de **día** (YYYYMMDD), pero se podrán analizar por:
- Día individual
- Mes (agrupando días)
- Trimestre (agrupando meses)
- Año (agrupando trimestres)

---

## Conclusiones de la Fase 2

✅ Se definieron las **fórmulas exactas** para calcular cada indicador
✅ Se establecieron las **correspondencias** entre conceptos y campos reales
✅ Se determinó el **nivel de granularidad** para cada dimensión
✅ Se identificaron **limitaciones** (falta de geolocalización) y soluciones
✅ Se creó el **modelo conceptual ampliado** con toda la información técnica

**Siguiente fase:** Diseño del Modelo Lógico (Esquema en Estrella con SQL)
