-- ============================================================================
-- FASE 3: MODELO LÓGICO - CREACIÓN DE TABLA DE HECHOS
-- Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
-- Metodología: Hefesto
-- Base de Datos: SQLite
-- ============================================================================

-- Eliminar tabla existente si existe
DROP TABLE IF EXISTS HECHOS_HUELLA_HIDRICA_IA;

-- ============================================================================
-- TABLA DE HECHOS: HECHOS_HUELLA_HIDRICA_IA
-- ============================================================================
-- Representa: Huella Hídrica del Uso Académico de IA
-- Clave primaria: Compuesta (idGeografia, idEstudiante, idTiempo)
-- Registros esperados: ~10,000 combinaciones únicas agregadas

CREATE TABLE HECHOS_HUELLA_HIDRICA_IA (
    -- ========================================================================
    -- CLAVES FORÁNEAS (Dimensiones)
    -- ========================================================================
    idGeografia INTEGER NOT NULL,
    idEstudiante INTEGER NOT NULL,
    idTiempo INTEGER NOT NULL,

    -- ========================================================================
    -- INDICADORES (Hechos / Métricas)
    -- ========================================================================

    -- Indicador 1: Consumo de Agua Estimado
    -- Fórmula: Total_Prompts × 0.5 litros/prompt
    -- Función: SUM
    -- Unidad: Litros
    Huella_Hidrica REAL NOT NULL CHECK (Huella_Hidrica >= 0),

    -- Indicador 2: Cantidad Total de Prompts
    -- Campo: TotalPrompts del dataset AI Usage
    -- Función: SUM
    -- Unidad: Cantidad (entero)
    Total_Prompts INTEGER NOT NULL CHECK (Total_Prompts >= 0),

    -- Indicador 3: Duración Total de las Sesiones
    -- Campo: SessionLengthMin del dataset AI Usage
    -- Función: SUM
    -- Unidad: Minutos
    Duracion_Total_Sesiones REAL NOT NULL CHECK (Duracion_Total_Sesiones >= 0),

    -- Indicador 4: Número de Sesiones de IA
    -- Campo: COUNT(SessionID) del dataset AI Usage
    -- Función: COUNT
    -- Unidad: Cantidad (entero)
    Numero_Sesiones INTEGER NOT NULL CHECK (Numero_Sesiones > 0),

    -- ========================================================================
    -- RESTRICCIONES
    -- ========================================================================

    -- Clave primaria compuesta
    PRIMARY KEY (idGeografia, idEstudiante, idTiempo),

    -- Claves foráneas
    FOREIGN KEY (idGeografia) REFERENCES DIM_GEOGRAFIA(idGeografia)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (idEstudiante) REFERENCES DIM_ESTUDIANTE(idEstudiante)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (idTiempo) REFERENCES DIM_TIEMPO(idTiempo)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
-- ============================================================================

-- Índice para consultas por geografía
CREATE INDEX idx_hechos_geografia ON HECHOS_HUELLA_HIDRICA_IA(idGeografia);

-- Índice para consultas por estudiante
CREATE INDEX idx_hechos_estudiante ON HECHOS_HUELLA_HIDRICA_IA(idEstudiante);

-- Índice para consultas por tiempo (más frecuente)
CREATE INDEX idx_hechos_tiempo ON HECHOS_HUELLA_HIDRICA_IA(idTiempo);

-- Índice compuesto para consultas geográfico-temporales
CREATE INDEX idx_hechos_geo_tiempo ON HECHOS_HUELLA_HIDRICA_IA(idGeografia, idTiempo);

-- Índice compuesto para consultas por estudiante y tiempo
CREATE INDEX idx_hechos_est_tiempo ON HECHOS_HUELLA_HIDRICA_IA(idEstudiante, idTiempo);

-- ============================================================================
-- VISTA: Resumen de Hechos
-- ============================================================================
-- Vista para obtener estadísticas generales rápidamente

CREATE VIEW V_RESUMEN_HECHOS AS
SELECT
    COUNT(*) AS Total_Registros,
    SUM(Huella_Hidrica) AS Huella_Total_Litros,
    SUM(Total_Prompts) AS Total_Prompts_General,
    SUM(Duracion_Total_Sesiones) AS Duracion_Total_Minutos,
    SUM(Numero_Sesiones) AS Total_Sesiones,
    AVG(Huella_Hidrica) AS Huella_Promedio,
    AVG(Total_Prompts) AS Prompts_Promedio,
    AVG(Duracion_Total_Sesiones) AS Duracion_Promedio,
    MIN(idTiempo) AS Fecha_Inicio,
    MAX(idTiempo) AS Fecha_Fin
FROM HECHOS_HUELLA_HIDRICA_IA;

-- ============================================================================
-- VISTA: Hechos con Dimensiones (para análisis fácil)
-- ============================================================================
-- Vista que une automáticamente todas las dimensiones

CREATE VIEW V_HECHOS_COMPLETO AS
SELECT
    -- Dimensión Geografía
    g.Pais,
    g.Nivel_Escasez_Agua,

    -- Dimensión Estudiante
    e.Nivel_Academico,
    e.Disciplina,

    -- Dimensión Tiempo
    t.Fecha,
    t.Anio,
    t.Trimestre,
    t.Mes,
    t.Nombre_Mes,
    t.Dia_Semana,

    -- Hechos
    h.Huella_Hidrica,
    h.Total_Prompts,
    h.Duracion_Total_Sesiones,
    h.Numero_Sesiones,

    -- Cálculos derivados
    ROUND(h.Total_Prompts * 1.0 / h.Numero_Sesiones, 2) AS Prompts_Por_Sesion,
    ROUND(h.Duracion_Total_Sesiones / h.Numero_Sesiones, 2) AS Duracion_Promedio_Sesion

FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo;

-- ============================================================================
-- VERIFICACIÓN DE CREACIÓN
-- ============================================================================

SELECT 'Tabla de hechos creada exitosamente:' AS Mensaje;

SELECT name AS Objeto, type AS Tipo, sql AS Definicion
FROM sqlite_master
WHERE (type = 'table' AND name = 'HECHOS_HUELLA_HIDRICA_IA')
   OR (type = 'view' AND name LIKE 'V_%')
ORDER BY type, name;

-- Verificar integridad referencial
SELECT 'Verificando claves foráneas:' AS Mensaje;

PRAGMA foreign_key_list(HECHOS_HUELLA_HIDRICA_IA);

-- ============================================================================
-- CONSULTAS DE EJEMPLO
-- ============================================================================

-- Ejemplo 1: Consumo de agua por país (Top 10)
/*
SELECT
    g.Pais,
    g.Nivel_Escasez_Agua,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Numero_Sesiones) AS Total_Sesiones,
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS Litros_Por_Sesion
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais, g.Nivel_Escasez_Agua
ORDER BY Total_Litros DESC
LIMIT 10;
*/

-- Ejemplo 2: Uso por disciplina académica
/*
SELECT
    e.Disciplina,
    e.Nivel_Academico,
    SUM(h.Total_Prompts) AS Total_Prompts,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Numero_Sesiones) AS Total_Sesiones,
    ROUND(AVG(h.Duracion_Total_Sesiones / h.Numero_Sesiones), 2) AS Duracion_Promedio
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina, e.Nivel_Academico
ORDER BY Total_Prompts DESC;
*/

-- Ejemplo 3: Tendencia temporal mensual
/*
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
*/

-- Ejemplo 4: Usar vista completa
/*
SELECT
    Pais,
    Disciplina,
    Anio,
    Trimestre,
    SUM(Huella_Hidrica) AS Total_Litros,
    SUM(Total_Prompts) AS Total_Prompts,
    SUM(Numero_Sesiones) AS Total_Sesiones
FROM V_HECHOS_COMPLETO
WHERE Anio = 2024
GROUP BY Pais, Disciplina, Anio, Trimestre
ORDER BY Total_Litros DESC
LIMIT 20;
*/

-- ============================================================================
-- NOTAS TÉCNICAS
-- ============================================================================

/*
CLAVE PRIMARIA COMPUESTA:
- La combinación (idGeografia, idEstudiante, idTiempo) identifica únicamente cada registro
- Representa datos agregados: todos los hechos de un país, un tipo de estudiante y una fecha
- No se usa un ID autoincrementado porque los hechos agregados no requieren identificador único adicional

INDICADORES (HECHOS):
1. Huella_Hidrica: El KPI principal, calculado como Total_Prompts × 0.5 L/prompt
2. Total_Prompts: Suma de consultas enviadas a la IA
3. Duracion_Total_Sesiones: Suma de minutos de uso
4. Numero_Sesiones: Conteo de sesiones individuales

FUNCIONES DE AGREGACIÓN:
- Todos los indicadores se suman (SUM) en consultas de análisis
- Permiten cálculos derivados como promedios: Total_Prompts / Numero_Sesiones

RESTRICCIONES DE INTEGRIDAD:
- ON DELETE RESTRICT: No permite eliminar dimensiones con hechos asociados
- ON UPDATE CASCADE: Actualiza automáticamente las FKs si cambia la PK de dimensión
- CHECK constraints: Valida que los valores sean lógicos (no negativos)

VISTAS:
- V_RESUMEN_HECHOS: KPIs generales del data warehouse
- V_HECHOS_COMPLETO: Join automático con todas las dimensiones (útil para Power BI)

ÍNDICES:
- Se crean en cada FK para optimizar JOINs
- Índices compuestos optimizan consultas frecuentes (geografía+tiempo, estudiante+tiempo)
- Mejoran significativamente el rendimiento en agregaciones

PRÓXIMOS PASOS:
1. Cargar datos con: 4_integracion_datos/scripts/carga_inicial.py
2. Validar datos con: 04_consultas_ejemplo.sql
3. Conectar con Power BI para visualizaciones
*/
