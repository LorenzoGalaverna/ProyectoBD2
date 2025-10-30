# 🚀 Guía Rápida: Conectar Power BI al Data Warehouse

## ✅ Data Warehouse Listo

**Base de datos SQLite creada exitosamente:**
- **Ubicación:** `/Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db`
- **Tamaño:** ~2-3 MB
- **Modelo:** Esquema en Estrella (3 dimensiones + 1 tabla de hechos)

---

## 📊 Datos Cargados

### Dimensiones
- **DIM_GEOGRAFIA:** 20 países
- **DIM_ESTUDIANTE:** 21 combinaciones (nivel académico × disciplina)
- **DIM_TIEMPO:** 366 fechas (jun-2024 a jun-2025)

### Hechos
- **HECHOS_HUELLA_HIDRICA_IA:** 9,586 registros agregados
  - Huella hídrica total: **28,037.50 litros**
  - Total de prompts: **56,075**
  - Total de sesiones: **10,000**

---

## 🔌 Conectar Power BI

### Método 1: Importar con Conector SQLite (Recomendado)

1. **Abrir Power BI Desktop**

2. **Obtener datos → Más**
   - Buscar "SQLite"
   - Si no aparece, descargar el conector desde: https://www.sqlite.org/download.html

3. **Seleccionar archivo de base de datos:**
   ```
   /Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db
   ```

4. **Seleccionar todas las tablas:**
   - ☑️ DIM_GEOGRAFIA
   - ☑️ DIM_ESTUDIANTE
   - ☑️ DIM_TIEMPO
   - ☑️ HECHOS_HUELLA_HIDRICA_IA

5. **Cargar**

### Método 2: Importar con ODBC (Alternativo)

1. **Instalar SQLite ODBC Driver** (si no lo tienes):
   ```bash
   brew install sqliteodbc
   ```

2. **Power BI → Obtener datos → ODBC**

3. **Configurar DSN o usar cadena de conexión:**
   ```
   Driver=SQLite3;Database=/Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db
   ```

---

## 🔗 Verificar Relaciones en Power BI

Power BI debería detectar automáticamente las relaciones. Verifica en **Vista de Modelo**:

| Desde (Dimensión) | Campo | Hasta (Hechos) | Campo | Cardinalidad |
|-------------------|-------|----------------|-------|--------------|
| DIM_GEOGRAFIA | idGeografia | HECHOS_HUELLA_HIDRICA_IA | idGeografia | 1:* (Uno a muchos) |
| DIM_ESTUDIANTE | idEstudiante | HECHOS_HUELLA_HIDRICA_IA | idEstudiante | 1:* |
| DIM_TIEMPO | idTiempo | HECHOS_HUELLA_HIDRICA_IA | idTiempo | 1:* |

**Configuración de relaciones:**
- Dirección de filtro cruzado: **Bidireccional** (o de dimensión a hechos)
- Activar: ☑️ Asumir integridad referencial

---

## 📈 Medidas DAX Sugeridas

Crea estas medidas en Power BI para facilitar el análisis:

### Medidas Básicas

```dax
// KPI 1: Total de Huella Hídrica
Total Huella Hídrica =
SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica])

// KPI 2: Total de Sesiones
Total Sesiones =
SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])

// KPI 3: Total de Prompts
Total Prompts =
SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts])

// KPI 4: Duración Total
Duración Total =
SUM(HECHOS_HUELLA_HIDRICA_IA[Duracion_Total_Sesiones])
```

### Medidas Calculadas

```dax
// Litros por Sesión
Litros por Sesión =
DIVIDE(
    [Total Huella Hídrica],
    [Total Sesiones],
    0
)

// Prompts por Sesión
Prompts por Sesión =
DIVIDE(
    [Total Prompts],
    [Total Sesiones],
    0
)

// Duración Promedio (minutos)
Duración Promedio =
DIVIDE(
    [Duración Total],
    [Total Sesiones],
    0
)

// Litros por Prompt
Litros por Prompt =
DIVIDE(
    [Total Huella Hídrica],
    [Total Prompts],
    0
)
```

### Medidas con Contexto

```dax
// Porcentaje del Total por País
% del Total =
DIVIDE(
    [Total Huella Hídrica],
    CALCULATE([Total Huella Hídrica], ALL(DIM_GEOGRAFIA)),
    0
)

// Ranking de Países
Ranking País =
RANKX(
    ALL(DIM_GEOGRAFIA[Pais]),
    [Total Huella Hídrica],
    ,
    DESC,
    Dense
)

// Crecimiento Mensual
Crecimiento Mensual =
VAR MesActual = [Total Huella Hídrica]
VAR MesAnterior =
    CALCULATE(
        [Total Huella Hídrica],
        DATEADD(DIM_TIEMPO[Fecha], -1, MONTH)
    )
RETURN
DIVIDE(MesActual - MesAnterior, MesAnterior, 0)
```

---

## 📊 Visualizaciones Sugeridas

### Página 1: Dashboard Ejecutivo

1. **Tarjetas (Cards)** - KPIs principales:
   - Total Huella Hídrica (28K litros)
   - Total Sesiones (10K)
   - Total Prompts (56K)
   - Litros/Sesión (2.80 L)

2. **Gráfico de Barras** - Top 10 países por consumo:
   - Eje X: País
   - Eje Y: Total Huella Hídrica
   - Etiquetas de datos: Activadas

3. **Gráfico de Líneas** - Tendencia temporal:
   - Eje X: Fecha (por mes)
   - Eje Y: Total Huella Hídrica
   - Línea de tendencia: Activada

4. **Gráfico de Anillos** - Distribución por nivel académico:
   - Leyenda: Nivel_Academico
   - Valores: Total Sesiones

### Página 2: Análisis Geográfico

1. **Mapa** - Consumo por país:
   - Ubicación: País
   - Tamaño de burbuja: Total Huella Hídrica
   - Color: Nivel_Escasez_Agua

2. **Tabla** - Detalle por país:
   - País
   - Nivel de Escasez
   - Total Litros
   - Total Sesiones
   - Litros/Sesión

3. **Gráfico de Barras Agrupadas** - Consumo vs Escasez:
   - Eje X: Nivel_Escasez_Agua
   - Eje Y: Total Huella Hídrica
   - Leyenda: País (Top 5)

### Página 3: Análisis Académico

1. **Matriz (Heatmap)** - Disciplina × Nivel Académico:
   - Filas: Disciplina
   - Columnas: Nivel_Academico
   - Valores: Total Prompts
   - Formato condicional: Escala de colores

2. **Gráfico de Barras Horizontales** - Uso por disciplina:
   - Eje Y: Disciplina
   - Eje X: Total Prompts
   - Ordenar: Descendente

3. **Gráfico de Columnas Apiladas** - Distribución temporal por nivel:
   - Eje X: Mes
   - Eje Y: Total Sesiones
   - Leyenda: Nivel_Academico

### Página 4: Análisis Temporal

1. **Gráfico de Áreas** - Evolución mensual:
   - Eje X: Fecha (mes)
   - Eje Y: Total Huella Hídrica
   - Series: Por Nivel_Academico

2. **Gráfico de Columnas** - Comparación trimestral:
   - Eje X: Trimestre
   - Eje Y: Múltiples métricas (Huella, Prompts, Sesiones)

3. **Segmentadores (Slicers)**:
   - Año
   - Trimestre
   - Disciplina
   - País

---

## 🎨 Formato Sugerido

### Tema de Colores
- **Primario:** Azul (#1F77B4) - Representa agua
- **Secundario:** Verde (#2CA02C) - Sostenibilidad
- **Alerta:** Rojo (#D62728) - Alto consumo/escasez

### Fuentes
- Títulos: Segoe UI Semibold, 14-16pt
- Texto: Segoe UI, 10-12pt
- KPIs: Segoe UI Bold, 24-32pt

---

## 🔍 Consultas SQL de Validación

Antes de analizar en Power BI, puedes validar los datos con SQLite:

```bash
sqlite3 database/datawarehouse.db
```

```sql
-- Verificar totales
SELECT
    'Total Huella Hídrica (L)' AS Metrica,
    SUM(Huella_Hidrica) AS Valor
FROM HECHOS_HUELLA_HIDRICA_IA
UNION ALL
SELECT 'Total Prompts', SUM(Total_Prompts)
FROM HECHOS_HUELLA_HIDRICA_IA
UNION ALL
SELECT 'Total Sesiones', SUM(Numero_Sesiones)
FROM HECHOS_HUELLA_HIDRICA_IA;

-- Top 5 países
SELECT
    g.Pais,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Numero_Sesiones) AS Sesiones
FROM HECHOS_HUELLA_HIDRICA_IA h
JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais
ORDER BY Total_Litros DESC
LIMIT 5;

-- Distribución por nivel académico
SELECT
    e.Nivel_Academico,
    COUNT(DISTINCT h.idTiempo) AS Dias_Activos,
    SUM(h.Numero_Sesiones) AS Total_Sesiones,
    ROUND(SUM(h.Huella_Hidrica), 2) AS Total_Litros
FROM HECHOS_HUELLA_HIDRICA_IA h
JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Nivel_Academico
ORDER BY Total_Litros DESC;
```

---

## 📝 Checklist de Implementación

- [x] Data Warehouse creado (SQLite)
- [x] Dimensiones cargadas (3 tablas)
- [x] Hechos cargados (9,586 registros)
- [ ] Power BI conectado
- [ ] Relaciones verificadas
- [ ] Medidas DAX creadas
- [ ] Visualizaciones implementadas
- [ ] Dashboard publicado

---

## 🆘 Solución de Problemas

### Problema: Power BI no encuentra el archivo SQLite

**Solución:** Usa la ruta absoluta completa:
```
/Users/matiasvidal/dev/ProyectoBD2/dw_hefesto_sql/database/datawarehouse.db
```

### Problema: Error "No se pudo cargar datos"

**Solución:** Verifica que tengas el conector SQLite instalado. En macOS:
```bash
brew install sqlite3
```

### Problema: Las relaciones no se crean automáticamente

**Solución:** Créalas manualmente en Vista de Modelo usando los campos idGeografia, idEstudiante, idTiempo.

### Problema: Los valores no coinciden

**Solución:** Asegúrate de sumar, no contar. Usa `SUM()` en lugar de `COUNT()` para las métricas.

---

## 🎯 Próximos Pasos

1. **Abrir Power BI** y conectar al archivo `datawarehouse.db`
2. **Verificar relaciones** en Vista de Modelo
3. **Crear medidas DAX** de la lista de arriba
4. **Construir visualizaciones** según las sugerencias
5. **Publicar dashboard** en Power BI Service (opcional)
6. **Programar actualización incremental** con el script `actualizacion_incremental.py`

---

**¡Tu Data Warehouse está listo para análisis! 🎉**

Para más consultas SQL de ejemplo, revisa:
`3_modelo_logico/sql/03_consultas_ejemplo.sql`
