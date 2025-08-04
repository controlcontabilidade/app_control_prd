#!/bin/bash
# Script EXTREMO de inicialização para ambiente Render
# Foco máximo em economia de memória

echo "🚀 Iniciando aplicação com otimizações EXTREMAS para Render..."

# Variáveis de ambiente para economia máxima de memória
export FLASK_ENV=production
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=1
export PYTHONIOENCODING=utf-8

# Configurações Gunicorn EXTREMAS
export WEB_CONCURRENCY=1
export WORKER_CONNECTIONS=3
export WORKER_TIMEOUT=10
export MAX_REQUESTS=3
export MAX_REQUESTS_JITTER=1

# Configurações específicas para memória limitada
export MALLOC_ARENA_MAX=1
export MALLOC_MMAP_MAX_=32768
export MALLOC_TRIM_THRESHOLD_=131072

echo "⚙️ Variáveis de ambiente EXTREMAS configuradas"
echo "🧠 MALLOC_ARENA_MAX: $MALLOC_ARENA_MAX"
echo "🔧 WEB_CONCURRENCY: $WEB_CONCURRENCY"
echo "⏱️ WORKER_TIMEOUT: $WORKER_TIMEOUT"

# Verificar memória disponível (se possível)
if command -v free >/dev/null 2>&1; then
    echo "💾 Memória disponível:"
    free -h
fi

# Iniciar com configuração ultra-otimizada
echo "🚀 Iniciando Gunicorn com configuração EXTREMA..."
exec gunicorn \
    --config gunicorn.ultra.conf.py \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class sync \
    --worker-connections 3 \
    --max-requests 3 \
    --max-requests-jitter 1 \
    --timeout 10 \
    --graceful-timeout 5 \
    --worker-tmp-dir /tmp \
    --log-level warning \
    --no-sendfile \
    --reuse-port \
    wsgi:app
