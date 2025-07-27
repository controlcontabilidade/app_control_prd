# Control Contabilidade - Sistema de Clientes

Sistema de gestão de clientes desenvolvido em Python Flask para a Control Contabilidade LTDA.

## 🚀 Deploy em Produção

### Opção 1: Render.com (Recomendado - Gratuito)

1. **Criar conta no Render.com**
   - Acesse: https://render.com
   - Faça login com GitHub

2. **Preparar repositório GitHub**
   - Faça upload deste projeto para um repositório GitHub
   - Certifique-se que o arquivo `service-account-key.json` **NÃO** está no repositório público

3. **Configurar Service Account**
   - No Render, adicione o conteúdo do `service-account-key.json` como variável de ambiente
   - Nome: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Valor: Cole todo o conteúdo do arquivo JSON

4. **Variáveis de ambiente necessárias**:
   ```
   GOOGLE_SHEETS_ID=1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s
   GOOGLE_SHEETS_API_KEY=AIzaSyA2HSqIGfYI51rzCa5p7duPJUMG5VtU3TA
   SECRET_KEY=sua-chave-secreta-muito-forte-aqui
   GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
   ```

5. **Comando de build**: `pip install -r requirements.txt`
6. **Comando de start**: `gunicorn wsgi:app`

### Opção 2: Railway.app ($5/mês)

1. Acesse: https://railway.app
2. Conecte seu GitHub
3. Deploy automático
4. Configure as mesmas variáveis de ambiente

### Opção 3: PythonAnywhere (Plano gratuito)

1. Acesse: https://www.pythonanywhere.com
2. Upload dos arquivos
3. Configure WSGI
4. Configure variáveis de ambiente

## 🔧 Configuração Local

1. Clone o repositório
2. Instale dependências: `pip install -r requirements.txt`
3. Coloque o arquivo `service-account-key.json` na raiz
4. Execute: `python app.py`

## 📋 Funcionalidades

- ✅ CRUD completo de clientes
- ✅ Integração com Google Sheets
- ✅ Sistema de autenticação Service Account
- ✅ Interface moderna com identidade Control
- ✅ Sistema responsivo
- ✅ 50+ campos de dados por cliente

## 🎨 Identidade Visual

- Cores Control Contabilidade
- Logo personalizado
- Interface profissional
- Responsivo para mobile

## 📞 Suporte

Control Contabilidade LTDA
- Endereço: Av. Desembargador Moreira, 2120, 16º Andar, Aldeota, Fortaleza/CE
- WhatsApp: (85) 3085-7555
- Site: https://www.controlcontabilidade.com/

---
© 2024 Control Contabilidade LTDA. Sistema desenvolvido para gestão interna de clientes.
