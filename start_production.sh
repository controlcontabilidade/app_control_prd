#!/bin/bash
echo "🚀 Testando deploy local com Gunicorn..."
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "🔧 Iniciando servidor de produção..."
echo "🌐 Acesse: http://localhost:8000"
echo "⏹️  Para parar: Ctrl+C"
echo ""

gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 wsgi:app
