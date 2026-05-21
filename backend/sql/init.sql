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

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL REFERENCES roles(id),
    activo BOOLEAN DEFAULT true,
    ultimo_acceso TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_dni ON usuarios(dni);
CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);
CREATE INDEX idx_usuarios_activo ON usuarios(activo) WHERE activo = true;

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
    observaciones TEXT,
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
    lider_id INT NOT NULL REFERENCES usuarios(id),
    supervisor_id INT NOT NULL REFERENCES usuarios(id),
    estado VARCHAR(20) DEFAULT 'Activo',
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_estado_grupo CHECK (estado IN ('Activo', 'Inactivo', 'Finalizado')),
    UNIQUE (codigo, parada_id)  -- Mismo código reusable en diferente parada
);

CREATE TABLE grupos_integrantes (
    id SERIAL PRIMARY KEY,
    grupo_id INT NOT NULL REFERENCES grupos_trabajo(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_salida DATE,
    activo BOOLEAN DEFAULT true,
    CONSTRAINT chk_fechas_integrante CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

-- Evitar duplicado: un usuario solo puede estar activo una vez en el mismo grupo
CREATE UNIQUE INDEX idx_grupo_usuario_activo_unico 
    ON grupos_integrantes(grupo_id, usuario_id) WHERE activo = true;

CREATE INDEX idx_grupos_parada ON grupos_trabajo(parada_id);
CREATE INDEX idx_grupos_integrantes_activos ON grupos_integrantes(grupo_id, activo) WHERE activo = true;

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
    codigo_interno VARCHAR(15) UNIQUE NOT NULL,  -- Short code mnemotécnico: HER-001, EPP-023
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INT NOT NULL REFERENCES categorias_materiales(id),
    tipo_material VARCHAR(20) NOT NULL,
    
    -- Campos económicos
    costo_reposicion DECIMAL(10, 2),
    moneda VARCHAR(3) DEFAULT 'PEN',
    proveedor VARCHAR(200),
    
    -- Campos específicos para EPPs
    vida_util_dias INT,
    requiere_certificacion BOOLEAN DEFAULT false,
    requiere_inspeccion BOOLEAN DEFAULT false,
    certificacion_norma VARCHAR(100),
    
    -- Control de inventario
    es_devolutivo BOOLEAN NOT NULL,
    stock_minimo INT,
    unidad_medida VARCHAR(20),
    
    -- Metadata
    imagen_url VARCHAR(500),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tipo_material CHECK (tipo_material IN ('Herramienta', 'EPP_Devolutivo', 'EPP_Consumible', 'Suministro'))
);

CREATE INDEX idx_catalogo_codigo ON catalogo_materiales(codigo_interno);
CREATE INDEX idx_catalogo_nombre_trgm ON catalogo_materiales USING gin (nombre gin_trgm_ops);
CREATE INDEX idx_catalogo_categoria ON catalogo_materiales(categoria_id);
CREATE INDEX idx_catalogo_activo ON catalogo_materiales(activo) WHERE activo = true;

-- ============================================================================
-- SECCIÓN E: INVENTARIO FÍSICO
-- ============================================================================

CREATE TABLE inventario_fisico (
    id SERIAL PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE,  -- NULLABLE en v1. Se llenará en fase futura con lector de barras
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    numero_serie VARCHAR(100),
    
    -- Estado y ubicación
    estado VARCHAR(20) NOT NULL DEFAULT 'Disponible',
    ubicacion_fisica VARCHAR(100),  -- Estante A-12, Casillero B-05
    ubicacion_macro VARCHAR(20) NOT NULL DEFAULT 'Ciudad',  -- Ciudad, Transito_Compra, Mina
    
    -- Fechas de control
    fecha_adquisicion DATE,
    fecha_ultima_inspeccion DATE,
    proxima_inspeccion DATE,
    
    -- Observaciones
    observaciones TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_estado_inventario CHECK (estado IN (
        'Disponible', 'En_Uso', 'Malograda', 'En_Mantenimiento', 
        'Perdida', 'Baja', 'En_Ciudad', 'En_Transito_Compra'
    )),
    CONSTRAINT chk_ubicacion_macro CHECK (ubicacion_macro IN ('Ciudad', 'Transito_Compra', 'Mina'))
);

CREATE INDEX idx_inventario_catalogo ON inventario_fisico(catalogo_id);
CREATE INDEX idx_inventario_estado ON inventario_fisico(estado);
CREATE INDEX idx_inventario_ubicacion_macro ON inventario_fisico(ubicacion_macro);
CREATE INDEX idx_inventario_disponible ON inventario_fisico(catalogo_id, estado) WHERE estado = 'Disponible';

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
    tarea_id INT,
    
    -- Programación
    turno VARCHAR(10) NOT NULL,
    fecha_programada DATE NOT NULL,
    
    -- Estado del flujo
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    aprobado_por_id INT REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    despachado_por_id INT REFERENCES usuarios(id),
    fecha_despacho TIMESTAMP,
    motivo_rechazo TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_turno CHECK (turno IN ('Dia', 'Noche')),
    CONSTRAINT chk_estado_reserva CHECK (estado IN ('Pendiente', 'Aprobada', 'Rechazada', 'Despachada', 'Cancelada'))
);

CREATE TABLE reservas_detalle (
    id SERIAL PRIMARY KEY,
    reserva_id INT NOT NULL REFERENCES reservas(id) ON DELETE CASCADE,
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    cantidad_solicitada INT NOT NULL DEFAULT 1,
    inventario_fisico_ids JSONB,
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
    inventario_fisico_id INT REFERENCES inventario_fisico(id),  -- NULLABLE v1
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    parada_id INT NOT NULL REFERENCES paradas(id),
    cantidad INT DEFAULT 1,
    
    -- Actores (NULLABLE en v1)
    usuario_ejecuta_id INT REFERENCES usuarios(id),
    grupo_destino_id INT REFERENCES grupos_trabajo(id),
    usuario_receptor_id INT REFERENCES usuarios(id),
    
    -- Contexto (NULLABLE en v1)
    tarea_id INT,
    reserva_id INT,
    
    -- Estados (para auditoría)
    estado_origen VARCHAR(20),
    estado_destino VARCHAR(20),
    
    -- Observaciones
    observaciones TEXT,
    
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
-- SECCIÓN I: TAREAS Y TRABAJOS DE RIESGO
-- ============================================================================

CREATE TABLE tipos_actividades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE tareas (
    id SERIAL PRIMARY KEY,
    codigo_tarea VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo_actividad_id INT NOT NULL REFERENCES tipos_actividades(id),
    parada_id INT NOT NULL REFERENCES paradas(id),
    grupo_id INT NOT NULL REFERENCES grupos_trabajo(id),
    
    -- Programación
    fecha_programada DATE NOT NULL,
    duracion_estimada_horas DECIMAL(5, 2),
    prioridad VARCHAR(10) DEFAULT 'Media',
    estado VARCHAR(20) DEFAULT 'Planificada',
    
    -- Responsables
    creado_por_id INT NOT NULL REFERENCES usuarios(id),
    responsable_antapaccay_nombre VARCHAR(200),
    responsable_antapaccay_cargo VARCHAR(200),
    responsable_antapaccay_contacto VARCHAR(100),
    
    -- Fechas de ejecución
    fecha_inicio_real TIMESTAMP,
    fecha_fin_real TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_prioridad CHECK (prioridad IN ('Alta', 'Media', 'Baja')),
    CONSTRAINT chk_estado_tarea CHECK (estado IN ('Planificada', 'En_Ejecucion', 'Completada', 'Cancelada'))
);

CREATE TABLE tareas_riesgos (
    tarea_id INT NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    tipo_riesgo_id INT NOT NULL REFERENCES tipos_riesgos(id) ON DELETE CASCADE,
    PRIMARY KEY (tarea_id, tipo_riesgo_id)
);

CREATE TABLE tareas_epps_requeridos (
    id SERIAL PRIMARY KEY,
    tarea_id INT NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    catalogo_id INT NOT NULL REFERENCES catalogo_materiales(id),
    cantidad_requerida INT DEFAULT 1,
    UNIQUE (tarea_id, catalogo_id)
);

CREATE INDEX idx_tareas_parada ON tareas(parada_id);
CREATE INDEX idx_tareas_grupo ON tareas(grupo_id);
CREATE INDEX idx_tareas_fecha ON tareas(fecha_programada);
CREATE INDEX idx_tareas_estado ON tareas(estado);
CREATE INDEX idx_tareas_nombre_trgm ON tareas USING gin (nombre gin_trgm_ops);
CREATE INDEX idx_tareas_descripcion_trgm ON tareas USING gin (descripcion gin_trgm_ops);

-- ============================================================================
-- SECCIÓN J: FOREIGN KEYS FALTANTES
-- ============================================================================

ALTER TABLE historial_movimientos ADD CONSTRAINT fk_historial_tarea
    FOREIGN KEY (tarea_id) REFERENCES tareas(id);

ALTER TABLE historial_movimientos ADD CONSTRAINT fk_historial_reserva
    FOREIGN KEY (reserva_id) REFERENCES reservas(id);

ALTER TABLE reservas ADD CONSTRAINT fk_reserva_tarea
    FOREIGN KEY (tarea_id) REFERENCES tareas(id);

-- ============================================================================
-- SECCIÓN K: TRIGGERS Y FUNCIONES
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

CREATE TRIGGER update_inventario_updated_at BEFORE UPDATE ON inventario_fisico
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tareas_updated_at BEFORE UPDATE ON tareas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Validar que solo herramientas/EPPs devolutivos tengan inventario_fisico
CREATE OR REPLACE FUNCTION validar_devolutivo()
RETURNS TRIGGER AS $$
DECLARE
    es_dev BOOLEAN;
BEGIN
    SELECT es_devolutivo INTO es_dev FROM catalogo_materiales WHERE id = NEW.catalogo_id;
    
    IF NOT es_dev THEN
        RAISE EXCEPTION 'Solo materiales devolutivos pueden tener inventario físico individual';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_devolutivo BEFORE INSERT ON inventario_fisico
    FOR EACH ROW EXECUTE FUNCTION validar_devolutivo();

-- Función: Auto-marcar pérdidas 3 días después del cierre de parada
-- (Se ejecuta vía scheduled task en backend, no como trigger automático)
-- CORREGIDO: sintaxis UPDATE...FROM válida para PostgreSQL + inserta registro en historial
CREATE OR REPLACE FUNCTION marcar_perdidas_cierre_parada(p_parada_id INT)
RETURNS TABLE(herramienta_id INT, catalogo_nombre VARCHAR, grupo_nombre VARCHAR, costo DECIMAL) AS $$
BEGIN
    RETURN QUERY
    WITH perdidas AS (
        UPDATE inventario_fisico i
        SET estado = 'Perdida',
            updated_at = CURRENT_TIMESTAMP
        FROM historial_movimientos hm,
             catalogo_materiales cm
        WHERE hm.inventario_fisico_id = i.id
            AND i.catalogo_id = cm.id
            AND hm.parada_id = p_parada_id
            AND i.estado = 'En_Uso'
            AND hm.tipo_movimiento = 'Entrega'
            AND hm.timestamp = (
                SELECT MAX(hm2.timestamp)
                FROM historial_movimientos hm2
                WHERE hm2.inventario_fisico_id = i.id
            )
        RETURNING i.id, i.catalogo_id, cm.nombre AS cat_nombre, cm.costo_reposicion, hm.grupo_destino_id
    ),
    -- Insertar registro de auditoría en historial por cada herramienta marcada como perdida
    registro_perdida AS (
        INSERT INTO historial_movimientos (tipo_movimiento, inventario_fisico_id, catalogo_id, parada_id, grupo_destino_id, estado_origen, estado_destino, observaciones)
        SELECT 'Perdida', p.id, p.catalogo_id, p_parada_id, p.grupo_destino_id, 'En_Uso', 'Perdida', 'Auto-marcado por cierre de parada (+3 días)'
        FROM perdidas p
    )
    SELECT p.id, p.cat_nombre, g.nombre, p.costo_reposicion
    FROM perdidas p
    LEFT JOIN grupos_trabajo g ON g.id = p.grupo_destino_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECCIÓN L: VISTAS ÚTILES
-- ============================================================================

-- Vista: Inventario con detalles del catálogo
CREATE VIEW v_inventario_detallado AS
SELECT 
    i.id,
    COALESCE(i.codigo_barras, 'SIN-BARRA-' || i.id::TEXT) AS identificador,
    i.estado,
    i.ubicacion_fisica,
    i.ubicacion_macro,
    c.codigo_interno AS short_code,
    c.nombre,
    c.tipo_material,
    cat.nombre AS categoria,
    c.costo_reposicion,
    i.fecha_adquisicion,
    i.fecha_ultima_inspeccion
FROM inventario_fisico i
JOIN catalogo_materiales c ON i.catalogo_id = c.id
JOIN categorias_materiales cat ON c.categoria_id = cat.id;

-- Vista: Herramientas actualmente en uso por grupo
-- CORREGIDO: usa MAX(timestamp) en lugar de MAX(id) para orden cronológico
CREATE VIEW v_herramientas_en_uso AS
SELECT 
    g.id AS grupo_id,
    g.nombre AS grupo_nombre,
    p.id AS parada_id,
    p.nombre AS parada_nombre,
    i.id AS inventario_id,
    c.codigo_interno AS short_code,
    c.nombre AS herramienta,
    c.costo_reposicion,
    h.timestamp AS fecha_entrega,
    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - h.timestamp)) AS dias_en_uso
FROM historial_movimientos h
JOIN inventario_fisico i ON h.inventario_fisico_id = i.id
JOIN catalogo_materiales c ON i.catalogo_id = c.id
JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
JOIN paradas p ON h.parada_id = p.id
WHERE i.estado = 'En_Uso'
    AND h.tipo_movimiento = 'Entrega'
    AND h.timestamp = (
        SELECT MAX(hm2.timestamp)
        FROM historial_movimientos hm2 
        WHERE hm2.inventario_fisico_id = i.id
    );

-- Vista: Dashboard de métricas para residente (solo devolutivas)
CREATE VIEW v_dashboard_metricas AS
SELECT 
    COUNT(*) FILTER (WHERE estado = 'Disponible') AS total_disponibles,
    COUNT(*) FILTER (WHERE estado = 'En_Uso') AS total_en_uso,
    COUNT(*) FILTER (WHERE estado = 'Malograda') AS total_malogradas,
    COUNT(*) FILTER (WHERE estado = 'En_Mantenimiento') AS total_en_mantenimiento,
    COUNT(*) FILTER (WHERE estado = 'Perdida') AS total_perdidas,
    COUNT(*) FILTER (WHERE estado = 'Baja') AS total_bajas,
    SUM(c.costo_reposicion) FILTER (WHERE i.estado = 'Perdida') AS costo_perdidas,
    SUM(c.costo_reposicion) FILTER (WHERE i.estado = 'En_Uso') AS costo_en_uso
FROM inventario_fisico i
JOIN catalogo_materiales c ON i.catalogo_id = c.id;

-- Vista: Pendientes de cierre por parada activa
CREATE VIEW v_pendientes_cierre_parada AS
SELECT 
    p.id AS parada_id,
    p.nombre AS parada_nombre,
    p.fecha_fin AS parada_fecha_fin,
    g.id AS grupo_id,
    g.nombre AS grupo_nombre,
    COUNT(i.id) AS herramientas_pendientes,
    SUM(c.costo_reposicion) AS costo_pendiente,
    CASE 
        WHEN p.fecha_fin IS NOT NULL AND CURRENT_DATE > p.fecha_fin + INTERVAL '3 days' 
        THEN 'VENCIDO' 
        ELSE 'PENDIENTE' 
    END AS estado_cierre
FROM paradas p
JOIN historial_movimientos h ON h.parada_id = p.id
JOIN inventario_fisico i ON h.inventario_fisico_id = i.id
JOIN catalogo_materiales c ON i.catalogo_id = c.id
JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
WHERE i.estado = 'En_Uso'
    AND h.tipo_movimiento = 'Entrega'
    AND h.timestamp = (
        SELECT MAX(hm2.timestamp)
        FROM historial_movimientos hm2 
        WHERE hm2.inventario_fisico_id = i.id
    )
GROUP BY p.id, p.nombre, p.fecha_fin, g.id, g.nombre;

-- Vista: Pérdidas por parada
CREATE VIEW v_perdidas_por_parada AS
SELECT 
    p.id AS parada_id,
    p.nombre AS parada_nombre,
    g.id AS grupo_id,
    g.nombre AS grupo_nombre,
    i.id AS inventario_id,
    c.codigo_interno AS short_code,
    c.nombre AS herramienta,
    c.costo_reposicion,
    h.timestamp AS fecha_perdida
FROM historial_movimientos h
JOIN inventario_fisico i ON h.inventario_fisico_id = i.id
JOIN catalogo_materiales c ON i.catalogo_id = c.id
JOIN paradas p ON h.parada_id = p.id
LEFT JOIN grupos_trabajo g ON h.grupo_destino_id = g.id
WHERE i.estado = 'Perdida'
    AND h.tipo_movimiento IN ('Perdida', 'Baja')
    AND h.timestamp = (
        SELECT MAX(hm2.timestamp)
        FROM historial_movimientos hm2 
        WHERE hm2.inventario_fisico_id = i.id
    );

-- ============================================================================
-- SECCIÓN M: DATOS SEMILLA
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
('CREAR_TAREA', 'Crear tareas', 'Tareas'),
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
WHERE codigo IN ('VER_INVENTARIO', 'CREAR_RESERVA', 'VER_DASHBOARD_GRUPO', 'VER_PETAR', 'CREAR_TAREA', 'ASIGNAR_GRUPO');

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
WHERE codigo IN ('VER_PETAR');

-- Crear usuarios de prueba
-- NOTA: Los password_hash son placeholders. Generar con passlib.hash.bcrypt antes de usar.
-- Ejemplo: python -c "from passlib.hash import bcrypt; print(bcrypt.hash('admin123'))"

-- Contraseñas de prueba (SOLO para desarrollo, cambiar en producción):
-- carlos.rodriguez → admin123
-- admin             → admin123
-- juan.perez        → almacen123
INSERT INTO usuarios (dni, nombre, apellido, email, password_hash, rol_id) VALUES
('12345678', 'Carlos', 'Rodríguez', 'carlos.rodriguez@sermul.pe', 
 '$2b$12$rc3qP35fMrn0kWU.7zZssOhaaGHVjPu3.gb2mMIb8iI.382DcBIEe',  -- admin123
 (SELECT id FROM roles WHERE codigo = 'RESIDENTE'));

INSERT INTO usuarios (dni, nombre, apellido, email, password_hash, rol_id) VALUES
('87654321', 'Sistema', 'Admin', 'admin@sermul.pe',
 '$2b$12$rc3qP35fMrn0kWU.7zZssOhaaGHVjPu3.gb2mMIb8iI.382DcBIEe',  -- admin123
 (SELECT id FROM roles WHERE codigo = 'ADMIN'));

INSERT INTO usuarios (dni, nombre, apellido, email, password_hash, rol_id) VALUES
('11223344', 'Juan', 'Pérez', 'juan.perez@sermul.pe',
 '$2b$12$tf4rSDYGVmiTckAtyKjQSu2YY0e7Ou3TiDKxzu1T.izb8svBJdor.',  -- almacen123
 (SELECT id FROM roles WHERE codigo = 'ALMACENERO'));

-- Sprint 1: Usuarios para grupo de trabajo
-- Contraseña: sermul123
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) VALUES
('22334455', 'Pedro', 'Quispe', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'LIDER_MEC')),
('33445566', 'Luis', 'Mamani', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('44556677', 'José', 'Huamán', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('55667788', 'Diego', 'Sánchez', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('66778899', 'Miguel', 'Torres', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR'));

-- Insertar Parada de ejemplo
INSERT INTO paradas (codigo, nombre, fecha_inicio, fecha_fin, estado) VALUES
('PAR-2026-001', 'Mantenimiento Molino SAG - Mayo 2026', '2026-05-10', NULL, 'Activa');

-- Sprint 1: Grupo de trabajo para pruebas de check-in/out
INSERT INTO grupos_trabajo (codigo, nombre, parada_id, lider_id, supervisor_id, estado)
SELECT 'GRP-001', 'Grupo A - Molino SAG', p.id, l.id, s.id, 'Activo'
FROM paradas p, usuarios l, usuarios s
WHERE p.codigo = 'PAR-2026-001'
  AND l.dni = '22334455'
  AND s.dni = '12345678';

INSERT INTO grupos_integrantes (grupo_id, usuario_id, fecha_ingreso, activo)
SELECT g.id, u.id, '2026-05-10', true
FROM grupos_trabajo g, usuarios u
WHERE g.codigo = 'GRP-001'
  AND u.dni IN ('22334455', '33445566', '44556677', '55667788', '66778899');

-- Insertar Categorías
INSERT INTO categorias_materiales (nombre, tipo_general) VALUES
('Herramientas Eléctricas', 'Herramienta'),
('Herramientas Manuales', 'Herramienta'),
('EPP - Protección de Cabeza', 'EPP'),
('EPP - Protección de Manos', 'EPP'),
('EPP - Protección Respiratoria', 'EPP'),
('EPP - Trabajo en Altura', 'EPP'),
('Consumibles Generales', 'Consumible');

-- Insertar catálogo de ejemplo
INSERT INTO catalogo_materiales 
(codigo_interno, nombre, categoria_id, tipo_material, costo_reposicion, es_devolutivo) VALUES
('HER-001', 'Taladro Percutor Bosch GSB 18V', 1, 'Herramienta', 850.00, true),
('HER-002', 'Amoladora Bosch GWS 18V', 1, 'Herramienta', 720.00, true),
('HER-003', 'Llave Combinada 13mm', 2, 'Herramienta', 45.00, true),
('HER-004', 'Llave de Impacto Milwaukee M18', 1, 'Herramienta', 1250.00, true),
('HER-005', 'Esmeril Angular DeWalt 4 1/2"', 1, 'Herramienta', 580.00, true),
('EPP-001', 'Casco de Seguridad MSA V-Gard', 3, 'EPP_Devolutivo', 120.00, true),
('EPP-002', 'Guantes de Nitrilo (par)', 4, 'EPP_Consumible', 15.00, false),
('EPP-003', 'Arnés de Seguridad Completo', 6, 'EPP_Devolutivo', 680.00, true),
('EPP-004', 'Respirador 3M 6200', 5, 'EPP_Devolutivo', 195.00, true),
('CONS-001', 'Tornillos 1/4" x 100 unidades', 7, 'Suministro', 28.00, false);

-- Actualizar campos específicos de EPPs
UPDATE catalogo_materiales SET 
    vida_util_dias = 365,
    requiere_certificacion = true,
    certificacion_norma = 'ANSI Z89.1',
    requiere_inspeccion = true
WHERE codigo_interno = 'EPP-001';

UPDATE catalogo_materiales SET 
    vida_util_dias = 180,
    requiere_certificacion = true,
    certificacion_norma = 'ANSI Z359',
    requiere_inspeccion = true
WHERE codigo_interno = 'EPP-003';

UPDATE catalogo_materiales SET 
    vida_util_dias = 730,
    requiere_certificacion = true,
    certificacion_norma = 'NIOSH 42 CFR 84',
    requiere_inspeccion = true
WHERE codigo_interno = 'EPP-004';

-- Insertar inventario físico de ejemplo (sin código de barras)
INSERT INTO inventario_fisico (catalogo_id, estado, ubicacion_fisica, ubicacion_macro, fecha_adquisicion) VALUES
-- Taladros (HER-001): 2 disponibles, 1 en uso
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-001'), 'Disponible', 'Estante A-12', 'Mina', '2026-01-15'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-001'), 'Disponible', 'Estante A-12', 'Mina', '2026-01-15'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-001'), 'En_Uso', 'Estante A-12', 'Mina', '2026-01-15'),
-- Amoladoras (HER-002): 1 disponible, 1 en tránsito
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-002'), 'Disponible', 'Estante B-04', 'Mina', '2026-03-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-002'), 'En_Ciudad', 'Bodega Principal', 'Ciudad', '2026-03-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-002'), 'En_Transito_Compra', NULL, 'Transito_Compra', '2026-04-20'),
-- Llaves combinadas (HER-003): 3 disponibles
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-003'), 'Disponible', 'Gaveta C-01', 'Mina', '2026-02-10'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-003'), 'Disponible', 'Gaveta C-01', 'Mina', '2026-02-10'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-003'), 'Disponible', 'Gaveta C-01', 'Mina', '2026-02-10'),
-- Llave de impacto (HER-004): 2 disponibles
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-004'), 'Disponible', 'Estante D-08', 'Mina', '2026-04-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-004'), 'Disponible', 'Estante D-08', 'Mina', '2026-04-01'),
-- Esmeril (HER-005): 1 en Ciudad, 1 disponible
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-005'), 'Disponible', 'Estante B-06', 'Mina', '2026-05-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-005'), 'En_Ciudad', 'Bodega Principal', 'Ciudad', '2026-05-01'),
-- Cascos (EPP-001): 3 disponibles
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-001'), 'Disponible', 'Estante E-01', 'Mina', '2026-01-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-001'), 'Disponible', 'Estante E-01', 'Mina', '2026-01-01'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-001'), 'Disponible', 'Estante E-01', 'Mina', '2026-01-01'),
-- Arneses (EPP-003): 1 disponible
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-003'), 'Disponible', 'Estante F-03', 'Mina', '2026-02-15'),
-- Respiradores (EPP-004): 2 disponibles
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-004'), 'Disponible', 'Estante G-02', 'Mina', '2026-03-10'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'EPP-004'), 'Disponible', 'Estante G-02', 'Mina', '2026-03-10');

-- Insertar Tipos de Riesgos
INSERT INTO tipos_riesgos (codigo, nombre, requiere_supervision_ssoma, color_hex) VALUES
('TRAB_ALTURA', 'Trabajo en Altura (> 1.80m)', true, '#FF5733'),
('ESP_CONFINADO', 'Espacio Confinado', true, '#C70039'),
('TRAB_CALIENTE', 'Trabajo en Caliente (soldadura/corte)', true, '#FFC300'),
('ENERG_PELIGROSA', 'Energías Peligrosas', true, '#DAF7A6'),
('QUIMICOS', 'Manejo de Químicos', true, '#900C3F');

-- Insertar PETARs de ejemplo
INSERT INTO petars (codigo, nombre, tipo_riesgo_id, version, fecha_actualizacion, archivo_pdf_url, aprobado_por) VALUES
('PETAR-001', 'Procedimiento de Trabajo en Altura', 
 (SELECT id FROM tipos_riesgos WHERE codigo = 'TRAB_ALTURA'),
 'v2.1', '2026-03-01', '/static/petars/petar-001-v2.1.pdf', 
 'Ing. María González - Supervisor SSOMA Antapaccay'),
('PETAR-002', 'Bloqueo y Etiquetado de Energías (LOTO)', 
 (SELECT id FROM tipos_riesgos WHERE codigo = 'ENERG_PELIGROSA'),
 'v1.8', '2026-02-15', '/static/petars/petar-002-v1.8.pdf', 
 'Ing. Pedro Castro - Gerente SSOMA Antapaccay');

-- ============================================================================
-- FIN DEL SCRIPT DDL
-- ============================================================================

COMMENT ON TABLE paradas IS 'Entidad principal. Agrupa toda la actividad de un mantenimiento programado.';
COMMENT ON TABLE historial_movimientos IS 'Log de movimientos. Flexible en v1 (FKs opcionales). Uso de particionamiento por año.';
COMMENT ON COLUMN inventario_fisico.codigo_barras IS 'NULLABLE en v1. Se llenará en fase futura con lectores de código de barras.';
COMMENT ON COLUMN inventario_fisico.ubicacion_macro IS 'Ubicación logística: Ciudad, Transito_Compra, Mina.';
COMMENT ON COLUMN catalogo_materiales.codigo_interno IS 'Short code mnemotécnico para digitación manual rápida (máx 15 caracteres).';
COMMENT ON COLUMN catalogo_materiales.es_devolutivo IS 'true=se controla individualmente, false=se entrega a granel sin inventario físico.';
