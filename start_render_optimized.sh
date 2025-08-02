#!/bin/bash
# Script de startup otimizado para Render.com com 512MB RAM
# start_render_optimized.sh

echo "🚀 Iniciando aplicação com otimizações para Render 512MB..."

# Configurar variáveis de ambiente para economia de memória
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=1

# Configurações específicas do Python para economia de memória
export MALLOC_TRIM_THRESHOLD_=100000
export MALLOC_MMAP_THRESHOLD_=100000
export MALLOC_MMAP_MAX_=2

# Configurações do Flask para produção
export FLASK_ENV=production
export FLASK_DEBUG=false

# Configurações de workers Gunicorn
export WEB_CONCURRENCY=1
export WORKER_CONNECTIONS=25
export WORKER_TIMEOUT=20

echo "🧠 Configurações de memória aplicadas"
echo "📊 Memória disponível:"
free -h 2>/dev/null || echo "Comando 'free' não disponível"

# Instalar apenas dependências essenciais
echo "📦 Instalando dependências otimizadas..."
pip install --no-cache-dir -r requirements.render.txt

echo "🔥 Iniciando Gunicorn com configuração otimizada..."
exec gunicorn --config gunicorn.render.conf.py wsgi:app
