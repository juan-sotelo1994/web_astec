-- =========================
-- CLIENTES
-- =========================
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    numero_identificacion VARCHAR(50) NOT NULL UNIQUE,
    tipo_identificador VARCHAR(50),
    nombre_empresa VARCHAR(100),
    sector_economico VARCHAR(100),
    nombre_representante VARCHAR(100),
    contacto_cliente VARCHAR(100),
    direccion_cliente VARCHAR(100),
    pais_cliente VARCHAR(100),
    departamento_cliente VARCHAR(100),
    ciudad_cliente VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- SERVICIOS
-- =========================
CREATE TABLE servicios (
    id_servicios INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- =========================
-- PROVEEDORES
-- =========================
CREATE TABLE proveedores (
    id_proveedores INT AUTO_INCREMENT PRIMARY KEY,
    nombre_proveedor VARCHAR(100),
    nombre_representante VARCHAR(100),
    nit VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    servicio_id INT,

    FOREIGN KEY (servicio_id)
        REFERENCES servicios(id_servicios)
);

-- =========================
-- PRODUCTOS
-- =========================
CREATE TABLE productos (
    id_productos INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100),
    descripcion_producto TEXT,
    precio_unitario_producto DECIMAL(10,2),
    moneda VARCHAR(10) DEFAULT 'COP',
    stock INT DEFAULT 0,
    proveedor_id INT,

    FOREIGN KEY (proveedor_id)
        REFERENCES proveedores(id_proveedores)
);

-- =========================
-- USUARIOS
-- =========================
CREATE TABLE usuarios (
    id_usuarios INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100),
    nombre VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50),
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- FACTURAS
-- =========================
CREATE TABLE facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2),
    estado ENUM('pendiente','pagada','anulada'),

    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuarios)
);

-- =========================
-- DETALLE FACTURA
-- =========================
CREATE TABLE detalle_factura (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2),

    subtotal DECIMAL(12,2)
        GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,

    FOREIGN KEY (factura_id)
        REFERENCES facturas(id_factura)
        ON DELETE CASCADE,

    FOREIGN KEY (producto_id)
        REFERENCES productos(id_productos)
);

-- =========================
-- COMPRAS
-- =========================
CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    proveedor_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2),

    FOREIGN KEY (proveedor_id)
        REFERENCES proveedores(id_proveedores)
);

-- =========================
-- DETALLE COMPRA
-- =========================
CREATE TABLE detalle_compra (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    costo DECIMAL(10,2),

    subtotal DECIMAL(12,2)
        GENERATED ALWAYS AS (cantidad * costo) STORED,

    FOREIGN KEY (compra_id)
        REFERENCES compras(id_compra)
        ON DELETE CASCADE,

    FOREIGN KEY (producto_id)
        REFERENCES productos(id_productos)
);

-- =========================
-- TOKENS RECUPERACIÓN
-- =========================
CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracion TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (email)
);

-- =========================
-- COTIZACIONES
-- =========================
CREATE TABLE cotizaciones (
    id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2),
    estado ENUM('borrador','enviada','aprobada','rechazada'),

    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuarios)
);

-- =========================
-- DETALLE COTIZACION
-- =========================
CREATE TABLE detalle_cotizacion (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    cotizacion_id INT,
    producto_id INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),

    subtotal DECIMAL(12,2)
        GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,

    FOREIGN KEY (cotizacion_id)
        REFERENCES cotizaciones(id_cotizacion)
        ON DELETE CASCADE,

    FOREIGN KEY (producto_id)
        REFERENCES productos(id_productos)
);

-- =========================
-- MOVIMIENTOS CONTABLES
-- =========================
CREATE TABLE movimientos_contables (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT,
    tipo ENUM('ingreso','gasto') NOT NULL,
    monto DECIMAL(12,2) NOT NULL,

    referencia_id INT,
    referencia_tipo VARCHAR(20)
);

-- =========================
-- ÍNDICES (rendimiento)
-- =========================
CREATE INDEX idx_factura_cliente ON facturas(cliente_id);
CREATE INDEX idx_factura_usuario ON facturas(usuario_id);
CREATE INDEX idx_detalle_factura_producto ON detalle_factura(producto_id);
CREATE INDEX idx_compra_proveedor ON compras(proveedor_id);
CREATE INDEX idx_detalle_compra_producto ON detalle_compra(producto_id);
