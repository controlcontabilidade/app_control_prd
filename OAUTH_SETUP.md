# Configuração OAuth2 para Google Sheets

## ⚠️ IMPORTANTE: Para usar escrita no Google Sheets, você precisa configurar OAuth2

O Google Sheets não permite escrita usando apenas API Key. Para salvar dados diretamente na planilha, você precisa configurar OAuth2.

## 📋 Passo a passo:

### 1. Acesse o Google Cloud Console
- Vá para: https://console.cloud.google.com/

### 2. Criar/Selecionar Projeto
- Crie um novo projeto ou selecione um existente
- Anote o ID do projeto

### 3. Ativar APIs
- Vá em "APIs e serviços" > "Biblioteca"
- Busque e ative: "Google Sheets API"
- Busque e ative: "Google Drive API"

### 4. Criar Credenciais OAuth2
- Vá em "APIs e serviços" > "Credenciais"
- Clique em "Criar credenciais" > "ID do cliente OAuth 2.0"
- Escolha "Aplicativo para computador"
- Dê um nome (ex: "Flask Sheets App")

### 5. Baixar Credenciais
- Clique no ícone de download das credenciais criadas
- Salve o arquivo como `credentials.json` na raiz do projeto
- ⚠️ NUNCA commite este arquivo no git!

### 6. Configurar .gitignore
Adicione no `.gitignore`:
```
credentials.json
token.pickle
```

### 7. Executar Aplicação
```bash
python app_oauth.py
```

Na primeira execução:
- Abrirá o navegador para autenticação
- Faça login com sua conta Google
- Autorize o acesso às planilhas
- O token será salvo em `token.pickle`

## 🔧 Estrutura dos arquivos de credenciais:

### credentials.json
```json
{
  "installed": {
    "client_id": "SEU_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "seu-projeto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "SEU_CLIENT_SECRET",
    "redirect_uris": [
      "urn:ietf:wg:oauth:2.0:oob",
      "http://localhost"
    ]
  }
}
```

## 🚀 Testando

Após configurar OAuth2:

1. Execute: `python app_oauth.py`
2. Acesse: http://localhost:5001/test_save
3. Verifique se salvou na planilha

## 🔐 Segurança

- ✅ `credentials.json` - Nunca committar no git
- ✅ `token.pickle` - Nunca committar no git
- ✅ Usar variáveis de ambiente em produção
- ✅ Renovar tokens periodicamente

## 📱 Alternativas

Se não quiser configurar OAuth2:

1. **Usar formulário do Google**: Criar Google Form que salva na planilha
2. **Usar Zapier/Integromat**: Conectar Flask com Google Sheets via webhook
3. **Usar armazenamento local**: SQLite ou JSON local com sincronização manual

## 🔧 Instalação de dependências OAuth2

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Essas dependências já estão no requirements.txt do projeto.
