-- ============================================================================
-- CONSULTAS DE ANÁLISIS PARA POWER BI
-- Data Warehouse: Huella Hídrica del Uso de IA en Estudiantes
-- Metodología: Hefesto
-- ============================================================================
-- Estas consultas responden a las preguntas de negocio de la Fase 1
-- Pueden ser usadas directamente en Power BI o herramientas de visualización
-- ============================================================================

-- ============================================================================
-- PREGUNTA 1: Consumo Total por País, Disciplina y Tiempo
-- ============================================================================

-- 1.1 Consumo de Agua por País (Top 10)
-- ============================================================================
SELECT
    g.Pais AS País,
    g.Nivel_Escasez_Agua AS 'Nivel de Escasez',
    SUM(h.Huella_Hidrica) AS 'Total Litros Consumidos',
    SUM(h.Total_Prompts) AS 'Total de Prompts',
    SUM(h.Numero_Sesiones) AS 'Total de Sesiones',
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS 'Litros por Sesión',
    ROUND(SUM(h.Total_Prompts) * 1.0 / SUM(h.Numero_Sesiones), 2) AS 'Prompts por Sesión'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais, g.Nivel_Escasez_Agua
ORDER BY SUM(h.Huella_Hidrica) DESC
LIMIT 10;

-- 1.2 Consumo de Agua por Disciplina Académica
-- ============================================================================
SELECT
    e.Disciplina,
    e.Nivel_Academico AS 'Nivel Académico',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    SUM(h.Huella_Hidrica) AS 'Total Litros',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    ROUND(AVG(h.Duracion_Total_Sesiones / h.Numero_Sesiones), 2) AS 'Duración Promedio (min)',
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS 'Litros por Sesión'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina, e.Nivel_Academico
ORDER BY SUM(h.Total_Prompts) DESC;

-- 1.3 Tendencia Temporal Mensual
-- ============================================================================
SELECT
    t.Anio AS Año,
    t.Mes,
    t.Nombre_Mes AS 'Nombre del Mes',
    SUM(h.Huella_Hidrica) AS 'Total Litros',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    ROUND(AVG(h.Duracion_Total_Sesiones / h.Numero_Sesiones), 2) AS 'Duración Promedio'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Anio, t.Mes, t.Nombre_Mes
ORDER BY t.Anio, t.Mes;

-- 1.4 Tendencia por Trimestre
-- ============================================================================
SELECT
    t.Anio AS Año,
    t.Trimestre,
    'Q' || t.Trimestre AS 'Quarter',
    SUM(h.Huella_Hidrica) AS 'Total Litros',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    COUNT(DISTINCT t.idTiempo) AS 'Días con Actividad'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Anio, t.Trimestre
ORDER BY t.Anio, t.Trimestre;

-- ============================================================================
-- PREGUNTA 2: Huella Hídrica vs Escasez de Agua
-- ============================================================================

-- 2.1 Consumo vs Nivel de Escasez por País
-- ============================================================================
SELECT
    g.Nivel_Escasez_Agua AS 'Nivel de Escasez',
    COUNT(DISTINCT g.Pais) AS 'Número de Países',
    SUM(h.Huella_Hidrica) AS 'Consumo Total (L)',
    ROUND(AVG(h.Huella_Hidrica), 2) AS 'Consumo Promedio (L)',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Nivel_Escasez_Agua
ORDER BY SUM(h.Huella_Hidrica) DESC;

-- 2.2 Países con Mayor Impacto (Alto Consumo + Alta Escasez)
-- ============================================================================
SELECT
    g.Pais AS País,
    g.Nivel_Escasez_Agua AS 'Nivel de Escasez',
    SUM(h.Huella_Hidrica) AS 'Consumo Total (L)',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    CASE
        WHEN SUM(h.Huella_Hidrica) > 1500 AND g.Nivel_Escasez_Agua IN ('High', 'Extreme')
        THEN '🚨 CRÍTICO'
        WHEN SUM(h.Huella_Hidrica) > 1000 AND g.Nivel_Escasez_Agua = 'Moderate'
        THEN '⚠️ ALTO'
        ELSE '✅ MODERADO'
    END AS 'Nivel de Impacto'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais, g.Nivel_Escasez_Agua
ORDER BY SUM(h.Huella_Hidrica) DESC;

-- ============================================================================
-- PREGUNTA 3: Promedio de Prompts y Duración por Tarea
-- ============================================================================

-- 3.1 Estadísticas por Disciplina
-- ============================================================================
SELECT
    e.Disciplina,
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    ROUND(SUM(h.Total_Prompts) * 1.0 / SUM(h.Numero_Sesiones), 2) AS 'Promedio Prompts por Sesión',
    ROUND(SUM(h.Duracion_Total_Sesiones) / SUM(h.Numero_Sesiones), 2) AS 'Duración Promedio (min)',
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS 'Huella Promedio por Sesión (L)'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina
ORDER BY SUM(h.Total_Prompts) DESC;

-- 3.2 Matriz: Disciplina × Nivel Académico
-- ============================================================================
SELECT
    e.Disciplina,
    e.Nivel_Academico AS 'Nivel Académico',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    SUM(h.Numero_Sesiones) AS 'Sesiones',
    ROUND(SUM(h.Total_Prompts) * 1.0 / SUM(h.Numero_Sesiones), 2) AS 'Prompts/Sesión',
    ROUND(SUM(h.Duracion_Total_Sesiones) / SUM(h.Numero_Sesiones), 2) AS 'Duración/Sesión (min)',
    SUM(h.Huella_Hidrica) AS 'Huella Total (L)'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina, e.Nivel_Academico
ORDER BY e.Disciplina, e.Nivel_Academico;

-- ============================================================================
-- PREGUNTA 4: Correlación Nivel Académico vs Consumo
-- ============================================================================

-- 4.1 Consumo por Nivel Académico
-- ============================================================================
SELECT
    e.Nivel_Academico AS 'Nivel Académico',
    SUM(h.Huella_Hidrica) AS 'Consumo Total (L)',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS 'Consumo por Sesión (L)',
    ROUND(SUM(h.Total_Prompts) * 1.0 / SUM(h.Numero_Sesiones), 2) AS 'Prompts por Sesión',
    ROUND(SUM(h.Duracion_Total_Sesiones) / SUM(h.Numero_Sesiones), 2) AS 'Duración por Sesión (min)',
    ROUND(100.0 * SUM(h.Numero_Sesiones) / (SELECT SUM(Numero_Sesiones) FROM HECHOS_HUELLA_HIDRICA_IA), 2) AS 'Porcentaje del Total (%)'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Nivel_Academico
ORDER BY SUM(h.Huella_Hidrica) DESC;

-- 4.2 Distribución Temporal por Nivel Académico
-- ============================================================================
SELECT
    t.Anio AS Año,
    t.Trimestre,
    e.Nivel_Academico AS 'Nivel Académico',
    SUM(h.Huella_Hidrica) AS 'Consumo (L)',
    SUM(h.Numero_Sesiones) AS 'Sesiones'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Anio, t.Trimestre, e.Nivel_Academico
ORDER BY t.Anio, t.Trimestre, e.Nivel_Academico;

-- ============================================================================
-- ANÁLISIS ADICIONALES PARA DASHBOARDS
-- ============================================================================

-- 5.1 KPIs Generales
-- ============================================================================
SELECT
    'KPIs Generales' AS Categoría,
    SUM(Huella_Hidrica) AS 'Huella Total (L)',
    SUM(Total_Prompts) AS 'Prompts Totales',
    SUM(Duracion_Total_Sesiones) AS 'Minutos Totales',
    SUM(Numero_Sesiones) AS 'Sesiones Totales',
    ROUND(SUM(Huella_Hidrica) / SUM(Numero_Sesiones), 2) AS 'Litros por Sesión',
    ROUND(SUM(Total_Prompts) * 1.0 / SUM(Numero_Sesiones), 2) AS 'Prompts por Sesión',
    ROUND(SUM(Duracion_Total_Sesiones) / SUM(Numero_Sesiones), 2) AS 'Minutos por Sesión'
FROM HECHOS_HUELLA_HIDRICA_IA;

-- 5.2 Top 5 Combinaciones País + Disciplina
-- ============================================================================
SELECT
    g.Pais AS País,
    e.Disciplina,
    e.Nivel_Academico AS 'Nivel',
    SUM(h.Huella_Hidrica) AS 'Consumo (L)',
    SUM(h.Numero_Sesiones) AS 'Sesiones'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY g.Pais, e.Disciplina, e.Nivel_Academico
ORDER BY SUM(h.Huella_Hidrica) DESC
LIMIT 5;

-- 5.3 Actividad por Día de la Semana
-- ============================================================================
SELECT
    t.Dia_Semana AS 'Día de la Semana',
    SUM(h.Numero_Sesiones) AS 'Total Sesiones',
    SUM(h.Total_Prompts) AS 'Total Prompts',
    SUM(h.Huella_Hidrica) AS 'Consumo (L)',
    ROUND(AVG(h.Duracion_Total_Sesiones / h.Numero_Sesiones), 2) AS 'Duración Promedio (min)'
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Dia_Semana
ORDER BY SUM(h.Numero_Sesiones) DESC;

-- 5.4 Uso de Vista Completa (simplifica consultas)
-- ============================================================================
SELECT
    País,
    Disciplina,
    'Nivel Académico',
    Año,
    Mes,
    Nombre_Mes,
    SUM(Huella_Hidrica) AS 'Consumo (L)',
    SUM(Total_Prompts) AS 'Prompts',
    SUM(Numero_Sesiones) AS 'Sesiones',
    ROUND(AVG(Prompts_Por_Sesion), 2) AS 'Prompts/Sesión',
    ROUND(AVG(Duracion_Promedio_Sesion), 2) AS 'Min/Sesión'
FROM V_HECHOS_COMPLETO
WHERE Año = 2024
GROUP BY País, Disciplina, Nivel_Academico, Año, Mes, Nombre_Mes
ORDER BY SUM(Huella_Hidrica) DESC
LIMIT 20;

-- ============================================================================
-- CONSULTA MAESTRA PARA POWER BI (Conectar directamente a esta vista)
-- ============================================================================
-- Esta consulta puede ser usada como fuente de datos principal en Power BI

SELECT
    -- IDs (útiles para relaciones en Power BI)
    h.idGeografia,
    h.idEstudiante,
    h.idTiempo,

    -- Geografía
    g.Pais,
    g.Nivel_Escasez_Agua,

    -- Estudiante
    e.Nivel_Academico,
    e.Disciplina,

    -- Tiempo
    t.Fecha,
    t.Anio,
    t.Trimestre,
    t.Mes,
    t.Nombre_Mes,
    t.Dia_Semana,

    -- Hechos (métricas)
    h.Huella_Hidrica,
    h.Total_Prompts,
    h.Duracion_Total_Sesiones,
    h.Numero_Sesiones,

    -- Métricas calculadas
    ROUND(h.Total_Prompts * 1.0 / h.Numero_Sesiones, 2) AS Prompts_Por_Sesion,
    ROUND(h.Duracion_Total_Sesiones / h.Numero_Sesiones, 2) AS Duracion_Promedio_Sesion,
    ROUND(h.Huella_Hidrica / h.Numero_Sesiones, 2) AS Litros_Por_Sesion

FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
ORDER BY t.Fecha, g.Pais, e.Disciplina;

-- ============================================================================
-- NOTAS PARA POWER BI
-- ============================================================================
/*
CONEXIÓN A POWER BI:
1. Obtener datos → Base de datos SQLite
2. Ruta: /Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db
3. Usar la "CONSULTA MAESTRA" de arriba como fuente principal

ALTERNATIVAMENTE:
- Importar cada tabla de dimensión y hechos por separado
- Dejar que Power BI cree las relaciones automáticamente
- Ventaja: Mejor rendimiento y modelo de datos más flexible

RELACIONES EN POWER BI:
- DIM_GEOGRAFIA[idGeografia] → HECHOS[idGeografia]
- DIM_ESTUDIANTE[idEstudiante] → HECHOS[idEstudiante]
- DIM_TIEMPO[idTiempo] → HECHOS[idTiempo]
- Cardinalidad: 1:* (uno a muchos)
- Dirección de filtro: Bidireccional o de dimensión a hechos

MEDIDAS DAX SUGERIDAS:
Total Huella Hídrica = SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica])
Total Sesiones = SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
Promedio Prompts = DIVIDE(SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts]), SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones]))
Litros por Sesión = DIVIDE(SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica]), SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones]))
*/
