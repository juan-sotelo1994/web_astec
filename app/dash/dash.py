import sqlite3
from flask import render_template, request, redirect, url_for
from . import dashboard_bp

def get_db():
    # Usamos una base de datos SQLite local para pruebas y desarrollo
    conn = sqlite3.connect('astec.db')
    conn.row_factory = sqlite3.Row
    # Crear la tabla si no existe basada en la estructura proporcionada
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
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
        )
    ''')
    conn.commit()
    return conn

@dashboard_bp.route('/dashboard')
def dash_view():
    return render_template('dashboard.html')

@dashboard_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db()
    
    # Manejar el guardado del formulario (Registrar Cliente)
    if request.method == 'POST':
        # Capturar todos los campos del formulario
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
            # Aquí podrías retornar un mensaje de error si el ID ya existe
            pass
        
        conn.close()
        # Redirige de nuevo a la vista de clientes para refrescar los datos mostrados
        return redirect(url_for('dashboard.clientes'))

    # Método GET - Mostrar la página y la lista
    # Consultar todos los clientes registrados
    clientes_records = conn.execute('SELECT * FROM clientes ORDER BY fecha_creacion DESC').fetchall()
    
    # Calcular estadísticas básicas para las tarjetas
    total_clientes = len(clientes_records)
    # Por ahora como simulación, los nuevos clientes son total_clientes
    nuevos_clientes = total_clientes
    
    paises_unicos = set([c['pais_cliente'] for c in clientes_records if c['pais_cliente']])
    total_paises = len(paises_unicos)
    
    conn.close()

    # Pasar los datos al html
    return render_template(
        'clientes.html', 
        clientes=clientes_records, 
        total_clientes=total_clientes, 
        nuevos_clientes=nuevos_clientes, 
        total_paises=total_paises
    )