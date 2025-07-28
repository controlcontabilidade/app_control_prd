# 🏢 Control Contabilidade - Sistema de Gestão de Clientes

Sistema web para gestão de clientes da Control Contabilidade, com integração Google Sheets e sistema de fallback robusto.

## 🚀 Características Principais

- **💾 Multi-Storage**: Google Sheets (Service Account/OAuth) + JSON local + Sistema de Fallback
- **🔐 Autenticação**: Sistema de usuários com roles (admin/user) + fallback automático
- **📊 Dashboard**: Interface moderna com estatísticas e monitoramento em tempo real
- **🔧 Otimizado**: Configurado para Render 512MB com otimização agressiva de memória
- **📱 Responsivo**: Interface Bootstrap moderna e intuitiva
- **🛡️ Robusto**: Sistema de fallback automático quando Google Sheets não está disponível

---

## 🏗️ Arquitetura

### **Storage Services**
```
┌─ Google Sheets Service Account (Produção)
├─ Google Sheets OAuth (Desenvolvimento)  
├─ Local JSON Storage (Desenvolvimento)
└─ Render Fallback Service (Emergência)
```

### **Inicialização (Prioridade)**
1. **Service Account** → Produção (Render)
2. **OAuth** → Desenvolvimento local
3. **JSON Local** → Backup/desenvolvimento
4. **Fallback** → Emergência (quando auth falha)

---

## 📦 Instalação

### **Desenvolvimento Local**
```bash
# Clone do repositório
git clone <repo-url>
cd projeto_control_app_clientes

# Instalar dependências mínimas
pip install -r requirements.minimal.txt

# Configurar variáveis de ambiente
copy credentials_example.json credentials.json
# Editar credentials.json com suas credenciais

# Executar aplicação
python app.py
```

### **Deploy no Render**
```bash
# Configurar variáveis de ambiente no Render:
FLASK_ENV=production
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GOOGLE_SHEETS_ID=1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s
SECRET_KEY=sua-chave-secreta-super-forte
PYTHONOPTIMIZE=2
WEB_CONCURRENCY=1

# Build Command:
pip install --no-cache-dir -r requirements.txt

# Start Command:
gunicorn --config gunicorn.conf.py wsgi:application
```

---

## ⚙️ Otimizações de Memória

### **Para Render 512MB Plan**

- **1 Worker Gunicorn** (ao invés de 4)
- **25 Conexões max** por worker (ao invés de 1000)
- **100 Requests max** por worker (recicla automaticamente)
- **400MB Limite** por worker
- **Garbage Collection** agressivo
- **Lazy Loading** de serviços
- **Batch Processing** para operações pesadas

### **Estimativa de Economia**
- **Antes**: ~650MB (ultrapassava limite)
- **Depois**: ~260MB (50% do limite)
- **Economia**: ~390MB (60% redução)

---

## 🛡️ Sistema de Fallback

### **Quando Ativa**
- Falha na autenticação Google Sheets
- Service Account inválida ou expirada
- Google Sheets API indisponível
- Rede instável/timeout

### **Recursos no Modo Fallback**
- ✅ Interface funcional completa
- ✅ Dados de exemplo para demonstração
- ✅ Salvamento temporário local
- ✅ Alertas visuais de status
- ⚠️ Dados não sincronizam com Google Sheets

### **Identificação Visual**
- 🟡 Badge "MODO OFFLINE" no dashboard
- ⚠️ Alerta laranja no topo da página
- 📊 Sistema de status em tempo real

---

## 🔍 Monitoramento

### **APIs de Diagnóstico**
```bash
# Status de autenticação
GET /api/auth-status

# Status de memória  
GET /api/memory-status

# Health check geral
GET /test
```

### **Scripts de Monitoramento**
```bash
# Validação pré-deploy
python validate_deploy.py

# Monitoramento contínuo (requer requests)
python monitor_production.py https://sua-app.render.com

# Monitoramento de 2 horas com checks a cada 10min
python monitor_production.py https://sua-app.render.com monitor --interval 10 --hours 2
```

---

## 📊 Modelo de Dados

### **Cliente** (50+ campos)
```python
{
    "id": "uuid4",
    "nomeEmpresa": "Empresa LTDA",           # Obrigatório
    "cnpj": "12.345.678/0001-90",           # Obrigatório  
    "razaoSocialReceita": "Empresa LTDA",    # Obrigatório
    "ct": True,                             # Contabilidade
    "fs": False,                            # Folha Salarial
    "dp": True,                             # Departamento Pessoal
    "ativo": True,                          # Soft delete
    # ... mais 40+ campos
}
```

### **Usuário**
```python
{
    "id": "uuid4",
    "username": "admin",
    "password": "hash_bcrypt",
    "role": "admin|user",
    "active": True
}
```

---

## 🗂️ Estrutura do Código

```
app.py                    # 🎯 Aplicação principal Flask
wsgi.py                   # 🚀 Entry point WSGI (Gunicorn)
memory_optimizer.py       # 🧠 Otimizador de memória
gunicorn.conf.py         # ⚙️ Config Gunicorn otimizada
check_dependencies.py    # 📦 Loader de dependências

services/
├── google_sheets_service_account.py  # 🔐 Service Account (produção)
├── google_sheets_oauth_service.py    # 🔓 OAuth (desenvolvimento)
├── local_storage_service.py          # 💾 Armazenamento local
├── render_fallback_service.py        # 🛡️ Fallback emergência
├── user_service.py                   # 👤 Gestão usuários
├── import_service.py                 # 📊 Importação Excel
└── report_service.py                 # 📈 Relatórios

templates/
├── base.html                         # 🎨 Layout completo
├── base_simple.html                  # 🎨 Layout minimalista  
├── index_modern.html                 # 🏠 Dashboard moderno
├── client_form_modern.html           # 📝 Formulário cliente
└── client_view_modern.html           # 👁️ Visualização cliente

static/
├── css/                              # 🎨 Estilos CSS
├── js/                               # ⚡ JavaScript
└── images/                           # 🖼️ Imagens
```

---

## 🔧 Comandos Úteis

### **Desenvolvimento**
```bash
# Executar em modo debug
python app.py

# Testar imports
python check_dependencies.py

# Criar usuário admin
python create_admin_user.py

# Limpar dados corrompidos
python clean_corrupted.py
```

### **Diagnóstico**
```bash
# Verificar configuração deploy
python validate_deploy.py

# Debug template específico
python debug_template.py

# Análise de memória
python test_memory.py

# Verificar dependências render
python check_deploy_readiness.py
```

### **Google Sheets**
```bash
# Debug posições de dados
python debug_write_positions.py

# Migrar posições
python migrate_data_positions.py

# Analisar campos Onvio
python analyze_onvio_fields.py
```

---

## 🚨 Troubleshooting

### **Erro: "Serviço de autenticação indisponível"**
1. Verificar variável `GOOGLE_SERVICE_ACCOUNT_JSON` no Render
2. Validar JSON do Service Account
3. Confirmar permissões na planilha Google
4. Ver `TROUBLESHOOTING_RENDER.md` para guia completo

### **Erro: Memória insuficiente**
1. Verificar configuração Gunicorn (1 worker)
2. Monitorar `/api/memory-status`
3. Ativar otimizações de produção
4. Ver `OTIMIZACOES_MEMORIA.md`

### **Erro: Importação de dependências**
```bash
# Instalar dependências específicas
pip install pandas openpyxl  # Para import completo
pip install -r requirements.minimal.txt  # Para versão lite
```

---

## 📈 Performance

### **Tempos de Resposta**
- **Dashboard**: ~500ms
- **Listagem clientes**: ~800ms  
- **Formulário cliente**: ~300ms
- **API status**: ~100ms

### **Uso de Memória (Render 512MB)**
- **Inicialização**: ~80MB
- **Operação normal**: ~150-200MB
- **Pico (import Excel)**: ~250MB
- **Limite configurado**: 400MB

---

## 🔐 Segurança

- **Autenticação**: Flask sessions + bcrypt
- **Autorização**: Role-based (@admin_required, @login_required)
- **CSRF**: Flask-WTF protection
- **Sanitização**: Werkzeug secure_filename
- **Env vars**: Credenciais nunca em código

---

## 📚 Documentação Adicional

- `TROUBLESHOOTING_RENDER.md` - Guia completo de problemas no Render
- `OTIMIZACOES_MEMORIA.md` - Detalhes das otimizações de memória
- `ESTRUTURA_LIMPA.md` - Estrutura limpa do projeto
- `.github/copilot-instructions.md` - Instruções para AI

---

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch feature (`git checkout -b feature/nova-feature`)
3. Commit das mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para branch (`git push origin feature/nova-feature`)
5. Abrir Pull Request

---

## 📞 Suporte

- 📧 **Email**: suporte@controlcontabilidade.com
- 📱 **WhatsApp**: (11) 99999-9999
- 🌐 **Status**: https://sua-app.render.com/api/auth-status
- 📊 **Monitor**: https://sua-app.render.com/api/memory-status

---

## 📄 Licença

Este projeto está sob licença proprietária da Control Contabilidade.

---

**🏢 Control Contabilidade © 2024**
