# 🎯 OTIMIZAÇÕES RENDER - REDUÇÃO DE MEMÓRIA

## 📊 Objetivo
Reduzir o consumo de memória da aplicação de **500MB para <256MB** no Render.

## 🚀 Otimizações Implementadas

### 1. 🧠 Memory Optimizer Lite
- **Arquivo**: `memory_optimizer_lite.py`
- **Recursos**: Garbage collection agressivo, limpeza após requests
- **Configurações**: GC threshold (10,1,1), cache mínimo
- **Impacto**: ~20-30MB economizados

### 2. ⚙️ Configuração Gunicorn Ultra-Otimizada
- **Arquivo**: `gunicorn.render.optimized.conf.py`
- **Workers**: 1 apenas (vs múltiplos anteriores)
- **Conexões**: 3 por worker (vs 100+ anteriores)
- **Timeout**: 15s (vs 30s+ anteriores)
- **Max Requests**: 25 (restart frequente)
- **Preload App**: True (economia de memória)
- **Impacto**: ~50-80MB economizados

### 3. 📦 Requirements Mínimos
- **Arquivo**: `requirements.render.minimal.txt`
- **Removidos**: pandas, numpy, openpyxl, psutil
- **Mantidos**: Apenas essenciais (Flask, Google API)
- **Tamanho**: ~30 pacotes vs 50+ anteriores
- **Impacto**: ~100-150MB economizados

### 4. 🔧 App.py Otimizado
- **Upload**: 256KB máximo (vs 2MB)
- **Cache**: Zero cache (vs 30s+)
- **Sessions**: 5 minutos (vs 10+ minutos)
- **GC**: Extremamente agressivo após cada request
- **Impacto**: ~20-40MB economizados

### 5. 🌐 WSGI Otimizado
- **Logging**: Apenas erros
- **Bytecode**: Desabilitado
- **GC**: Múltipla limpeza no startup
- **Variáveis**: Limpeza de vars desnecessárias
- **Impacto**: ~10-20MB economizados

### 6. 🗄️ Google Sheets Service Otimizado
- **Arquivo**: `services/google_sheets_render_optimized.py`
- **Cache**: 30s TTL (vs permanente)
- **Batch Size**: 10 itens (vs 100+)
- **Limpeza**: GC após cada operação
- **Lazy Loading**: Dados carregados sob demanda
- **Impacto**: ~30-50MB economizados

## 📈 Estimativa de Consumo de Memória

| Componente | Antes | Depois | Economia |
|------------|-------|--------|----------|
| Python Runtime | ~40MB | ~30MB | 10MB |
| Flask + Deps | ~80MB | ~40MB | 40MB |
| Google API | ~50MB | ~25MB | 25MB |
| Pandas/NumPy | ~150MB | ~0MB | 150MB |
| App Logic | ~30MB | ~15MB | 15MB |
| Cache/Buffer | ~100MB | ~20MB | 80MB |
| Overhead | ~50MB | ~20MB | 30MB |
| **TOTAL** | **~500MB** | **~150MB** | **350MB** |

## 🎯 Configurações Render Específicas

### Variáveis de Ambiente
```bash
RENDER=true
GOOGLE_SERVICE_ACCOUNT_JSON="{"type":"service_account",...}"
GOOGLE_SHEETS_ID="1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
SECRET_KEY="your-secret-key"
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command (Procfile)
```bash
web: gunicorn --config gunicorn.render.optimized.conf.py wsgi:app
```

## 🔍 Monitoramento e Debug

### Logs para Verificar
1. **Startup**: Procurar por "🎯 Render Memory Optimizer carregado"
2. **Requests**: Memory cleanup após cada request
3. **GC**: Coletas de lixo frequentes
4. **Workers**: Apenas 1 worker ativo

### Comandos de Debug
```bash
# Verificar uso de memória
ps aux | grep gunicorn

# Logs da aplicação
heroku logs --tail (ou equivalente Render)

# Verificar workers
pgrep -f gunicorn
```

## ⚠️ Limitações das Otimizações

### Funcionalidades Impactadas
1. **Upload**: Limitado a 256KB
2. **Importação Excel**: Desabilitada (sem openpyxl)
3. **Cache**: Muito limitado (30s máximo)
4. **Concorrência**: Apenas 1 worker
5. **Sessões**: Apenas 5 minutos

### Possíveis Problemas
1. **Timeout**: Operações longas podem falhar
2. **Concorrência**: Menos requests simultâneos
3. **Cache Miss**: Mais requests ao Google Sheets
4. **Restart Frequente**: Workers reiniciam a cada 25 requests

## 🔄 Como Reverter

### Script de Reversão
```bash
python optimize_render.py revert
```

### Manual
1. Restaurar `requirements.original.txt` → `requirements.txt`
2. Alterar Procfile para configuração anterior
3. Remover otimizadores de memória

## 📋 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Requirements.txt otimizado
- [ ] Gunicorn config otimizado
- [ ] Procfile atualizado
- [ ] WSGI otimizado
- [ ] Memory optimizer ativo
- [ ] Upload limitado
- [ ] Logs configurados

## 🎯 Resultados Esperados

### Antes da Otimização
- **Memória**: ~500MB
- **Boot Time**: 60-90s
- **Workers**: 2-4
- **Dependências**: 50+ pacotes

### Depois da Otimização
- **Memória**: ~150MB
- **Boot Time**: 30-45s
- **Workers**: 1
- **Dependências**: ~30 pacotes

### Redução Total
- **Memória**: 70% menos
- **Dependências**: 40% menos
- **Boot Time**: 30% mais rápido
- **Custo**: Potencial redução de plano

---

**Data**: Agosto 2025  
**Status**: ✅ IMPLEMENTADO  
**Objetivo**: 🎯 <256MB de memória no Render
