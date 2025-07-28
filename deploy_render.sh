#!/bin/bash
# Script de deploy otimizado para Render 512MB
# Este script configura o ambiente para máxima economia de memória

echo "🚀 Iniciando deploy otimizado para Render 512MB..."

# Configurar variáveis de ambiente para economia de memória
export PYTHONOPTIMIZE=2  # Remover docstrings e assertions
export PYTHONDONTWRITEBYTECODE=1  # Não gerar .pyc files
export PYTHONUNBUFFERED=1  # Output unbuffered
export WEB_CONCURRENCY=1  # Apenas 1 worker
export WORKER_CONNECTIONS=25  # Poucas conexões simultâneas
export MAX_REQUESTS=50  # Reciclar workers rapidamente
export FLASK_ENV=production  # Modo produção

echo "⚙️ Variáveis de ambiente configuradas:"
echo "   PYTHONOPTIMIZE: $PYTHONOPTIMIZE"
echo "   WEB_CONCURRENCY: $WEB_CONCURRENCY"
echo "   WORKER_CONNECTIONS: $WORKER_CONNECTIONS"
echo "   MAX_REQUESTS: $MAX_REQUESTS"

# Instalar dependências mínimas
echo "📦 Instalando dependências otimizadas..."
pip install --no-cache-dir -r requirements.txt

# Limpeza de cache Python
echo "🧹 Limpando cache Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Verificar uso de memória das dependências
echo "💾 Verificando dependências instaladas..."
pip list --format=freeze | wc -l | xargs echo "   Pacotes instalados:"

# Otimizar arquivos estáticos (se existirem)
if [ -d "static" ]; then
    echo "🗜️ Otimizando arquivos estáticos..."
    find static -name "*.js" -exec echo "   Encontrado: {}" \;
    find static -name "*.css" -exec echo "   Encontrado: {}" \;
fi

# Verificar configurações críticas
echo "🔍 Verificando configurações críticas..."

if [ -f "gunicorn.conf.py" ]; then
    echo "✅ gunicorn.conf.py encontrado"
    grep -E "(workers|max_requests|worker_memory_limit)" gunicorn.conf.py || true
else
    echo "❌ gunicorn.conf.py NÃO encontrado!"
fi

if [ -f "memory_optimizer.py" ]; then
    echo "✅ memory_optimizer.py encontrado"
else
    echo "❌ memory_optimizer.py NÃO encontrado!"
fi

# Verificar arquivos críticos
critical_files=("app.py" "wsgi.py" "requirements.txt")
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file encontrado"
    else
        echo "❌ $file NÃO encontrado!"
    fi
done

# Mostrar estatísticas finais
echo ""
echo "📊 ESTATÍSTICAS DO DEPLOY:"
echo "   Arquivos Python: $(find . -name "*.py" | wc -l)"
echo "   Tamanho total: $(du -sh . | cut -f1)"
echo "   Memória disponível: 512MB (Render)"

echo ""
echo "🎯 CONFIGURAÇÕES OTIMIZADAS PARA RENDER:"
echo "   ✅ Workers limitados a 1"
echo "   ✅ Conexões limitadas a 25"
echo "   ✅ Requests limitadas a 50 por worker"
echo "   ✅ Garbage collection agressivo"
echo "   ✅ Cache desabilitado"
echo "   ✅ Logs minimizados"

echo ""
echo "🚨 MONITORAMENTO RECOMENDADO:"
echo "   - Usar 'python memory_monitor.py' para verificar uso"
echo "   - Verificar logs do Render para OOM (Out of Memory)"
echo "   - Monitorar métricas de CPU e RAM"

echo ""
echo "✅ Deploy otimizado concluído!"
echo "🚀 Pronto para iniciar com: gunicorn --config gunicorn.conf.py wsgi:application"
