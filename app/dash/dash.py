from flask import render_template, request, redirect, url_for
from . import dashboard_bp
from werkzeug.security import generate_password_hash
import mysql.connector
from db import obtener_conexion

def get_db():
    conn = obtener_conexion()
    return conn

@dashboard_bp.route('/dashboard')
def dash_view():
    return render_template('dashboard.html')

@dashboard_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        id_edit = request.form.get('id_edit')
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

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE clientes SET
                        numero_identificacion=%s, tipo_identificador=%s, nombre_empresa=%s, sector_economico=%s,
                        nombre_representante=%s, contacto_cliente=%s, direccion_cliente=%s, pais_cliente=%s,
                        departamento_cliente=%s, ciudad_cliente=%s, telefono=%s, email=%s
                    WHERE id_cliente=%s
                ''', (numero_id, tipo_id, empresa, sector, representante,
                      contacto, direccion, pais, departamento, ciudad, telefono, email, id_edit))
            else:
                cursor.execute('''
                    INSERT INTO clientes (
                        numero_identificacion, tipo_identificador, nombre_empresa, sector_economico,
                        nombre_representante, contacto_cliente, direccion_cliente, pais_cliente,
                        departamento_cliente, ciudad_cliente, telefono, email
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (numero_id, tipo_id, empresa, sector, representante, 
                      contacto, direccion, pais, departamento, ciudad, telefono, email))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass
        finally:
            cursor.close()
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
        id_edit = request.form.get('id_edit')
        cliente_id = request.form.get('cliente_id')
        vendedor_id = request.form.get('vendedor_id') or request.form.get('usuario_id')
        estado = request.form.get('estado')
        if not estado or estado.lower() not in ['borrador','enviada','aprobada','rechazada']:
            estado = 'borrador'
        total = request.form.get('total')

        # dummy usuario for MVP
        usuario_id = vendedor_id 

        tipos = request.form.getlist('item_tipo[]')
        ids = request.form.getlist('item_id[]')
        cants = request.form.getlist('item_cantidad[]')
        precios = request.form.getlist('item_precio[]')

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE cotizaciones SET
                        cliente_id=%s, usuario_id=%s, vendedor_id=%s, estado=%s, total=%s
                    WHERE id_cotizacion=%s
                ''', (cliente_id, usuario_id, vendedor_id, estado, total, id_edit))
                
                cursor.execute('DELETE FROM detalle_cotizacion WHERE cotizacion_id=%s', (id_edit,))
                cotizacion_id = id_edit
            else:
                cursor.execute('''
                    INSERT INTO cotizaciones (cliente_id, usuario_id, vendedor_id, estado, total) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (cliente_id, usuario_id, vendedor_id, estado, total))
                
                cursor.execute("SELECT LAST_INSERT_ID()")
                cotizacion_id = cursor.fetchone()[0]

            for tipo, item_id, cant, precio in zip(tipos, ids, cants, precios):
                if not item_id or not cant or not precio: continue
                if tipo == 'producto':
                    cursor.execute('INSERT INTO detalle_cotizacion (cotizacion_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)', (cotizacion_id, item_id, cant, precio))
                else:
                    cursor.execute('INSERT INTO detalle_cotizacion (cotizacion_id, servicio_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)', (cotizacion_id, item_id, cant, precio))

            conn.commit()
        except Exception:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.cotizaciones'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.*, cl.nombre_empresa, v.nombre_completo as vendedor_nombre
        FROM cotizaciones c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id_cliente
        LEFT JOIN vendedores v ON c.vendedor_id = v.id_vendedor
        ORDER BY c.fecha DESC
    ''')
    cotizaciones_records = cursor.fetchall()
    total_cotizaciones = len(cotizaciones_records)
    cursor.execute("SELECT COUNT(*) as c FROM cotizaciones WHERE estado='borrador'")
    pendients = cursor.fetchone()
    pendientes = pendients['c'] if pendients else 0
    cursor.execute("SELECT SUM(total) as t FROM cotizaciones")
    sum_r = cursor.fetchone()
    total_sum = sum_r['t'] if sum_r and sum_r['t'] else 0
    total_sum_fmt = f"${total_sum:,.2f}" if total_sum else "$0.00"
    cursor.execute("SELECT id_cliente, nombre_empresa, numero_identificacion FROM clientes")
    clientes_list = cursor.fetchall()
    
    cursor.execute("SELECT id_vendedor, nombre_completo FROM vendedores")
    vendedores_list = cursor.fetchall()
    
    cursor.execute("SELECT id_productos AS id_producto, nombre_producto, precio_unitario_producto, stock FROM productos")
    productos_list = cursor.fetchall()
    cursor.execute("SELECT id_servicios AS id_servicio, nombre FROM servicios")
    servicios_list = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('cotizaciones.html', cotizaciones=cotizaciones_records, total_cotizaciones=total_cotizaciones, pendientes=pendientes, total_sum_fmt=total_sum_fmt, clientes=clientes_list, vendedores=vendedores_list, productos=productos_list, servicios=servicios_list)


@dashboard_bp.route('/servicios', methods=['GET', 'POST'])
def servicios():
    conn = get_db()
    if conn is None: return "Error de BD"
    if request.method == 'POST':
        id_edit = request.form.get('id_edit')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('UPDATE servicios SET nombre=%s, descripcion=%s WHERE id_servicios=%s', (nombre, descripcion, id_edit))
            else:
                cursor.execute('INSERT INTO servicios (nombre, descripcion) VALUES (%s, %s)', (nombre, descripcion))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.servicios'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id_servicios AS id_servicio, id_servicios, nombre, descripcion FROM servicios ORDER BY id_servicios DESC')
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
        id_edit = request.form.get('id_edit')
        nombre = request.form.get('nombre_proveedor')
        representante = request.form.get('nombre_representante')
        nit = request.form.get('nit')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')
        servicio_id = request.form.get('servicio_id')

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE proveedores SET
                        nombre_proveedor=%s, nombre_representante=%s, nit=%s, telefono=%s, email=%s, direccion=%s, servicio_id=%s
                    WHERE id_proveedores=%s
                ''', (nombre, representante, nit, telefono, email, direccion, servicio_id, id_edit))
            else:
                cursor.execute('''
                    INSERT INTO proveedores (nombre_proveedor, nombre_representante, nit, telefono, email, direccion, servicio_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (nombre, representante, nit, telefono, email, direccion, servicio_id))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.proveedores'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.id_proveedores AS id_proveedor, p.id_proveedores, p.nombre_proveedor, 
               p.nombre_representante, p.nit, p.telefono, p.email, p.direccion, 
               p.servicio_id, s.nombre as servicio_nombre 
        FROM proveedores p 
        LEFT JOIN servicios s ON p.servicio_id = s.id_servicios 
        ORDER BY p.id_proveedores DESC
    ''')
    proveedores_records = cursor.fetchall()
    cursor.execute('SELECT id_servicios AS id_servicio, nombre FROM servicios')
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
        id_edit = request.form.get('id_edit')
        nombre_producto = request.form.get('nombre_producto')
        descripcion_producto = request.form.get('descripcion_producto')
        precio_unitario_producto = request.form.get('precio_unitario_producto')
        moneda = request.form.get('moneda')
        stock = request.form.get('stock')
        proveedor_id = request.form.get('proveedor_id')

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE productos SET
                        nombre_producto=%s, descripcion_producto=%s, precio_unitario_producto=%s, moneda=%s, stock=%s, proveedor_id=%s
                    WHERE id_productos=%s
                ''', (nombre_producto, descripcion_producto, precio_unitario_producto, moneda, stock, proveedor_id, id_edit))
            else:
                cursor.execute('''
                    INSERT INTO productos (nombre_producto, descripcion_producto, precio_unitario_producto, moneda, stock, proveedor_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (nombre_producto, descripcion_producto, precio_unitario_producto, moneda, stock, proveedor_id))
            conn.commit()
        except Exception:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.productos'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT p.id_productos AS id_producto, p.id_productos, p.nombre_producto, 
               p.descripcion_producto, p.precio_unitario_producto, p.moneda, 
               p.stock, p.proveedor_id, pr.nombre_proveedor 
        FROM productos p 
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id_proveedores 
        ORDER BY p.id_productos DESC
    ''')
    productos_records = cursor.fetchall()
    cursor.execute('SELECT id_proveedores AS id_proveedor, nombre_proveedor FROM proveedores')
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
        id_edit = request.form.get('id_edit')
        empresa = request.form.get('nombre_empresa')
        nombre = request.form.get('nombre_completo')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')
        telefono = request.form.get('telefono')
        
        cursor = conn.cursor()
        try:
            if id_edit:
                if password:
                    p_hash = generate_password_hash(password)
                    cursor.execute('''
                        UPDATE usuarios SET nombre_empresa=%s, nombre=%s, email=%s, password_hash=%s, rol=%s, telefono=%s 
                        WHERE id_usuarios=%s
                    ''', (empresa, nombre, email, p_hash, rol, telefono, id_edit))
                else:
                    cursor.execute('''
                        UPDATE usuarios SET nombre_empresa=%s, nombre=%s, email=%s, rol=%s, telefono=%s 
                        WHERE id_usuarios=%s
                    ''', (empresa, nombre, email, rol, telefono, id_edit))
            else:
                p_hash = generate_password_hash(password) if password else ""
                cursor.execute('''
                    INSERT INTO usuarios (nombre_empresa, nombre, email, password_hash, rol, telefono) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (empresa, nombre, email, p_hash, rol, telefono))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.usuarios'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id_usuarios AS id_usuario, id_usuarios, nombre_empresa, 
               nombre AS nombre_completo, nombre, email, rol, telefono, fecha_creacion 
        FROM usuarios ORDER BY id_usuarios DESC
    ''')
    usuarios_records = cursor.fetchall()
    total_usuarios = len(usuarios_records)
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios_records, total=total_usuarios)


@dashboard_bp.route('/vendedores', methods=['GET', 'POST'])
def vendedores():
    conn = get_db()
    if conn is None: return "Error de BD"
    if request.method == 'POST':
        id_edit = request.form.get('id_edit')
        numero_identificacion = request.form.get('numero_identificacion')
        nombre_completo = request.form.get('nombre_completo')
        telefono = request.form.get('telefono')
        ciudad = request.form.get('ciudad')
        comision_porcentaje = request.form.get('comision_porcentaje')
        if not comision_porcentaje:
            comision_porcentaje = 0.00

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE vendedores SET
                        numero_identificacion=%s, nombre_completo=%s, telefono=%s, ciudad=%s, comision_porcentaje=%s
                    WHERE id_vendedor=%s
                ''', (numero_identificacion, nombre_completo, telefono, ciudad, comision_porcentaje, id_edit))
            else:
                cursor.execute('''
                    INSERT INTO vendedores (numero_identificacion, nombre_completo, telefono, ciudad, comision_porcentaje) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (numero_identificacion, nombre_completo, telefono, ciudad, comision_porcentaje))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.vendedores'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM vendedores ORDER BY id_vendedor DESC')
    vendedores_records = cursor.fetchall()
    total_vendedores = len(vendedores_records)
    cursor.close()
    conn.close()
    return render_template('vendedores.html', vendedores=vendedores_records, total_vendedores=total_vendedores)


@dashboard_bp.route('/ventas', methods=['GET', 'POST'])
def ventas():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        id_edit = request.form.get('id_edit')
        cliente_id = request.form.get('cliente_id')
        vendedor_id = request.form.get('vendedor_id')
        cotizacion_id = request.form.get('cotizacion_id') or None
        # dummy usuario for MVP, you could read from session later
        usuario_id = vendedor_id 
        total = request.form.get('total')
        metodo_pago = request.form.get('metodo_pago')
        estado = request.form.get('estado_venta')
        if not estado or estado.lower() not in ['completada','cancelada','devolucion']:
            estado = 'completada'

        tipos = request.form.getlist('item_tipo[]')
        ids = request.form.getlist('item_id[]')
        cants = request.form.getlist('item_cantidad[]')
        precios = request.form.getlist('item_precio[]')

        cursor = conn.cursor()
        try:
            if id_edit:
                cursor.execute('''
                    UPDATE ventas SET cliente_id=%s, vendedor_id=%s, total_venta=%s, metodo_pago=%s, estado_venta=%s, cotizacion_id=%s 
                    WHERE id_venta=%s
                ''', (cliente_id, vendedor_id, total, metodo_pago, estado, cotizacion_id, id_edit))
                venta_id = id_edit
            else:
                cursor.execute('''
                    INSERT INTO ventas (cliente_id, vendedor_id, usuario_id, cotizacion_id, total_venta, metodo_pago, estado_venta) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (cliente_id, vendedor_id, usuario_id, cotizacion_id, total, metodo_pago, estado))
                
                cursor.execute("SELECT LAST_INSERT_ID()")
                venta_id = cursor.fetchone()[0]
                
                # Crear movimiento contable por la venta
                if estado == 'completada':
                    cursor.execute('''
                        INSERT INTO movimientos_contables (descripcion, tipo, monto, venta_id) 
                        VALUES (%s, 'ingreso', %s, %s)
                    ''', (f"Venta directa #{venta_id}", total, venta_id))

            # Insertar los detalles solo en creación (por la complejidad de los triggers)
            if not id_edit:
                for tipo, item_id, cant, precio in zip(tipos, ids, cants, precios):
                    if not item_id or not cant or not precio: continue
                    if tipo == 'producto':
                        cursor.execute('INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario_aplicado) VALUES (%s, %s, %s, %s)', (venta_id, item_id, cant, precio))
                    else:
                        cursor.execute('INSERT INTO detalle_venta (venta_id, servicio_id, cantidad, precio_unitario_aplicado) VALUES (%s, %s, %s, %s)', (venta_id, item_id, cant, precio))

            conn.commit()
        except Exception as e:
            print("Error Ventas:", e)
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.ventas'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT v.*, c.nombre_empresa 
        FROM ventas v 
        LEFT JOIN clientes c ON v.cliente_id = c.id_cliente 
        ORDER BY v.fecha_venta DESC
    ''')
    ventas_records = cursor.fetchall()
    total_ventas = len(ventas_records)
    
    cursor.execute("SELECT SUM(total_venta) as s FROM ventas WHERE estado_venta = 'completada'")
    ing_res = cursor.fetchone()
    ingresos = ing_res['s'] if ing_res and ing_res['s'] else 0
    
    cursor.execute("SELECT id_cliente, nombre_empresa, numero_identificacion FROM clientes")
    clientes_list = cursor.fetchall()
    
    cursor.execute("SELECT id_vendedor, nombre_completo FROM vendedores")
    vendedores_list = cursor.fetchall()
    
    cursor.execute("SELECT id_cotizacion FROM cotizaciones WHERE estado='aprobada'")
    cotizaciones_list = cursor.fetchall()
    
    cursor.execute("SELECT id_productos AS id_producto, nombre_producto, precio_unitario_producto, stock FROM productos")
    productos_list = cursor.fetchall()
    cursor.execute("SELECT id_servicios AS id_servicio, nombre, precio_sugerido FROM servicios")
    servicios_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('ventas.html', ventas=ventas_records, total_ventas=total_ventas, 
                           ingresos_fmt=f"${float(ingresos):,.2f}", clientes=clientes_list, 
                           vendedores=vendedores_list, cotizaciones=cotizaciones_list, 
                           productos=productos_list, servicios=servicios_list)


@dashboard_bp.route('/facturas', methods=['GET', 'POST'])
def facturas():
    conn = get_db()
    if conn is None: return "Error de BD"
    
    if request.method == 'POST':
        id_edit = request.form.get('id_edit')
        venta_id = request.form.get('venta_id')
        numero_factura = request.form.get('numero_factura')
        estado = request.form.get('estado_factura')
        if not estado or estado.lower() not in ['pendiente','pagada','anulada']:
            estado = 'pendiente'

        cursor = conn.cursor(dictionary=True)
        try:
            # Recuperar el total de la venta referenciada
            cursor.execute('SELECT total_venta FROM ventas WHERE id_venta=%s', (venta_id,))
            v_res = cursor.fetchone()
            total_f = v_res['total_venta'] if v_res else 0.00
            
            if id_edit:
                cursor.execute('''
                    UPDATE facturas SET venta_id=%s, numero_factura=%s, estado_factura=%s, total_factura=%s 
                    WHERE id_factura=%s
                ''', (venta_id, numero_factura, estado, total_f, id_edit))
            else:
                cursor.execute('''
                    INSERT INTO facturas (venta_id, numero_factura, estado_factura, total_factura) 
                    VALUES (%s, %s, %s, %s)
                ''', (venta_id, numero_factura, estado, total_f))
                
            conn.commit()
        except Exception as e:
            print("Error Facturas:", e)
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard.facturas'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
         SELECT f.*, v.fecha_venta, c.nombre_empresa 
         FROM facturas f
         JOIN ventas v ON f.venta_id = v.id_venta
         JOIN clientes c ON v.cliente_id = c.id_cliente
         ORDER BY f.fecha_emision DESC
    ''')
    facturas_records = cursor.fetchall()
    
    cursor.execute("SELECT id_venta, total_venta, cliente_id FROM ventas")
    ventas_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('facturas.html', facturas=facturas_records, ventas=ventas_list)