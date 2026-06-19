import re
import pandas as pd
import numpy as np

def auditar_y_limpiar_contactos(df_clientes):
    """Realiza la auditoría de calidad de datos y limpieza sobre la entidad de clientes.
    
    Aplica expresiones regulares (Regex) para validar la estructura de números 
    telefónicos y correos electrónicos, identificando registros huérfanos o inválidos.
    
    Args:
        df_clientes (pd.DataFrame): DataFrame original extraído de crm_clientes.
        
    Returns:
        pd.DataFrame: DataFrame enriquecido con banderas de auditoría y strings estandarizados.
    """
    if df_clientes is None or df_clientes.empty:
        print("WARNING - DataFrame de clientes vacío o nulo. Cancelando proceso de limpieza.")
        return None

    # Clonar el DataFrame para evitar efectos secundarios (SettingWithCopyWarning)
    df_clean = df_clientes.copy()
    
    print("LOG - Inicializando auditoría de canales de contacto...")

    # 1. Estandarización y manejo de valores nulos/vacíos en strings
    df_clean['telefono'] = df_clean['telefono'].astype(str).str.strip()
    df_clean['correo'] = df_clean['correo'].astype(str).str.lower().str.strip()

    # 2. Definición de Patrones de Validación (Regex)
    # Patrón Teléfono: Valida exactamente 10 dígitos numéricos
    pattern_tel = r'^\d{10}$'
    # Patrón Correo: Estructura estándar de email (usuario@dominio.extension)
    pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 3. Auditoría de Calidad: Creación de Banderas (Flags Booleanas)
    df_clean['tel_valido'] = df_clean['telefono'].apply(lambda x: bool(re.match(pattern_tel, x)))
    df_clean['correo_valido'] = df_clean['correo'].apply(lambda x: bool(re.match(pattern_email, x)))
    
    # 4. Clasificación de Contactabilidad Operativa
    # Un registro es "Moroso Sin Contacto" si ambos canales principales fallan
    df_clean['sin_contacto'] = (~df_clean['tel_valido']) & (~df_clean['correo_valido'])

    # 5. Métricas de Auditoría para el Log del Sistema
    total_registros = len(df_clean)
    tels_invalidos = total_registros - df_clean['tel_valido'].sum()
    correos_invalidos = total_registros - df_clean['correo_valido'].sum()
    sin_puntos_contacto = df_clean['sin_contacto'].sum()

    print(f"LOG - Auditoría completada.")
    print(f"  |-- Total evaluados: {total_registros} registros.")
    print(f"  |-- Teléfonos inválidos/nulos detectados: {tels_invalidos}")
    print(f"  |-- Correos inválidos/nulos detectados: {correos_invalidos}")
    print(f"  |-- Clientes críticos 'Sin Contacto': {sin_puntos_contacto}")

    return df_clean

def preprocesar_cartera_financiera(df_creditos):
    """Normaliza y audita las métricas financieras del modelo de créditos de cobranza.
    
    Asegura la coherencia numérica de los saldos pendientes y mitiga inconsistencias 
    por valores nulos en el balance financiero.
    
    Args:
        df_creditos (pd.DataFrame): DataFrame original extraído de creditos_cobranza.
        
    Returns:
        pd.DataFrame: DataFrame con balances corregidos y tipos de datos alineados.
    """
    if df_creditos is None or df_creditos.empty:
        print("WARNING - DataFrame de créditos vacío o nulo. Cancelando preprocesamiento.")
        return None

    df_clean = df_creditos.copy()
    
    # Asegurar tipos numéricos y rellenar nulos críticos con cero (0.00) en saldo pendiente
    df_clean['monto_credito'] = pd.to_numeric(df_clean['monto_credito'], errors='coerce').fillna(0.0)
    df_clean['saldo_pendiente'] = pd.to_numeric(df_clean['saldo_pendiente'], errors='coerce').fillna(0.0)
    
    # Asegurar el tipado de fechas para optimizar filtros temporales posteriores
    df_clean['fecha_vencimiento'] = pd.to_datetime(df_clean['fecha_vencimiento'], errors='coerce')
    
    return df_clean

if __name__ == "__main__":
    # Datos mock de entrada para pruebas unitarias internas de desarrollo
    data_prueba = {
        'cliente_id': [101, 102, 103],
        'nombre': ['Juan Pérez', 'Ana Gómez', 'Carlos Rivas'],
        'telefono': ['5512345678', '123-invalid', 'None'],
        'correo': ['juan@gworld.com', 'ana_erronea.com', ''],
        'estatus_crm': ['Activo', 'Activo', 'Inactivo']
    }
    df_test = pd.DataFrame(data_prueba)
    
    # Ejecución del pipeline de limpieza sobre el entorno de prueba
    df_auditado = auditar_y_limpiar_contactos(df_test)
