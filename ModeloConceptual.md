# Modelo Conceptual del Data Warehouse
## Análisis de Uso de IA y Consumo de Agua

---

## a) Definición del Cálculo de los Indicadores

### 1. Consumo de Agua Estimado
- **Hechos**: (Cantidad Total de Prompts) × (Factor de Consumo de Litros por Prompt)
- **Función de sumarización**: `SUM`
- **Aclaración**: Este indicador estima la huella hídrica total. Se calcula multiplicando los prompts de cada sesión por un factor de consumo predefinido (por ejemplo, 0.5 litros por prompt, un valor hipotético que representaría el agua usada en la refrigeración del centro de datos).
- **Fórmula**:
  ```
  Consumo_Agua_Estimado = SUM(TotalPrompts × 0.5)
  ```

### 2. Cantidad Total de Prompts
- **Hechos**: `TotalPrompts`
- **Función de sumarización**: `SUM`
- **Aclaración**: Representa la suma de todos los prompts enviados al asistente de IA.
- **Fórmula**:
  ```
  Cantidad_Total_Prompts = SUM(TotalPrompts)
  ```

### 3. Duración Total de las Sesiones
- **Hechos**: `SessionLengthMin`
- **Función de sumarización**: `SUM`
- **Aclaración**: Es la suma de la duración en minutos de todas las sesiones de IA.
- **Fórmula**:
  ```
  Duracion_Total_Sesiones = SUM(SessionLengthMin)
  ```

### 4. Número de Sesiones de IA
- **Hechos**: `SessionID`
- **Función de sumarización**: `COUNT`
- **Aclaración**: Representa el conteo total de sesiones de interacción con la IA.
- **Fórmula**:
  ```
  Numero_Sesiones = COUNT(DISTINCT SessionID)
  ```

---

## b) Establecer Correspondencias

### Fuentes de Datos
1. **AI Assistant Usage in Student Life**
2. **Global Water Consumption Dataset**

### Mapeo de Perspectivas con Fuentes de Datos

#### Perspectiva "Geografía (País)"
- **Campo**: `Country`
- **Fuentes**: 
  - AI Assistant Usage in Student Life → `Country`
  - Global Water Consumption Dataset → `Country`

#### Perspectiva "Tiempo (Año)"
- **Campos**: 
  - Global Water Consumption Dataset → `Year`
  - AI Assistant Usage in Student Life → `SessionDate` (extracción del año)

#### Perspectiva "Estudiante"
- **Campos**:
  - AI Assistant Usage in Student Life → `StudentLevel`
  - AI Assistant Usage in Student Life → `Discipline`

### Mapeo de Indicadores con Fuentes de Datos

| Indicador | Campo Fuente | Dataset |
|-----------|--------------|---------|
| Cantidad Total de Prompts | `TotalPrompts` | AI Assistant Usage in Student Life |
| Duración Total de las Sesiones | `SessionLengthMin` | AI Assistant Usage in Student Life |
| Número de Sesiones de IA | `SessionID` | AI Assistant Usage in Student Life |
| Consumo de Agua Estimado | `TotalPrompts` × Factor (0.5 L/prompt) | AI Assistant Usage in Student Life + Factor Externo |

---

## c) Nivel de Granularidad

### Perspectiva "Geografía"
- **Country**: Identificación del país
- **Water Scarcity Level**: Contextualización del consumo de agua con la disponibilidad en la región
  - Fuente: Global Water Consumption Dataset

### Perspectiva "Estudiante"
- **StudentLevel**: Comparación del uso entre niveles académicos
  - Valores: Pregrado, Posgrado
  - Fuente: AI Assistant Usage in Student Life
- **Discipline**: Análisis de diferencias entre áreas de estudio
  - Fuente: AI Assistant Usage in Student Life

### Perspectiva "Tiempo"
- **Año**: Análisis de tendencias anuales
- **Trimestre**: Análisis detallado dentro del año (Q1, Q2, Q3, Q4)
- **Mes**: Granularidad mensual (1-12)

---

## d) Modelo Conceptual Ampliado

### Esquema Estrella (Star Schema)

```
                    ┌─────────────────────┐
                    │   DIM_GEOGRAFIA     │
                    ├─────────────────────┤
                    │ PK: GeografiaID     │
                    │ Country             │
                    │ WaterScarcityLevel  │
                    │ Region              │
                    └─────────────────────┘
                             │
                             │
    ┌─────────────────────┐ │ ┌─────────────────────┐
    │   DIM_ESTUDIANTE    │ │ │    DIM_TIEMPO       │
    ├─────────────────────┤ │ ├─────────────────────┤
    │ PK: EstudianteID    │ │ │ PK: TiempoID        │
    │ StudentLevel        │ │ │ Fecha               │
    │ Discipline          │ │ │ Año                 │
    │ AcademicYear        │ │ │ Trimestre           │
    └─────────────────────┘ │ │ Mes                 │
             │              │ │ Semana              │
             │              │ │ DiaSemana           │
             │              │ └─────────────────────┘
             │              │              │
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                ┌───────────────────────────┐
                │     FACT_USO_IA_AGUA      │
                ├───────────────────────────┤
                │ PK: FactID                │
                │ FK: GeografiaID           │
                │ FK: EstudianteID          │
                │ FK: TiempoID              │
                ├───────────────────────────┤
                │ INDICADORES (Hechos):     │
                │ - TotalPrompts            │
                │ - SessionLengthMin        │
                │ - NumeroSesiones          │
                │ - ConsumoAguaEstimado     │
                │ - FactorConsumoLitros     │
                └───────────────────────────┘
```

### Detalle de las Tablas Dimensionales

#### DIM_GEOGRAFIA
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| GeografiaID | INT | Clave primaria |
| Country | VARCHAR(100) | Nombre del país |
| WaterScarcityLevel | VARCHAR(50) | Nivel de escasez de agua (Low, Medium, High) |
| Region | VARCHAR(100) | Región geográfica |

#### DIM_ESTUDIANTE
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| EstudianteID | INT | Clave primaria |
| StudentLevel | VARCHAR(50) | Nivel académico (Undergraduate, Graduate) |
| Discipline | VARCHAR(100) | Disciplina de estudio |
| AcademicYear | VARCHAR(20) | Año académico |

#### DIM_TIEMPO
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| TiempoID | INT | Clave primaria |
| Fecha | DATE | Fecha completa |
| Año | INT | Año (2020-2024) |
| Trimestre | INT | Trimestre (1-4) |
| Mes | INT | Mes (1-12) |
| Semana | INT | Número de semana en el año |
| DiaSemana | VARCHAR(20) | Nombre del día de la semana |

#### FACT_USO_IA_AGUA
| Atributo | Tipo | Función | Descripción |
|----------|------|---------|-------------|
| FactID | INT | PK | Clave primaria de la tabla de hechos |
| GeografiaID | INT | FK | Referencia a DIM_GEOGRAFIA |
| EstudianteID | INT | FK | Referencia a DIM_ESTUDIANTE |
| TiempoID | INT | FK | Referencia a DIM_TIEMPO |
| TotalPrompts | INT | SUM | Cantidad de prompts en la sesión |
| SessionLengthMin | DECIMAL(10,2) | SUM | Duración de la sesión en minutos |
| NumeroSesiones | INT | COUNT | Conteo de sesiones |
| ConsumoAguaEstimado | DECIMAL(10,2) | SUM | Consumo estimado de agua en litros |
| FactorConsumoLitros | DECIMAL(5,2) | - | Factor de conversión (0.5 L/prompt) |

---

## Consultas Analíticas Ejemplo

### 1. Consumo de agua estimado por país y año
```sql
SELECT 
    g.Country,
    t.Año,
    SUM(f.ConsumoAguaEstimado) AS ConsumoTotal_Litros,
    SUM(f.TotalPrompts) AS PromptsTotal
FROM FACT_USO_IA_AGUA f
JOIN DIM_GEOGRAFIA g ON f.GeografiaID = g.GeografiaID
JOIN DIM_TIEMPO t ON f.TiempoID = t.TiempoID
GROUP BY g.Country, t.Año
ORDER BY ConsumoTotal_Litros DESC;
```

### 2. Uso de IA por disciplina y nivel académico
```sql
SELECT 
    e.Discipline,
    e.StudentLevel,
    COUNT(f.NumeroSesiones) AS TotalSesiones,
    SUM(f.TotalPrompts) AS TotalPrompts,
    AVG(f.SessionLengthMin) AS DuracionPromedioMin
FROM FACT_USO_IA_AGUA f
JOIN DIM_ESTUDIANTE e ON f.EstudianteID = e.EstudianteID
GROUP BY e.Discipline, e.StudentLevel
ORDER BY TotalPrompts DESC;
```

### 3. Análisis de consumo de agua vs escasez hídrica
```sql
SELECT 
    g.Country,
    g.WaterScarcityLevel,
    SUM(f.ConsumoAguaEstimado) AS ConsumoTotal_Litros,
    COUNT(f.NumeroSesiones) AS TotalSesiones
FROM FACT_USO_IA_AGUA f
JOIN DIM_GEOGRAFIA g ON f.GeografiaID = g.GeografiaID
GROUP BY g.Country, g.WaterScarcityLevel
ORDER BY ConsumoTotal_Litros DESC;
```

### 4. Tendencia temporal de uso de IA
```sql
SELECT 
    t.Año,
    t.Trimestre,
    SUM(f.TotalPrompts) AS PromptsTotal,
    SUM(f.SessionLengthMin) AS DuracionTotal,
    SUM(f.ConsumoAguaEstimado) AS ConsumoAguaTotal
FROM FACT_USO_IA_AGUA f
JOIN DIM_TIEMPO t ON f.TiempoID = t.TiempoID
GROUP BY t.Año, t.Trimestre
ORDER BY t.Año, t.Trimestre;
```

---

## Consideraciones Adicionales

### Factor de Consumo de Agua
- **Valor utilizado**: 0.5 litros por prompt
- **Justificación**: Valor hipotético que representa el agua utilizada en la refrigeración de centros de datos
- **Nota**: Este valor puede ajustarse según estudios más precisos sobre el consumo real

### Integración de Datos
1. **Extracción**: Obtener datos de ambos datasets
2. **Transformación**: 
   - Extraer año de `SessionDate`
   - Calcular trimestre y mes
   - Aplicar factor de consumo de agua
   - Normalizar nombres de países
3. **Carga**: Poblar dimensiones primero, luego tabla de hechos

### Calidad de Datos
- Validar consistencia de países entre ambos datasets
- Manejar valores nulos en campos críticos
- Verificar rangos válidos para fechas y valores numéricos
