# 🚀 Deploy Otimizado para Render.com (512MB RAM)

Este guia contém otimizações específicas para executar a aplicação SIGEC no Render.com com limite de 512MB de RAM.

## 🧠 Otimizações Implementadas

### 1. **Configurações de Memória**
- Garbage Collection ultra-agressivo (threshold: 100, 2, 2)
- Cache limitado a 30 segundos
- Processamento em lotes de 5-15 registros
- Limite máximo de 15 clientes por requisição

### 2. **Configurações do Gunicorn**
- 1 worker apenas
- 25 conexões simultâneas máximo
- Timeout de 20 segundos
- Reinicialização de worker a cada 50 requests
- Preload app habilitado

### 3. **Dependências Otimizadas**
- Removido pandas (economiza ~100MB)
- Removido openpyxl (economiza ~20MB)
- Removido psutil (economiza ~10MB)
- Apenas dependências essenciais

### 4. **Configurações Python**
- `PYTHONOPTIMIZE=2` (otimização máxima)
- `PYTHONDONTWRITEBYTECODE=1` (sem .pyc)
- `PYTHONHASHSEED=1` (determinístico)

## 📋 Configuração no Render.com

### 1. **Variáveis de Ambiente**
Configure as seguintes variáveis no painel do Render:

```bash
# Essenciais
FLASK_ENV=production
FLASK_DEBUG=false
GOOGLE_SHEETS_ID=sua_planilha_id_aqui
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Otimizações de memória
PYTHONOPTIMIZE=2
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
WEB_CONCURRENCY=1
WORKER_CONNECTIONS=25
WORKER_TIMEOUT=20
```

### 2. **Comando de Build**
```bash
pip install --no-cache-dir -r requirements.render.txt
```

### 3. **Comando de Start**
```bash
gunicorn --config gunicorn.render.conf.py wsgi:app
```

OU usar o script otimizado:
```bash
chmod +x start_render_optimized.sh && ./start_render_optimized.sh
```

### 4. **Configurações de Serviço**
- **Environment**: Python 3.11
- **Build Command**: `pip install --no-cache-dir -r requirements.render.txt`
- **Start Command**: `gunicorn --config gunicorn.render.conf.py wsgi:app`
- **Instance Type**: Starter (512MB RAM)

## 📊 Monitoramento de Memória

A aplicação inclui endpoint de monitoramento:
- `/api/memory-status` - Status de memória em tempo real
- Alertas automáticos quando próximo do limite

## ⚠️ Limitações Implementadas

Para funcionar com 512MB, algumas limitações foram necessárias:

1. **Clientes por página**: Máximo 15
2. **Upload de arquivo**: Máximo 1MB
3. **Cache**: Apenas 30 segundos
4. **Importação Excel**: Desabilitada (economiza 120MB+)
5. **Workers**: Apenas 1 simultâneo

## 🔧 Troubleshooting

### Erro de Memória
Se ainda houver problemas de memória:

1. **Reduza MAX_ROWS_PER_REQUEST** no `memory_optimizer.py`
2. **Diminua BATCH_SIZE** para 3 ou menos
3. **Aumente frequência de GC** no app.py

### Performance
Para melhorar performance sem aumentar memória:

1. **Implemente paginação** no frontend
2. **Use carregamento lazy** para campos não essenciais
3. **Considere cache Redis** externo (Redis Lab free tier)

## 📈 Upgrade Path

Para funcionalidades completas, considere upgrade para:
- **Starter Plus (1GB)**: Habilita importação Excel
- **Standard (2GB)**: Remove todas as limitações

## 🆘 Suporte

Se problemas persistirem:
1. Verifique logs no Render Dashboard
2. Monitore `/api/memory-status`
3. Ajuste configurações em `memory_optimizer.py`

---

**Importante**: Estas otimizações priorizam estabilidade sobre funcionalidade. Para ambiente de desenvolvimento, use configurações normais.
