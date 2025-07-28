# 🔧 Configuração de Variáveis de Ambiente

Este projeto foi atualizado para **remover credenciais hardcoded** e usar variáveis de ambiente tanto localmente quanto em produção.

## 📁 **Desenvolvimento Local (.env)**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Google Sheets API
GOOGLE_SHEETS_API_KEY=sua_api_key_aqui
GOOGLE_SHEETS_ID=seu_spreadsheet_id_aqui

# Flask
SECRET_KEY=sua_secret_key_segura_aqui
FLASK_ENV=development
FLASK_DEBUG=1

# Service Account (opcional - se usando Service Account)
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

## 🌐 **Produção (Render)**

No painel do Render, configure as seguintes **Environment Variables**:

### **Obrigatórias:**
- `GOOGLE_SHEETS_API_KEY` = Sua API Key do Google Sheets
- `GOOGLE_SHEETS_ID` = ID da sua planilha do Google Sheets
- `SECRET_KEY` = Chave secreta segura para Flask

### **Opcionais:**
- `GOOGLE_SERVICE_ACCOUNT_JSON` = JSON do Service Account (uma linha)
- `FLASK_ENV` = production
- `FLASK_DEBUG` = False

## 🔑 **Como Obter as Credenciais**

### **Google Sheets API Key:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a Google Sheets API
3. Crie uma API Key
4. Configure restrições de IP/domínio (recomendado)

### **Google Sheets ID:**
1. Abra sua planilha no Google Sheets
2. Na URL: `https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/edit`
3. Copie o `SEU_ID_AQUI`

### **Service Account (Opcional):**
1. No Google Cloud Console, crie um Service Account
2. Baixe o arquivo JSON
3. Para produção: coloque todo o JSON em uma linha
4. Para local: salve como `service-account-key.json`

## 🚀 **Iniciando o Projeto**

### **Local:**
```bash
# Instalar dependências
pip install -r requirements.minimal.txt

# Verificar se .env existe e está configurado
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Configurado' if os.getenv('GOOGLE_SHEETS_ID') else '❌ Configure .env')"

# Iniciar aplicação
python app.py
```

### **Render:**
- As variáveis de ambiente são carregadas automaticamente
- Use `requirements.txt` para deploy otimizado
- O arquivo `wsgi.py` é o ponto de entrada

## 🔒 **Segurança**

- ✅ **Nunca** commite arquivos `.env` ou `service-account-key.json`
- ✅ `.gitignore` já está configurado para ignorar estes arquivos
- ✅ Credenciais são carregadas via variáveis de ambiente
- ✅ Service Account tem permissões limitadas apenas ao necessário

## 🐛 **Correção de Duplicação**

O problema de duplicação de cadastros foi corrigido com:

1. **Busca otimizada de ID** - busca apenas na coluna necessária
2. **Validação rigorosa** - não permite operações com ID inválido
3. **Sem fallback perigoso** - não cria novo registro quando deveria atualizar
4. **Logs detalhados** - facilita debug de problemas

## 📋 **Verificação de Funcionamento**

Para testar se tudo está funcionando:

1. Crie um novo cliente
2. Edite o cliente criado
3. Verifique se não há duplicação na planilha
4. Logs devem mostrar `ATUALIZANDO CLIENTE` ao invés de `NOVO CLIENTE`

```
✅ [SERVICE] ===== OPERAÇÃO: ATUALIZAÇÃO =====
✅ [SERVICE] Cliente existe na linha X - ATUALIZANDO
```
