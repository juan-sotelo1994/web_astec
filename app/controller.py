import mysql.connector
from flask import session
from db import obtener_conexion

# ==========================================
# GESTIÓN DE CLIENTES
# ==========================================
def insertar_cliente(id_cliente, tipo_id, empresa, sector, representante, contacto, direccion, pais, departamento, telefono, email):
    conexion = obtener_conexion()
    if not conexion: return
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO clientes (
                numero_identificacion, tipo_identificador, nombre_empresa, sector_economico,
                nombre_representante, contacto_cliente, direccion_cliente, pais_cliente,
                departamento_cliente, telefono, email
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (id_cliente, tipo_id, empresa, sector, representante, contacto, direccion, pais, departamento, telefono, email))
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error insertando cliente: {e}")
    finally:
        conexion.close()

def obtener_clientes():
    conexion = obtener_conexion()
    if not conexion: return []
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT * FROM clientes ORDER BY fecha_creacion DESC')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo clientes: {e}")
        return []
    finally:
        conexion.close()

def eliminar_cliente(id_cliente):
    conexion = obtener_conexion()
    if not conexion: return
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        conexion.commit()
    except Exception as e:
        print(f"Error eliminando cliente: {e}")
    finally:
        conexion.close()


# ==========================================
# GESTIÓN DE SERVICIOS
# ==========================================
def insertar_servicio(nombre, descripcion):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO servicios (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
        conexion.commit()
    except Exception as e:
        print(f"Error insertando servicio: {e}")
    finally:
        if conexion: conexion.close()

def obtener_servicios():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT id_servicios AS id_servicio, id_servicios, nombre, descripcion FROM servicios')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo servicios: {e}")
        return []
    finally:
        if conexion: conexion.close()

def eliminar_servicio(id_servicio):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM servicios WHERE id_servicios = %s", (id_servicio,))
        conexion.commit()
    except Exception as e:
        print(f"Error eliminando servicio: {e}")
    finally:
        if conexion: conexion.close()


# ==========================================
# GESTIÓN DE PROVEEDORES
# ==========================================
def insertar_proveedor(nombre, representante, nit, telefono, email, direccion, servicio_id):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO proveedores (nombre_proveedor, nombre_representante, nit, telefono, email, direccion, servicio_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (nombre, representante, nit, telefono, email, direccion, servicio_id))
        conexion.commit()
    except Exception as e:
        print(f"Error insertando proveedor: {e}")
    finally:
        if conexion: conexion.close()

def obtener_proveedores():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
            SELECT p.id_proveedores AS id_proveedor, p.*, s.nombre as servicio_nombre 
            FROM proveedores p 
            LEFT JOIN servicios s ON p.servicio_id = s.id_servicios 
            ORDER BY p.id_proveedores DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo proveedores: {e}")
        return []
    finally:
        if conexion: conexion.close()

def eliminar_proveedor(id_proveedor):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM proveedores WHERE id_proveedores = %s", (id_proveedor,))
        conexion.commit()
    except Exception as e:
        print(f"Error eliminando proveedor: {e}")
    finally:
        if conexion: conexion.close()


# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================
def insertar_usuario(empresa, nombre, email, password_hash, rol, telefono):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre_empresa, nombre, email, password_hash, rol, telefono) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (empresa, nombre, email, password_hash, rol, telefono))
        conexion.commit()
    except Exception as e:
        print(f"Error insertando usuario: {e}")
    finally:
        if conexion: conexion.close()

def obtener_usuarios():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT id_usuarios AS id_usuario, u.*, nombre AS nombre_completo FROM usuarios u ORDER BY id_usuarios DESC')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []
    finally:
        if conexion: conexion.close()

def eliminar_usuario(id_usuario):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuarios = %s", (id_usuario,))
        conexion.commit()
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
    finally:
        if conexion: conexion.close()
        
def actualizar_usuario(empresa, nombre, email, rol, telefono, id_usuario):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            UPDATE usuarios SET nombre_empresa = %s, nombre = %s, email = %s, rol = %s, telefono = %s 
            WHERE id_usuarios = %s
        ''', (empresa, nombre, email, rol, telefono, id_usuario))
        conexion.commit()
    except Exception as e:
        print(f"Error actualizando usuario: {e}")
    finally:
        if conexion: conexion.close()

def obtener_usuario_por_id(id_usuario):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuarios AS id_usuario, nombre_empresa, nombre AS nombre_completo, email, rol, telefono FROM usuarios WHERE id_usuarios = %s", (id_usuario,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error obteniendo usuario por id: {e}")
        return None
    finally:
        if conexion: conexion.close()


# ==========================================
# GESTIÓN DE COTIZACIONES
# ==========================================
def insertar_cotizacion(cliente_id, usuario_id, estado, total):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO cotizaciones (cliente_id, usuario_id, estado, total) 
            VALUES (%s, %s, %s, %s)
        ''', (cliente_id, usuario_id, estado, total))
        conexion.commit()
    except Exception as e:
        print(f"Error insertando cotizacion: {e}")
    finally:
        if conexion: conexion.close()

def obtener_cotizaciones():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
            SELECT id_cotizacion, cliente_id, usuario_id AS vendedor_id, 
                   fecha AS fecha_emision, total, estado 
            FROM cotizaciones ORDER BY fecha DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo cotizaciones: {e}")
        return []
    finally:
        if conexion: conexion.close()


# ==========================================
# GESTIÓN DE FACTURAS Y MOVIMIENTOS
# ==========================================
def insertar_factura(cliente_id, usuario_id, total, estado):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO facturas (cliente_id, usuario_id, total, estado) 
            VALUES (%s, %s, %s, %s)
        ''', (cliente_id, usuario_id, total, estado))
        
        cursor.execute("SELECT LAST_INSERT_ID() AS last_id")
        res = cursor.fetchone()
        factura_id = res['last_id'] if res and isinstance(res, dict) else (res[0] if res else 0)
        
        # Registrar el ingreso automatizado en la caja de contabilidad
        cursor.execute('''
            INSERT INTO movimientos_contables (descripcion, tipo, monto, referencia_id, referencia_tipo) 
            VALUES (%s, 'ingreso', %s, %s, 'factura')
        ''', (f"Venta con Factura #{factura_id}", total, factura_id))
        
        conexion.commit()
    except Exception as e:
        print(f"Error insertando factura: {e}")
    finally:
        if conexion: conexion.close()

def obtener_facturas():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
            SELECT f.id_factura, f.cliente_id, f.usuario_id, f.fecha, 
                   f.total, f.estado, c.nombre_empresa 
            FROM facturas f 
            LEFT JOIN clientes c ON f.cliente_id = c.id_cliente 
            ORDER BY f.fecha DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo facturas: {e}")
        return []
    finally:
        if conexion: conexion.close()

def obtener_movimientos_ingresos():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM movimientos_contables 
            WHERE tipo = 'ingreso' 
            ORDER BY fecha DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo movimientos: {e}")
        return []
    finally:
        if conexion: conexion.close()
