import os
import pandas as pd
from sqlalchemy import create_engine

def obtener_conexion_db():
    """Establece la conexión base con el servidor relacional SQL Server.
    
    Returns:
        sqlalchemy.engine.Engine: Objeto de conexión activo o None en caso de fallo.
    """
    driver = "ODBC Driver 17 for SQL Server"
    server = "localhost"
    database = "cobranza_gworld"
    
    # Conexión mediante Trusted_Connection (Autenticación integrada de Windows)
    connection_url = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"
    
    try:
        engine = create_engine(connection_url)
        return engine
    except Exception as e:
        print(f"ERROR - Fallo en la conexión hacia la base de datos: {str(e)}")
        return None

def extraer_tablas_cobranza():
    """Ejecuta la extracción de las entidades del modelo relacional 
    de cobranza (CRM, Créditos y Transacciones).
    
    Returns:
        tuple: DataFrames correspondientes a (clientes, creditos, pagos) o (None, None, None)
    """
    engine = obtener_conexion_db()
    if engine is None:
        return None, None, None
    
    print("LOG - Inicializando extracción ETL de cobranza_gworld...")
    
    try:
        # Dimensión Clientes (Datos de origen CRM)
        query_clientes = "SELECT cliente_id, nombre, telefono, correo, estatus_crm FROM crm_clientes;"
        df_clientes = pd.read_sql(query_clientes, engine)
        print(f"LOG - Extracción exitosa: crm_clientes [{df_clientes.shape[0]} registros].")
        
        # Dimensión Financiera (Saldos y productos de Créditos)
        query_creditos = """
            SELECT credito_id, cliente_id, monto_credito, saldo_pendiente, fecha_vencimiento, producto 
            FROM creditos_cobranza;
        """
        df_creditos = pd.read_sql(query_creditos, engine)
        print(f"LOG - Extracción exitosa: creditos_cobranza [{df_creditos.shape[0]} registros].")
        
        # Tabla de Hechos Transaccionales (Log de Pagos Recientes)
        query_pagos = "SELECT pago_id, credito_id, monto_pagado, fecha_pago, estatus_pago FROM pagos_recientes;"
        df_pagos = pd.read_sql(query_pagos, engine)
        print(f"LOG - Extracción exitosa: pagos_recientes [{df_pagos.shape[0]} registros].")
        
        print("LOG - Pipeline de extracción completado satisfactoriamente.")
        return df_clientes, df_creditos, df_pagos
        
    except Exception as e:
        print(f"ERROR - Fallo durante la ejecución de queries de extracción: {str(e)}")
        return None, None, None

if __name__ == "__main__":
    # Ejecución de prueba y validación estructural del Pipeline
    df_cli, df_cred, df_pag = extraer_tablas_cobranza()
    
    if df_cli is not None:
        print("\n--- VALIDACIÓN ESTRUCTURAL ---")
        print("Estructura de Clientes:", df_cli.columns.tolist())
        print("Estructura de Créditos:", df_cred.columns.tolist())
