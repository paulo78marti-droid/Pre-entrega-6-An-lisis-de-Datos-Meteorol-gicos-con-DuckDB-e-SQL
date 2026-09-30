-- ==============================================================================
-- Trabajo Práctico: Pre-entrega 6 - Análisis Meteorológico con DuckDB
-- Coderhouse - Data Science II
-- ==============================================================================

-- 1. Carga del archivo CSV como una vista virtual (tabla virtual)
-- Usamos COALESCE para la limpieza de valores nulos
CREATE VIEW IF NOT EXISTS tabla_clima AS 
SELECT 
    date AS fecha,
    COALESCE(precipitation, 0) AS precipitacion,
    COALESCE(temp_max, 0) AS temp_maxima,
    COALESCE(temp_min, 0) AS temp_minima,
    COALESCE(wind, 0) AS viento,
    COALESCE(weather, 'Sin datos') AS clima
FROM read_csv_auto('data/weather_data.csv');


-- 2. Consulta 1: Promedios mensuales de temperatura y lluvias acumuladas
SELECT '--- CONSULTA 1: PROMEDIOS MENSUALES DE TEMPERATURA Y LLUVIAS ---' AS titulo;

SELECT 
    STRFTIME(CAST(fecha AS DATE), '%Y-%m') AS mes_anio,
    COUNT(*) AS dias_registrados,
    ROUND(AVG(temp_maxima), 2) AS promedio_temp_max,
    ROUND(AVG(temp_minima), 2) AS promedio_temp_min,
    ROUND(SUM(precipitacion), 2) AS total_precipitacion
FROM tabla_clima
GROUP BY mes_anio
ORDER BY mes_anio;


-- 3. Consulta 2: Valores máximos y mínimos según el tipo de clima
SELECT '--- CONSULTA 2: MÁXIMOS Y MÍNIMOS POR TIPO DE CLIMA ---' AS titulo;

SELECT 
    clima,
    COUNT(*) AS cantidad_dias,
    MAX(temp_maxima) AS temp_maxima_historica,
    MIN(temp_minima) AS temp_minima_historica,
    MAX(viento) AS viento_maximo
FROM tabla_clima
GROUP BY clima
ORDER BY cantidad_dias DESC;


-- 4. Consulta 3: Filtrado complejo de días con condiciones climáticas extremas
SELECT '--- CONSULTA 3: DÍAS DE CALOR EXTREMO (>= 25°C) O LLUVIAS FUERTES (>= 20mm) ---' AS titulo;

SELECT 
    fecha,
    clima,
    temp_maxima,
    temp_minima,
    precipitacion,
    viento
FROM tabla_clima
WHERE temp_maxima >= 25.0 OR precipitacion >= 20.0
ORDER BY temp_maxima DESC
LIMIT 15;
