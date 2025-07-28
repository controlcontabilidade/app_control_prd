import os
import sys
import logging
import gc

# Configurar logging para produção
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)

# Forçar garbage collection para economizar memória
gc.collect()

try:
    from app import app
    print("✅ Aplicação importada com sucesso")
    print(f"🧠 Memory optimization: Enabled")
    
    # Configurações de produção para baixo consumo de memória
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Reduzido para 8MB
    
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
    print(f"🧠 Memory-optimized mode: {'ON' if not debug_mode else 'OFF'}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
