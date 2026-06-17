CREATE DATABASE cobranza_gworld
CREATE TABLE crm_clientes (
    cliente_id INT PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    estatus_crm VARCHAR(50) -- Ej. Activo, En Gestión, Ilocalizable
);

-- Tabla de Finanzas/Créditos: Contiene el estado financiero de las cuentas
CREATE TABLE creditos_cobranza (
    credito_id INT PRIMARY KEY,
    cliente_id INT,
    monto_credito DECIMAL(10,2),
    saldo_pendiente DECIMAL(10,2),
    fecha_vencimiento DATE,
    producto VARCHAR(50) -- Ej. Tarjeta, Préstamo Personal, Automotriz
);

-- Tabla de Transacciones: Registro de los últimos pagos recibidos
CREATE TABLE pagos_recientes (
    pago_id INT PRIMARY KEY,
    credito_id INT,
    monto_pagado DECIMAL(10,2),
    fecha_pago DATE,
    estatus_pago VARCHAR(20) -- Ej. Aprobado, Rechazado, Pendiente
);


INSERT INTO crm_clientes VALUES 
(101, 'Carlos Mendoza', '5551234567', 'carlos.m@mail.com', 'Activo'),
(102, 'Ana Rodríguez',  '5559876543', 'ana.rod@mail.com', 'En Gestión'),
(103, 'Luis Morales',   '5555554433', 'luis.m@mail.com', 'Ilocalizable'),
(104, 'Sofia López',    '5551112233', 'sofia.l@mail.com', 'Activo');

INSERT INTO creditos_cobranza VALUES 
(5001, 101, 50000.00, 15000.00, '2026-04-15', 'Tarjeta de Crédito'),
(5002, 102, 30000.00, 25000.00, '2026-01-10', 'Préstamo Personal'),
(5003, 103, 12000.00, 0.00,      '2026-06-01', 'Tarjeta de Crédito'), -- Al corriente
(5004, 104, 80000.00, 60000.00, '2025-11-20', 'Automotriz');

-- Registro de pagos para validar filtros
INSERT INTO pagos_recientes VALUES 
(901, 5001, 2000.00, '2026-06-10', 'Aprobado'),   -- Pago reciente válido
(902, 5002, 5000.00, '2026-06-12', 'Rechazado'),   -- No disminuyó deuda real
(904, 5004, 1500.00, '2026-05-01', 'Aprobado');   -- Pago antiguo


-- CONSULTA OPTIMIZADA (EXTRACCIÓN AUTOMÁTICA DE CARTERA CRÍTICA)

WITH ResumenPagos AS (
    -- Agrupamos los pagos aprobados recientes para no duplicar filas al hacer el JOIN
    SELECT 
        credito_id,
        SUM(monto_pagado) AS total_pagado_reciente,
        MAX(fecha_pago) AS ultima_fecha_pago
    FROM pagos_recientes
    WHERE estatus_pago = 'Aprobado'
    GROUP BY credito_id
)
SELECT 
    c.cliente_id AS [ID Cliente],
    c.nombre AS [Nombre Cliente],
    c.telefono AS [Teléfono Contacto],
    cr.producto AS [Tipo de Producto],
    cr.saldo_pendiente AS [Saldo Vencido],
    cr.fecha_vencimiento AS [Fecha de Vencimiento],
    
    -- Cálculo dinámico de los días de atraso usando la fecha del sistema
    DATEDIFF(day, cr.fecha_vencimiento, GETDATE()) AS [Días de Mora],
    
    -- Categorización automática del nivel de riesgo para el equipo de llamadas
    CASE 
        WHEN DATEDIFF(day, cr.fecha_vencimiento, GETDATE()) BETWEEN 1 AND 30 THEN 'Riesgo Bajo (Mora Temprana)'
        WHEN DATEDIFF(day, cr.fecha_vencimiento, GETDATE()) BETWEEN 31 AND 90 THEN 'Riesgo Medio'
        WHEN DATEDIFF(day, cr.fecha_vencimiento, GETDATE()) > 90 THEN 'Riesgo Alto (Mora Avanzada)'
        ELSE 'Sin Riesgo'
    END AS [Segmento Riesgo],
    
    -- Datos del último abono registrado
    ISNULL(p.total_pagado_reciente, 0) AS [Último Monto Abonado],
    p.ultima_fecha_pago AS [Fecha Último Abono]

FROM creditos_cobranza cr
INNER JOIN crm_clientes c ON cr.cliente_id = c.cliente_id
LEFT JOIN ResumenPagos p ON cr.credito_id = p.credito_id

-- FILTROS CRÍTICOS DE COBRANZA:
WHERE cr.saldo_pendiente > 0                            -- Cuentas que aún deben dinero
  AND cr.fecha_vencimiento < GETDATE()                 -- Cuentas cuya fecha límite ya pasó
  AND c.estatus_crm <> 'Ilocalizable'                  -- Excluimos de la base de marcado si no hay cómo llamarle
  
-- Ordenamos priorizando los saldos más altos y las cuentas más antiguas
ORDER BY [Saldo Vencido] DESC, [Días de Mora] DESC;
