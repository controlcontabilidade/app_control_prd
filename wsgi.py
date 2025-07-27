import os
import sys
import logging

# Configurar logging para produção
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)

try:
    from app import app
    print("✅ Aplicação importada com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    sys.exit(1)

# Para Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🚀 Iniciando aplicação na porta {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
