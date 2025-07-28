# Configuração Gunicorn Otimizada para Render (Baixa Memória)
# Este arquivo é usado quando o Render não consegue usar o Procfile

import os
import multiprocessing

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
wsgi_module = "wsgi:application"

# OTIMIZAÇÕES CRÍTICAS PARA MEMÓRIA NO RENDER
workers = 1  # CRITICAL: Apenas 1 worker para economizar RAM
worker_class = "gthread"  # Threads ao invés de processos
threads = 2  # Máximo 2 threads por worker
worker_connections = 100  # Reduzido para economizar memória

# Limites de requisições (ajuda com vazamentos de memória)
max_requests = 1000
max_requests_jitter = 100

# Timeouts otimizados
timeout = 30
keepalive = 2
graceful_timeout = 30

# Configurações de memória
preload_app = False  # CRITICAL: Não precarregar para economizar RAM
max_worker_connections = 100

# Logs para produção
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações do processo
daemon = False
pidfile = None
tmp_upload_dir = None

# Security
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Callbacks para otimização de memória
def when_ready(server):
    server.log.info("🚀 Servidor Gunicorn iniciado (modo otimizado)")
    server.log.info(f"🧠 Workers: {workers} | Threads: {threads}")

def worker_int(worker):
    worker.log.info("🔄 Worker interrompido, limpando memória")
    import gc
    gc.collect()

def on_exit(server):
    server.log.info("🛑 Servidor Gunicorn finalizado")

# Configurações específicas para Render
if os.environ.get('RENDER'):
    # Configurações específicas para Render
    bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
    workers = 1  # Render free tier tem pouca RAM
    timeout = 30
    keepalive = 2
