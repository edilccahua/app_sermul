-- ============================================================================
-- SERMUL - Sistema de Gestión de Herramientas
-- Base de Datos: PostgreSQL 15+
-- Versión: 3.0
-- Fecha: Mayo 2026
-- ============================================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- SECCIÓN A: GESTIÓN DE USUARIOS Y PERMISOS (RBAC)
-- ============================================================================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,  -- RESIDENTE, ADMIN, SUP_MEC, SUP_SSOMA, LIDER_MEC, ALMACENERO, TRABAJADOR
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    nivel_jerarquico INT NOT NULL,  -- 1=Residente/Admin, 2=Supervisor/Almacenero, 3=Líder, 4=Trabajador
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permisos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles_permisos (
    rol_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id INT NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- ============================================================================
-- SECCIÓN A-bis: ESPECIALIDADES TÉCNICAS
-- ============================================================================

CREATE TABLE especialidad_tecnica (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    creado_por_id INT,
    actualizado_por_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL REFERENCES roles(id),
    especialidad_id INT REFERENCES especialidad_tecnica(id),
    activo BOOLEAN DEFAULT true,
    ultimo_acceso TIMESTAMP,
    creado_por_id INT REFERENCES usuarios(id),
    actualizado_por_id INT REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_dni ON usuarios(dni);
CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);
CREATE INDEX idx_usuarios_activo ON usuarios(activo) WHERE activo = true;

-- FK de especialidad_tecnica a usuarios (circular, requiere ALTER posterior)
ALTER TABLE especialidad_tecnica ADD CONSTRAINT fk_especialidad_creado_por
    FOREIGN KEY (creado_por_id) REFERENCES usuarios(id);
ALTER TABLE especialidad_tecnica ADD CONSTRAINT fk_especialidad_actualizado_por
    FOREIGN KEY (actualizado_por_id) REFERENCES usuarios(id);

-- ============================================================================
-- SECCIÓN B: PARADAS DE PLANTA
-- ============================================================================

CREATE TABLE paradas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,  -- PAR-2026-001
    nombre VARCHAR(200) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,  -- NULL mientras esté activa
    estado VARCHAR(20) NOT NULL DEFAULT 'Planificada',
    empresa_contratista VARCHAR(200) DEFAULT 'SERMUL EIRL' NOT NULL,
    gerencia_contrato VARCHAR(200),
    responsable_cma VARCHAR(200),
    ubicacion VARCHAR(100),
    creado_por_id INT REFERENCES usuarios(id),
    actualizado_por_id INT REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_estado_parada CHECK (estado IN ('Planificada', 'Activa', 'Finalizada'))
);

CREATE INDEX idx_paradas_estado ON paradas(estado);
CREATE INDEX idx_paradas_fechas ON paradas(fecha_inicio, fecha_fin);

-- ============================================================================
-- SECCIÓN C: GRUPOS DE TRABAJO
-- ============================================================================

CREATE TABLE grupos_trabajo (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL,  -- GRP-001. Nombres reusables entre paradas
    nombre VARCHAR(150) NOT NULL,
    parada_id INT NOT NULL REFERENCES paradas(id),
    descripcion TEXT,
    circuito_area VARCHAR(200),
    creado_por_id INT REFERENCES usuarios(id),
    actualizado_por_id INT REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (codigo, parada_id)  -- Mismo código reusable en diferente parada
);

CREATE TABLE grupos_integrantes (
    id SERIAL PRIMARY KEY,
    grupo_id INT NOT NULL REFERENCES grupos_trabajo(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_salida DATE,
    activo BOOLEAN DEFAULT true,
    es_lider_frente BOOLEAN DEFAULT false,
    CONSTRAINT chk_fechas_integrante CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

CREATE INDEX idx_grupos_parada ON grupos_trabajo(parada_id);
CREATE INDEX idx_grupos_integrantes_activos ON grupos_integrantes(grupo_id, activo) WHERE activo = true;
CREATE INDEX idx_grupo_lider ON grupos_integrantes(grupo_id, es_lider_frente) WHERE es_lider_frente = true;

-- ============================================================================
-- SECCIÓN D: CATÁLOGO DE MATERIALES
-- ============================================================================

CREATE TABLE categorias_materiales (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    tipo_general VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_general CHECK (tipo_general IN ('Herramienta', 'EPP', 'Consumible'))
);

CREATE TABLE catalogo_materiales (
    id SERIAL PRIMARY KEY,
    codigo_interno VARCHAR(15) NOT NULL,  -- Short code mnemotécnico TIPO-MARCA: TALELC-BOSCH, AMOLAN-BOSCH
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INT NOT NULL REFERENCES categorias_materiales(id),
    tipo_material VARCHAR(30) NOT NULL,
    
    -- Campos de identificación
    marca VARCHAR(100),
    modelo VARCHAR(100),
    fecha_ingreso DATE DEFAULT CURRENT_DATE,

    -- Campos económicos
    costo_reposicion DECIMAL(10, 2),
    moneda VARCHAR(3) DEFAULT 'PEN',
    proveedor VARCHAR(200),
    
    -- Campos específicos para EPPs
    vida_util_dias INT,
    requiere_certificacion BOOLEAN DEFAULT false,
    
    -- Control de inventario
    es_devolutivo BOOLEAN NOT NULL,
    stock_minimo INT,
    unidad_medida VARCHAR(20),
    talla VARCHAR(20),

    -- Contadores de stock (Sprint 2.8: modelo por cantidad)
    cant_disponible INT NOT NULL DEFAULT 0,
    cant_en_uso INT NOT NULL DEFAULT 0,
    cant_malograda INT NOT NULL DEFAULT 0,
    cant_perdida INT NOT NULL DEFAULT 0,
    
    -- Metadata
    creado_por_id INT REFERENCES usuarios(id),
    actualizado_por_id INT REFERENCES usuarios(id),
    imagen_url VARCHAR(500),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tipo_material CHECK (tipo_material IN ('HERRAMIENTA_DEVOLUTIVA', 'EPP_DEVOLUTIVO', 'EPP_CONSUMIBLE', 'CONSUMIBLE'))
);

-- Índice único parcial: permite soft-delete sin colisión de códigos (C-07)
CREATE UNIQUE INDEX idx_catalogo_codigo_activo
    ON catalogo_materiales(codigo_interno) WHERE activo = true;
CREATE INDEX idx_catalogo_nombre_trgm ON catalogo_materiales USING gin (nombre gin_trgm_ops);
CREATE INDEX idx_catalogo_categoria ON catalogo_materiales(categoria_id);
CREATE INDEX idx_catalogo_activo ON catalogo_materiales(activo) WHERE activo = true;

-- ============================================================================
-- SECCIÓN E: INVENTARIO FÍSICO — ELIMINADO en Sprint 2.8 (modelo por cantidad)
-- ============================================================================
-- La tabla inventario_fisico fue eliminada. El control de stock ahora se hace
-- mediante contadores en catalogo_materiales (cant_disponible, cant_en_uso, etc.)

-- ============================================================================
-- SECCIÓN F: KITS (BOM) -- [FUTURO - Urgente Fase 2]
-- ============================================================================

-- Las tablas kits y kits_detalle se implementarán en Fase 2.
-- Se dejan documentadas para referencia de la migración futura.

/*
CREATE TABLE kits (
    id SERIAL PRIMARY KEY,
    codigo_kit VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE kits_detalle (
    id SERIAL PRIMARY KEY,
    kit_id INT NOT NULL REFERENCES kits(id) ON DELETE CASCADE,
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    cantidad INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_cantidad_kit CHECK (cantidad > 0),
    UNIQUE (kit_id, catalogo_id)
);
*/

-- ============================================================================
-- SECCIÓN G: SISTEMA DE RESERVAS
-- ============================================================================

CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    codigo_reserva VARCHAR(30) UNIQUE NOT NULL,
    
    -- Vínculos
    parada_id INT NOT NULL REFERENCES paradas(id),
    grupo_id INT NOT NULL REFERENCES grupos_trabajo(id),
    creado_por_id INT NOT NULL REFERENCES usuarios(id),
    
    -- Programación
    turno VARCHAR(10),
    fecha_programada DATE NOT NULL,
    
    -- Estado del flujo
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    aprobado_por_id INT REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    despachado_por_id INT REFERENCES usuarios(id),
    actualizado_por_id INT REFERENCES usuarios(id),
    fecha_despacho TIMESTAMP,
    motivo_rechazo TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_estado_reserva CHECK (estado IN ('Pendiente', 'Aprobada', 'Rechazada', 'Despachada', 'Cancelada'))
);

CREATE TABLE reservas_detalle (
    id SERIAL PRIMARY KEY,
    reserva_id INT NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    cantidad_solicitada INT NOT NULL DEFAULT 1,
    cantidad_despachada INT DEFAULT 0,
    CONSTRAINT chk_cantidad_solicitada CHECK (cantidad_solicitada > 0)
);

CREATE INDEX idx_reservas_grupo ON reservas(grupo_id);
CREATE INDEX idx_reservas_parada ON reservas(parada_id);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reservas_fecha ON reservas(fecha_programada);

-- ============================================================================
-- SECCIÓN H: HISTORIAL DE MOVIMIENTOS (Flexible en v1)
-- ============================================================================

CREATE TABLE historial_movimientos (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Tipo de transacción
    tipo_movimiento VARCHAR(30) NOT NULL,
    
    -- Referencias (solo catalogo_id y parada_id son NOT NULL en v1)
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    parada_id INT NOT NULL REFERENCES paradas(id),
    cantidad INT NOT NULL DEFAULT 1,
    
    -- Actores (NULLABLE en v1)
    usuario_ejecuta_id INT REFERENCES usuarios(id),
    grupo_destino_id INT REFERENCES grupos_trabajo(id),
    usuario_receptor_id INT REFERENCES usuarios(id),
    
    -- Contexto (NULLABLE en v1)
    reserva_id INT REFERENCES reservas(id),
    
    -- Estados (para auditoría)
    estado_origen VARCHAR(20),
    estado_destino VARCHAR(20),
    
    -- Observaciones (Sprint 2.8)
    observaciones TEXT,
    observacion_entrega TEXT,
    observacion_recepcion TEXT,
    
    CONSTRAINT chk_tipo_movimiento CHECK (tipo_movimiento IN (
        'Entrega', 'Devolucion', 'Perdida', 'Paso_Mantenimiento', 
        'Retorno_Mantenimiento', 'Baja', 'Ajuste_Inventario',
        'Recepcion_Mina', 'Salida_Ciudad', 'Ingreso_Compra'
    )),
    PRIMARY KEY (id, timestamp)  -- PK compuesta: PostgreSQL exige la columna de partición en la PK
) PARTITION BY RANGE (timestamp);

-- Crear particiones por año
CREATE TABLE historial_movimientos_2026 PARTITION OF historial_movimientos
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE historial_movimientos_2027 PARTITION OF historial_movimientos
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

-- Índices en tabla particionada
CREATE INDEX idx_historial_timestamp ON historial_movimientos(timestamp DESC);
CREATE INDEX idx_historial_catalogo ON historial_movimientos(catalogo_id);
CREATE INDEX idx_historial_parada ON historial_movimientos(parada_id);
CREATE INDEX idx_historial_grupo ON historial_movimientos(grupo_destino_id);
CREATE INDEX idx_historial_tipo ON historial_movimientos(tipo_movimiento);

-- ============================================================================
-- SECCIÓN I: RIESGOS Y PETARs (Post-MVP)
-- ============================================================================

CREATE TABLE tipos_riesgos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    requiere_supervision_ssoma BOOLEAN DEFAULT false,
    color_hex VARCHAR(7),
    icono VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE petars (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    tipo_riesgo_id INT NOT NULL REFERENCES tipos_riesgos(id),
    version VARCHAR(20) NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    archivo_pdf_url TEXT NOT NULL,  -- TEXT para URLs/paths largos
    aprobado_por VARCHAR(200),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SECCIÓN J: TRIGGERS Y FUNCIONES
-- ============================================================================

-- Trigger: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paradas_updated_at BEFORE UPDATE ON paradas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_grupos_updated_at BEFORE UPDATE ON grupos_trabajo
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_catalogo_updated_at BEFORE UPDATE ON catalogo_materiales
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_especialidad_updated_at BEFORE UPDATE ON especialidad_tecnica
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON reservas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función: Auto-marcar pérdidas 3 días después del cierre de parada
-- Sprint 2.8: ahora opera sobre contadores de catalogo_materiales en vez de inventario_fisico
-- (Se ejecuta vía scheduled task en backend, no como trigger automático)
-- CORREGIDO: sintaxis UPDATE...FROM válida para PostgreSQL + inserta registro en historial
CREATE OR REPLACE FUNCTION marcar_perdidas_cierre_parada(p_parada_id INT)
RETURNS TABLE(catalogo_id INT, catalogo_nombre VARCHAR, grupo_nombre VARCHAR, cantidad_perdida INT, costo DECIMAL) AS $$
BEGIN
    RETURN QUERY
    WITH perdidas_agrupadas AS (
        -- Encontrar materiales con entregas a esta parada sin devolución posterior
        SELECT 
            hm.catalogo_id,
            hm.grupo_destino_id,
            SUM(hm.cantidad) AS cant_pendiente
        FROM historial_movimientos hm
        WHERE hm.parada_id = p_parada_id
            AND hm.tipo_movimiento = 'Entrega'
            AND NOT EXISTS (
                SELECT 1 FROM historial_movimientos hm2
                WHERE hm2.catalogo_id = hm.catalogo_id
                    AND hm2.grupo_destino_id = hm.grupo_destino_id
                    AND hm2.tipo_movimiento IN ('Devolucion', 'Perdida', 'Paso_Mantenimiento')
                    AND hm2.timestamp > hm.timestamp
            )
        GROUP BY hm.catalogo_id, hm.grupo_destino_id
        HAVING SUM(hm.cantidad) > 0
    ),
    actualizar_contadores AS (
        UPDATE catalogo_materiales cm
        SET cant_en_uso = cm.cant_en_uso - pa.cant_pendiente,
            cant_perdida = cm.cant_perdida + pa.cant_pendiente,
            updated_at = CURRENT_TIMESTAMP
        FROM perdidas_agrupadas pa
        WHERE cm.id = pa.catalogo_id
        RETURNING cm.id, cm.nombre, cm.costo_reposicion, pa.cant_pendiente, pa.grupo_destino_id
    ),
    registro_perdida AS (
        INSERT INTO historial_movimientos (tipo_movimiento, catalogo_id, parada_id, grupo_destino_id, cantidad, estado_origen, estado_destino, observaciones)
        SELECT 'Perdida', ac.id, p_parada_id, ac.grupo_destino_id, ac.cant_pendiente, 'En_Uso', 'Perdida', 'Auto-marcado por cierre de parada (+3 días)'
        FROM actualizar_contadores ac
    )
    SELECT ac.id, ac.nombre, g.nombre, ac.cant_pendiente, ac.costo_reposicion
    FROM actualizar_contadores ac
    LEFT JOIN grupos_trabajo g ON g.id = ac.grupo_destino_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECCIÓN L: VISTAS ÚTILES
-- ============================================================================

-- Vista: Stock de materiales (Sprint 2.8: reemplaza v_inventario_detallado)
CREATE VIEW v_stock_materiales AS
SELECT 
    cm.id,
    cm.codigo_interno,
    cm.nombre,
    cat.nombre AS categoria,
    cm.tipo_material,
    cm.costo_reposicion,
    cm.moneda,
    (cm.cant_disponible + cm.cant_en_uso + cm.cant_malograda + cm.cant_perdida) AS cantidad_total,
    cm.cant_disponible,
    cm.cant_en_uso,
    cm.cant_malograda,
    cm.cant_perdida
FROM catalogo_materiales cm
JOIN categorias_materiales cat ON cm.categoria_id = cat.id;

-- Vista: Herramientas en uso por grupo (Sprint 2.8: sin inventario_fisico)
DROP VIEW IF EXISTS v_herramientas_en_uso;
CREATE VIEW v_herramientas_en_uso AS
SELECT 
    g.id AS grupo_id,
    g.codigo AS codigo_grupo,
    g.nombre AS nombre_grupo,
    p.id AS parada_id,
    p.nombre AS parada_nombre,
    cm.id AS catalogo_id,
    cm.codigo_interno,
    cm.nombre AS nombre_herramienta,
    cm.descripcion,
    cm.marca,
    cm.costo_reposicion,
    SUM(h.cantidad) AS cantidad_en_uso,
    MAX(h.timestamp) AS ultima_entrega,
    EXTRACT(DAY FROM NOW() - MAX(h.timestamp)) AS dias_en_uso
FROM historial_movimientos h
JOIN catalogo_materiales cm ON h.catalogo_id = cm.id
JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
JOIN paradas p ON h.parada_id = p.id
WHERE h.tipo_movimiento = 'Entrega'
  AND NOT EXISTS (
      SELECT 1 FROM historial_movimientos h2
      WHERE h2.catalogo_id = h.catalogo_id
        AND h2.grupo_destino_id = h.grupo_destino_id
        AND h2.tipo_movimiento IN ('Devolucion', 'Perdida', 'Paso_Mantenimiento')
        AND h2.timestamp > h.timestamp
  )
GROUP BY g.id, g.codigo, g.nombre, p.id, p.nombre, cm.id, cm.codigo_interno, cm.nombre, cm.descripcion, cm.marca, cm.costo_reposicion
HAVING SUM(h.cantidad) > 0;

-- Vista: Dashboard de métricas (Sprint 2.8: desde catalogo_materiales)
CREATE VIEW v_dashboard_metricas AS
SELECT
    COUNT(*) FILTER (WHERE cm.tipo_material IN ('HERRAMIENTA_DEVOLUTIVA', 'EPP_DEVOLUTIVO')) AS total_devolutivos,
    SUM(cm.cant_disponible) AS disponibles,
    SUM(cm.cant_en_uso) AS en_uso,
    SUM(cm.cant_malograda) AS malogradas,
    SUM(cm.cant_perdida) AS perdidas,
    SUM(cm.cant_perdida * cm.costo_reposicion) AS costo_total_perdidas,
    SUM((cm.cant_disponible + cm.cant_en_uso + cm.cant_malograda + cm.cant_perdida) * cm.costo_reposicion) AS costo_total_inventario
FROM catalogo_materiales cm;

-- Vista: Pendientes de cierre por parada activa
CREATE VIEW v_pendientes_cierre_parada AS
SELECT 
    p.id AS parada_id,
    p.codigo AS codigo_parada,
    p.nombre AS parada_nombre,
    p.fecha_fin AS parada_fecha_fin,
    g.id AS grupo_id,
    g.nombre AS grupo_nombre,
    cm.id AS catalogo_id,
    cm.codigo_interno,
    cm.nombre AS nombre_herramienta,
    SUM(h.cantidad) AS cantidad_pendiente,
    MAX(h.timestamp) AS ultima_entrega,
    EXTRACT(DAY FROM NOW() - MAX(h.timestamp)) AS dias_en_uso,
    CASE 
        WHEN p.fecha_fin IS NOT NULL AND CURRENT_DATE > p.fecha_fin + INTERVAL '3 days' 
        THEN 'VENCIDO' 
        ELSE 'PENDIENTE' 
    END AS estado_vencimiento
FROM paradas p
JOIN historial_movimientos h ON h.parada_id = p.id
JOIN catalogo_materiales cm ON h.catalogo_id = cm.id
JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
WHERE h.tipo_movimiento = 'Entrega'
    AND p.estado IN ('Activa', 'Finalizada')
    AND NOT EXISTS (
        SELECT 1 FROM historial_movimientos h2
        WHERE h2.catalogo_id = h.catalogo_id
            AND h2.grupo_destino_id = h.grupo_destino_id
            AND h2.tipo_movimiento IN ('Devolucion', 'Perdida', 'Paso_Mantenimiento')
            AND h2.timestamp > h.timestamp
    )
GROUP BY p.id, p.codigo, p.nombre, p.fecha_fin, g.id, g.nombre, cm.id, cm.codigo_interno, cm.nombre;

-- Vista: Pérdidas por parada
CREATE VIEW v_perdidas_por_parada AS
SELECT 
    p.id AS parada_id,
    p.codigo AS codigo_parada,
    p.nombre AS nombre_parada,
    cm.id AS catalogo_id,
    cm.codigo_interno,
    cm.nombre AS nombre_herramienta,
    cm.costo_reposicion,
    SUM(h.cantidad) AS cantidad_perdida,
    SUM(h.cantidad * cm.costo_reposicion) AS costo_total,
    g.nombre AS nombre_grupo,
    g.id AS grupo_id
FROM historial_movimientos h
JOIN catalogo_materiales cm ON h.catalogo_id = cm.id
JOIN paradas p ON h.parada_id = p.id
LEFT JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
WHERE h.tipo_movimiento = 'Perdida'
GROUP BY p.id, p.codigo, p.nombre, cm.id, cm.codigo_interno, cm.nombre, cm.costo_reposicion, g.nombre, g.id;

-- ============================================================================
-- SECCIÓN M: RBAC (Roles y Permisos)
-- ============================================================================

-- Insertar Roles
INSERT INTO roles (codigo, nombre, descripcion, nivel_jerarquico) VALUES
('RESIDENTE', 'Residente', 'Gerente de operaciones, responsable final', 1),
('ADMIN', 'Administrador del Sistema', 'Configuración y gestión total del sistema', 1),
('SUP_MEC', 'Supervisor Mecánico', 'Coordina varios grupos de trabajo', 2),
('SUP_SSOMA', 'Supervisor SSOMA', 'Observa cumplimiento de seguridad (rol observador)', 2),
('ALMACENERO', 'Almacenero', 'Opera el almacén de herramientas. Crea usuarios y grupos', 2),
('LIDER_MEC', 'Líder Mecánico', 'Responsable directo de un grupo', 3),
('TRABAJADOR', 'Trabajador', 'Integrante de grupo de trabajo', 4);

-- Insertar Permisos
INSERT INTO permisos (codigo, nombre, modulo) VALUES
('CHECK_OUT', 'Entregar herramientas', 'Activos'),
('CHECK_IN', 'Recibir herramientas', 'Activos'),
('VER_INVENTARIO', 'Ver inventario completo', 'Activos'),
('EDITAR_INVENTARIO', 'Editar inventario físico', 'Activos'),
('CAMBIAR_UBICACION', 'Cambiar ubicación macro', 'Activos'),
('CREAR_RESERVA', 'Crear reservas', 'Reservas'),
('APROBAR_RESERVA', 'Aprobar/rechazar reservas', 'Reservas'),
('DESPACHAR_RESERVA', 'Despachar reservas', 'Reservas'),
('CREAR_PARADA', 'Crear/editar paradas', 'Paradas'),
('CERRAR_PARADA', 'Cerrar paradas', 'Paradas'),
('GESTIONAR_GRUPOS', 'Crear/editar grupos', 'Grupos'),
('IMPORTAR_EXCEL', 'Cargar grupos por Excel', 'Grupos'),
('ASIGNAR_GRUPO', 'Asignar trabajadores a grupos', 'Tareas'),
('SUBIR_PETAR', 'Subir PETARs', 'PETARs'),
('VER_PETAR', 'Ver PETARs', 'PETARs'),
('VER_DASHBOARD_COMPLETO', 'Ver dashboard ejecutivo', 'Dashboards'),
('VER_DASHBOARD_GRUPO', 'Ver dashboard de grupos asignados', 'Dashboards'),
('EXPORTAR_REPORTES', 'Exportar reportes', 'Dashboards'),
('ADMIN_USUARIOS', 'Administrar usuarios', 'Admin'),
('CONFIG_SISTEMA', 'Configuración del sistema', 'Admin');

-- Asignar todos los permisos al Residente
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'RESIDENTE'), id FROM permisos;

-- Asignar todos los permisos al Admin
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'ADMIN'), id FROM permisos;

-- Asignar permisos al Almacenero (todos excepto configuración del sistema y cierre de parada)
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'ALMACENERO'), id FROM permisos
WHERE codigo NOT IN ('CONFIG_SISTEMA', 'CERRAR_PARADA', 'CREAR_PARADA');

-- Asignar permisos a Supervisor Mecánico
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'SUP_MEC'), id FROM permisos
WHERE codigo IN ('VER_INVENTARIO', 'CREAR_RESERVA', 'VER_DASHBOARD_GRUPO', 'VER_PETAR', 'ASIGNAR_GRUPO');

-- Asignar permisos a Supervisor SSOMA
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'SUP_SSOMA'), id FROM permisos
WHERE codigo IN ('VER_INVENTARIO', 'VER_DASHBOARD_GRUPO', 'VER_PETAR', 'SUBIR_PETAR');

-- Asignar permisos a Líder Mecánico
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'LIDER_MEC'), id FROM permisos
WHERE codigo IN ('VER_INVENTARIO', 'CREAR_RESERVA', 'VER_DASHBOARD_GRUPO', 'VER_PETAR');

-- Asignar permisos a Trabajador
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT (SELECT id FROM roles WHERE codigo = 'TRABAJADOR'), id FROM permisos
WHERE codigo IN ('VER_PETAR', 'VER_INVENTARIO');

-- ============================================================================
-- FIN DEL SCRIPT DDL
-- ============================================================================

COMMENT ON TABLE paradas IS 'Entidad principal. Agrupa toda la actividad de un mantenimiento programado.';
COMMENT ON TABLE historial_movimientos IS 'Log de movimientos. Sprint 2.8: control por cantidad, sin inventario_fisico. Particionado por año.';
COMMENT ON COLUMN catalogo_materiales.codigo_interno IS 'Short code formato TIPO-MARCA para digitación manual rápida (máx 15 caracteres).';
COMMENT ON COLUMN catalogo_materiales.es_devolutivo IS 'true=herramienta/EPP que se entrega y devuelve, false=consumible de uso único.';

-- ============================================================================
-- USUARIO ADMIN INICIAL
-- ============================================================================
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) 
VALUES ('12345678', 'ADMIN', 'ADMIN', '$2b$12$1dSaPV57.9rCqMKJyKFNquoa54F0lnKJG4CK0bFQbF2Tpm3REz.1y', (SELECT id FROM roles WHERE codigo='ADMIN'));
