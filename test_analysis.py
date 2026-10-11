import unittest
import os
import io
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import duckdb
from analysis import ejecutar_analisis

class TestAnalisisMeteorologico(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.csv_path = os.path.join('data', 'weather_data.csv')
        cls.con = duckdb.connect(database=':memory:')
        
        # Crear vista virtual tabla_clima
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
        cls.con.execute(query_vista)

    def test_01_archivo_csv_existe(self):
        """Verifica que el archivo CSV de datos meteorológicos existe y no está vacío."""
        self.assertTrue(os.path.exists(self.csv_path), "El archivo 'data/weather_data.csv' no existe.")
        self.assertGreater(os.path.getsize(self.csv_path), 0, "El archivo CSV está vacío.")

    def test_02_vista_tabla_clima_creada(self):
        """Verifica que la vista virtual 'tabla_clima' contiene datos y columnas correctas."""
        df = self.con.execute("SELECT * FROM tabla_clima LIMIT 5;").df()
        self.assertEqual(len(df), 5, "La vista tabla_clima debe retornar filas.")
        columnas_esperadas = {'fecha', 'precipitacion', 'temp_maxima', 'temp_minima', 'viento', 'clima'}
        self.assertTrue(columnas_esperadas.issubset(set(df.columns)), f"Faltan columnas en la vista. Encontradas: {df.columns}")

    def test_03_consulta1_promedios_mensuales(self):
        """Verifica el cálculo de promedios mensuales y totales de precipitación."""
        query1 = """
        SELECT 
            STRFTIME(CAST(fecha AS DATE), '%Y-%m') AS mes_anio,
            COUNT(*) AS dias_registrados,
            ROUND(AVG(temp_maxima), 2) AS promedio_temp_max,
            ROUND(AVG(temp_minima), 2) AS promedio_temp_min,
            ROUND(SUM(precipitacion), 2) AS total_precipitacion
        FROM tabla_clima
        GROUP BY mes_anio
        ORDER BY mes_anio;
        """
        res = self.con.execute(query1).df()
        self.assertGreater(len(res), 0, "Consulta 1 no devolvió registros.")
        self.assertIn('promedio_temp_max', res.columns)
        self.assertIn('total_precipitacion', res.columns)
        # Verificar que todos los promedios y totales no contengan nulos
        self.assertFalse(res.isnull().values.any(), "Consulta 1 contiene valores nulos no deseados.")

    def test_04_consulta2_maximos_por_clima(self):
        """Verifica la agrupación por clima y cálculo de máximos/mínimos."""
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
        res = self.con.execute(query2).df()
        self.assertGreater(len(res), 0, "Consulta 2 no devolvió registros.")
        climas_encontrados = set(res['clima'].tolist())
        self.assertTrue({'rain', 'sun'}.issubset(climas_encontrados), "Deben existir categorías de clima como 'rain' y 'sun'.")

    def test_05_consulta3_condiciones_extremas(self):
        """Verifica el filtro de condiciones extremas (temp >= 25 o lluvia >= 20)."""
        query3 = """
        SELECT 
            fecha, clima, temp_maxima, temp_minima, precipitacion, viento
        FROM tabla_clima
        WHERE temp_maxima >= 25.0 OR precipitacion >= 20.0
        ORDER BY temp_maxima DESC;
        """
        res = self.con.execute(query3).df()
        self.assertGreater(len(res), 0, "Consulta 3 no devolvió días de condiciones extremas.")
        # Verificar que todos los registros cumplan la condición lógica
        for _, row in res.iterrows():
            cumple_condicion = (row['temp_maxima'] >= 25.0) or (row['precipitacion'] >= 20.0)
            self.assertTrue(cumple_condicion, f"Registro no cumple la condición: {row}")

    def test_06_ejecucion_script_completo(self):
        """Ejecuta la función principal ejecutar_analisis y verifica que finaliza sin errores."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            ejecutar_analisis()
        finally:
            sys.stdout = sys.__stdout__
        
        output_str = captured_output.getvalue()
        self.assertIn("Iniciando análisis de datos meteorológicos con DuckDB", output_str)
        self.assertIn("Análisis completado con éxito.", output_str)

if __name__ == '__main__':
    unittest.main(verbosity=2)
