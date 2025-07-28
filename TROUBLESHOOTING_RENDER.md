# 🚨 TROUBLESHOOTING - Erro de Autenticação no Render

## ❌ PROBLEMA: "Serviço de autenticação indisponível"

Este erro indica que a aplicação não consegue se autenticar com o Google Sheets API no ambiente do Render.

---

## 🔍 DIAGNÓSTICO RÁPIDO

### 1. **Verificar Status no Render**
Acesse: `https://sua-app.render.com/api/auth-status`

### 2. **Verificar Logs do Render**
No painel do Render, vá em **Logs** e procure por:
- `❌ Erro na autenticação Service Account`
- `🔐 Variável de ambiente não encontrada`
- `❌ JSON parseado com erro`

---

## ✅ SOLUÇÕES

### **Solução 1: Verificar Variável de Ambiente**

1. **Acessar Render Dashboard:**
   - Vá para seu serviço no Render
   - Clique em **Environment**

2. **Verificar `GOOGLE_SERVICE_ACCOUNT_JSON`:**
   ```
   ✅ Deve estar definida
   ✅ Deve conter JSON válido
   ✅ Deve estar em UMA LINHA apenas
   ✅ Deve usar aspas duplas (não simples)
   ```

3. **Formato Correto:**
   ```json
   {"type":"service_account","project_id":"seu-projeto","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n","client_email":"nome@projeto.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs/nome%40projeto.iam.gserviceaccount.com"}
   ```

### **Solução 2: Recriar Service Account**

1. **Google Cloud Console:**
   - Acesse https://console.cloud.google.com
   - Vá em **IAM & Admin > Service Accounts**

2. **Criar Nova Service Account:**
   - Clique **CREATE SERVICE ACCOUNT**
   - Nome: `render-control-app`
   - ID: `render-control-app`

3. **Configurar Permissões:**
   - **Role:** `Editor` ou `Google Sheets API`
   - Clique **DONE**

4. **Gerar Nova Chave:**
   - Clique na service account criada
   - Vá em **Keys > ADD KEY > Create new key**
   - Escolha **JSON**
   - Download do arquivo

5. **Habilitar APIs:**
   ```
   ✅ Google Sheets API
   ✅ Google Drive API (opcional)
   ```

### **Solução 3: Configurar Render Corretamente**

1. **Environment Variables no Render:**
   ```bash
   FLASK_ENV=production
   GOOGLE_SHEETS_ID=1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s
   GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
   SECRET_KEY=sua-chave-secreta-aqui
   PYTHONOPTIMIZE=2
   WEB_CONCURRENCY=1
   ```

2. **Build Command:**
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

3. **Start Command:**
   ```bash
   gunicorn --config gunicorn.conf.py wsgi:application
   ```

### **Solução 4: Verificar Planilha Google**

1. **Compartilhar Planilha:**
   - Abra a planilha no Google Sheets
   - Clique **Compartilhar**
   - Adicione o email da service account
   - Permissão: **Editor**

2. **Verificar ID da Planilha:**
   - URL: `https://docs.google.com/spreadsheets/d/ID_AQUI/edit`
   - O `ID_AQUI` deve ser igual à `GOOGLE_SHEETS_ID`

---

## 🛠️ MODO DE RECUPERAÇÃO

Se nada funcionar, a aplicação ativará automaticamente o **Modo Fallback**:

### **Recursos Disponíveis:**
- ✅ Interface funcional
- ✅ Dados de exemplo para teste
- ✅ Salvamento temporário local
- ⚠️ Dados não sincronizam com Google Sheets

### **Identificar Modo Fallback:**
- Badge amarelo "MODO OFFLINE" no dashboard
- Alerta laranja no topo da página
- Mensagem: "Sistema em modo de manutenção"

---

## 🔧 COMANDOS DE DEBUG

### **1. Testar Localmente:**
```bash
# Definir variáveis
$env:FLASK_ENV="production"
$env:GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# Executar diagnóstico
python check_deploy_readiness.py

# Testar autenticação
python -c "
from services.google_sheets_service_account import GoogleSheetsServiceAccountService
service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
print('✅ Autenticação OK')
"
```

### **2. Verificar JSON:**
```bash
python -c "
import json, os
json_str = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
if json_str:
    data = json.loads(json_str)
    print(f'✅ JSON válido - Project: {data.get(\"project_id\")}')
else:
    print('❌ Variável não definida')
"
```

---

## 📞 SUPORTE

### **Se o problema persistir:**

1. **Verificar APIs no Google Cloud:**
   - https://console.cloud.google.com/apis/dashboard
   - Verificar se Google Sheets API está habilitada
   - Verificar cotas e limites

2. **Logs Detalhados:**
   - Habilitar logs debug no Render
   - Verificar `/api/auth-status` para diagnóstico completo

3. **Rollback:**
   - Use branch anterior que funcionava
   - Ou ative modo local temporariamente

### **Contato:**
- 📧 Email: suporte@controlcontabilidade.com
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Status: https://sua-app.render.com/api/auth-status

---

## ✅ CHECKLIST DE VERIFICAÇÃO

- [ ] Variável `GOOGLE_SERVICE_ACCOUNT_JSON` definida no Render
- [ ] JSON é válido (testar com json.loads())
- [ ] Service Account existe no Google Cloud
- [ ] Google Sheets API habilitada
- [ ] Planilha compartilhada com service account
- [ ] ID da planilha correto na variável `GOOGLE_SHEETS_ID`  
- [ ] Build e Start commands corretos no Render
- [ ] Aplicação reiniciada após mudanças
- [ ] Logs do Render verificados
- [ ] API `/api/auth-status` testada

**🎯 Se todos os itens estiverem OK, a autenticação deve funcionar normalmente!**
