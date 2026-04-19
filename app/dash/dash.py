from flask import render_template, request, redirect, url_for
from . import dashboard_bp
from werkzeug.security import generate_password_hash
import mysql.connector
from db import obtener_conexion

def get_db():
    conn = obtener_conexion()
    if conn is None:
        return None
        
    cursor = conn.cursor()
    
    # 1. TABLAS MAESTRAS
    cursor.execute('''CREATE TABLE IF NOT EXISTS servicios (
        id_servicio INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
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
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
        nombre_proveedor VARCHAR(100) NOT NULL,
        nombre_representante VARCHAR(100),
        nit VARCHAR(20) UNIQUE,
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion TEXT,
        servicio_id INT,
        FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicio)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
        id_productos INT AUTO_INCREMENT PRIMARY KEY,
        nombre_producto VARCHAR(100) NOT NULL,
        descripcion_producto TEXT,
        precio_unitario_producto NUMERIC(10,2) NOT NULL,
        moneda VARCHAR(10) DEFAULT 'COP',
        stock INT DEFAULT 0,
        proveedor_id INT,
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedor)
    )''')

    # 2. PERSONAL Y SEGURIDAD
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendedor (
        id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
        tipo_identificador VARCHAR(100),
        nombre_empresa VARCHAR(100),
        direccion_empresa VARCHAR(100),
        pais_empresa VARCHAR(100),
        departamento_empresa VARCHAR(100),
        ciudad_empresa VARCHAR(100)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INT AUTO_INCREMENT PRIMARY KEY,
        nombre_empresa VARCHAR(100),
        nombre_completo VARCHAR(100),
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(50),
        telefono VARCHAR(20)
    )''')

    # 3. PROCESO DE PRE-VENTA
    cursor.execute('''CREATE TABLE IF NOT EXISTS cotizaciones (
        id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id VARCHAR(50) NOT NULL,
        vendedor_id INT NOT NULL,
        fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento DATE,
        estado VARCHAR(20) DEFAULT 'Pendiente', 
        total NUMERIC(12,2) DEFAULT 0,
        observaciones TEXT
    )''')

    # 4. TRANSACCIONES REALES
    cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (
        id_factura INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id VARCHAR(50) NOT NULL,
        usuario_id INT NOT NULL,
        vendedor_id INT NOT NULL,
        cotizacion_id INT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total NUMERIC(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'Emitida'
    )''')

    # 5. CONTABILIDAD
    cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos_contables (
        id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descripcion TEXT,
        tipo VARCHAR(10),
        monto NUMERIC(12,2) NOT NULL,
        factura_id INT,
        compra_id INT
    )''')

    conn.commit()
    cursor.close()
    return conn

@dashboard_bp.route('/dashboard')
def dash_view():
    return render_template('dashboard.html')

@dashboard_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        numero_id = request.form.get('numero_identificacion')
        tipo_id = request.form.get('tipo_identificador')
        empresa = request.form.get('nombre_empresa')
        sector = request.form.get('sector_economico')
        representante = request.form.get('nombre_representante')
        contacto = request.form.get('contacto_cliente')
        direccion = request.form.get('direccion_cliente')
        pais = request.form.get('pais_cliente')
        departamento = request.form.get('departamento_cliente')
        ciudad = request.form.get('ciudad_cliente')
        telefono = request.form.get('telefono')
        email = request.form.get('email')

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (
                    numero_identificacion, tipo_identificador, nombre_empresa, sector_economico,
                    nombre_representante, contacto_cliente, direccion_cliente, pais_cliente,
                    departamento_cliente, ciudad_cliente, telefono, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (numero_id, tipo_id, empresa, sector, representante, 
                  contacto, direccion, pais, departamento, ciudad, telefono, email))
            conn.commit()
            cursor.close()
        except mysql.connector.IntegrityError:
            pass
        conn.close()
        return redirect(url_for('dashboard.clientes'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM clientes ORDER BY fecha_creacion DESC')
    clientes_records = cursor.fetchall()
    
    total_clientes = len(clientes_records)
    nuevos_clientes = total_clientes
    total_paises = len(set([c['pais_cliente'] for c in clientes_records if c.get('pais_cliente')]))
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes_records, total_clientes=total_clientes, nuevos_clientes=nuevos_clientes, total_paises=total_paises)

@dashboard_bp.route('/cotizaciones', methods=['GET', 'POST'])
def cotizaciones():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        vendedor_id = request.form.get('vendedor_id')
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        estado = request.form.get('estado')
        total = request.form.get('total')
        observaciones = request.form.get('observaciones')

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cotizaciones (
                cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s)
        ''', (cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.cotizaciones'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM cotizaciones ORDER BY fecha_emision DESC')
    cotizaciones_records = cursor.fetchall()
    
    total_cotizaciones = len(cotizaciones_records)
    
    cursor.execute("SELECT COUNT(*) as c FROM cotizaciones WHERE estado='Pendiente'")
    pendientes = cursor.fetchone()['c'] or 0
    
    cursor.execute("SELECT SUM(total) as t FROM cotizaciones")
    sum_res = cursor.fetchone()
    total_sum = sum_res['t'] if sum_res and sum_res['t'] else 0
    total_sum_fmt = f"${total_sum:,.2f}"
    
    cursor.execute("SELECT id_cliente, nombre_empresa, numero_identificacion FROM clientes")
    clientes_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('cotizaciones.html', cotizaciones=cotizaciones_records, total_cotizaciones=total_cotizaciones, pendientes=pendientes, total_sum_fmt=total_sum_fmt, clientes=clientes_list)


@dashboard_bp.route('/servicios', methods=['GET', 'POST'])
def servicios():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO servicios (nombre, descripcion) VALUES (%s, %s)', (nombre, descripcion))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.servicios'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM servicios ORDER BY id_servicio DESC')
    servicios_records = cursor.fetchall()
    total_servicios = len(servicios_records)
    cursor.close()
    conn.close()
    return render_template('servicios.html', servicios=servicios_records, total_servicios=total_servicios)


@dashboard_bp.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        nombre = request.form.get('nombre_proveedor')
        representante = request.form.get('nombre_representante')
        nit = request.form.get('nit')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')
        servicio_id = request.form.get('servicio_id')

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO proveedores (nombre_proveedor, nombre_representante, nit, telefono, email, direccion, servicio_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (nombre, representante, nit, telefono, email, direccion, servicio_id))
            conn.commit()
            cursor.close()
        except mysql.connector.IntegrityError:
            pass # Ignorar NITs duplicados por ahora
            
        conn.close()
        return redirect(url_for('dashboard.proveedores'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, s.nombre as servicio_nombre 
        FROM proveedores p 
        LEFT JOIN servicios s ON p.servicio_id = s.id_servicio 
        ORDER BY p.id_proveedor DESC
    ''')
    proveedores_records = cursor.fetchall()
    
    cursor.execute('SELECT * FROM servicios')
    servicios_list = cursor.fetchall()
    total_proveedores = len(proveedores_records)
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_records, servicios=servicios_list, total=total_proveedores)


@dashboard_bp.route('/productos', methods=['GET', 'POST'])
def productos():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        nombre_producto = request.form.get('nombre_producto')
        descripcion_producto = request.form.get('descripcion_producto')
        precio_unitario_producto = request.form.get('precio_unitario_producto')
        moneda = request.form.get('moneda')
        stock = request.form.get('stock')
        proveedor_id = request.form.get('proveedor_id')

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre_producto, descripcion_producto, precio_unitario_producto, moneda, stock, proveedor_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre_producto, descripcion_producto, precio_unitario_producto, moneda, stock, proveedor_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.productos'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.*, pr.nombre_proveedor 
        FROM productos p 
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id_proveedor 
        ORDER BY p.id_productos DESC
    ''')
    productos_records = cursor.fetchall()
    
    cursor.execute('SELECT * FROM proveedores')
    proveedores_list = cursor.fetchall()
    total_productos = len(productos_records)
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=productos_records, proveedores=proveedores_list, total=total_productos)


@dashboard_bp.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        empresa = request.form.get('nombre_empresa')
        nombre = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')
        telefono = request.form.get('telefono')
        
        # Encriptando la contraseña
        p_hash = generate_password_hash(password)

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nombre_empresa, nombre_completo, email, password_hash, rol, telefono) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (empresa, nombre, email, p_hash, rol, telefono))
            conn.commit()
            cursor.close()
        except mysql.connector.IntegrityError:
            pass
            
        conn.close()
        return redirect(url_for('dashboard.usuarios'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios ORDER BY id_usuario DESC')
    usuarios_records = cursor.fetchall()
    total_usuarios = len(usuarios_records)
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios_records, total=total_usuarios)


@dashboard_bp.route('/facturas', methods=['GET', 'POST'])
def facturas():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        usuario_id = request.form.get('usuario_id')
        vendedor_id = request.form.get('vendedor_id')
        cotizacion_id = request.form.get('cotizacion_id') or None
        total = request.form.get('total')
        estado = request.form.get('estado')

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO facturas (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado))
        
        # Obtener el último ID insertado
        cursor.execute("SELECT LAST_INSERT_ID() as last_id")
        res = cursor.fetchone()
        factura_id = res[0]
        
        # Registrar un movimiento contable automático de INGRESO
        cursor.execute('''
            INSERT INTO movimientos_contables (descripcion, tipo, monto, factura_id) 
            VALUES (%s, %s, %s, %s)
        ''', (f"Venta con Factura #{factura_id}", "INGRESO", total, factura_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.facturas'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
                 SELECT f.*, c.nombre_empresa 
                 FROM facturas f 
                 LEFT JOIN clientes c ON f.cliente_id = c.id_cliente 
                 ORDER BY f.fecha DESC
    ''')
    facturas_records = cursor.fetchall()
    
    total_facturas = len(facturas_records)
    
    cursor.execute("SELECT SUM(total) as s FROM facturas WHERE estado != 'Anulada'")
    ing_res = cursor.fetchone()
    ingresos = ing_res['s'] if ing_res and ing_res['s'] else 0
    
    cursor.execute("SELECT * FROM clientes")
    clientes_list = cursor.fetchall()
    
    cursor.execute("SELECT * FROM usuarios")
    usuarios_list = cursor.fetchall()
    
    # Dummy vendedores
    cursor.execute("SELECT * FROM vendedor")
    vendedores_list = cursor.fetchall()
    
    cursor.execute("SELECT * FROM cotizaciones WHERE estado='Aprobada'")
    cotizaciones_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('facturas.html', facturas=facturas_records, total_facturas=total_facturas, ingresos=f"${float(ingresos):,.2f}", clientes=clientes_list, usuarios=usuarios_list, vendedores=vendedores_list, cotizaciones=cotizaciones_list)


@dashboard_bp.route('/ventas')
def ventas():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT * FROM movimientos_contables 
        WHERE tipo = 'INGRESO' 
        ORDER BY fecha DESC
    ''')
    movimientos = cursor.fetchall()
    
    total_ingresos = sum([float(m['monto']) for m in movimientos])
    total_count = len(movimientos)
    cursor.close()
    conn.close()
    return render_template('ventas.html', movimientos=movimientos, total_ingresos=f"${total_ingresos:,.2f}", total_count=total_count)