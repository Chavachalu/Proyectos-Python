import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Configuración de Logs para auditoría básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_performance_report(segmented_data_path, output_excel_path):
    """
    Agrupa la cartera segmentada para calcular KPIs clave de cobranza
    y exporta un libro de Excel con múltiples pestañas para Negocio.
    """
    try:
        logging.info("Cargando datos de la cartera segmentada...")
        df = pd.read_csv(segmented_data_path)
        
        # Validar que existan las columnas necesarias generadas en el paso 03
        required_cols = ['bucket_mora', 'saldo_pendiente', 'monto_pagado', 'id_cliente']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Faltan columnas clave en el archivo de entrada.")
            
        logging.info("Calculando KPIs agregados por Bucket de Mora...")
        
        # 1. Resumen Ejecutivo (Agrupación por Bucket de Mora)
        # Resumen de saldos, pagos y tasas de recuperación
        summary_report = df.groupby('bucket_mora').agg(
            total_clientes=('id_cliente', 'count'),
            cartera_vencida=('saldo_pendiente', 'sum'),
            total_recuperado=('monto_pagado', 'sum')
        ).reset_index()
        
        # Calcular la Tasa de Recuperación por bucket: (Pagado / (Pendiente + Pagado)) * 100
        summary_report['tasa_recuperacion_pct'] = np.where(
            (summary_report['cartera_vencida'] + summary_report['total_recuperado']) > 0,
            (summary_report['total_recuperado'] / (summary_report['cartera_vencida'] + summary_report['total_recuperado'])) * 100,
            0.0
        ).round(2)
        
        # 2. Clientes Críticos (Mora Tardía con saldos altos para estrategia prioritaria)
        logging.info("Filtrando cuentas de alto riesgo para el equipo operativo...")
        critical_accounts = df[
            (df['bucket_mora'] == 'Mora Tardía') & 
            (df['saldo_pendiente'] > 0)
        ].sort_values(by='saldo_pendiente', ascending=False).head(100)
        
        # 3. Exportación automatizada a Excel en diferentes pestañas
        logging.info(f"Exportando reportes finales a: {output_excel_path}")
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            summary_report.to_excel(writer, sheet_name='Resumen KPIs', index=False)
            critical_accounts.to_excel(writer, sheet_name='Top 100 Críticos', index=False)
            
        logging.info("¡Reporte MIS generado y guardado con éxito!")
        return True
        
    except Exception as e:
        logging.error(f"Error al generar el reporte de rendimiento: {str(e)}")
        return False

if __name__ == "__main__":
    # Rutas simuladas para entorno local
    INPUT_FILE = "data/03_cartera_segmentada.csv"
    OUTPUT_FILE = "outputs/Reporte_Cobranza_MIS.xlsx"
    
    # Ejecutar la automatización del reporte
    generate_performance_report(INPUT_FILE, OUTPUT_FILE)
