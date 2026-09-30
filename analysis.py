# ==============================================================================
# Trabajo Práctico: Pre-entrega 6 - Análisis de Datos Meteorológicos con DuckDB
# Coderhouse - Data Science II
# ==============================================================================

import duckdb

def ejecutar_analisis():
    print("Iniciando análisis de datos meteorológicos con DuckDB...\n")

    # Conexión a DuckDB en memoria (sin crear base de datos en archivo binario)
    con = duckdb.connect(database=':memory:')

    # 1. Cargar el archivo CSV directamente como una tabla virtual
    # Usamos COALESCE para asegurar el correcto manejo de valores nulos
    query_vista = """
    CREATE VIEW tabla_clima AS 
    SELECT 
        date AS fecha,
        COALESCE(precipitation, 0) AS precipitacion,
        COALESCE(temp_max, 0) AS temp_maxima,
        COALESCE(temp_min, 0) AS temp_minima,
        COALESCE(wind, 0) AS viento,
        COALESCE(weather, 'Sin datos') AS clima
    FROM read_csv_auto('data/weather_data.csv');
    """
    con.execute(query_vista)
    print("1. Vista virtual 'tabla_clima' creada correctamente.\n")

    # 2. Consulta 1: Promedios mensuales de temperatura y precipitación total
    print("--- Consulta 1: Promedios mensuales de temperatura y lluvias ---")
    query1 = """
    SELECT 
        STRFTIME(CAST(fecha AS DATE), '%Y-%m') AS mes_anio,
        COUNT(*) AS dias_registrados,
        ROUND(AVG(temp_maxima), 2) AS promedio_temp_max,
        ROUND(AVG(temp_minima), 2) AS promedio_temp_min,
        ROUND(SUM(precipitacion), 2) AS total_precipitacion
    FROM tabla_clima
    GROUP BY mes_anio
    ORDER BY mes_anio
    LIMIT 10;
    """
    res1 = con.execute(query1).df()
    print(res1.to_string(index=False))
    print("\n" + "="*60 + "\n")

    # 3. Consulta 2: Máximos de temperatura y viento según la condición del clima
    print("--- Consulta 2: Valores máximos por tipo de clima ---")
    query2 = """
    SELECT 
        clima,
        COUNT(*) AS cantidad_dias,
        MAX(temp_maxima) AS temp_maxima_historica,
        MIN(temp_minima) AS temp_minima_historica,
        MAX(viento) AS viento_maximo
    FROM tabla_clima
    GROUP BY clima
    ORDER BY cantidad_dias DESC;
    """
    res2 = con.execute(query2).df()
    print(res2.to_string(index=False))
    print("\n" + "="*60 + "\n")

    # 4. Consulta 3: Filtrado complejo de días con condiciones climáticas extremas
    print("--- Consulta 3: Días de calor extremo (>= 25°C) o lluvias fuertes (>= 20mm) ---")
    query3 = """
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
    LIMIT 10;
    """
    res3 = con.execute(query3).df()
    print(res3.to_string(index=False))
    print("\nAnálisis completado con éxito.")

if __name__ == "__main__":
    ejecutar_analisis()
