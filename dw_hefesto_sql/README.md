# Data Warehouse - Huella Hídrica del Uso de IA en Estudiantes

**Metodología:** Hefesto
**Base de Datos:** MySQL 8.0 (Docker)
**Visualización:** Power BI
**Fecha:** Octubre 2025
**Última actualización:** Noviembre 2025 - Migración a MySQL + Docker

---

## 📋 Descripción del Proyecto

Este proyecto implementa un **Data Warehouse** completo siguiendo la **metodología Hefesto** para analizar el impacto ambiental (específicamente la huella hídrica) del uso de asistentes de IA por parte de estudiantes a nivel global.

### Objetivos

- Analizar el consumo de agua estimado derivado del uso de IA académica
- Cruzar datos de uso de IA con niveles de escasez de agua por país
- Generar conciencia sobre el impacto ambiental de la tecnología
- Proporcionar análisis estratégico para toma de decisiones

---

## 🗂️ Estructura del Proyecto

```
ProyectoBD2/
│
├── dw_hefesto_sql/
│   │
│   ├── 1_analisis_requerimientos/
│   │   └── FASE1_ANALISIS_REQUERIMIENTOS.md    # Preguntas de negocio, indicadores
│   │
│   ├── 2_analisis_oltp/
│   │   └── FASE2_ANALISIS_OLTP.md              # Cálculos, correspondencias
│   │
│   ├── 3_modelo_logico/
│   │   ├── FASE3_MODELO_LOGICO.md              # Diseño del esquema en estrella
│   │   └── sql/
│   │       ├── 01_crear_dimensiones.sql        # Scripts SQL (referencia SQLite)
│   │       ├── 02_crear_hechos.sql
│   │       └── 03_consultas_ejemplo.sql
│   │
│   ├── 4_integracion_datos/
│   │   └── scripts/
│   │       ├── carga_inicial.py                # ETL: Carga inicial (MySQL)
│   │       └── actualizacion_incremental.py    # ETL: Actualizaciones (MySQL)
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py                         # ✨ Módulo de conexión MySQL
│   │
│   ├── database/
│   │   └── datawarehouse.db                    # [Obsoleto] SQLite (mantener compatibilidad)
│   │
│   ├── Pipfile                                 # Dependencias Python
│   └── README.md                               # Este archivo
│
├── mysql-init/
│   └── 01-schema.sql                           # ✨ Schema MySQL (auto-ejecutado)
│
├── archive (2)/
│   └── ai_assistant_usage_student_life.csv     # Dataset fuente: AI Usage
│
├── archive (3)/
│   └── cleaned_global_water_consumption.csv    # Dataset fuente: Water Consumption
│
├── docker-compose.yml                          # ✨ Configuración Docker MySQL
├── .env                                        # ✨ Variables de entorno (credenciales)
├── .gitignore                                  # Archivos ignorados por Git
└── INSTRUCCIONES_MYSQL_POWERBI.md              # ✨ Guía completa MySQL + Power BI
```

**✨ = Archivos nuevos de la migración a MySQL**

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- ✅ **Docker Desktop** (Windows/Mac) o **Docker Engine** (Linux)
  - Descargar: https://www.docker.com/products/docker-desktop
  - Verificar: `docker --version` y `docker-compose --version`

- ✅ **Python 3.13** (o compatible 3.8+)
  - Verificar: `python --version`

- ✅ **Power BI Desktop** (para visualizaciones)
  - Descargar: https://powerbi.microsoft.com/desktop/
  - MySQL Connector se instala con Power BI

### Guía de Inicio Rápido

**Para instrucciones detalladas paso a paso, consulta:**
📘 **[INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md)**

### Instalación Resumida

#### 1. Verificar archivos fuente CSV

```bash
# Los datasets deben estar en:
ProyectoBD2/
├── archive (2)/ai_assistant_usage_student_life.csv
└── archive (3)/cleaned_global_water_consumption.csv
```

#### 2. Levantar MySQL con Docker

```bash
# Desde la raíz del proyecto (ProyectoBD2/)
cd /home/marcosdon28/ProyectoBD2

# Levantar contenedor MySQL en segundo plano
docker-compose up -d

# Verificar que está corriendo
docker ps
# Deberías ver: datawarehouse_mysql
```

#### 3. Instalar dependencias Python

```bash
cd dw_hefesto_sql

# Opción A: Con pipenv (recomendado)
pipenv install
pipenv shell

# Opción B: Con pip directamente
pip install pandas numpy matplotlib mysql-connector-python python-dotenv
```

#### 4. Ejecutar carga inicial de datos

```bash
# Desde dw_hefesto_sql/
python 4_integracion_datos/scripts/carga_inicial.py
```

✅ **¡Listo!** El Data Warehouse está cargado y funcionando en MySQL.

---

## 📊 Modelo del Data Warehouse

### Esquema en Estrella

```
          DIM_GEOGRAFIA
                │
                │
    ┌───────────┼───────────┐
    │           │           │
DIM_ESTUDIANTE ─┤  HECHOS   ├─ DIM_TIEMPO
                │   (FACT)  │
                └───────────┘
```

### Tablas

| Tabla | Tipo | Registros | Descripción |
|-------|------|-----------|-------------|
| **DIM_GEOGRAFIA** | Dimensión | ~500 | Países + año + nivel de escasez de agua |
| **DIM_ESTUDIANTE** | Dimensión | ~21 | Nivel académico + disciplina |
| **DIM_TIEMPO** | Dimensión | ~366 | Fechas con jerarquía temporal |
| **HECHOS_HUELLA_HIDRICA_IA** | Hechos | ~9,586 | Métricas agregadas |

**Nota:** DIM_GEOGRAFIA tiene granularidad por año (20 países × 25 años = 500 combinaciones)

### Indicadores (Métricas)

1. **Huella_Hidrica**: Consumo de agua estimado en litros (TotalPrompts × 0.5 L)
2. **Total_Prompts**: Cantidad total de consultas a la IA
3. **Duracion_Total_Sesiones**: Tiempo total de uso en minutos
4. **Numero_Sesiones**: Conteo de sesiones de IA

---

## ⚙️ Ejecución del ETL

### Paso 1: Carga Inicial

**⚠️ Prerequisito:** Docker debe estar corriendo con MySQL activo.

```bash
# Verificar que MySQL está corriendo
docker ps | grep datawarehouse_mysql

# Ejecutar carga inicial
cd 4_integracion_datos/scripts
python carga_inicial.py
```

**¿Qué hace este script?**
1. Se conecta a MySQL (usando credenciales de `.env`)
2. Limpia las tablas existentes (TRUNCATE)
3. Extrae datos de los CSVs fuente
4. Limpia y transforma los datos
5. Carga las 3 dimensiones en MySQL
6. Carga la tabla de hechos agregada en MySQL

**Salida esperada:**
```
================================================================================
                    CARGA INICIAL DEL DATA WAREHOUSE
               Huella Hídrica del Uso de IA en Estudiantes
================================================================================
Inicio: 2025-11-06 15:30:00
================================================================================

[PASO 0] VERIFICANDO CONEXIÓN Y LIMPIANDO TABLAS
   ✓ Conexión a MySQL exitosa
   ✓ Tablas limpias, listas para carga inicial

[PASO 1] EXTRACCIÓN DE DATOS
   📥 Extrayendo AI Assistant Usage...
      ✓ 10,000 registros extraídos
   📥 Extrayendo Global Water Consumption...
      ✓ 500 registros extraídos

[PASO 2] TRANSFORMACIÓN Y LIMPIEZA DE DATOS
   ✓ 10,000 registros limpios de AI Usage
   ✓ 500 registros limpios de Water Consumption

[PASO 3] CARGA DE DIMENSIONES
   🌍 Cargando DIM_GEOGRAFIA...
      ✓ 500 combinaciones (país + año) cargadas
      ✓ Países únicos: 20
      ✓ Rango de años: 2000 - 2024
   🎓 Cargando DIM_ESTUDIANTE...
      ✓ 21 combinaciones cargadas
   📅 Cargando DIM_TIEMPO...
      ✓ 366 fechas cargadas

[PASO 4] CARGA DE HECHOS
   📊 Cargando HECHOS_HUELLA_HIDRICA_IA...
      ✓ 9,586 hechos cargados exitosamente
      ✓ Huella hídrica total: 123,456.00 litros

================================================================================
                         ✅ CARGA INICIAL COMPLETADA
================================================================================

PRÓXIMOS PASOS:
   1. Validar datos: docker exec -it datawarehouse_mysql mysql -u dw_user -pdw_pass datawarehouse_db
   2. Ver resumen: SELECT * FROM V_RESUMEN_HECHOS;
   3. Conectar Power BI usando MySQL Connector
```

### Paso 2: Actualización Incremental (Opcional)

Para actualizar el DW con datos nuevos (ventana de 30 días):

```bash
python actualizacion_incremental.py
```

**Política de actualización:**
- Frecuencia: Diaria
- Ventana: Últimos 30 días
- Dimensiones: Carga total (son pequeñas)
- Hechos: Reemplazo de ventana temporal

---

## 🔍 Consultas y Análisis

### Validar la Carga

Verifica que los datos se cargaron correctamente en MySQL:

```bash
# Conectarse a MySQL desde el contenedor Docker
docker exec -it datawarehouse_mysql mysql -u dw_user -pdw_pass datawarehouse_db
```

Dentro de MySQL:

```sql
-- Ver totales por tabla
SELECT COUNT(*) AS Total FROM DIM_GEOGRAFIA;              -- Debe ser ~500
SELECT COUNT(*) AS Total FROM DIM_ESTUDIANTE;             -- Debe ser ~21
SELECT COUNT(*) AS Total FROM DIM_TIEMPO;                 -- Debe ser ~366
SELECT COUNT(*) AS Total FROM HECHOS_HUELLA_HIDRICA_IA;   -- Debe ser ~9,586

-- Ver resumen de hechos (usando vista)
SELECT * FROM V_RESUMEN_HECHOS;

-- Ver ejemplos de datos completos
SELECT * FROM V_HECHOS_COMPLETO LIMIT 10;

-- Salir de MySQL
EXIT;
```

### Consultas de Análisis

**Consultas SQL de ejemplo (adaptadas a MySQL):**

```sql
-- 1. Consumo de agua por país (Top 10)
SELECT
    g.Pais,
    g.Nivel_Escasez_Agua,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Total_Prompts) AS Total_Prompts,
    ROUND(SUM(h.Huella_Hidrica) / SUM(h.Numero_Sesiones), 2) AS Litros_Por_Sesion
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_GEOGRAFIA g ON h.idGeografia = g.idGeografia
GROUP BY g.Pais, g.Nivel_Escasez_Agua
ORDER BY Total_Litros DESC
LIMIT 10;

-- 2. Uso por disciplina académica
SELECT
    e.Disciplina,
    e.Nivel_Academico,
    SUM(h.Total_Prompts) AS Total_Prompts,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Numero_Sesiones) AS Total_Sesiones
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_ESTUDIANTE e ON h.idEstudiante = e.idEstudiante
GROUP BY e.Disciplina, e.Nivel_Academico
ORDER BY Total_Prompts DESC;

-- 3. Tendencia temporal mensual
SELECT
    t.Anio,
    t.Mes,
    t.Nombre_Mes,
    SUM(h.Huella_Hidrica) AS Total_Litros,
    SUM(h.Total_Prompts) AS Total_Prompts
FROM HECHOS_HUELLA_HIDRICA_IA h
INNER JOIN DIM_TIEMPO t ON h.idTiempo = t.idTiempo
GROUP BY t.Anio, t.Mes, t.Nombre_Mes
ORDER BY t.Anio, t.Mes;
```

**Referencia adicional:** Scripts SQL originales (SQLite) en `3_modelo_logico/sql/03_consultas_ejemplo.sql`

---

## 📈 Conectar con Power BI

**📘 Para instrucciones detalladas con capturas de pantalla, consulta:**
**[INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md) - Sección "Paso 4: Conectar Power BI a MySQL"**

### Resumen de Conexión

#### 1. Abrir Power BI Desktop

- Click en **Obtener datos** (Get Data)
- Buscar: **MySQL database**
- Click en **Conectar**

#### 2. Configurar Conexión

**Parámetros:**

| Campo | Valor |
|-------|-------|
| Servidor | `localhost` |
| Base de datos | `datawarehouse_db` |
| Usuario | `dw_user` |
| Contraseña | `dw_pass` |

#### 3. Seleccionar Tablas

Marcar las siguientes tablas para importar:

- ✅ `DIM_GEOGRAFIA`
- ✅ `DIM_ESTUDIANTE`
- ✅ `DIM_TIEMPO`
- ✅ `HECHOS_HUELLA_HIDRICA_IA`
- ✅ `V_HECHOS_COMPLETO` (Vista pre-unida - **recomendada**)

#### 4. Verificar Relaciones

Power BI debería crear automáticamente las relaciones:

| Desde | Hasta | Campo | Cardinalidad |
|-------|-------|-------|--------------|
| DIM_GEOGRAFIA | HECHOS | idGeografia | 1:* |
| DIM_ESTUDIANTE | HECHOS | idEstudiante | 1:* |
| DIM_TIEMPO | HECHOS | idTiempo | 1:* |

**Nota:** Si usas la vista `V_HECHOS_COMPLETO`, ya tiene todas las dimensiones unidas (no necesitas crear relaciones).

### Medidas DAX Sugeridas

```dax
// KPIs principales
Total Huella Hídrica = SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica])

Total Sesiones = SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])

Total Prompts = SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts])

Litros por Sesión =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Huella_Hidrica]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )

Prompts por Sesión =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Total_Prompts]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )

Duración Promedio =
    DIVIDE(
        SUM(HECHOS_HUELLA_HIDRICA_IA[Duracion_Total_Sesiones]),
        SUM(HECHOS_HUELLA_HIDRICA_IA[Numero_Sesiones])
    )
```

### Visualizaciones Sugeridas

1. **Gráfico de Barras**: Top 10 países por consumo de agua
2. **Gráfico de Líneas**: Tendencia temporal mensual
3. **Matriz**: Disciplina × Nivel Académico (heatmap)
4. **Gráfico de Barras Agrupadas**: Consumo vs Escasez por país
5. **Tarjetas (Cards)**: KPIs principales (Huella Total, Sesiones, Prompts)
6. **Gráfico de Anillos**: Distribución por nivel académico
7. **Tabla**: Detalle de top combinaciones país + disciplina

---

## 📚 Documentación de las Fases Hefesto

Cada fase de la metodología Hefesto está completamente documentada:

### Fase 1: Análisis de Requerimientos
📄 `1_analisis_requerimientos/FASE1_ANALISIS_REQUERIMIENTOS.md`

- Preguntas de negocio
- Identificación de indicadores y perspectivas
- Modelo conceptual

### Fase 2: Análisis de OLTP
📄 `2_analisis_oltp/FASE2_ANALISIS_OLTP.md`

- Cálculo de indicadores (fórmulas)
- Correspondencias con fuentes de datos
- Nivel de granularidad
- Modelo conceptual ampliado

### Fase 3: Modelo Lógico
📄 `3_modelo_logico/FASE3_MODELO_LOGICO.md`

- Diseño del esquema en estrella
- Definición de tablas de dimensiones
- Definición de tabla de hechos
- Diagramas y relaciones
- Scripts SQL completos

### Fase 4: Integración de Datos
📄 Scripts Python en `4_integracion_datos/scripts/`

- Proceso ETL de carga inicial
- Proceso ETL de actualización incremental
- Políticas de actualización

---

## 🔧 Notas Técnicas

### Arquitectura MySQL + Docker

**Ventajas de la arquitectura actual:**

✅ **Portabilidad:** Docker permite levantar el entorno en cualquier máquina
✅ **Escalabilidad:** MySQL soporta mayores volúmenes que SQLite
✅ **Compatibilidad:** Power BI tiene soporte nativo para MySQL
✅ **Persistencia:** Volúmenes Docker mantienen datos entre reinicios
✅ **Profesional:** Preparado para entornos de producción

**Configuración Docker:**
- **Imagen:** MySQL 8.0
- **Puerto:** 3306 (expuesto para conexiones externas)
- **Volumen:** `mysql_data` (persistente)
- **Charset:** UTF8MB4 (soporte Unicode completo)
- **Engine:** InnoDB (transacciones ACID, FK, índices)

**Credenciales (por defecto en `.env`):**
```
Host: localhost:3306
Database: datawarehouse_db
Usuario: dw_user
Contraseña: dw_pass
```

### Factor de Consumo de Agua

El proyecto utiliza un **factor hipotético de 0.5 litros/prompt** que representa:
- Energía consumida por el procesamiento de IA
- Agua usada en refrigeración de centros de datos
- Basado en estimaciones de huella de carbono de modelos LLM

⚠️ **Nota:** Este factor es educativo y puede ajustarse según estudios reales.

### Asignación Geográfica

El dataset de AI Usage **NO incluye información geográfica**. Por tanto:
- Se asignan países **aleatoriamente** a las sesiones
- La asignación es **reproducible** (seed=42)
- Permite relacionar ambas fuentes de datos
- Los análisis geográficos son **ilustrativos**

### Granularidad de DIM_GEOGRAFIA

**Novedad en esta versión:**
- DIM_GEOGRAFIA ahora incluye **granularidad por año**
- Permite analizar variación temporal de escasez de agua por país
- 20 países × 25 años (2000-2024) = **500 combinaciones**
- Ejemplo: "India - 2020 - High" vs "India - 2024 - Extreme"

### Optimizaciones

- **Índices creados** en todas las FK y campos de búsqueda frecuente
- **Vistas SQL** (V_RESUMEN_HECHOS, V_HECHOS_COMPLETO)
- **Agregación previa** en la tabla de hechos por (país, estudiante, fecha)
- **Integridad referencial** con FOREIGN KEYS y restricciones CHECK
- **Motor InnoDB** para transacciones ACID y rendimiento óptimo

---

## 🐛 Solución de Problemas

### 1. Docker: "Can't connect to MySQL server"

**Causa:** Docker no está corriendo o MySQL no está levantado.

**Solución:**
```bash
# Verificar que Docker está corriendo
docker ps

# Si no hay contenedores, levantar MySQL
docker-compose up -d

# Verificar logs del contenedor
docker logs datawarehouse_mysql

# Verificar health check
docker inspect datawarehouse_mysql | grep Health
```

### 2. Python: "Access denied for user 'dw_user'"

**Causa:** Credenciales incorrectas o archivo `.env` no existe.

**Solución:**
```bash
# Verificar que existe .env en la raíz del proyecto
ls -la /home/marcosdon28/ProyectoBD2/.env

# Verificar contenido
cat /home/marcosdon28/ProyectoBD2/.env

# Debería contener:
# MYSQL_USER=dw_user
# MYSQL_PASSWORD=dw_pass
# MYSQL_DATABASE=datawarehouse_db
```

### 3. Python: "ModuleNotFoundError: No module named 'mysql'"

**Causa:** Dependencias no instaladas.

**Solución:**
```bash
# Instalar dependencias
cd dw_hefesto_sql
pipenv install

# O con pip:
pip install mysql-connector-python python-dotenv pandas numpy
```

### 4. Power BI: No encuentra el conector MySQL

**Causa:** MySQL Connector no instalado o desactualizado.

**Solución:**
1. Descargar e instalar: https://dev.mysql.com/downloads/connector/net/
2. Reiniciar Power BI Desktop
3. Verificar en "Obtener datos" que aparece "MySQL database"

### 5. Docker: Puerto 3306 ya está en uso

**Causa:** Otro servicio (MySQL local) está usando el puerto.

**Solución:**
```bash
# Verificar qué usa el puerto 3306
# Linux/Mac:
lsof -i :3306

# Windows:
netstat -ano | findstr :3306

# Opciones:
# 1. Detener el MySQL local
# 2. O cambiar el puerto en docker-compose.yml:
#    ports:
#      - "3307:3306"  # Usar puerto 3307 en host
```

### 6. ETL: "Archivos CSV no encontrados"

**Causa:** Rutas incorrectas a los datasets.

**Solución:**
```bash
# Verificar que los archivos existen:
ls -la /home/marcosdon28/ProyectoBD2/archive\ \(2\)/
ls -la /home/marcosdon28/ProyectoBD2/archive\ \(3\)/

# Deben existir:
# - ai_assistant_usage_student_life.csv
# - cleaned_global_water_consumption.csv
```

### 7. MySQL: "Table doesn't exist"

**Causa:** Script de inicialización no se ejecutó.

**Solución:**
```bash
# Recrear el contenedor (esto ejecutará el script de inicialización)
docker-compose down -v
docker-compose up -d

# Esperar 10 segundos y verificar tablas
docker exec -it datawarehouse_mysql mysql -u dw_user -pdw_pass -e "USE datawarehouse_db; SHOW TABLES;"
```

### 8. Power BI: No muestra relaciones automáticamente

**Causa:** Power BI no detecta las relaciones.

**Solución:**
1. Ir a vista de **Modelo** (icono de diagrama)
2. Crear relaciones manualmente arrastrando campos
3. O importar la vista `V_HECHOS_COMPLETO` que ya tiene todo unido

**📘 Para más problemas y soluciones, consulta:**
[INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md) - Sección "Solución de problemas"

---

## 📊 Resultados Esperados

### KPIs Globales (aproximados)

Los valores pueden variar ligeramente dependiendo de la asignación aleatoria de países (seed=42):

- **Huella Hídrica Total:** ~123,000 - 125,000 litros
- **Total de Prompts:** ~250,000
- **Total de Sesiones:** ~10,000
- **Duración Total:** ~200,000 minutos
- **Promedio Litros/Sesión:** ~12.5 L
- **Promedio Prompts/Sesión:** ~25

### Dimensiones

- **Geografía:** 500 combinaciones (20 países × 25 años)
- **Estudiantes:** 21 combinaciones (3 niveles × 7 disciplinas)
- **Tiempo:** 366 fechas (junio 2024 - junio 2025)
- **Hechos agregados:** ~9,586 registros únicos

---

## 👥 Créditos

**Proyecto Académico:** Base de Datos 2 - UCC
**Metodología:** Hefesto
**Fuentes de Datos:**
- [AI Assistant Usage in Student Life (Kaggle)](https://www.kaggle.com/datasets/ayeshasal89/ai-assistant-usage-in-student-life-synthetic)
- [Global Water Consumption Dataset (Kaggle)](https://www.kaggle.com/datasets/atharvasoundankar/global-water-consumption-dataset-2000-2024)

---

## 📝 Licencia

Este proyecto es de uso académico y educativo.

---

## 🚀 Próximos Pasos

### Para comenzar (primera vez):

1. ✅ **Levantar Docker MySQL:**
   ```bash
   docker-compose up -d
   ```

2. ✅ **Instalar dependencias Python:**
   ```bash
   cd dw_hefesto_sql && pipenv install
   ```

3. ✅ **Ejecutar carga inicial:**
   ```bash
   python 4_integracion_datos/scripts/carga_inicial.py
   ```

4. ✅ **Validar datos en MySQL:**
   ```bash
   docker exec -it datawarehouse_mysql mysql -u dw_user -pdw_pass datawarehouse_db
   ```

5. 📊 **Conectar Power BI:**
   - Seguir instrucciones en [INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md)
   - Crear dashboard con visualizaciones sugeridas

6. 📈 **Programar actualización incremental:**
   ```bash
   # Ejecutar manualmente
   python 4_integracion_datos/scripts/actualizacion_incremental.py

   # O programar con cron (Linux/Mac)
   0 2 * * * cd /ruta/proyecto && python actualizacion_incremental.py

   # O Task Scheduler (Windows)
   ```

7. 📄 **Documentar hallazgos** en informe final

### Comandos útiles:

```bash
# Ver logs de MySQL
docker logs datawarehouse_mysql

# Detener MySQL
docker-compose down

# Reiniciar MySQL
docker restart datawarehouse_mysql

# Backup de la base de datos
docker exec datawarehouse_mysql mysqldump -u dw_user -pdw_pass datawarehouse_db > backup.sql

# Probar conexión Python a MySQL
python dw_hefesto_sql/config/database.py
```

---

## 📚 Recursos Adicionales

- 📘 **[INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md)** - Guía completa paso a paso
- 📄 **Documentación de fases Hefesto** - En cada carpeta `1_`, `2_`, `3_`, `4_`
- 🐳 **Docker Compose:** https://docs.docker.com/compose/
- 🐬 **MySQL 8.0:** https://dev.mysql.com/doc/
- 📊 **Power BI:** https://docs.microsoft.com/power-bi/

---

**¿Preguntas o problemas?**
1. Consulta [INSTRUCCIONES_MYSQL_POWERBI.md](../INSTRUCCIONES_MYSQL_POWERBI.md) - Sección "Solución de problemas"
2. Revisa la documentación en cada carpeta de fase
3. Verifica los comentarios en los scripts SQL y Python
