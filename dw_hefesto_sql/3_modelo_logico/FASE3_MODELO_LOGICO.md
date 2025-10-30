# FASE 3: MODELO LÓGICO DEL DATA WAREHOUSE

**Proyecto:** Data Warehouse - Huella Hídrica del Uso de IA en Estudiantes
**Metodología:** Hefesto
**Fecha:** Octubre 2025

---

## a) Tipo de Modelo Lógico del DW

### Esquema Seleccionado: ⭐ **ESTRELLA (Star Schema)**

**Justificación:**
- ✅ **Simplicidad:** Fácil de entender y mantener
- ✅ **Performance:** Consultas rápidas con menos JOINs
- ✅ **Ideal para BI:** Compatible con Power BI, Tableau, etc.
- ✅ **Estándar en Hefesto:** Recomendado por la metodología

**Características del esquema:**
- Una tabla de hechos central
- Múltiples tablas de dimensiones conectadas directamente
- Sin jerarquías normalizadas (modelo desnormalizado)

---

## b) Tablas de Dimensiones

### Dimensión 1: DIM_GEOGRAFIA

**Origen:** Perspectiva "Geografía" + Dataset "Global Water Consumption"

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **idGeografia** | INTEGER (PK) | Clave primaria autoincremental |
| **Pais** | TEXT | Nombre del país |
| **Nivel_Escasez_Agua** | TEXT | Nivel de escasez (Low, Moderate, High) |

**SQL de creación:**
```sql
CREATE TABLE DIM_GEOGRAFIA (
    idGeografia INTEGER PRIMARY KEY AUTOINCREMENT,
    Pais TEXT NOT NULL UNIQUE,
    Nivel_Escasez_Agua TEXT NOT NULL
);

CREATE INDEX idx_geografia_pais ON DIM_GEOGRAFIA(Pais);
```

**Granularidad:** Nivel de país

**Registros esperados:** ~20 países

---

### Dimensión 2: DIM_ESTUDIANTE

**Origen:** Perspectiva "Estudiante" + Dataset "AI Usage"

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **idEstudiante** | INTEGER (PK) | Clave primaria autoincremental |
| **Nivel_Academico** | TEXT | Nivel educativo (Undergraduate, Graduate, High School) |
| **Disciplina** | TEXT | Área de estudio (Computer Science, Engineering, etc.) |

**SQL de creación:**
```sql
CREATE TABLE DIM_ESTUDIANTE (
    idEstudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    Nivel_Academico TEXT NOT NULL,
    Disciplina TEXT NOT NULL,
    UNIQUE(Nivel_Academico, Disciplina)
);

CREATE INDEX idx_estudiante_nivel ON DIM_ESTUDIANTE(Nivel_Academico);
CREATE INDEX idx_estudiante_disciplina ON DIM_ESTUDIANTE(Disciplina);
```

**Granularidad:** Combinación de nivel académico + disciplina

**Registros esperados:** ~21 combinaciones (3 niveles × 7 disciplinas)

---

### Dimensión 3: DIM_TIEMPO

**Origen:** Perspectiva "Tiempo" + SessionDate del dataset "AI Usage"

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **idTiempo** | INTEGER (PK) | Clave en formato YYYYMMDD (ej: 20241015) |
| **Fecha** | DATE | Fecha completa |
| **Anio** | INTEGER | Año (2024, 2025) |
| **Trimestre** | INTEGER | Trimestre (1-4) |
| **Mes** | INTEGER | Mes (1-12) |
| **Nombre_Mes** | TEXT | Nombre del mes (Enero, Febrero, ...) |
| **Dia_Semana** | TEXT | Día de la semana (Monday, Tuesday, ...) |

**SQL de creación:**
```sql
CREATE TABLE DIM_TIEMPO (
    idTiempo INTEGER PRIMARY KEY,
    Fecha DATE NOT NULL UNIQUE,
    Anio INTEGER NOT NULL,
    Trimestre INTEGER NOT NULL,
    Mes INTEGER NOT NULL,
    Nombre_Mes TEXT NOT NULL,
    Dia_Semana TEXT NOT NULL
);

CREATE INDEX idx_tiempo_fecha ON DIM_TIEMPO(Fecha);
CREATE INDEX idx_tiempo_anio_mes ON DIM_TIEMPO(Anio, Mes);
```

**Granularidad:** Nivel de día

**Registros esperados:** ~366 días (de jun-2024 a jun-2025)

**Nota:** idTiempo usa formato numérico YYYYMMDD para eficiencia:
- 20241015 = 15 de octubre de 2024
- Facilita comparaciones y rangos

---

## c) Tabla de Hechos

### HECHOS_HUELLA_HIDRICA_IA

**Representa:** El área de estudio "Huella Hídrica del Uso Académico de IA"

#### Estructura Completa

| Campo | Tipo | Rol | Descripción |
|-------|------|-----|-------------|
| **idGeografia** | INTEGER (FK) | Clave Foránea | → DIM_GEOGRAFIA |
| **idEstudiante** | INTEGER (FK) | Clave Foránea | → DIM_ESTUDIANTE |
| **idTiempo** | INTEGER (FK) | Clave Foránea | → DIM_TIEMPO |
| **Huella_Hidrica** | REAL | Hecho (Métrica) | Consumo de agua estimado (litros) |
| **Total_Prompts** | INTEGER | Hecho (Métrica) | Cantidad total de prompts |
| **Duracion_Total_Sesiones** | REAL | Hecho (Métrica) | Duración en minutos |
| **Numero_Sesiones** | INTEGER | Hecho (Métrica) | Conteo de sesiones |

#### Clave Primaria

**Clave Primaria Compuesta:** `(idGeografia, idEstudiante, idTiempo)`

Esta combinación identifica únicamente cada registro agregado:
- Un país específico
- Una combinación de nivel académico + disciplina
- Una fecha específica

#### SQL de creación

```sql
CREATE TABLE HECHOS_HUELLA_HIDRICA_IA (
    idGeografia INTEGER NOT NULL,
    idEstudiante INTEGER NOT NULL,
    idTiempo INTEGER NOT NULL,
    Huella_Hidrica REAL NOT NULL,
    Total_Prompts INTEGER NOT NULL,
    Duracion_Total_Sesiones REAL NOT NULL,
    Numero_Sesiones INTEGER NOT NULL,

    PRIMARY KEY (idGeografia, idEstudiante, idTiempo),

    FOREIGN KEY (idGeografia) REFERENCES DIM_GEOGRAFIA(idGeografia),
    FOREIGN KEY (idEstudiante) REFERENCES DIM_ESTUDIANTE(idEstudiante),
    FOREIGN KEY (idTiempo) REFERENCES DIM_TIEMPO(idTiempo)
);

CREATE INDEX idx_hechos_geografia ON HECHOS_HUELLA_HIDRICA_IA(idGeografia);
CREATE INDEX idx_hechos_estudiante ON HECHOS_HUELLA_HIDRICA_IA(idEstudiante);
CREATE INDEX idx_hechos_tiempo ON HECHOS_HUELLA_HIDRICA_IA(idTiempo);
```

#### Funciones de Agregación

| Indicador | Función SQL | Ejemplo de Query |
|-----------|-------------|------------------|
| **Huella Hídrica** | `SUM(Huella_Hidrica)` | Total de litros consumidos |
| **Total Prompts** | `SUM(Total_Prompts)` | Total de consultas |
| **Duración Sesiones** | `SUM(Duracion_Total_Sesiones)` | Total de minutos |
| **Número Sesiones** | `SUM(Numero_Sesiones)` | Total de sesiones |

**Promedio de Prompts por Sesión:**
```sql
SELECT SUM(Total_Prompts) / SUM(Numero_Sesiones) AS Promedio_Prompts
FROM HECHOS_HUELLA_HIDRICA_IA;
```

---

## d) Uniones (JOINs)

### Diagrama del Esquema en Estrella

```
                    ┌─────────────────────┐
                    │   DIM_GEOGRAFIA     │
                    │ ─────────────────── │
                    │ PK: idGeografia     │
                    │     Pais            │
                    │     Nivel_Escasez   │
                    └──────────┬──────────┘
                               │
                               │ 1
                               │
                               │ N
              ┌────────────────┼────────────────┐
              │                │                │
              │                │                │
┌─────────────▼──────┐  ┌──────▼────────────────────┐  ┌───────────────▼──────┐
│  DIM_ESTUDIANTE    │  │ HECHOS_HUELLA_HIDRICA_IA  │  │   DIM_TIEMPO         │
│ ────────────────── │  │ ──────────────────────────│  │ ──────────────────── │
│ PK: idEstudiante   │  │ PK: (idGeografia,         │  │ PK: idTiempo         │
│     Nivel_Academico│  │      idEstudiante,        │  │     Fecha            │
│     Disciplina     │  │      idTiempo)            │  │     Anio             │
└────────────────────┘  │                           │  │     Trimestre        │
                        │ FK: idGeografia           │  │     Mes              │
                        │ FK: idEstudiante          │  │     Nombre_Mes       │
                        │ FK: idTiempo              │  │     Dia_Semana       │
                        │                           │  └──────────────────────┘
                        │ Huella_Hidrica      (SUM) │
                        │ Total_Prompts       (SUM) │
                        │ Duracion_Sesiones   (SUM) │
                        │ Numero_Sesiones    (COUNT)│
                        └───────────────────────────┘
```

### Tipos de JOIN

Todas las uniones son de tipo **INNER JOIN** ya que:
- Los hechos SIEMPRE deben tener todas sus dimensiones
- No permitimos hechos "huérfanos" sin geografía, estudiante o tiempo
- Garantiza integridad referencial

### Ejemplos de Consultas con JOIN

#### Consulta 1: Consumo de agua por país

```sql
SELECT
    g.Pais,
    g.Nivel_Escasez_Agua,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Numero_Sesiones) AS Total_Sesiones
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais, g.Nivel_Escasez_Agua
ORDER BY Total_Litros DESC;
```

#### Consulta 2: Uso por disciplina académica

```sql
SELECT
    e.Disciplina,
    e.Nivel_Academico,
    SUM(h.Total_Prompts) AS Total_Prompts,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    AVG(h.Duracion_Total_Sesiones / h.Numero_Sesiones) AS Duracion_Promedio
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina, e.Nivel_Academico
ORDER BY Total_Prompts DESC;
```

#### Consulta 3: Tendencia temporal

```sql
SELECT
    t.Anio,
    t.Mes,
    t.Nombre_Mes,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Total_Prompts) AS Total_Prompts,
    SUM(h.Numero_Sesiones) AS Total_Sesiones
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Anio, t.Mes, t.Nombre_Mes
ORDER BY t.Anio, t.Mes;
```

#### Consulta 4: Análisis completo (todas las dimensiones)

```sql
SELECT
    g.Pais,
    e.Nivel_Academico,
    e.Disciplina,
    t.Anio,
    t.Trimestre,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Total_Prompts) AS Total_Prompts,
    SUM(h.Numero_Sesiones) AS Total_Sesiones
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
WHERE t.Anio = 2024
GROUP BY g.Pais, e.Nivel_Academico, e.Disciplina, t.Anio, t.Trimestre
ORDER BY Total_Litros DESC;
```

---

## Resumen del Modelo Lógico

### Estadísticas del Modelo

| Elemento | Cantidad | Notas |
|----------|----------|-------|
| **Tablas de Dimensiones** | 3 | Geografía, Estudiante, Tiempo |
| **Tablas de Hechos** | 1 | HECHOS_HUELLA_HIDRICA_IA |
| **Total de Tablas** | 4 | Esquema completo |
| **Claves Primarias** | 4 | 3 simples + 1 compuesta |
| **Claves Foráneas** | 3 | En la tabla de hechos |
| **Índices** | 9 | Para optimizar consultas |
| **Métricas (Hechos)** | 4 | Huella, Prompts, Duración, Sesiones |

### Cardinalidades

```
DIM_GEOGRAFIA (20)  ──┐
                      ├──► HECHOS (~10,000 agregados)
DIM_ESTUDIANTE (21) ──┤
                      │
DIM_TIEMPO (366)  ────┘
```

**Registros estimados en hechos:** ~10,000 combinaciones únicas de (país, estudiante, fecha)

---

## Archivos SQL Generados

En la carpeta `3_modelo_logico/sql/` encontrarás:

1. **01_crear_dimensiones.sql** - Crea las 3 tablas de dimensiones
2. **02_crear_hechos.sql** - Crea la tabla de hechos con FKs
3. **03_crear_indices.sql** - Crea índices para optimización
4. **04_consultas_ejemplo.sql** - Queries de ejemplo para análisis

---

## Conclusiones de la Fase 3

✅ Se seleccionó el **esquema en estrella** como modelo lógico
✅ Se diseñaron **3 tablas de dimensiones** con sus campos y tipos
✅ Se diseñó la **tabla de hechos** con 4 métricas clave
✅ Se definieron las **relaciones (FK)** y tipos de JOIN
✅ Se crearon **índices** para optimizar consultas
✅ Se documentaron **consultas SQL de ejemplo** para cada pregunta de negocio

**Siguiente fase:** Integración de Datos (ETL - Carga Inicial y Actualización)
