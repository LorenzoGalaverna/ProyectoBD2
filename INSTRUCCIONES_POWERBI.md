# 📊 Instrucciones: Conectar Power BI al Data Warehouse PostgreSQL

## 🎯 Objetivo
Conectar Power BI Desktop directamente a la base de datos PostgreSQL para análisis en tiempo real del Data Warehouse de Huella Hídrica del Uso de IA.

---

## 📋 Pre-requisitos

### 1. **Contenedor PostgreSQL corriendo**
```bash
# Verificar que el contenedor está activo
docker ps | grep datawarehouse_postgres

# Si no está corriendo, iniciarlo
docker-compose up -d
```

### 2. **Instalar Driver ODBC de PostgreSQL**

#### Windows:
1. Descargar el driver desde: https://www.postgresql.org/ftp/odbc/versions/msi/
2. Instalar `psqlodbc_x64.msi` (versión 64-bit)
3. Reiniciar Power BI Desktop

#### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install odbc-postgresql

# Mac (Homebrew)
brew install psqlodbc
```

---

## 🔌 PASO 1: Conectar Power BI a PostgreSQL

### 1.1 Abrir Power BI Desktop
- Iniciar Power BI Desktop
- Clic en **"Obtener datos"** (Get Data)

### 1.2 Seleccionar PostgreSQL
1. En la ventana de conectores, buscar **"PostgreSQL database"**
2. Clic en **"Conectar"**

### 1.3 Configurar la conexión

**Parámetros de conexión:**
```
Servidor:        localhost
Base de datos:   datawarehouse_db
```

**Opciones avanzadas (opcional):**
- Instrucción SQL: *(dejar vacío para importar todas las tablas)*
- Modo de conectividad de datos: **Importar** (recomendado)

Clic en **"Aceptar"**

### 1.4 Autenticación

Seleccionar **"Base de datos"** en el panel izquierdo

**Credenciales:**
```
Nombre de usuario:  dwuser
Contraseña:         dwpass
```

Clic en **"Conectar"**

---

## 📊 PASO 2: Importar Tablas y Vistas

### 2.1 Seleccionar objetos de la base de datos

En el **Navegador** que aparece, verás:

**✅ Tablas a importar:**
- ☑️ `DIM_GEOGRAFIA` (500 registros)
- ☑️ `DIM_ESTUDIANTE` (21 registros)
- ☑️ `DIM_TIEMPO` (366 registros)
- ☑️ `HECHOS_HUELLA_HIDRICA_IA` (9,586 registros)

**✅ Vistas a importar (opcional pero recomendado):**
- ☑️ `V_RESUMEN_HECHOS` - Vista resumen con KPIs principales
- ☑️ `V_HECHOS_COMPLETO` - Vista desnormalizada para análisis rápido

### 2.2 Vista previa
- Puedes hacer clic en cada tabla para ver una vista previa de los datos
- Verifica que las columnas preserven las mayúsculas (ej: `Pais`, `Anio`)

### 2.3 Cargar datos
- Seleccionar las 4 tablas + 2 vistas
- Clic en **"Cargar"** (Load)
- Esperar a que se importen los datos

---

## 🔗 PASO 3: Crear Relaciones (Modelo de Datos)

Power BI debería detectar automáticamente las relaciones por los nombres de las columnas. Si no:

### 3.1 Ir a Vista de Modelo
- Clic en el ícono de **"Modelo"** (Model) en el panel izquierdo

### 3.2 Crear relaciones manualmente (si es necesario)

**RELACIÓN 1: Geografia → Hechos**
```
De:   DIM_GEOGRAFIA[idGeografia]
A:    HECHOS_HUELLA_HIDRICA_IA[idGeografia]
Cardinalidad:  Varios a uno (*:1)
Dirección de filtro cruzado:  Ambas (Both)
```

**RELACIÓN 2: Estudiante → Hechos**
```
De:   DIM_ESTUDIANTE[idEstudiante]
A:    HECHOS_HUELLA_HIDRICA_IA[idEstudiante]
Cardinalidad:  Varios a uno (*:1)
Dirección de filtro cruzado:  Ambas (Both)
```

**RELACIÓN 3: Tiempo → Hechos**
```
De:   DIM_TIEMPO[idTiempo]
A:    HECHOS_HUELLA_HIDRICA_IA[idTiempo]
Cardinalidad:  Varios a uno (*:1)
Dirección de filtro cruzado:  Ambas (Both)
```

### 3.3 Verificar el esquema estrella
Deberías ver:
- **Tabla de hechos** en el centro: `HECHOS_HUELLA_HIDRICA_IA`
- **3 dimensiones** alrededor: Geografia, Estudiante, Tiempo

---

## 📈 PASO 4: Crear Medidas DAX

### 4.1 Crear una nueva tabla para medidas
1. En Vista de Datos, clic derecho en el panel de campos
2. "Nueva tabla" → Nombrarla `_Medidas`

### 4.2 Medidas básicas esenciales

```dax
// ============================================================================
// MEDIDAS PRINCIPALES
// ============================================================================

Total Huella Hídrica =
SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica])

Total Prompts =
SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts])

Total Sesiones =
SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])

Duración Total (Minutos) =
SUM(HECHOS_HUELLA_HIDRICA_IA[Duracion_Total_Sesiones])

// ============================================================================
// PROMEDIOS
// ============================================================================

Huella Promedio por Sesión =
DIVIDE([Total Huella Hídrica], [Total Sesiones], 0)

Prompts Promedio por Sesión =
DIVIDE([Total Prompts], [Total Sesiones], 0)

Duración Promedio por Sesión =
DIVIDE([Duración Total (Minutos)], [Total Sesiones], 0)

// ============================================================================
// ANÁLISIS DE ESCASEZ DE AGUA
// ============================================================================

Consumo en Zonas de Alta Escasez =
CALCULATE(
    [Total Huella Hídrica],
    DIM_GEOGRAFIA[Nivel_Escasez_Agua] = "High"
)

Consumo en Zonas de Escasez Moderada =
CALCULATE(
    [Total Huella Hídrica],
    DIM_GEOGRAFIA[Nivel_Escasez_Agua] = "Moderate"
)

% Consumo en Zonas de Riesgo =
VAR ConsumoTotal = [Total Huella Hídrica]
VAR ConsumoRiesgo =
    CALCULATE(
        [Total Huella Hídrica],
        DIM_GEOGRAFIA[Nivel_Escasez_Agua] IN {"High", "Moderate"}
    )
RETURN
DIVIDE(ConsumoRiesgo, ConsumoTotal, 0)

// ============================================================================
// ÍNDICES Y RANKINGS
// ============================================================================

Índice de Riesgo Hídrico =
VAR Consumo = [Total Huella Hídrica]
VAR FactorEscasez =
    SWITCH(
        SELECTEDVALUE(DIM_GEOGRAFIA[Nivel_Escasez_Agua]),
        "Low", 1,
        "Moderate", 2,
        "High", 3,
        1
    )
RETURN
Consumo * FactorEscasez

Ranking País por Consumo =
RANKX(
    ALL(DIM_GEOGRAFIA[Pais]),
    [Total Huella Hídrica],
    ,
    DESC,
    DENSE
)

// ============================================================================
// ANÁLISIS TEMPORAL
// ============================================================================

Consumo Mes Anterior =
CALCULATE(
    [Total Huella Hídrica],
    DATEADD(DIM_TIEMPO[Fecha], -1, MONTH)
)

Variación vs Mes Anterior =
VAR Actual = [Total Huella Hídrica]
VAR Anterior = [Consumo Mes Anterior]
RETURN
DIVIDE(Actual - Anterior, Anterior, 0)

Variación % =
FORMAT([Variación vs Mes Anterior], "0.0%")

// ============================================================================
// CONTADORES
// ============================================================================

Países Analizados =
DISTINCTCOUNT(DIM_GEOGRAFIA[Pais])

Disciplinas Únicas =
DISTINCTCOUNT(DIM_ESTUDIANTE[Disciplina])

Días con Actividad =
DISTINCTCOUNT(DIM_TIEMPO[Fecha])
```

---

## 🎨 PASO 5: Visualizaciones Recomendadas

### 📊 Dashboard Principal: "Impacto Ambiental de IA"

#### **PÁGINA 1: Resumen Ejecutivo**

**KPIs Principales (Tarjetas):**
1. Total Huella Hídrica → Formato: "28,037.5 L"
2. Total Sesiones → Formato: "10,000"
3. Países Analizados → Formato: "20"
4. % Consumo en Zonas de Riesgo → Formato: "72%"

**Gráfico 1: Tendencia Temporal**
- Tipo: Gráfico de líneas
- Eje X: `DIM_TIEMPO[Fecha]` (agrupado por Mes)
- Eje Y: `[Total Huella Hídrica]`
- Título: "Evolución Mensual de Huella Hídrica"

**Gráfico 2: Top 10 Países**
- Tipo: Gráfico de barras horizontales
- Eje Y: `DIM_GEOGRAFIA[Pais]`
- Eje X: `[Total Huella Hídrica]`
- Ordenar: Descendente
- Filtro: Top 10

#### **PÁGINA 2: Análisis de Escasez de Agua**

**Gráfico 3: Consumo por Nivel de Escasez**
- Tipo: Gráfico de barras apiladas
- Eje X: `DIM_GEOGRAFIA[Nivel_Escasez_Agua]`
- Eje Y: `[Total Huella Hídrica]`
- Colores personalizados:
  - Low = Verde (#2ECC71)
  - Moderate = Amarillo (#F39C12)
  - High = Rojo (#E74C3C)

**Gráfico 4: Mapa Geográfico**
- Tipo: Mapa
- Ubicación: `DIM_GEOGRAFIA[Pais]`
- Tamaño de burbuja: `[Total Huella Hídrica]`
- Color: `DIM_GEOGRAFIA[Nivel_Escasez_Agua]`

**Tabla: Países en Alto Riesgo**
- Columnas:
  - `DIM_GEOGRAFIA[Pais]`
  - `DIM_GEOGRAFIA[Nivel_Escasez_Agua]`
  - `[Total Huella Hídrica]`
  - `[Índice de Riesgo Hídrico]`
- Filtro: `Nivel_Escasez_Agua = "High"`
- Ordenar: Por Índice de Riesgo descendente

#### **PÁGINA 3: Análisis Académico**

**Gráfico 5: Matriz Disciplina × Nivel Académico**
- Tipo: Matriz
- Filas: `DIM_ESTUDIANTE[Disciplina]`
- Columnas: `DIM_ESTUDIANTE[Nivel_Academico]`
- Valores: `[Total Huella Hídrica]`, `[Total Prompts]`
- Formato condicional: Barras de datos

**Gráfico 6: Distribución por Nivel Académico**
- Tipo: Gráfico de anillos (Donut)
- Leyenda: `DIM_ESTUDIANTE[Nivel_Academico]`
- Valores: `[Total Sesiones]`

#### **PÁGINA 4: Análisis Temporal de Escasez**

**Gráfico 7: Evolución de Escasez por País**
- Tipo: Gráfico de líneas múltiples
- Eje X: `DIM_GEOGRAFIA[Anio]`
- Eje Y: Conteo de países
- Leyenda: `DIM_GEOGRAFIA[Nivel_Escasez_Agua]`
- Áreas apiladas

**Gráfico 8: Matriz de Calor País × Año**
- Tipo: Tabla con formato condicional
- Filas: `DIM_GEOGRAFIA[Pais]`
- Columnas: `DIM_GEOGRAFIA[Anio]`
- Valores: `DIM_GEOGRAFIA[Nivel_Escasez_Agua]`
- Formato: Escala de colores (Verde → Amarillo → Rojo)

---

## ✅ PASO 6: Validación de Datos

### Valores esperados para verificar importación correcta:

```
✓ Total Huella Hídrica:  28,037.50 litros
✓ Total Prompts:         56,075
✓ Total Sesiones:        10,000
✓ Registros en Hechos:   9,586
✓ Países únicos:         20
✓ Combinaciones Geografia: 500
✓ Fechas:                366 (Jun 2024 - Jun 2025)
```

### Consulta SQL para verificar datos (opcional):
```sql
-- Ejecutar en PostgreSQL
SELECT * FROM V_RESUMEN_HECHOS;
```

---

## 🔄 Actualización de Datos

### Opción 1: Actualización Manual
1. En Power BI Desktop → Pestaña **"Inicio"**
2. Clic en **"Actualizar"** (Refresh)
3. Los datos se recargarán desde PostgreSQL

### Opción 2: Actualización Automática (Power BI Service)
1. Publicar el informe en Power BI Service
2. Configurar actualización programada:
   - Configuración del conjunto de datos
   - Actualización programada
   - Frecuencia: Diaria / Semanal

### Actualizar el Data Warehouse (ETL):
```bash
# Carga incremental (últimos 30 días)
cd dw_hefesto_sql
python3 4_integracion_datos/scripts/actualizacion_incremental.py

# Después de actualizar, refrescar Power BI
```

---

## 🛠️ Solución de Problemas

### Problema 1: No aparece el conector PostgreSQL
**Solución:** Instalar el driver ODBC de PostgreSQL (ver Pre-requisitos)

### Problema 2: Error de conexión "Cannot connect to server"
**Solución:**
```bash
# Verificar que el contenedor está corriendo
docker ps | grep postgres

# Verificar puerto 5432 abierto
netstat -an | grep 5432

# Reiniciar contenedor si es necesario
docker-compose restart
```

### Problema 3: Nombres de columnas en minúsculas
**Solución:** El schema ya está configurado con comillas dobles para preservar mayúsculas. Si aparecen en minúsculas, refrescar la conexión.

### Problema 4: Relaciones no se crean automáticamente
**Solución:** Crear manualmente siguiendo el PASO 3

### Problema 5: Datos no se actualizan
**Solución:**
1. Verificar que el ETL se ejecutó correctamente
2. En Power BI: Inicio → Actualizar
3. Si persiste: Eliminar y recrear la conexión

---

## 📚 Recursos Adicionales

### Documentación del Proyecto:
- [README.md](README.md) - Documentación completa del proyecto
- [docker-compose.yml](docker-compose.yml) - Configuración de PostgreSQL
- [.env](.env) - Variables de entorno

### Documentación Externa:
- [Power BI + PostgreSQL](https://learn.microsoft.com/es-es/power-bi/connect-data/desktop-connect-postgresql)
- [DAX Reference](https://dax.guide/)
- [PostgreSQL ODBC Driver](https://odbc.postgresql.org/)

---

## 🎯 Insights Clave a Descubrir

Una vez conectado, podrás responder preguntas como:

1. **¿Qué países consumen más agua por uso de IA?**
2. **¿El uso de IA es mayor en zonas con escasez de agua?**
3. **¿Qué disciplinas académicas tienen mayor huella hídrica?**
4. **¿Cómo ha evolucionado la escasez de agua en los últimos años?**
5. **¿Existe correlación entre nivel académico y consumo?**
6. **¿Qué países requieren atención urgente?** (Alta escasez + Alto consumo)

---

## 🚀 Próximos Pasos

1. ✅ Conectar Power BI a PostgreSQL
2. ✅ Importar tablas y vistas
3. ✅ Verificar relaciones
4. ✅ Crear medidas DAX
5. ✅ Construir dashboard
6. ✅ Publicar en Power BI Service
7. ✅ Compartir insights con el equipo

---

## 📞 Soporte

Si tienes problemas:
1. Verificar que PostgreSQL está corriendo: `docker ps`
2. Revisar logs: `docker logs datawarehouse_postgres`
3. Probar conexión desde terminal: `psql -h localhost -U dwuser -d datawarehouse_db`

---

**¡Tu Data Warehouse está listo para análisis avanzado en Power BI! 🌍💧📊**
