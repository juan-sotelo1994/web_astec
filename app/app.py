from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def login():
    return render_template('/recuperarcuenta/login.html')  

@app.route('/recuperar')
def recuperar():
    return render_template('recuperarcuenta/recuepera.html')

@app.route('/verificacion')
def verificacion():
    # En desarrollo deberías recibir POST desde /recuperar, pero por visualización permitimos GET temporalmente
    return render_template('recuperarcuenta/verificacion.html')

@app.route('/newp')
def newp():
    return render_template('recuperarcuenta/Newp.html')

if __name__ == '__main__':
    app.run(debug=True, port=5711) 


app.route('/dashboard')
    
