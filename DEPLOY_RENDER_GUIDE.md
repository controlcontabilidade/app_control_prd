# 🚀 Guia de Deploy no Render

## ✅ Alterações Realizadas para Deploy

### 1. **Requirements.txt Atualizado**
```
pandas==2.1.4
openpyxl==3.1.2
werkzeug==3.0.1
```

### 2. **Runtime.txt Atualizado**
```
python-3.11.7
```

### 3. **Google Sheets Range Corrigido**
```
GOOGLE_SHEETS_RANGE = 'Clientes!A:BC'
```

### 4. **WSGI.py Melhorado**
- Logging para produção
- Tratamento de erros de importação
- Configuração para Gunicorn

## 🔧 Configuração no Render

### Variáveis de Ambiente Necessárias:
```
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-super-segura-aqui
GOOGLE_SHEETS_API_KEY=sua-api-key-aqui
GOOGLE_SHEETS_ID=1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s
```

### Comandos de Build:
```
pip install -r requirements.txt
```

### Comando de Start:
```
gunicorn --worker-class=gthread --workers=4 --worker-connections=1000 --max-requests=1000 --max-requests-jitter=100 --preload --timeout=120 --keep-alive=5 --bind=0.0.0.0:$PORT wsgi:application
```

## 📋 Checklist de Deploy

- [x] ✅ Pandas adicionado ao requirements.txt
- [x] ✅ OpenPyxl adicionado ao requirements.txt
- [x] ✅ Werkzeug adicionado ao requirements.txt
- [x] ✅ Runtime Python atualizado para 3.11.7
- [x] ✅ Google Sheets range corrigido (A:BC)
- [x] ✅ Tratamento de erro para pandas melhorado
- [x] ✅ WSGI.py otimizado para produção
- [x] ✅ Logging configurado para produção

## 🐛 Solução do Erro Original

**Erro:** `ModuleNotFoundError: No module named 'pandas'`

**Solução:**
1. ✅ Adicionado `pandas==2.1.4` ao requirements.txt
2. ✅ Adicionado `openpyxl==3.1.2` ao requirements.txt (dependência do pandas para Excel)
3. ✅ Melhorado tratamento de importação do pandas no código
4. ✅ Runtime Python atualizado para versão compatível

## 🔄 Próximos Passos

1. **Commitar as alterações**
2. **Fazer push para o repositório**
3. **Deploy no Render será automático**
4. **Configurar variáveis de ambiente no painel do Render**
5. **Testar a funcionalidade de importação**

## 🔗 Links Importantes

- **Aplicação:** Será disponibilizada pelo Render após deploy
- **Google Sheets:** https://docs.google.com/spreadsheets/d/1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s
- **Repositório:** GitHub do projeto

---
**Status:** ✅ Pronto para deploy
**Última atualização:** $(date)
