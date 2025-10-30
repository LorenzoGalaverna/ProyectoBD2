-- ============================================================================
-- FASE 3: MODELO LÓGICO - CREACIÓN DE DIMENSIONES
-- Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
-- Metodología: Hefesto
-- Base de Datos: SQLite
-- ============================================================================

-- Eliminar tablas existentes si existen (para recrear)
DROP TABLE IF EXISTS DIM_GEOGRAFIA;
DROP TABLE IF EXISTS DIM_ESTUDIANTE;
DROP TABLE IF EXISTS DIM_TIEMPO;

-- ============================================================================
-- DIMENSIÓN 1: GEOGRAFÍA
-- ============================================================================
-- Origen: Dataset "Global Water Consumption"
-- Granularidad: País
-- Registros esperados: ~20 países

CREATE TABLE DIM_GEOGRAFIA (
    idGeografia INTEGER PRIMARY KEY AUTOINCREMENT,
    Pais TEXT NOT NULL UNIQUE,
    Nivel_Escasez_Agua TEXT NOT NULL,

    -- Validación de nivel de escasez
    CHECK (Nivel_Escasez_Agua IN ('Low', 'Moderate', 'High', 'Extreme'))
);

-- Índice para búsquedas por país
CREATE INDEX idx_geografia_pais ON DIM_GEOGRAFIA(Pais);

-- Índice para filtros por nivel de escasez
CREATE INDEX idx_geografia_escasez ON DIM_GEOGRAFIA(Nivel_Escasez_Agua);

-- ============================================================================
-- DIMENSIÓN 2: ESTUDIANTE
-- ============================================================================
-- Origen: Dataset "AI Assistant Usage in Student Life"
-- Granularidad: Combinación de Nivel Académico + Disciplina
-- Registros esperados: ~21 combinaciones (3 niveles × 7 disciplinas)

CREATE TABLE DIM_ESTUDIANTE (
    idEstudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    Nivel_Academico TEXT NOT NULL,
    Disciplina TEXT NOT NULL,

    -- Combinación única de nivel + disciplina
    UNIQUE(Nivel_Academico, Disciplina),

    -- Validación de niveles académicos
    CHECK (Nivel_Academico IN ('Undergraduate', 'Graduate', 'High School'))
);

-- Índice para filtros por nivel académico
CREATE INDEX idx_estudiante_nivel ON DIM_ESTUDIANTE(Nivel_Academico);

-- Índice para filtros por disciplina
CREATE INDEX idx_estudiante_disciplina ON DIM_ESTUDIANTE(Disciplina);

-- Índice compuesto para búsquedas combinadas
CREATE INDEX idx_estudiante_combo ON DIM_ESTUDIANTE(Nivel_Academico, Disciplina);

-- ============================================================================
-- DIMENSIÓN 3: TIEMPO
-- ============================================================================
-- Origen: Generada a partir de SessionDate del dataset AI Usage
-- Granularidad: Día
-- Registros esperados: ~366 días (jun-2024 a jun-2025)
-- Formato de clave: YYYYMMDD (numérico)

CREATE TABLE DIM_TIEMPO (
    idTiempo INTEGER PRIMARY KEY,     -- Formato: YYYYMMDD (ej: 20241015)
    Fecha DATE NOT NULL UNIQUE,       -- Fecha completa
    Anio INTEGER NOT NULL,            -- Año (2024, 2025)
    Trimestre INTEGER NOT NULL,       -- Trimestre (1-4)
    Mes INTEGER NOT NULL,             -- Mes (1-12)
    Nombre_Mes TEXT NOT NULL,         -- Nombre del mes
    Dia_Semana TEXT NOT NULL,         -- Día de la semana (Monday, Tuesday, ...)

    -- Validaciones
    CHECK (Trimestre BETWEEN 1 AND 4),
    CHECK (Mes BETWEEN 1 AND 12),
    CHECK (Anio BETWEEN 2000 AND 2100)
);

-- Índice para búsquedas por fecha
CREATE INDEX idx_tiempo_fecha ON DIM_TIEMPO(Fecha);

-- Índice para análisis por año
CREATE INDEX idx_tiempo_anio ON DIM_TIEMPO(Anio);

-- Índice compuesto para análisis temporal
CREATE INDEX idx_tiempo_anio_mes ON DIM_TIEMPO(Anio, Mes);

-- Índice para análisis trimestral
CREATE INDEX idx_tiempo_trimestre ON DIM_TIEMPO(Anio, Trimestre);

-- ============================================================================
-- VERIFICACIÓN DE CREACIÓN
-- ============================================================================

-- Listar todas las tablas creadas
SELECT 'Tablas de dimensiones creadas exitosamente:' AS Mensaje;

SELECT name AS Tabla, sql AS Definicion
FROM sqlite_master
WHERE type = 'table'
  AND name LIKE 'DIM_%'
ORDER BY name;

-- Listar todos los índices creados
SELECT 'Índices creados exitosamente:' AS Mensaje;

SELECT name AS Indice, tbl_name AS Tabla, sql AS Definicion
FROM sqlite_master
WHERE type = 'index'
  AND name LIKE 'idx_%'
ORDER BY tbl_name, name;

-- ============================================================================
-- NOTAS TÉCNICAS
-- ============================================================================

/*
DIMENSIÓN GEOGRAFÍA:
- Campo "Pais" debe coincidir con los valores en el dataset de agua
- "Nivel_Escasez_Agua" contextualiza el consumo de agua por región
- La combinación única asegura que no haya países duplicados

DIMENSIÓN ESTUDIANTE:
- Representa las características del perfil académico
- La combinación (Nivel_Academico, Disciplina) es única
- Permite analizar patrones por tipo de estudiante

DIMENSIÓN TIEMPO:
- idTiempo en formato YYYYMMDD facilita comparaciones numéricas
- Ejemplo: WHERE idTiempo >= 20240101 AND idTiempo <= 20241231
- Los campos Anio, Trimestre, Mes permiten agregaciones jerárquicas
- Fecha almacenada como DATE para compatibilidad con herramientas BI

ÍNDICES:
- Se crean índices en campos de búsqueda frecuente
- Índices compuestos optimizan consultas con múltiples condiciones
- Mejoran el rendimiento de JOINs y GROUP BY

PRÓXIMOS PASOS:
1. Ejecutar: 02_crear_hechos.sql (crear tabla de hechos)
2. Ejecutar: 03_crear_indices.sql (índices adicionales)
3. Cargar datos con: 4_integracion_datos/scripts/carga_inicial.py
*/
