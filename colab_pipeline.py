# ==============================================================================
# Script de Prueba del Pipeline Meteorológico con DuckDB para Google Colab
# Curso: Data Science II - Coderhouse
# Alumno/a: Paulo Martino
# ==============================================================================

import os
import time
import urllib.request
import duckdb
import pandas as pd

def preparar_entorno():
    """
    Crea la carpeta de datos y descarga el dataset weather_data.csv si no existe.
    Garantiza que el script funcione autónomamente en Google Colab.
    """
    print("🚀 Preparando el entorno en Google Colab...")
    os.makedirs("data", exist_ok=True)
    
    csv_path = os.path.join("data", "weather_data.csv")
    parquet_path = os.path.join("data", "weather_data.parquet")
    
    # Si no existe el CSV localmente en Colab, se descarga automáticamente
    if not os.path.exists(csv_path):
        url = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/seattle-weather.csv"
        print(f"📥 Descargando dataset desde {url}...")
        urllib.request.urlretrieve(url, csv_path)
        print("✅ Archivo 'data/weather_data.csv' listo.")
    else:
        print("✅ Archivo 'data/weather_data.csv' encontrado localmente.")
        
    return csv_path, parquet_path

def ejecutar_pipeline_colab():
    """
    Ejecuta la conexión a DuckDB, creación de la vista virtual, exportación a Parquet,
    consultas analíticas SQL y benchmark de velocidad.
    """
    csv_path, parquet_path = preparar_entorno()
    
    print("\n🦆 Conectando a DuckDB en memoria...")
    con = duckdb.connect(database=":memory:")
    
    # 1. Crear vista virtual desde CSV usando read_csv_auto y COALESCE
    query_vista = f"""
    CREATE VIEW tabla_clima AS 
    SELECT 
        date AS fecha,
        COALESCE(precipitation, 0) AS precipitacion,
        COALESCE(temp_max, 0) AS temp_maxima,
        COALESCE(temp_min, 0) AS temp_minima,
        COALESCE(wind, 0) AS viento,
        COALESCE(weather, 'Sin datos') AS clima
    FROM read_csv_auto('{csv_path}');
    """
    con.execute(query_vista)
    print("✅ Vista virtual 'tabla_clima' creada correctamente.\n")
    
    # Generar el archivo Parquet para pruebas columnar directamente desde el CSV
    con.execute(f"COPY (SELECT * FROM read_csv_auto('{csv_path}')) TO '{parquet_path}' (FORMAT PARQUET);")
    print("✅ Archivo Parquet creado en 'data/weather_data.parquet'.")
    
    # 2. Consulta 1: Promedios mensuales y acumulado de lluvias
    print("\n" + "="*70)
    print("📊 CONSULTA 1: Promedios mensuales de temperatura y lluvias totales")
    print("="*70)
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
    df1 = con.execute(query1).df()
    print(df1.to_string(index=False))
    
    # 3. Consulta 2: Valores extremos por tipo de clima
    print("\n" + "="*70)
    print("📊 CONSULTA 2: Extremidades climáticas (Temp Máx, Mín y Viento)")
    print("="*70)
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
    df2 = con.execute(query2).df()
    print(df2.to_string(index=False))
    
    # 4. Consulta 3: Días de calor extremo o lluvias fuertes
    print("\n" + "="*70)
    print("📊 CONSULTA 3: Días extremos (Temp >= 25°C o Lluvia >= 20mm)")
    print("="*70)
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
    df3 = con.execute(query3).df()
    print(df3.to_string(index=False))
    
    # 5. Benchmark de velocidad CSV vs Parquet
    print("\n" + "="*70)
    print("⚡ BENCHMARK DE VELOCIDAD DUCKDB (CSV vs PARQUET)")
    print("="*70)
    
    t0 = time.time()
    con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{csv_path}')").fetchall()
    t_csv = (time.time() - t0) * 1000
    
    t0 = time.time()
    con.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchall()
    t_parquet = (time.time() - t0) * 1000
    
    print(f"⏱️ Tiempo de consulta en CSV:     {t_csv:.2f} ms")
    print(f"⏱️ Tiempo de consulta en Parquet: {t_parquet:.2f} ms")
    
    print("\n🎉 ¡Pipeline ejecutado exitosamente!")

if __name__ == "__main__":
    ejecutar_pipeline_colab()
