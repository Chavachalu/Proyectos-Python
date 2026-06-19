-- 1. CREACIÓN DE LA BASE DE DATOS Y TABLAS
CREATE DATABASE CobranzaMIS_DB;
GO
USE CobranzaMIS_DB;
GO

-- Tabla Dimensión: Cartera de Clientes
CREATE TABLE cartera_clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre_cliente VARCHAR(100),
    segmento_cartera VARCHAR(50), -- 'Mora Temprana', 'Mora Tardía', 'Vigente'
    saldo_pendiente DECIMAL(18,2),
    dias_atraso_rango VARCHAR(30),
    estatus_cuenta VARCHAR(20)
);

-- Tabla Hechos: Historial de Pagos (CRM)
CREATE TABLE pagos_crm (
    id_pago INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT FOREIGN KEY REFERENCES cartera_clientes(id_cliente),
    monto_pagado DECIMAL(18,2),
    fecha_pago DATETIME
);
GO

-- 2. POBLAR TABLA DE CLIENTES (2,500 registros simulados)
SET NOCOUNT ON;
DECLARE @i INT = 1;
DECLARE @random_seg INT;
DECLARE @saldo DECIMAL(18,2);

WHILE @i <= 2500
BEGIN
    SET @random_seg = ABS(CHECKSUM(NEWID())) % 3;
    SET @saldo = CAST((ABS(CHECKSUM(NEWID())) % 50000) + 500 AS DECIMAL(18,2));

    INSERT INTO cartera_clientes (nombre_cliente, segmento_cartera, saldo_pendiente, dias_atraso_rango, estatus_cuenta)
    VALUES (
        'Cliente Anonimizado_' + CAST(@i AS VARCHAR(10)),
        CASE @random_seg 
            WHEN 0 THEN 'Vigente' 
            WHEN 1 THEN 'Mora Temprana' 
            ELSE 'Mora Tardía' 
        END,
        CASE WHEN @random_seg = 0 THEN 0 ELSE @saldo END,
        CASE @random_seg 
            WHEN 0 THEN '0 dias' 
            WHEN 1 THEN '1-30 dias' 
            ELSE '31-90 dias' 
        END,
        'Activo'
    );
    SET @i = @i + 1;
END;
GO

-- 3. POBLAR TABLA DE PAGOS (10,000 transacciones masivas aleatorias)
DECLARE @j INT = 1;
DECLARE @rand_cliente INT;
DECLARE @rand_monto DECIMAL(18,2);
DECLARE @rand_dias_atras INT;

WHILE @j <= 10000
BEGIN
    -- Selecciona un cliente aleatorio entre los 2500 creados
    SET @rand_cliente = (ABS(CHECKSUM(NEWID())) % 2500) + 1;
    SET @rand_monto = CAST((ABS(CHECKSUM(NEWID())) % 4500) + 100 AS DECIMAL(18,2));
    SET @rand_dias_atras = ABS(CHECKSUM(NEWID())) % 180; -- Pagos distribuidos en los últimos 6 meses

    INSERT INTO pagos_crm (id_cliente, monto_pagado, fecha_pago)
    VALUES (
        @rand_cliente,
        @rand_monto,
        DATEADD(day, -@rand_dias_atras, GETDATE())
    );
    SET @j = @j + 1;
END;
GO

-- 4. VALIDACIÓN DE CARGA MIGRADA
SELECT 'cartera_clientes' AS Tabla, COUNT(*) AS TotalRegistros FROM cartera_clientes
UNION ALL
SELECT 'pagos_crm' AS Tabla, COUNT(*) AS TotalRegistros FROM pagos_crm;
