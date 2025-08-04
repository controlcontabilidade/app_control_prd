# -*- coding: utf-8 -*-
"""
Memory Optimizer ULTRA-AGRESSIVO para Render 512MB - V2
Foco em redução de consumo em estado idle
"""
import os
import gc
import sys
import threading
import time
import weakref
from functools import lru_cache

class UltraMemoryOptimizer:
    """Otimizador ultra-agressivo de memória para ambientes extremamente limitados"""
    
    _cleanup_thread = None
    _active_objects = set()
    _memory_monitor_active = False
    
    @staticmethod
    def setup_extreme_memory_optimization():
        """Configurações EXTREMAS para economizar memória"""
        print("🧠 Iniciando otimizações EXTREMAS de memória...")
        
        # GC ULTRA-AGRESSIVO
        gc.set_threshold(50, 2, 2)  # Extremamente agressivo
        gc.enable()
        
        # Configurações Python extremas
        sys.dont_write_bytecode = True
        sys.setrecursionlimit(200)  # Muito baixo
        
        # Clear all possible caches
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        # Desabilitar debug completamente
        gc.set_debug(0)
        
        # Limpar módulos não essenciais IMEDIATAMENTE
        UltraMemoryOptimizer._clear_heavy_modules()
        
        # Configurar GC automático contínuo
        UltraMemoryOptimizer._start_continuous_cleanup()
        
        print("✅ Otimizações EXTREMAS aplicadas")
    
    @staticmethod
    def _clear_heavy_modules():
        """Remove módulos pesados da memória"""
        heavy_modules = [
            # Pandas (muito pesado)
            'pandas', 'pandas.core', 'pandas.io', 'pandas._libs',
            'pandas.plotting', 'pandas.tseries', 'pandas.api',
            
            # NumPy (pesado)
            'numpy', 'numpy.core', 'numpy.lib', 'numpy.linalg',
            'numpy.random', 'numpy.fft', 'numpy.polynomial',
            
            # Matplotlib/Plotting
            'matplotlib', 'matplotlib.pyplot', 'seaborn',
            
            # OpenPyXL (se não necessário)
            'openpyxl.workbook', 'openpyxl.worksheet', 'openpyxl.styles',
            
            # Google API helpers desnecessários
            'google.api_core._helpers', 'google.auth._helpers',
            'google.oauth2._helpers', 'google.auth.transport._helpers',
            
            # HTTP/Request helpers
            'urllib3.poolmanager', 'urllib3.connectionpool',
            'requests.adapters', 'requests.sessions',
            
            # Werkzeug debug e profiling
            'werkzeug.debug', 'werkzeug.serving', 'werkzeug.profiler',
            
            # Jinja2 não essenciais
            'jinja2.debug', 'jinja2.loaders', 'jinja2._compat',
            
            # Outros módulos pesados
            'babel.core', 'babel.dates', 'babel.numbers',
            'dateutil.parser', 'dateutil.tz',
            'pkg_resources', 'setuptools',
        ]
        
        cleared_count = 0
        for module_name in heavy_modules:
            if module_name in sys.modules:
                try:
                    del sys.modules[module_name]
                    cleared_count += 1
                except:
                    pass
        
        print(f"🧹 {cleared_count} módulos pesados removidos da memória")
        
        # Forçar limpeza múltiplas vezes
        for _ in range(5):
            gc.collect()
    
    @staticmethod
    def _start_continuous_cleanup():
        """Inicia thread de limpeza contínua de memória"""
        if UltraMemoryOptimizer._cleanup_thread is None:
            def cleanup_worker():
                while UltraMemoryOptimizer._memory_monitor_active:
                    try:
                        # Cleanup a cada 10 segundos
                        time.sleep(10)
                        
                        # GC múltiplo
                        collected = gc.collect()
                        if collected > 0:
                            print(f"🧹 GC automático: {collected} objetos coletados")
                        
                        # Clear type cache periodicamente
                        if hasattr(sys, '_clear_type_cache'):
                            sys._clear_type_cache()
                        
                    except Exception as e:
                        print(f"⚠️ Erro na limpeza automática: {e}")
                        
            UltraMemoryOptimizer._memory_monitor_active = True
            UltraMemoryOptimizer._cleanup_thread = threading.Thread(
                target=cleanup_worker, 
                daemon=True,
                name="MemoryCleanup"
            )
            UltraMemoryOptimizer._cleanup_thread.start()
            print("🔄 Thread de limpeza contínua iniciada")
    
    @staticmethod
    def cleanup_after_request():
        """Limpeza EXTREMA após cada requisição"""
        # GC triplo para garantir limpeza completa
        for _ in range(3):
            gc.collect()
        
        # Clear caches internos
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        # Limpar referências fracas
        try:
            import weakref
            weakref.getweakrefs(object())
        except:
            pass
    
    @staticmethod
    def optimize_flask_config(app):
        """Configurações EXTREMAS do Flask"""
        # Configurações básicas
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 30  # Cache mínimo
        
        # Sessões extremamente otimizadas
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = 900  # 15 minutos apenas
        
        # Desabilitar TUDO que não é essencial
        app.config['EXPLAIN_TEMPLATE_LOADING'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['PROPAGATE_EXCEPTIONS'] = None
        
        # Upload MÍNIMO
        app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB apenas
        
        print("⚙️ Configurações Flask EXTREMAS aplicadas")
    
    @staticmethod
    def get_memory_usage():
        """Obtém uso de memória atual"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f}MB"
        except ImportError:
            return "N/A"
    
    @staticmethod
    def force_cleanup():
        """Força limpeza completa de memória"""
        print("🧹 Executando limpeza forçada de memória...")
        
        # Limpar todos os caches conhecidos
        try:
            # Clear LRU caches
            for obj in gc.get_objects():
                if hasattr(obj, 'cache_clear') and callable(obj.cache_clear):
                    try:
                        obj.cache_clear()
                    except:
                        pass
        except:
            pass
        
        # GC múltiplo
        for i in range(5):
            collected = gc.collect()
            print(f"🗑️ Passada GC {i+1}: {collected} objetos coletados")
        
        # Clear type cache
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        print(f"✅ Limpeza concluída. Memória atual: {UltraMemoryOptimizer.get_memory_usage()}")

# Configurações EXTREMAS para produção
ULTRA_MEMORY_SETTINGS = {
    'MAX_ROWS_PER_REQUEST': 10,  # EXTREMAMENTE baixo
    'BATCH_SIZE': 5,  # Muito pequeno
    'MAX_CONCURRENT_REQUESTS': 1,  # Apenas 1
    'CACHE_TIMEOUT': 15,  # Cache mínimo (15 segundos)
    'CONNECTION_POOL_SIZE': 1,  # Apenas 1 conexão
    'MAX_RETRIES': 1,  # 1 tentativa apenas
    'LAZY_LOADING_THRESHOLD': 3,  # Carregamento muito lazy
    'MEMORY_CLEANUP_INTERVAL': 10,  # Cleanup a cada 10s
}

def get_ultra_optimized_batch_size():
    """Tamanho de lote ultra-otimizado"""
    try:
        import psutil
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > 85:
            return 2  # Crítico - apenas 2 registros
        elif memory_percent > 75:
            return 3  # Alto - 3 registros
        elif memory_percent > 65:
            return 5  # Moderado - 5 registros
        else:
            return ULTRA_MEMORY_SETTINGS['BATCH_SIZE']
    except ImportError:
        return ULTRA_MEMORY_SETTINGS['BATCH_SIZE']

def setup_render_extreme_optimizations():
    """Configurações específicas do Render com foco em idle memory"""
    if os.environ.get('FLASK_ENV') == 'production':
        # Variáveis para mínimo uso de recursos
        os.environ.setdefault('WEB_CONCURRENCY', '1')  # 1 worker
        os.environ.setdefault('WORKER_CONNECTIONS', '10')  # Mínimo
        os.environ.setdefault('WORKER_TIMEOUT', '20')  # Timeout baixo
        os.environ.setdefault('MAX_REQUESTS', '25')  # Restart frequent
        os.environ.setdefault('MAX_REQUESTS_JITTER', '5')
        
        # Python extremo
        os.environ.setdefault('PYTHONHASHSEED', '1')
        os.environ.setdefault('PYTHONOPTIMIZE', '2')
        os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
        os.environ.setdefault('PYTHONUNBUFFERED', '1')  # Sem buffer
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        
        print("🚀 Configurações EXTREMAS do Render aplicadas")

# Backward compatibility
class MemoryOptimizer(UltraMemoryOptimizer):
    """Alias para compatibilidade"""
    
    @staticmethod
    def setup_production_memory_settings():
        return UltraMemoryOptimizer.setup_extreme_memory_optimization()

# Settings para compatibilidade
MEMORY_OPTIMIZED_SETTINGS = ULTRA_MEMORY_SETTINGS.copy()
MEMORY_OPTIMIZED_SETTINGS.update({
    'CACHE_TTL': ULTRA_MEMORY_SETTINGS['CACHE_TIMEOUT'],
    'MAX_ROWS_PER_REQUEST': ULTRA_MEMORY_SETTINGS['MAX_ROWS_PER_REQUEST'],
    'BATCH_SIZE': ULTRA_MEMORY_SETTINGS['BATCH_SIZE'],
    'CONNECTION_POOL_SIZE': ULTRA_MEMORY_SETTINGS['CONNECTION_POOL_SIZE'],
    'MAX_RETRIES': ULTRA_MEMORY_SETTINGS['MAX_RETRIES'],
})

def get_optimized_batch_size():
    """Função para compatibilidade"""
    return get_ultra_optimized_batch_size()
