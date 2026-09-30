# Pre-entrega 6: Análisis de Datos Meteorológicos con DuckDB e SQL
**Curso:** Data Science II - Coderhouse  
**Alumno/a:** Jorgelina  

---

## 📌 Descripción del Proyecto

En este trabajo práctico utilizo **DuckDB** como motor de análisis de datos embebido para procesar un dataset de clima en formato CSV y Parquet sin necesidad de instalar o configurar un servidor de base de datos tradicional pesada.

Con DuckDB podemos ejecutar consultas SQL directamente sobre los archivos de datos (`.csv` o `.parquet`), logrando una excelente velocidad y simplicidad.

---

## 📂 Estructura del Repositorio

* `data/weather_data.csv`: Archivo con 1.461 registros de datos meteorológicos diarios (2012 - 2015).
* `data/weather_data.parquet`: Mismo dataset en formato Parquet comprimido.
* `analysis.sql`: Script en lenguaje SQL con las consultas del análisis.
* `analysis.py`: Script en Python que ejecuta la conexión a DuckDB en memoria y muestra los resultados.
* `Objetivo.md`: Enunciado y consignas del trabajo práctico.
* `.gitignore`: Configuración para excluir binarios de bases de datos y ejecutables.
* `README.md`: Este documento explicativo con las instrucciones y resultados.

---

## 🚀 Cómo Ejecutar el Análisis

### Opción 1: Ejecución en Python (Recomendado)
Para correr el script desde Python, asegurate de tener instalada la librería `duckdb`:

```bash
pip install duckdb pandas
```

Y luego ejecutá el archivo:
```bash
python analysis.py
```

### Opción 2: Ejecución mediante DuckDB CLI
Podés ejecutar directamente el archivo `.sql` desde la consola con el binario de DuckDB:

```bash
./duckdb.exe -s ".read analysis.sql"
```

---

## 🔍 Consultas SQL Realizadas y Hallazgos Principales

### 1. Carga y Registro de la Tabla Virtual con Limpieza de Datos
Creamos una vista virtual llamada `tabla_clima` usando `read_csv_auto` y la función `COALESCE` para manejar los posibles valores nulos en temperaturas y precipitaciones:

```sql
CREATE VIEW tabla_clima AS 
SELECT 
    date AS fecha,
    COALESCE(precipitation, 0) AS precipitacion,
    COALESCE(temp_max, 0) AS temp_maxima,
    COALESCE(temp_min, 0) AS temp_minima,
    COALESCE(wind, 0) AS viento,
    COALESCE(weather, 'Sin datos') AS clima
FROM read_csv_auto('data/weather_data.csv');
```

---

### 2. Consulta 1: Promedios Mensuales de Temperatura y Lluvias Totales
Calculamos el promedio de temperatura máxima, mínima y la precipitación acumulada por mes:

* **Picos de temperatura:** Los meses de verano (Julio y Agosto) presentan temperaturas máximas promedio de entre **26 °C** y **28 °C**.
* **Pico de lluvia:** El mes con mayor acumulación de precipitación fue **Diciembre de 2015** con **284.5 mm** de lluvia.

---

### 3. Consulta 2: Extremos por Condición Climática
Agrupamos por el tipo de clima registrado (`rain`, `sun`, `fog`, `drizzle`, `snow`):

* Las condiciones más frecuentes en la serie son **Lluvia (`rain`) con 641 días** y **Sol (`sun`) con 640 días**.
* La temperatura máxima histórica registrada fue de **35.6 °C**.
* La temperatura mínima histórica registrada descendió a **-7.1 °C** en días soleados de invierno.

---

### 4. Consulta 3: Filtrado de Días con Condiciones Extremas
Filtramos los días que tuvieron temperaturas superiores a 25 °C o lluvias intensas (más de 20 mm):

* Se identificaron días de calor extremo principalmente entre los meses de Junio y Agosto de cada año.
* El viento máximo registrado durante estos eventos alcanzó los **9.5 m/s**.

---

## ⚡ Tiempos de Respuesta y Conclusión

Al probar la velocidad de respuesta de DuckDB sobre el dataset:
* **Consulta directa sobre CSV:** Tarda menos de **100 milisegundos**.
* **Consulta directa sobre Parquet:** Tarda aproximadamente **62 milisegundos** (un 37% más rápido gracias al formato columnar).
* **Ejecución del script completo con todas las consultas:** Tarda menos de **0.5 segundos**.

**Conclusión:** DuckDB es una herramienta súper liviana y potente para realizar análisis de datos de forma rápida sin necesidad de montar una infraestructura compleja.
