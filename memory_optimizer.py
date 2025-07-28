# -*- coding: utf-8 -*-
"""
Configurações otimizadas para ambientes com pouca memória (Render 512MB)
"""
import os
import gc
import sys

class MemoryOptimizer:
    """Classe para otimizar o uso de memória da aplicação"""
    
    @staticmethod
    def setup_production_memory_settings():
        """Configura otimizações de memória para produção"""
        if os.environ.get('FLASK_ENV') == 'production':
            # Garbage collection mais agressivo
            gc.set_threshold(500, 5, 5)  # Mais agressivo que o padrão (700, 10, 10)
            
            # Limpar cache de módulos Python não essenciais
            modules_to_clear = [
                'pandas._libs',
                'numpy.core',
                'matplotlib',
                'seaborn',
                'sklearn'
            ]
            
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Forçar coleta de lixo
            gc.collect()
            
            print("🧠 Otimizações de memória aplicadas para produção")
    
    @staticmethod
    def cleanup_after_request():
        """Limpa memória após cada requisição"""
        if os.environ.get('FLASK_ENV') == 'production':
            gc.collect()
    
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
