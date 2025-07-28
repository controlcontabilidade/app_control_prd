from flask import Flask

app = Flask(__name__)

@app.route('/')
def test():
    return """
    <h1>Servidor Flask Funcionando!</h1>
    <p><a href="/client/new">Ir para cadastro de cliente</a></p>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
