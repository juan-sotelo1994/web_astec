-- ==========================================
-- 1. TABLAS MAESTRAS (CATÁLOGOS)
-- ==========================================

CREATE TABLE servicios (
    id_servicios INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    precio_sugerido DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    numero_identificacion VARCHAR(50) NOT NULL UNIQUE,
    tipo_identificador VARCHAR(50),
    nombre_empresa VARCHAR(100),
    sector_economico VARCHAR(100),
    nombre_representante VARCHAR(100),
    contacto_cliente VARCHAR(100),
    direccion_cliente VARCHAR(255),
    pais_cliente VARCHAR(100),
    departamento_cliente VARCHAR(100),
    ciudad_cliente VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE proveedores (
    id_proveedores INT AUTO_INCREMENT PRIMARY KEY,
    nombre_proveedor VARCHAR(100) NOT NULL,
    nombre_representante VARCHAR(100),
    nit VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    servicio_id INT,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicios)
);

CREATE TABLE productos (
    id_productos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    descripcion_producto TEXT,
    precio_unitario_producto DECIMAL(10,2) NOT NULL,
    moneda VARCHAR(10) DEFAULT 'COP',
    stock INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    proveedor_id INT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedores)
);

-- ==========================================
-- 2. PERSONAL Y SEGURIDAD
-- ==========================================

CREATE TABLE vendedores (
    id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
    numero_identificacion VARCHAR(50) UNIQUE,
    nombre_completo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    ciudad VARCHAR(100),
    comision_porcentaje DECIMAL(5,2) DEFAULT 0.00
);

CREATE TABLE usuarios (
    id_usuarios INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100),
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50),
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (email)
);

-- ==========================================
-- 3. PROCESOS COMERCIALES (PRE-VENTA Y COMPRA)
-- ==========================================

CREATE TABLE cotizaciones (
    id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    usuario_id INT NOT NULL,
    vendedor_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_emision DATE,
    fecha_vencimiento DATE,
    total DECIMAL(12,2) DEFAULT 0.00,
    observaciones TEXT,
    estado ENUM('borrador','enviada','aprobada','rechazada') DEFAULT 'borrador',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuarios),
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id_vendedor)
);

CREATE TABLE detalle_cotizacion (
    id_detalle_cot INT AUTO_INCREMENT PRIMARY KEY,
    cotizacion_id INT NOT NULL,
    producto_id INT NULL,
    servicio_id INT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones(id_cotizacion) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id_productos),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicios),
    CONSTRAINT chk_cot_item CHECK ((producto_id IS NOT NULL AND servicio_id IS NULL) OR (producto_id IS NULL AND servicio_id IS NOT NULL))
);

CREATE TABLE ordenes_compra (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_estimado DECIMAL(12,2) DEFAULT 0.00,
    estado ENUM('pendiente', 'recibida', 'cancelada') DEFAULT 'pendiente',
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedores),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuarios)
);

-- ==========================================
-- 4. TRANSACCIONES (VENTAS Y FACTURAS)
-- ==========================================

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    vendedor_id INT NOT NULL,
    usuario_id INT NOT NULL,
    cotizacion_id INT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(12,2) DEFAULT 0.00,
    metodo_pago ENUM('efectivo', 'transferencia', 'tarjeta', 'credito') NOT NULL,
    estado_venta ENUM('completada', 'cancelada', 'devolucion') DEFAULT 'completada',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente),
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id_vendedor),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuarios),
    FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones(id_cotizacion)
);

CREATE TABLE detalle_venta (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NULL,
    servicio_id INT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario_aplicado DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario_aplicado) STORED,
    FOREIGN KEY (venta_id) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id_productos),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicios),
    CONSTRAINT chk_venta_item CHECK ((producto_id IS NOT NULL AND servicio_id IS NULL) OR (producto_id IS NULL AND servicio_id IS NOT NULL))
);

CREATE TABLE facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_factura ENUM('pendiente', 'pagada', 'anulada') DEFAULT 'pendiente',
    total_factura DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id_venta)
);

-- ==========================================
-- 5. COMPRAS E INVENTARIO
-- ==========================================

CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id INT NOT NULL,
    orden_id INT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2) DEFAULT 0.00,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedores),
    FOREIGN KEY (orden_id) REFERENCES ordenes_compra(id_orden)
);

CREATE TABLE detalle_compra (
    id_detalle_com INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * costo_unitario) STORED,
    FOREIGN KEY (compra_id) REFERENCES compras(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id_productos)
);

-- ==========================================
-- 6. CONTABILIDAD Y AUDITORÍA
-- ==========================================

CREATE TABLE movimientos_contables (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT,
    tipo ENUM('ingreso', 'egreso') NOT NULL,
    monto DECIMAL(12,2) NOT NULL,
    venta_id INT NULL,
    compra_id INT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id_venta),
    FOREIGN KEY (compra_id) REFERENCES compras(id_compra)
);

-- ==========================================
-- 7. AUTOMATIZACIÓN (TRIGGERS)
-- ==========================================

DELIMITER //
CREATE TRIGGER tr_actualizar_stock_venta
AFTER INSERT ON detalle_venta
FOR EACH ROW
BEGIN
    IF NEW.producto_id IS NOT NULL THEN
        UPDATE productos 
        SET stock = stock - NEW.cantidad 
        WHERE id_productos = NEW.producto_id;
    END IF;
END //

CREATE TRIGGER tr_actualizar_stock_compra
AFTER INSERT ON detalle_compra
FOR EACH ROW
BEGIN
    UPDATE productos 
    SET stock = stock + NEW.cantidad 
    WHERE id_productos = NEW.producto_id;
END //
DELIMITER ;

-- ==========================================
-- 8. INDICES DE RENDIMIENTO
-- ==========================================
CREATE INDEX idx_venta_cliente ON ventas(cliente_id);
CREATE INDEX idx_detalle_venta_item ON detalle_venta(producto_id, servicio_id);
CREATE INDEX idx_token_email ON password_reset_tokens(email);
