# Configuração Gunicorn Otimizada para Render (Baixa Memória)
# Este arquivo é usado quando o Render não consegue usar o Procfile

import os
import multiprocessing

# Configurações básicas
# Configuração Gunicorn otimizada para Render 512MB
import os
import multiprocessing

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1  # APENAS 1 worker para economizar memória (era 2)
worker_class = "sync"  # Sync é mais eficiente em memória que async
worker_connections = 50  # Reduzido de 1000 para 50

# Otimizações de memória críticas para Render 512MB
max_requests = 100  # Reciclar worker após 100 requests
max_requests_jitter = 10  # Adicionar variação
worker_memory_limit = 400 * 1024 * 1024  # 400MB limite por worker
preload_app = False  # NÃO precarregar app (economia de memória)

# Timeouts otimizados
timeout = 60  # Reduzido de 120 para 60 segundos
keepalive = 2
graceful_timeout = 30

# Configurações de logging minimalistas
accesslog = "-"
errorlog = "-"
loglevel = "warning"  # Menos logs = menos memória
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)s'  # Formato mínimo

# Configurações específicas para produção
if os.environ.get('FLASK_ENV') == 'production':
    # Ainda mais conservador em produção
    workers = 1
    worker_connections = 25
    max_requests = 50
    loglevel = "error"  # Apenas erros
    
    print("🧠 Gunicorn configurado para máxima economia de memória (Render 512MB)")
else:
    print("🔧 Gunicorn configurado para desenvolvimento")

# Funções de hook para monitoramento de memória
def when_ready(server):
    """Executado quando o servidor está pronto"""
    print(f"🚀 Gunicorn iniciado com {workers} worker(s)")
    print(f"💾 Configurado para Render 512MB - workers limitados")

def worker_exit(server, worker):
    """Executado quando um worker sai"""
    try:
        import gc
        gc.collect()
        print(f"🧹 Worker {worker.pid} finalizado - memoria limpa")
    except:
        pass

def on_starting(server):
    """Executado ao iniciar"""
    print("⚙️ Iniciando Gunicorn com configurações otimizadas para memória")
    
def pre_fork(server, worker):
    """Executado antes de fazer fork do worker"""
    try:
        import gc
        gc.collect()
    except:
        pass
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
