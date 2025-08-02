# -*- coding: utf-8 -*-
"""
Configurações ULTRA-OTIMIZADAS para ambientes com pouca memória (Render 512MB)
"""
import os
import gc
import sys

class MemoryOptimizer:
    """Classe para otimizar DRASTICAMENTE o uso de memória da aplicação"""
    
    @staticmethod
    def setup_production_memory_settings():
        """Configura otimizações AGRESSIVAS de memória para produção"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Garbage collection ULTRA-AGRESSIVO
            gc.set_threshold(200, 3, 3)  # Muito mais agressivo que o padrão
            
            # Desabilitar cache de bytecode para economizar RAM
            sys.dont_write_bytecode = True
            
            # Limitar recursão para economizar stack
            sys.setrecursionlimit(500)  # Reduzido de 1000
            
            # Configurar garbage collection para ser mais eficiente
            gc.set_debug(0)  # Desabilitar debug do GC
            
            # Limpar cache de módulos Python não essenciais AGRESSIVAMENTE
            modules_to_clear = [
                'pandas._libs', 'pandas.core', 'pandas.io',
                'numpy.core', 'numpy.lib', 'numpy.linalg',
                'matplotlib', 'seaborn', 'sklearn',
                'openpyxl.workbook', 'openpyxl.worksheet',
                'google.api_core._helpers', 'google.auth._helpers',
                'urllib3.poolmanager', 'requests.adapters',
                'werkzeug.debug', 'jinja2._compat',
                'babel.core', 'babel.dates'
            ]
            
            for module in modules_to_clear:
                if module in sys.modules:
                    try:
                        del sys.modules[module]
                    except:
                        pass
            
            # Forçar coleta de lixo múltiplas vezes
            for _ in range(3):
                gc.collect()
            
            print("🧠 Otimizações ULTRA-AGRESSIVAS de memória aplicadas para produção")
    
    @staticmethod
    def cleanup_after_request():
        """Limpa memória AGRESSIVAMENTE após cada requisição"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Múltiplas passadas de garbage collection
            gc.collect()
            gc.collect()  # Segunda passada para objetos com referências circulares
    
    @staticmethod
    def optimize_flask_config(app):
        """Otimiza configurações do Flask para MÍNIMO uso de memória"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Configurações JSON otimizadas
            app.config['JSON_SORT_KEYS'] = False
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
            app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60  # Cache muito curto
            
            # Configurações de sessão otimizadas
            app.config['SESSION_COOKIE_SECURE'] = True
            app.config['SESSION_COOKIE_HTTPONLY'] = True
            app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos
            
            # Desabilitar funcionalidades que consomem memória
            app.config['EXPLAIN_TEMPLATE_LOADING'] = False
            app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
            
            print("🧠 Configurações Flask otimizadas para economia de memória")
    
    @staticmethod
    def get_memory_usage():
        """Retorna o uso atual de memória (se psutil disponível)"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f}MB"
        except ImportError:
            return "N/A"
    
    @staticmethod
    def force_memory_cleanup():
        """Força limpeza agressiva de memória"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Limpar todos os caches possíveis
            if hasattr(gc, 'get_objects'):
                # Forçar coleta de todos os objetos não referenciados
                gc.collect()
                
            # Limpar cache do import system
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
                
            # Múltiplas passadas de GC
            for _ in range(5):
                gc.collect()

# Configurações específicas para ambientes de baixa memória
MEMORY_OPTIMIZED_SETTINGS = {
    'MAX_ROWS_PER_REQUEST': 25,  # Reduzido drasticamente de 100
    'BATCH_SIZE': 10,  # Reduzido de 50
    'MAX_CONCURRENT_REQUESTS': 1,  # Apenas 1 requisição por vez
    'CACHE_TIMEOUT': 30,  # Cache muito curto
    'MAX_UPLOAD_SIZE_MB': 2,  # Reduzido de 8MB
    'LAZY_LOADING_THRESHOLD': 5,  # Carregamento ainda mais lazy
}

def get_optimized_batch_size():
    """Retorna tamanho de lote otimizado baseado na memória disponível"""
    try:
        import psutil
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > 90:
            return 5  # Memória crítica
        elif memory_percent > 80:
            return 10  # Memória alta
        elif memory_percent > 70:
            return 15  # Memória moderada
        else:
            return MEMORY_OPTIMIZED_SETTINGS['BATCH_SIZE']  # Normal
    except ImportError:
        return MEMORY_OPTIMIZED_SETTINGS['BATCH_SIZE']

def setup_render_optimizations():
    """Configurações específicas para o Render com 512MB"""
    if os.environ.get('FLASK_ENV') == 'production':
        # Variáveis de ambiente específicas do Render
        os.environ.setdefault('WEB_CONCURRENCY', '1')  # Apenas 1 worker
        os.environ.setdefault('WORKER_CONNECTIONS', '50')  # Reduzido
        os.environ.setdefault('WORKER_TIMEOUT', '30')  # Timeout menor
        os.environ.setdefault('MAX_REQUESTS', '100')  # Reiniciar worker frequentemente
        os.environ.setdefault('MAX_REQUESTS_JITTER', '10')
        
        # Configurações Python específicas
        os.environ.setdefault('PYTHONHASHSEED', '1')  # Hash determinístico
        os.environ.setdefault('PYTHONOPTIMIZE', '2')  # Otimização máxima
        os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')  # Não escrever .pyc
        
        print("🚀 Configurações específicas do Render aplicadas")
    
    @staticmethod
    def optimize_flask_config(app):
        """Aplica configurações otimizadas ao Flask"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Reduzir tamanho máximo de upload
            app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB máximo
            
            # Configurações de cache mais agressivas
            app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 600  # 10 minutos
            
            # Desabilitar debug e funcionalidades não essenciais
            app.config['DEBUG'] = False
            app.config['TESTING'] = False
            
            # Configurar JSON para usar menos memória
            app.config['JSON_SORT_KEYS'] = False
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
            
            print("⚙️ Configurações Flask otimizadas para baixo consumo de memória")

# Configurações globais de otimização
MEMORY_OPTIMIZED_SETTINGS = {
    'BATCH_SIZE': 50,  # Processar dados em lotes menores
    'MAX_ROWS_PER_REQUEST': 100,  # Limitar número de linhas por requisição
    'CACHE_TTL': 300,  # Cache de 5 minutos (reduzido de 1 hora)
    'CONNECTION_POOL_SIZE': 5,  # Reduzir pool de conexões
    'MAX_RETRIES': 2,  # Reduzir tentativas de retry
}

def get_optimized_batch_size():
    """Retorna tamanho de lote otimizado baseado na memória disponível"""
    try:
        import psutil
        available_mb = psutil.virtual_memory().available / 1024 / 1024
        
        if available_mb < 100:  # Menos de 100MB disponível
            return 20
        elif available_mb < 200:  # Menos de 200MB disponível
            return 30
        else:
            return MEMORY_OPTIMIZED_SETTINGS['BATCH_SIZE']
    except ImportError:
        return MEMORY_OPTIMIZED_SETTINGS['BATCH_SIZE']
