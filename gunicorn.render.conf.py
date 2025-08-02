# Configuração Gunicorn ULTRA-OTIMIZADA para Render 512MB
# gunicorn.conf.py

import os
import multiprocessing

# Configurações de worker ULTRA-conservadoras
workers = 1  # Apenas 1 worker para economizar memória
worker_class = "sync"  # Sync é mais eficiente em memória
worker_connections = 25  # Reduzido drasticamente
max_requests = 50  # Reiniciar worker frequentemente
max_requests_jitter = 10  # Variação para evitar restart simultâneo

# Configurações de timeout agressivas
timeout = 20  # Timeout baixo
keepalive = 1  # Keepalive mínimo
graceful_timeout = 15  # Graceful timeout baixo

# Configurações de memória
preload_app = True  # Preload para economizar memória
worker_tmp_dir = "/dev/shm"  # Usar RAM para temporários (se disponível)

# Configurações de bind
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 64  # Backlog reduzido

# Configurações de log otimizadas
loglevel = "warning"  # Apenas warnings e erros
access_log_format = "%(h)s %(l)s %(t)s %(r)s %(s)s %(b)s"
errorlog = "-"
accesslog = "-"

# Configurações de processo
daemon = False
pidfile = None
tmp_upload_dir = None

# Limites de memória
limit_request_line = 2048  # Reduzido
limit_request_fields = 50  # Reduzido
limit_request_field_size = 4096  # Reduzido

# Hooks para otimização de memória
def when_ready(server):
    """Hook executado quando o servidor está pronto"""
    print("🚀 Gunicorn iniciado com configuração otimizada para 512MB")

def worker_int(worker):
    """Hook executado quando worker recebe SIGINT"""
    print(f"🔄 Worker {worker.pid} reiniciando para limpeza de memória")

def pre_fork(server, worker):
    """Hook executado antes de fazer fork do worker"""
    # Limpeza de memória antes do fork
    import gc
    gc.collect()

def post_fork(server, worker):
    """Hook executado após fork do worker"""
    # Configurações específicas do worker
    import gc
    gc.set_threshold(100, 2, 2)  # GC agressivo
    print(f"⚡ Worker {worker.pid} iniciado com GC otimizado")

def worker_abort(worker):
    """Hook executado quando worker aborta"""
    print(f"❌ Worker {worker.pid} abortado - liberando memória")
    import gc
    gc.collect()

# Configurações específicas para produção
if os.environ.get('FLASK_ENV') == 'production':
    # Configurações ainda mais agressivas para produção
    max_requests = 25  # Ainda menor em produção
    worker_connections = 15  # Ainda menor
    timeout = 15  # Timeout ainda menor
