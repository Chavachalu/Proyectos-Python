import pandas as pd
import numpy as np

def segmentar_cartera_mora(df_clientes, df_creditos):
    """Cruza la información de clientes y créditos para calcular la mora.
    
    Aplica las reglas de negocio para clasificar a los clientes en buckets 
    operativos según sus días de atraso y priorizar la estrategia de cobranza.
    
    Args:
        df_clientes (pd.DataFrame): DataFrame limpio con datos de CRM.
        df_creditos (pd.DataFrame): DataFrame preprocesado con saldos de créditos.
        
    Returns:
        pd.DataFrame: Cartera consolidada con la segmentación de mora asignada.
    """
    if df_clientes is None or df_creditos is None:
        print("WARNING - Datos de entrada incompletos para la segmentación.")
        return None

    print("LOG - Iniciando el cruce de información para segmentación...")
    
    # Consolidación de información mediante Left Join (Garantiza mantener toda la cartera)
    df_consolidado = pd.merge(df_clientes, df_creditos, on='cliente_id', how='left')
    
    # Calcular los días de atraso respecto a la fecha de corte (Simulación de fecha actual)
    fecha_corte = pd.Timestamp.now()
    df_consolidado['dias_atraso'] = (fecha_corte - df_consolidado['fecha_vencimiento']).dt.days
    
    # Normalizar valores: Si el saldo es cero o la fecha es futura, los días de atraso son 0
    df_consolidado['dias_atraso'] = df_consolidado['dias_atraso'].apply(lambda x: x if x > 0 else 0)
    df_consolidado['dias_atraso'] = df_consolidado['dias_atraso'].fillna(0).astype(int)

    print("LOG - Clasificando cuentas por buckets de mora...")
    
    # Definición de condiciones de negocio para la segmentación de cartera
    condiciones = [
        (df_consolidado['saldo_pendiente'] <= 0),
        (df_consolidado['dias_atraso'] == 0) & (df_consolidado['saldo_pendiente'] > 0),
        (df_consolidado['dias_atraso'] >= 1) & (df_consolidado['dias_atraso'] <= 30),
        (df_consolidado['dias_atraso'] >= 31) & (df_consolidado['dias_atraso'] <= 60),
        (df_consolidado['dias_atraso'] >= 61) & (df_consolidado['dias_atraso'] <= 90),
        (df_consolidado['dias_atraso'] > 90)
    ]
    
    buckets = ['Al Corriente (Sin Saldo)', 'Vigente (Con Saldo)', 'Mora Temprana (1-30)', 'Mora Media (31-60)', 'Mora Tardía (61-90)', 'Cuentas Castigadas (+90)']
    
    # Asignación de segmentos vectorizada
    df_consolidado['segmento_mora'] = np.select(condiciones, buckets, default='Por Clasificar')
    
    # Resumen ejecutivo para el log del sistema
    print("LOG - Distribución final de la cartera por segmento:")
    resumen = df_consolidado['segmento_mora'].value_counts()
    for segmento, conteo in resumen.items():
        print(f"  |-- {segmento}: {conteo} cuentas.")
        
    return df_consolidado

if __name__ == "__main__":
    # Mock data para testing del módulo de segmentación
    df_cli_mock = pd.DataFrame({'cliente_id': [1, 2, 3], 'nombre': ['Client A', 'Client B', 'Client C']})
    df_cred_mock = pd.DataFrame({
        'cliente_id': [1, 2, 3],
        'saldo_pendiente': [5000, 0, 12000],
        'fecha_vencimiento': [pd.Timestamp.now() - pd.Timedelta(days=15), pd.Timestamp.now(), pd.Timestamp.now() - pd.Timedelta(days=45)]
    })
    
    df_resultado = segmentar_cartera_mora(df_cli_mock, df_cred_mock)
