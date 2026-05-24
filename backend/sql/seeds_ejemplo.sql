-- ============================================================================
-- SERMUL — Seeds de Ejemplo (DATOS FICTICIOS - SEGURO PARA GIT)
-- Usar como plantilla para nuevos desarrolladores.
-- Copiar a seeds_desarrollo.sql y reemplazar con datos reales.
-- ============================================================================

-- Contraseña universal desarrollo: sermul123
-- Hash: $2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe

-- ============================================================================
-- 1. USUARIOS DE EJEMPLO
-- ============================================================================

-- Supervisores de Operación
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) VALUES
('70123400', 'Supervisor', 'Operaciones 1', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'SUP_MEC')),
('70123401', 'Supervisor', 'Operaciones 2', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'SUP_MEC'));

-- Supervisores SSOMA
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) VALUES
('40987600', 'Supervisor', 'SSOMA 1', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'SUP_SSOMA'));

-- Líderes
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) VALUES
('44567000', 'Líder', 'Ejemplo 1', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'LIDER_MEC')),
('44567001', 'Líder', 'Ejemplo 2', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'LIDER_MEC')),
('22334455', 'Pedro', 'Quispe', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'LIDER_MEC'));

-- Trabajadores
INSERT INTO usuarios (dni, nombre, apellido, password_hash, rol_id) VALUES
('33445566', 'Luis', 'Mamani', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('44556677', 'José', 'Huamán', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('55667788', 'Diego', 'Sánchez', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR')),
('66778899', 'Miguel', 'Torres', '$2b$12$j5MKNKdPemW0vNlsvZ.S1udemcRfIx4/tjWm0rurx.GmzCE778tBe', (SELECT id FROM roles WHERE codigo = 'TRABAJADOR'));
-- Agregar más trabajadores según necesidad

-- ============================================================================
-- 2. PARADAS DE EJEMPLO
-- ============================================================================

INSERT INTO paradas (codigo, nombre, fecha_inicio, fecha_fin, estado) VALUES
('PAR-2026-001', 'Parada de Prueba - Mayo 2026', '2026-05-10', NULL, 'Activa');

-- ============================================================================
-- 3. CATÁLOGO DE EJEMPLO (items básicos)
-- ============================================================================

INSERT INTO catalogo_materiales (codigo_interno, nombre, categoria_id, tipo_material, costo_reposicion, es_devolutivo) VALUES
('HER-001', 'Taladro Percutor de Prueba', 1, 'Herramienta', 850.00, true),
('HER-002', 'Amoladora de Prueba', 1, 'Herramienta', 720.00, true),
('HER-003', 'Llave Combinada de Prueba', 2, 'Herramienta', 45.00, true);

-- Agregar más items según necesidad (copiar de seeds_desarrollo.sql)

-- ============================================================================
-- 4. INVENTARIO FÍSICO DE EJEMPLO
-- ============================================================================

INSERT INTO inventario_fisico (catalogo_id, estado, ubicacion_fisica, ubicacion_macro, fecha_adquisicion) VALUES
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-001'), 'Disponible', 'Estante A-01', 'Mina', '2026-01-15'),
((SELECT id FROM catalogo_materiales WHERE codigo_interno = 'HER-001'), 'Disponible', 'Estante A-01', 'Mina', '2026-01-15');

-- ============================================================================
-- 5. GRUPO DE EJEMPLO
-- ============================================================================

INSERT INTO grupos_trabajo (codigo, nombre, parada_id, lider_id, supervisor_id, estado)
SELECT 'GRP-001', 'Grupo A - Prueba',
    (SELECT id FROM paradas WHERE codigo = 'PAR-2026-001'),
    (SELECT id FROM usuarios WHERE dni = '22334455'),
    (SELECT id FROM usuarios WHERE dni = '70123400'),
    'Activo';

INSERT INTO grupos_integrantes (grupo_id, usuario_id, fecha_ingreso, activo)
SELECT g.id, u.id, '2026-05-10', true
FROM grupos_trabajo g, usuarios u
WHERE g.codigo = 'GRP-001'
  AND u.dni IN ('22334455', '33445566', '44556677', '55667788', '66778899');

-- ============================================================================
-- FIN DATOS DE EJEMPLO
-- Para datos ricos: copiar y adaptar seeds_desarrollo.sql (NO incluir en git)
-- ============================================================================
