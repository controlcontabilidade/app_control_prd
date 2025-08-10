# -*- coding: utf-8 -*-
"""
Configuração Gunicorn ULTRA-OTIMIZADA para Render
Objetivo: Reduzir consumo de memória de 500MB para <256MB
"""

import os
import multiprocessing

# Configurações de binding
bind = "0.0.0.0:10000"  # Porta padrão do Render

# CONFIGURAÇÕES DE MEMÓRIA EXTREMAMENTE OTIMIZADAS PARA RENDER
# =============================================================

# WORKERS: Apenas 1 para economizar memória máxima
workers = 1  # MÍNIMO absoluto para Render 512MB

# WORKER CLASS: sync para menor consumo de memória
worker_class = "sync"

# CONEXÕES: Mínimo para economizar memória
worker_connections = 3  # Extremamente baixo

# TIMEOUTS: Baixos para forçar reciclagem
timeout = 15  # 15 segundos apenas
keepalive = 1  # 1 segundo apenas
graceful_timeout = 10  # 10 segundos para shutdown

# RECICLAGEM DE WORKERS: Muito frequente para limpar memória
max_requests = 25  # Reciclar após apenas 25 requests
max_requests_jitter = 5  # Adicionar aleatoriedade

# PRELOAD: Essencial para economizar memória
preload_app = True  # Carrega app antes de fork dos workers

# CONFIGURAÇÕES DE MEMÓRIA
# =========================

# Limitar memória por worker (se disponível)
worker_tmp_dir = "/dev/shm"  # Usar RAM tmpfs se disponível

# LOGGING: Mínimo para economizar I/O e memória
# ==============================================

# Logs essenciais apenas
loglevel = "warning"  # Apenas warnings e erros
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s'  # Formato mínimo
accesslog = "-"  # STDOUT
errorlog = "-"   # STDERR

# Desabilitar logs desnecessários
disable_redirect_access_to_syslog = True
capture_output = True

# CONFIGURAÇÕES DE PROCESSO
# ==========================

# Daemon: Não para Render
daemon = False

# PID file: Não necessário no Render
pidfile = None

# User/Group: Automático no Render
user = None
group = None

# CONFIGURAÇÕES DE STARTUP
# =========================

def on_starting(server):
    """Callback executado no início do Gunicorn"""
    print("🚀 Iniciando Gunicorn com configurações RENDER-OTIMIZADAS")
    print(f"   Workers: {workers}")
    print(f"   Worker Class: {worker_class}")
    print(f"   Conexões por Worker: {worker_connections}")
    print(f"   Timeout: {timeout}s")
    print(f"   Max Requests: {max_requests}")
    print(f"   Preload App: {preload_app}")

def on_reload(server):
    """Callback executado no reload"""
    print("🔄 Recarregando aplicação...")

def worker_int(worker):
    """Callback executado quando worker recebe SIGINT"""
    print(f"💥 Worker {worker.pid} interrompido")

def on_exit(server):
    """Callback executado na saída"""
    print("🛑 Finalizando Gunicorn")

# CONFIGURAÇÕES ESPECÍFICAS DO RENDER
# ====================================

# Detectar se está rodando no Render
if os.environ.get('RENDER'):
    print("🎯 Detectado ambiente Render - aplicando otimizações específicas")
    
    # Forçar configurações mínimas para Render
    workers = 1
    worker_connections = 3
    max_requests = 25
    timeout = 15
    
    # Configurações de memória ainda mais agressivas
    worker_tmp_dir = "/tmp"  # Usar /tmp no Render
    
    # Logs mínimos no Render
    loglevel = "error"  # Apenas erros no Render

# CONFIGURAÇÕES DE DESENVOLVIMENTO (para teste local)
# ===================================================
elif os.environ.get('FLASK_DEBUG') == '1':
    print("🔧 Modo desenvolvimento detectado")
    workers = 1
    loglevel = "debug"
    reload = True
    timeout = 30

print(f"⚙️ Configuração final:")
print(f"   Environment: {'Render' if os.environ.get('RENDER') else 'Other'}")
print(f"   Workers: {workers}")
print(f"   Memory optimization: EXTREME")
