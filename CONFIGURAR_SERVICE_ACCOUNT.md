# 🔐 Como Configurar Google Sheets com Service Account

## ✅ Vantagens da Service Account vs OAuth2:
- ✅ **Mais simples**: Não precisa de autenticação manual
- ✅ **Server-side**: Ideal para aplicações que rodam no servidor
- ✅ **Automática**: Funciona sem intervenção do usuário
- ✅ **Segura**: Credenciais ficam no servidor

## 📋 Passos para configurar:

### 1. 🌐 Acesse o Google Cloud Console
```
https://console.cloud.google.com/
```

### 2. 🎯 Selecione/Crie um Projeto
- Se não tem projeto, clique em "Novo Projeto"
- Nome sugerido: "Sistema-Clientes-Flask"

### 3. 🛠️ Ative a API do Google Sheets
- Vá em "APIs e Serviços" → "Biblioteca"
- Procure por "Google Sheets API"
- Clique em "Ativar"

### 4. 🔑 Crie uma Service Account
- Vá em "APIs e Serviços" → "Credenciais"
- Clique em "+ CRIAR CREDENCIAIS" → "Conta de serviço"
- Nome: `sheets-service-account`
- Descrição: `Service Account para acessar Google Sheets`
- Clique em "Criar e continuar"

### 5. 🎭 Configure Papéis (opcional)
- Pode pular esta etapa clicando em "Continuar"
- Ou adicionar papel "Editor" se quiser

### 6. 📁 Baixe a Chave JSON
- Na lista de Service Accounts, clique na que você criou
- Vá na aba "Chaves"
- Clique em "Adicionar chave" → "Criar nova chave"
- Escolha "JSON" e clique em "Criar"
- **Arquivo será baixado automaticamente**

### 7. 📋 Configure o arquivo no projeto
- Renomeie o arquivo baixado para: `service-account-key.json`
- Coloque na pasta raiz do projeto (junto com app.py)

### 8. 🔗 Compartilhe a planilha com a Service Account
- Abra sua planilha do Google Sheets
- Clique em "Compartilhar"
- Adicione o email da service account (ex: `sheets-service-account@projeto-123456.iam.gserviceaccount.com`)
- Dê permissão de "Editor"
- O email está no arquivo JSON no campo `client_email`

### 9. ✅ Teste a aplicação
```bash
python app.py
```

## 🔧 Configuração no app.py
```python
USE_SERVICE_ACCOUNT = True   # ✅ Habilitar Service Account
USE_OAUTH2 = False          # ❌ Desabilitar OAuth2
USE_GOOGLE_SHEETS = True    # ✅ Usar Google Sheets
```

## 🚨 Segurança
- ⚠️ **NUNCA** commite o arquivo `service-account-key.json` no Git
- ✅ Adicione no `.gitignore`: `service-account-key.json`
- ✅ Mantenha o arquivo seguro no servidor de produção

## 🆘 Troubleshooting

### Erro: "service-account-key.json não encontrado"
- ✅ Verifique se o arquivo está na pasta raiz
- ✅ Verifique se o nome está correto

### Erro: "403 Forbidden" 
- ✅ Compartilhe a planilha com o email da service account
- ✅ Dê permissão de "Editor"

### Erro: "API not enabled"
- ✅ Ative a Google Sheets API no Cloud Console

## 📞 Email da Service Account
Para encontrar o email da sua service account:
```bash
# Windows PowerShell
Get-Content service-account-key.json | ConvertFrom-Json | Select-Object client_email

# Ou abra o arquivo e procure por "client_email"
```

## 🎯 Exemplo de email da Service Account:
```
sheets-service-account@sistema-clientes-123456.iam.gserviceaccount.com
```

**Este email deve ser adicionado na planilha com permissão de Editor!**
