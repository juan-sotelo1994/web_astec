import sqlite3
from flask import render_template, request, redirect, url_for
from . import dashboard_bp
from werkzeug.security import generate_password_hash

def get_db():
    conn = sqlite3.connect('astec.db')
    conn.row_factory = sqlite3.Row
    
    # 1. TABLAS MAESTRAS
    conn.execute('''CREATE TABLE IF NOT EXISTS servicios (
        id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id_clientes TEXT PRIMARY KEY,
        Tipo_identificador VARCHAR(50),
        Nombre_empresa VARCHAR(100),
        Sector_Economico_cliente VARCHAR(100),
        nombre_representante VARCHAR(100),
        contacto_cliente VARCHAR(100),
        direccion_cliente VARCHAR(100),
        pais_cliente VARCHAR(100),
        Ddepartamento_cliente VARCHAR(100),
        telefono FLOAT,
        email VARCHAR(100),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_proveedor VARCHAR(100) NOT NULL,
        nombre_representante VARCHAR(100),
        nit VARCHAR(20) UNIQUE,
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion TEXT,
        servicio_id INTEGER,
        FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicio)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto VARCHAR(100) NOT NULL,
        descripcion_producto TEXT,
        precio_unitario_producto NUMERIC(10,2) NOT NULL,
        stock INTEGER DEFAULT 0,
        proveedor_id INTEGER,
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedor)
    )''')

    # 2. PERSONAL Y SEGURIDAD
    conn.execute('''CREATE TABLE IF NOT EXISTS vendedor (
        id_vendedor INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_identificador VARCHAR(100),
        nombre_empresa VARCHAR(100),
        direccion_empresa VARCHAR(100),
        pais_empresa VARCHAR(100),
        departamento_empresa VARCHAR(100),
        ciudad_empresa VARCHAR(100)
    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_empresa VARCHAR(100),
        nombre_completo VARCHAR(100),
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(50),
        telefono VARCHAR(20)
    )''')

    # 3. PROCESO DE PRE-VENTA
    conn.execute('''CREATE TABLE IF NOT EXISTS cotizaciones (
        id_cotizacion INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id TEXT NOT NULL,
        vendedor_id INTEGER NOT NULL,
        fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento DATE,
        estado VARCHAR(20) DEFAULT 'Pendiente', 
        total NUMERIC(12,2) DEFAULT 0,
        observaciones TEXT
    )''')

    # 4. TRANSACCIONES REALES
    conn.execute('''CREATE TABLE IF NOT EXISTS facturas (
        id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        vendedor_id INTEGER NOT NULL,
        cotizacion_id INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total NUMERIC(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'Emitida'
    )''')

    # 5. CONTABILIDAD
    conn.execute('''CREATE TABLE IF NOT EXISTS movimientos_contables (
        id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descripcion TEXT,
        tipo VARCHAR(10),
        monto NUMERIC(12,2) NOT NULL,
        factura_id INTEGER,
        compra_id INTEGER
    )''')

    conn.commit()
    return conn

@dashboard_bp.route('/dashboard')
def dash_view():
    return render_template('dashboard.html')

@dashboard_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db()
    
    if request.method == 'POST':
        id_clientes = request.form.get('id_clientes')
        tipo_id = request.form.get('Tipo_identificador')
        empresa = request.form.get('Nombre_empresa')
        sector = request.form.get('Sector_Economico_cliente')
        representante = request.form.get('nombre_representante')
        contacto = request.form.get('contacto_cliente')
        direccion = request.form.get('direccion_cliente')
        pais = request.form.get('pais_cliente')
        departamento = request.form.get('Ddepartamento_cliente')
        telefono = request.form.get('telefono')
        email = request.form.get('email')

        try:
            conn.execute('''
                INSERT INTO clientes (
                    id_clientes, Tipo_identificador, Nombre_empresa, Sector_Economico_cliente,
                    nombre_representante, contacto_cliente, direccion_cliente, pais_cliente,
                    Ddepartamento_cliente, telefono, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_clientes, tipo_id, empresa, sector, representante, 
                  contacto, direccion, pais, departamento, telefono, email))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
        return redirect(url_for('dashboard.clientes'))

    clientes_records = conn.execute('SELECT * FROM clientes ORDER BY fecha_creacion DESC').fetchall()
    total_clientes = len(clientes_records)
    nuevos_clientes = total_clientes
    total_paises = len(set([c['pais_cliente'] for c in clientes_records if c['pais_cliente']]))
    conn.close()
    return render_template('clientes.html', clientes=clientes_records, total_clientes=total_clientes, nuevos_clientes=nuevos_clientes, total_paises=total_paises)

@dashboard_bp.route('/cotizaciones', methods=['GET', 'POST'])
def cotizaciones():
    conn = get_db()
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        vendedor_id = request.form.get('vendedor_id')
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        estado = request.form.get('estado')
        total = request.form.get('total')
        observaciones = request.form.get('observaciones')

        conn.execute('''
            INSERT INTO cotizaciones (
                cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard.cotizaciones'))

    cotizaciones_records = conn.execute('SELECT * FROM cotizaciones ORDER BY fecha_emision DESC').fetchall()
    total_cotizaciones = len(cotizaciones_records)
    pendientes = conn.execute("SELECT COUNT(*) FROM cotizaciones WHERE estado='Pendiente'").fetchone()[0] or 0
    total_sum = conn.execute("SELECT SUM(total) FROM cotizaciones").fetchone()[0] or 0
    total_sum_fmt = f"${total_sum:,.2f}"
    clientes_list = conn.execute("SELECT id_clientes, Nombre_empresa FROM clientes").fetchall()
    conn.close()
    return render_template('cotizaciones.html', cotizaciones=cotizaciones_records, total_cotizaciones=total_cotizaciones, pendientes=pendientes, total_sum_fmt=total_sum_fmt, clientes=clientes_list)


@dashboard_bp.route('/servicios', methods=['GET', 'POST'])
def servicios():
    conn = get_db()
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        conn.execute('INSERT INTO servicios (nombre, descripcion) VALUES (?, ?)', (nombre, descripcion))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard.servicios'))
    
    servicios_records = conn.execute('SELECT * FROM servicios ORDER BY id_servicio DESC').fetchall()
    total_servicios = len(servicios_records)
    conn.close()
    return render_template('servicios.html', servicios=servicios_records, total_servicios=total_servicios)


@dashboard_bp.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    conn = get_db()
    if request.method == 'POST':
        nombre = request.form.get('nombre_proveedor')
        representante = request.form.get('nombre_representante')
        nit = request.form.get('nit')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')
        servicio_id = request.form.get('servicio_id')

        try:
            conn.execute('''
                INSERT INTO proveedores (nombre_proveedor, nombre_representante, nit, telefono, email, direccion, servicio_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, representante, nit, telefono, email, direccion, servicio_id))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Ignorar NITs duplicados por ahora
            
        conn.close()
        return redirect(url_for('dashboard.proveedores'))

    proveedores_records = conn.execute('''
        SELECT p.*, s.nombre as servicio_nombre 
        FROM proveedores p 
        LEFT JOIN servicios s ON p.servicio_id = s.id_servicio 
        ORDER BY p.id_proveedor DESC
    ''').fetchall()
    
    servicios_list = conn.execute('SELECT * FROM servicios').fetchall()
    total_proveedores = len(proveedores_records)
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_records, servicios=servicios_list, total=total_proveedores)


@dashboard_bp.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    conn = get_db()
    if request.method == 'POST':
        empresa = request.form.get('nombre_empresa')
        nombre = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')
        telefono = request.form.get('telefono')
        
        # Encriptando la contraseña dummy
        p_hash = generate_password_hash(password)

        try:
            conn.execute('''
                INSERT INTO usuarios (nombre_empresa, nombre_completo, email, password_hash, rol, telefono) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (empresa, nombre, email, p_hash, rol, telefono))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
            
        conn.close()
        return redirect(url_for('dashboard.usuarios'))

    usuarios_records = conn.execute('SELECT * FROM usuarios ORDER BY id_usuario DESC').fetchall()
    total_usuarios = len(usuarios_records)
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios_records, total=total_usuarios)


@dashboard_bp.route('/facturas', methods=['GET', 'POST'])
def facturas():
    conn = get_db()
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        usuario_id = request.form.get('usuario_id')
        vendedor_id = request.form.get('vendedor_id')
        cotizacion_id = request.form.get('cotizacion_id') or None
        total = request.form.get('total')
        estado = request.form.get('estado')

        conn.execute('''
            INSERT INTO facturas (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado))
        
        # También insertamos registrar un movimiento contable automático de INGRESO
        factura_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute('''
            INSERT INTO movimientos_contables (descripcion, tipo, monto, factura_id) 
            VALUES (?, ?, ?, ?)
        ''', (f"Venta con Factura #{factura_id}", "INGRESO", total, factura_id))
        
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard.facturas'))

    facturas_records = conn.execute('''
                 SELECT f.*, c.Nombre_empresa 
                 FROM facturas f 
                 LEFT JOIN clientes c ON f.cliente_id = c.id_clientes 
                 ORDER BY f.fecha DESC
    ''').fetchall()
    
    total_facturas = len(facturas_records)
    ingresos = conn.execute("SELECT SUM(total) FROM facturas WHERE estado != 'Anulada'").fetchone()[0] or 0
    clientes_list = conn.execute("SELECT * FROM clientes").fetchall()
    usuarios_list = conn.execute("SELECT * FROM usuarios").fetchall()
    # Dummy vendedores
    vendedores_list = conn.execute("SELECT * FROM vendedor").fetchall()
    cotizaciones_list = conn.execute("SELECT * FROM cotizaciones WHERE estado='Aprobada'").fetchall()
    
    conn.close()
    return render_template('facturas.html', facturas=facturas_records, total_facturas=total_facturas, ingresos=f"${ingresos:,.2f}", clientes=clientes_list, usuarios=usuarios_list, vendedores=vendedores_list, cotizaciones=cotizaciones_list)


@dashboard_bp.route('/ventas')
def ventas():
    conn = get_db()
    movimientos = conn.execute('''
        SELECT * FROM movimientos_contables 
        WHERE tipo = 'INGRESO' 
        ORDER BY fecha DESC
    ''').fetchall()
    
    total_ingresos = sum([m['monto'] for m in movimientos])
    total_count = len(movimientos)
    conn.close()
    return render_template('ventas.html', movimientos=movimientos, total_ingresos=f"${total_ingresos:,.2f}", total_count=total_count)