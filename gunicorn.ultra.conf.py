# -*- coding: utf-8 -*-
"""
Configuração EXTREMA do Gunicorn para Render 512MB
Foco em minimizar consumo de memória em idle
"""
import os
import multiprocessing

# Configurações de worker EXTREMAS
workers = 1  # Apenas 1 worker para economizar memória
worker_class = "sync"  # Sync é mais leve que async
worker_connections = 5  # Extremamente baixo
max_requests = 5  # Restart worker após poucas requisições
max_requests_jitter = 2  # Jitter baixo

# Timeouts EXTREMOS
timeout = 15  # 15 segundos apenas
keepalive = 1  # Keep-alive mínimo
graceful_timeout = 10  # Shutdown rápido

# Configurações de memória EXTREMAS
preload_app = False  # NÃO preload para economizar memória inicial
worker_tmp_dir = "/tmp"  # Usar tmpfs se disponível

# Logging mínimo para economizar I/O
accesslog = None  # Desabilitar access log
errorlog = "-"  # Apenas erros no stderr
loglevel = "warning"  # Log level mínimo
access_log_format = None  # Sem formato de log customizado

# Configurações de bind
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 64  # Backlog baixo

# Configurações de processo
daemon = False
pidfile = None
tmp_upload_dir = "/tmp"

# Configurações SSL (desabilitadas para economizar recursos)
keyfile = None
certfile = None

# Worker process management
worker_restart = True  # Restart workers on code changes
reload = False  # Não reload automático em produção

# Configurações de performance EXTREMAS
sendfile = True  # Usar sendfile quando possível
reuse_port = False  # Não usar SO_REUSEPORT
worker_class = "sync"  # Classe mais simples

def post_fork(server, worker):
    """Hook executado após fork do worker - aplicar otimizações extremas"""
    import gc
    import sys
    
    # GC extremamente agressivo no worker
    gc.set_threshold(25, 1, 1)
    
    # Configurações Python extremas
    sys.dont_write_bytecode = True
    
    # Limpar módulos desnecessários no worker
    modules_to_clear = [
        'pandas', 'numpy', 'matplotlib', 'seaborn',
        'openpyxl.workbook', 'openpyxl.worksheet',
        'werkzeug.debug', 'werkzeug.profiler'
    ]
    
    for module in modules_to_clear:
        if module in sys.modules:
            try:
                del sys.modules[module]
            except:
                pass
    
    # Forçar GC inicial no worker
    for _ in range(3):
        gc.collect()
    
    server.log.info(f"Worker {worker.pid} iniciado com otimizações extremas")

def when_ready(server):
    """Hook quando servidor está pronto"""
    server.log.info("Gunicorn EXTREMAMENTE otimizado iniciado - Render 512MB")

def worker_abort(worker):
    """Hook quando worker é abortado"""
    import gc
    
    # Limpeza antes de abortar
    gc.collect()
    worker.log.info(f"Worker {worker.pid} abortado após limpeza de memória")

# Configurações específicas do Render
if os.environ.get('RENDER'):
    # Configurações específicas para Render
    workers = 1
    worker_connections = 3
    max_requests = 3
    timeout = 10
    
    # Usar menos recursos no Render  
    worker_tmp_dir = "/tmp"
    tmp_upload_dir = "/tmp"
    
    print("🚀 Configuração EXTREMA para Render aplicada")
