# Como configurar Service Account para Google Sheets

## 1. Criar Service Account no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Selecione seu projeto (ou crie um novo)
3. Vá para "IAM & Admin" > "Service Accounts"
4. Clique em "CREATE SERVICE ACCOUNT"
5. Preencha:
   - Nome: "flask-sheets-service"
   - Descrição: "Service Account para Flask Google Sheets"
6. Clique "CREATE AND CONTINUE"
7. Adicione role: "Editor" ou "Google Sheets API" (mais restrito)
8. Clique "DONE"

## 2. Baixar arquivo de credenciais

1. Na lista de Service Accounts, clique nos 3 pontos da sua service account
2. Selecione "Manage keys"
3. Clique "ADD KEY" > "Create new key"
4. Selecione formato "JSON"
5. Clique "CREATE"
6. O arquivo será baixado automaticamente
7. Renomeie para "service-account-key.json"
8. Coloque na pasta raiz do projeto

## 3. Ativar APIs necessárias

1. Vá para "APIs & Services" > "Library"
2. Procure e ative:
   - Google Sheets API
   - Google Drive API (para compartilhamento)

## 4. Compartilhar planilha com Service Account

1. Abra sua planilha no Google Sheets
2. Clique em "Compartilhar"
3. Adicione o email da service account (ex: flask-sheets-service@projeto.iam.gserviceaccount.com)
4. Defina permissão como "Editor"
5. Clique "Enviar"

## 5. Formato correto do arquivo service-account-key.json

O arquivo deve ter esta estrutura:
```json
{
  "type": "service_account",
  "project_id": "seu-projeto",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "sua-service-account@projeto.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
}
```

## ⚠️ Segurança

- NUNCA compartilhe este arquivo
- Adicione ao .gitignore
- Use variáveis de ambiente em produção

## 🚀 Vantagens da Service Account

- ✅ Não precisa de autenticação manual
- ✅ Ideal para aplicações server-side
- ✅ Mais seguro que API Keys
- ✅ Acesso direto de leitura/escrita
- ✅ Sem limite de rate por usuário
