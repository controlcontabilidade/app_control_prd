import os
import sys
import logging
import gc

# Configurar logging mínimo para produção (economizar memória)
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.ERROR)  # Apenas erros
    
    # Otimizações de memória críticas para Render 512MB
    gc.set_threshold(500, 5, 5)  # GC mais agressivo
    
    # Limitar variáveis de ambiente desnecessárias
    unnecessary_env_vars = [
        'PYTHONPATH', 'PYTHON_PATH', 'PATH_INFO',
        'SCRIPT_NAME', 'REQUEST_METHOD', 'CONTENT_TYPE'
    ]
    for var in unnecessary_env_vars:
        if var in os.environ and var not in ['PORT', 'FLASK_ENV']:
            try:
                del os.environ[var]
            except:
                pass
    
    print("🧠 WSGI configurado para máxima economia de memória")
else:
    logging.basicConfig(level=logging.INFO)

# Forçar garbage collection antes de importar a aplicação
gc.collect()

try:
    # Importar aplicação com otimizações
    from app import app
    print("✅ Aplicação importada com sucesso")
    
    # Configurações finais de produção para baixo consumo de memória
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB apenas
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache 5 min
        
        # Desabilitar features não essenciais
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        print("🔧 Configurações de produção aplicadas (512MB mode)")
        
        # Limpeza final de memória
        gc.collect()
        
        # Tentar obter uso de memória atual
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"💾 Memória inicial da aplicação: {memory_mb:.1f}MB")
            
            if memory_mb > 450:  # Alerta se usar mais de 450MB
                print("⚠️ ATENÇÃO: Uso de memória alto para Render 512MB!")
        except ImportError:
            print("💾 psutil não disponível - monitoramento de memória limitado")
    
except ImportError as e:
    print(f"❌ Erro ao importar aplicação: {e}")
    sys.exit(1)

# Para Gunicorn
application = app

# Função para limpeza de memória após cada request
def cleanup_memory():
    """Limpa memória após requests"""
    if os.environ.get('FLASK_ENV') == 'production':
        gc.collect()

# Middleware para limpeza automática
class MemoryCleanupMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        finally:
            if os.environ.get('FLASK_ENV') == 'production':
                gc.collect()

# Aplicar middleware em produção
if os.environ.get('FLASK_ENV') == 'production':
    application = MemoryCleanupMiddleware(application)
    print("🧹 Middleware de limpeza de memória ativado")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🚀 Iniciando aplicação na porta {port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"🧠 Memory-optimized mode: {'ON' if not debug_mode else 'OFF'}")
    
    if not debug_mode:
        print("⚡ Render 512MB optimizations ACTIVE")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
