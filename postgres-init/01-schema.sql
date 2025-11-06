-- ============================================================================
-- SCHEMA DE INICIALIZACIÓN PARA POSTGRESQL
-- Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
-- Metodología: Hefesto
-- Base de Datos: PostgreSQL 16
-- NOTA: Se usan comillas dobles para preservar mayúsculas en nombres de columnas
-- ============================================================================

-- ============================================================================
-- LIMPIAR TABLAS EXISTENTES (si existen)
-- ============================================================================

DROP TABLE IF EXISTS HECHOS_HUELLA_HIDRICA_IA CASCADE;
DROP TABLE IF EXISTS DIM_GEOGRAFIA CASCADE;
DROP TABLE IF EXISTS DIM_ESTUDIANTE CASCADE;
DROP TABLE IF EXISTS DIM_TIEMPO CASCADE;

-- ============================================================================
-- DIMENSIÓN 1: GEOGRAFÍA
-- ============================================================================

CREATE TABLE DIM_GEOGRAFIA (
    "idGeografia" SERIAL PRIMARY KEY,
    "Pais" VARCHAR(100) NOT NULL,
    "Anio" INTEGER NOT NULL,
    "Nivel_Escasez_Agua" VARCHAR(20) NOT NULL,

    UNIQUE ("Pais", "Anio"),
    CHECK ("Nivel_Escasez_Agua" IN ('Low', 'Moderate', 'High', 'Extreme'))
);

-- Índices para DIM_GEOGRAFIA
CREATE INDEX idx_geografia_pais ON DIM_GEOGRAFIA("Pais");
CREATE INDEX idx_geografia_anio ON DIM_GEOGRAFIA("Anio");
CREATE INDEX idx_geografia_escasez ON DIM_GEOGRAFIA("Nivel_Escasez_Agua");

-- ============================================================================
-- DIMENSIÓN 2: ESTUDIANTE
-- ============================================================================

CREATE TABLE DIM_ESTUDIANTE (
    "idEstudiante" SERIAL PRIMARY KEY,
    "Nivel_Academico" VARCHAR(50) NOT NULL,
    "Disciplina" VARCHAR(100) NOT NULL,

    UNIQUE ("Nivel_Academico", "Disciplina"),
    CHECK ("Nivel_Academico" IN ('Undergraduate', 'Graduate', 'High School'))
);

-- Índices para DIM_ESTUDIANTE
CREATE INDEX idx_estudiante_nivel ON DIM_ESTUDIANTE("Nivel_Academico");
CREATE INDEX idx_estudiante_disciplina ON DIM_ESTUDIANTE("Disciplina");

-- ============================================================================
-- DIMENSIÓN 3: TIEMPO
-- ============================================================================

CREATE TABLE DIM_TIEMPO (
    "idTiempo" INTEGER PRIMARY KEY,
    "Fecha" DATE NOT NULL UNIQUE,
    "Anio" INTEGER NOT NULL,
    "Trimestre" INTEGER NOT NULL,
    "Mes" INTEGER NOT NULL,
    "Nombre_Mes" VARCHAR(20) NOT NULL,
    "Dia_Semana" VARCHAR(20) NOT NULL,

    CHECK ("Trimestre" BETWEEN 1 AND 4),
    CHECK ("Mes" BETWEEN 1 AND 12),
    CHECK ("Anio" BETWEEN 2000 AND 2100)
);

-- Índices para DIM_TIEMPO
CREATE INDEX idx_tiempo_fecha ON DIM_TIEMPO("Fecha");
CREATE INDEX idx_tiempo_anio_mes ON DIM_TIEMPO("Anio", "Mes");
CREATE INDEX idx_tiempo_anio ON DIM_TIEMPO("Anio");
CREATE INDEX idx_tiempo_trimestre ON DIM_TIEMPO("Anio", "Trimestre");

-- ============================================================================
-- TABLA DE HECHOS: HECHOS_HUELLA_HIDRICA_IA
-- ============================================================================

CREATE TABLE HECHOS_HUELLA_HIDRICA_IA (
    "idGeografia" INTEGER NOT NULL,
    "idEstudiante" INTEGER NOT NULL,
    "idTiempo" INTEGER NOT NULL,

    -- Indicadores (Métricas)
    "Huella_Hidrica" NUMERIC(12, 2) NOT NULL CHECK ("Huella_Hidrica" >= 0),
    "Total_Prompts" INTEGER NOT NULL CHECK ("Total_Prompts" >= 0),
    "Duracion_Total_Sesiones" NUMERIC(12, 2) NOT NULL CHECK ("Duracion_Total_Sesiones" >= 0),
    "Numero_Sesiones" INTEGER NOT NULL CHECK ("Numero_Sesiones" > 0),

    -- Clave primaria compuesta
    PRIMARY KEY ("idGeografia", "idEstudiante", "idTiempo"),

    -- Claves foráneas
    FOREIGN KEY ("idGeografia") REFERENCES DIM_GEOGRAFIA("idGeografia")
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("idEstudiante") REFERENCES DIM_ESTUDIANTE("idEstudiante")
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY ("idTiempo") REFERENCES DIM_TIEMPO("idTiempo")
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Índices para HECHOS_HUELLA_HIDRICA_IA
CREATE INDEX idx_hechos_geografia ON HECHOS_HUELLA_HIDRICA_IA("idGeografia");
CREATE INDEX idx_hechos_estudiante ON HECHOS_HUELLA_HIDRICA_IA("idEstudiante");
CREATE INDEX idx_hechos_tiempo ON HECHOS_HUELLA_HIDRICA_IA("idTiempo");
CREATE INDEX idx_hechos_geo_tiempo ON HECHOS_HUELLA_HIDRICA_IA("idGeografia", "idTiempo");
CREATE INDEX idx_hechos_est_tiempo ON HECHOS_HUELLA_HIDRICA_IA("idEstudiante", "idTiempo");

-- ============================================================================
-- VISTA: Resumen de Hechos
-- ============================================================================

CREATE VIEW V_RESUMEN_HECHOS AS
SELECT
    COUNT(*) AS "Total_Registros",
    SUM("Huella_Hidrica") AS "Huella_Total_Litros",
    SUM("Total_Prompts") AS "Total_Prompts_General",
    SUM("Duracion_Total_Sesiones") AS "Duracion_Total_Minutos",
    SUM("Numero_Sesiones") AS "Total_Sesiones",
    AVG("Huella_Hidrica") AS "Huella_Promedio",
    AVG("Total_Prompts") AS "Prompts_Promedio",
    AVG("Duracion_Total_Sesiones") AS "Duracion_Promedio",
    MIN("idTiempo") AS "Fecha_Inicio",
    MAX("idTiempo") AS "Fecha_Fin"
FROM HECHOS_HUELLA_HIDRICA_IA;

-- ============================================================================
-- VISTA: Hechos con Dimensiones (para análisis fácil)
-- ============================================================================

CREATE VIEW V_HECHOS_COMPLETO AS
SELECT
    -- Dimensión Geografía
    g."Pais",
    g."Anio" AS "Geografia_Anio",
    g."Nivel_Escasez_Agua",

    -- Dimensión Estudiante
    e."Nivel_Academico",
    e."Disciplina",

    -- Dimensión Tiempo
    t."Fecha",
    t."Anio",
    t."Trimestre",
    t."Mes",
    t."Nombre_Mes",
    t."Dia_Semana",

    -- Hechos
    h."Huella_Hidrica",
    h."Total_Prompts",
    h."Duracion_Total_Sesiones",
    h."Numero_Sesiones",

    -- Cálculos derivados
    ROUND(h."Total_Prompts"::NUMERIC / h."Numero_Sesiones", 2) AS "Prompts_Por_Sesion",
    ROUND(h."Duracion_Total_Sesiones" / h."Numero_Sesiones", 2) AS "Duracion_Promedio_Sesion"

FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h."idGeografia" = g."idGeografia"
INNER JOIN DIM_ESTUDIANTE e ON h."idEstudiante" = e."idEstudiante"
INNER JOIN DIM_TIEMPO t ON h."idTiempo" = t."idTiempo";

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

SELECT 'Schema creado exitosamente para PostgreSQL 16 con mayúsculas preservadas' AS "Mensaje";
SELECT COUNT(*) AS "Total_Tablas" FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
