import sqlite3
from flask import session

def obtener_conexion():
    # Nos conectamos a la BD SQLite actual en la raíz ("astec.db")
    conn = sqlite3.connect('astec.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# GESTIÓN DE CLIENTES
# ==========================================
def insertar_cliente(id_clientes, tipo_id, empresa, sector, representante, contacto, direccion, pais, departamento, telefono, email):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                INSERT INTO clientes (
                    id_clientes, Tipo_identificador, Nombre_empresa, Sector_Economico_cliente,
                    nombre_representante, contacto_cliente, direccion_cliente, pais_cliente,
                    Ddepartamento_cliente, telefono, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_clientes, tipo_id, empresa, sector, representante, contacto, direccion, pais, departamento, telefono, email))
            conexion.commit()
    except Exception as e:
        print(f"Error insertando cliente: {e}")
    finally:
        conexion.close()

def obtener_clientes():
    conexion = obtener_conexion()
    clientes = []
    try:
        clientes = conexion.execute('SELECT * FROM clientes ORDER BY fecha_creacion DESC').fetchall()
    except Exception as e:
        print(f"Error obteniendo clientes: {e}")
    finally:
        conexion.close()
    return clientes

def eliminar_cliente(id_cliente):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute("DELETE FROM clientes WHERE id_clientes = ?", (id_cliente,))
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
        with conexion:
            conexion.execute("INSERT INTO servicios (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
            conexion.commit()
    except Exception as e:
        print(f"Error insertando servicio: {e}")
    finally:
        conexion.close()

def obtener_servicios():
    conexion = obtener_conexion()
    servicios = []
    try:
        servicios = conexion.execute('SELECT * FROM servicios ORDER BY id_servicio DESC').fetchall()
    except Exception as e:
        print(f"Error obteniendo servicios: {e}")
    finally:
        conexion.close()
    return servicios

def eliminar_servicio(id_servicio):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute("DELETE FROM servicios WHERE id_servicio = ?", (id_servicio,))
            conexion.commit()
    except Exception as e:
        print(f"Error eliminando servicio: {e}")
    finally:
        conexion.close()

# ==========================================
# GESTIÓN DE PROVEEDORES
# ==========================================
def insertar_proveedor(nombre, representante, nit, telefono, email, direccion, servicio_id):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                INSERT INTO proveedores (nombre_proveedor, nombre_representante, nit, telefono, email, direccion, servicio_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, representante, nit, telefono, email, direccion, servicio_id))
            conexion.commit()
    except Exception as e:
        print(f"Error insertando proveedor: {e}")
    finally:
        conexion.close()

def obtener_proveedores():
    conexion = obtener_conexion()
    proveedores = []
    try:
        proveedores = conexion.execute('''
            SELECT p.*, s.nombre as servicio_nombre 
            FROM proveedores p 
            LEFT JOIN servicios s ON p.servicio_id = s.id_servicio 
            ORDER BY p.id_proveedor DESC
        ''').fetchall()
    except Exception as e:
        print(f"Error obteniendo proveedores: {e}")
    finally:
        conexion.close()
    return proveedores

def eliminar_proveedor(id_proveedor):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute("DELETE FROM proveedores WHERE id_proveedor = ?", (id_proveedor,))
            conexion.commit()
    except Exception as e:
        print(f"Error eliminando proveedor: {e}")
    finally:
        conexion.close()

# ==========================================
# GESTIÓN DE USUARIOS
# ==========================================
def insertar_usuario(empresa, nombre, email, password_hash, rol, telefono):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                INSERT INTO usuarios (nombre_empresa, nombre_completo, email, password_hash, rol, telefono) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (empresa, nombre, email, password_hash, rol, telefono))
            conexion.commit()
    except Exception as e:
        print(f"Error insertando usuario: {e}")
    finally:
        conexion.close()

def obtener_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    try:
        usuarios = conexion.execute('SELECT * FROM usuarios ORDER BY id_usuario DESC').fetchall()
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
    finally:
        conexion.close()
    return usuarios

def eliminar_usuario(id_usuario):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            conexion.commit()
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
    finally:
        conexion.close()
        
def actualizar_usuario(empresa, nombre, email, rol, telefono, id_usuario):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                UPDATE usuarios SET nombre_empresa = ?, nombre_completo = ?, email = ?, rol = ?, telefono = ? 
                WHERE id_usuario = ?
            ''', (empresa, nombre, email, rol, telefono, id_usuario))
            conexion.commit()
    except Exception as e:
        print(f"Error actualizando usuario: {e}")
    finally:
        conexion.close()

def obtener_usuario_por_id(id_usuario):
    conexion = obtener_conexion()
    usuario = None
    try:
        usuario = conexion.execute(
            "SELECT id_usuario, nombre_empresa, nombre_completo, email, rol, telefono FROM usuarios WHERE id_usuario = ?", (id_usuario,)
        ).fetchone()
    except Exception as e:
        print(f"Error obteniendo usuario por id: {e}")
    finally:
        conexion.close()
    return usuario
    
# ==========================================
# GESTIÓN DE COTIZACIONES
# ==========================================
def insertar_cotizacion(cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                INSERT INTO cotizaciones (cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cliente_id, vendedor_id, fecha_vencimiento, estado, total, observaciones))
            conexion.commit()
    except Exception as e:
        print(f"Error insertando cotizacion: {e}")
    finally:
        conexion.close()

def obtener_cotizaciones():
    conexion = obtener_conexion()
    cotizaciones = []
    try:
        cotizaciones = conexion.execute('SELECT * FROM cotizaciones ORDER BY fecha_emision DESC').fetchall()
    except Exception as e:
        print(f"Error obteniendo cotizaciones: {e}")
    finally:
        conexion.close()
    return cotizaciones

# ==========================================
# GESTIÓN DE FACTURAS Y MOVIMIENTOS
# ==========================================
def insertar_factura(cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado):
    conexion = obtener_conexion()
    try:
        with conexion:
            conexion.execute('''
                INSERT INTO facturas (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cliente_id, usuario_id, vendedor_id, cotizacion_id, total, estado))
            
            factura_id = conexion.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            # Registrar el ingreso automatizado en la caja de contabilidad
            conexion.execute('''
                INSERT INTO movimientos_contables (descripcion, tipo, monto, factura_id) 
                VALUES (?, ?, ?, ?)
            ''', (f"Venta con Factura #{factura_id}", "INGRESO", total, factura_id))
            
            conexion.commit()
    except Exception as e:
        print(f"Error insertando factura: {e}")
    finally:
        conexion.close()

def obtener_facturas():
    conexion = obtener_conexion()
    facturas = []
    try:
        facturas = conexion.execute('''
            SELECT f.*, c.Nombre_empresa 
            FROM facturas f 
            LEFT JOIN clientes c ON f.cliente_id = c.id_clientes 
            ORDER BY f.fecha DESC
        ''').fetchall()
    except Exception as e:
        print(f"Error obteniendo facturas: {e}")
    finally:
        conexion.close()
    return facturas

def obtener_movimientos_ingresos():
    conexion = obtener_conexion()
    movimientos = []
    try:
        movimientos = conexion.execute('''
            SELECT * FROM movimientos_contables 
            WHERE tipo = 'INGRESO' 
            ORDER BY fecha DESC
        ''').fetchall()
    except Exception as e:
        print(f"Error obteniendo movimientos: {e}")
    finally:
        conexion.close()
    return movimientos
