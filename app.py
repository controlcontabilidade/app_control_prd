from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
from datetime import datetime
from functools import wraps
from services.google_sheets_service import GoogleSheetsService
from services.local_storage_service import LocalStorageService
from services.meeting_service import MeetingService
from services.user_service import UserService
from services.report_service import ReportService

# Tentar importar serviço completo, usar lite como fallback
try:
    from check_dependencies import get_available_import_service
    ImportService, IMPORT_SERVICE_TYPE = get_available_import_service()
    print(f"✅ Serviço de importação: {IMPORT_SERVICE_TYPE}")
except Exception as e:
    print(f"❌ Erro ao carregar serviço de importação: {e}")
    ImportService = None
    IMPORT_SERVICE_TYPE = "none"

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configurações para upload de arquivos - OTIMIZADO PARA MEMÓRIA
# Reduzido de 16MB para 8MB para economizar RAM no Render
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB máximo (otimização Render)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Configurações de produção para baixo consumo de memória
if os.environ.get('FLASK_ENV') == 'production':
    import gc
    gc.set_threshold(700, 10, 10)  # Garbage collection mais agressivo
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache de arquivos estáticos

# Criar pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Carregar variáveis de ambiente (.env local / Render)
from dotenv import load_dotenv
load_dotenv()  # Carrega .env apenas localmente (Render usa variáveis nativas)

# Carregar configurações (compatível com produção)
USE_GOOGLE_SHEETS = True
USE_OAUTH2 = False  # OAuth2 para autenticação manual  
USE_SERVICE_ACCOUNT = True  # Service Account para aplicações server-side (RECOMENDADO)
GOOGLE_SHEETS_API_KEY = os.environ.get('GOOGLE_SHEETS_API_KEY')
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')
GOOGLE_SHEETS_RANGE = 'Clientes!A:CZ'

print(f"🔧 Configurações:")
print(f"   USE_GOOGLE_SHEETS: {USE_GOOGLE_SHEETS}")
print(f"   USE_OAUTH2: {USE_OAUTH2}")
print(f"   USE_SERVICE_ACCOUNT: {USE_SERVICE_ACCOUNT}")
print(f"   API_KEY: {GOOGLE_SHEETS_API_KEY[:10]}...")
print(f"   SPREADSHEET_ID: {GOOGLE_SHEETS_ID}")

# Inicializar serviços
try:
    if USE_GOOGLE_SHEETS and GOOGLE_SHEETS_ID:
        if USE_SERVICE_ACCOUNT:
            print("🔐 Tentando usar Google Sheets com Service Account...")
            from services.google_sheets_service_account import GoogleSheetsServiceAccountService
            storage_service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
            meeting_service = MeetingService(GOOGLE_SHEETS_ID)
            print("✅ Google Sheets Service Account criado")
            print("✅ Usando Google Sheets Service Account como armazenamento")
        elif USE_OAUTH2:
            print("🔐 Tentando usar Google Sheets com OAuth2...")
            from services.google_sheets_oauth_service import GoogleSheetsOAuthService
            storage_service = GoogleSheetsOAuthService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
            meeting_service = None  # OAuth2 não suporta atas por enquanto
            print("✅ Google Sheets OAuth2 service criado")
            print("✅ Usando Google Sheets OAuth2 como armazenamento")
        else:
            print("📊 Tentando usar Google Sheets com método híbrido...")
            storage_service = GoogleSheetsService(GOOGLE_SHEETS_API_KEY, GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
            meeting_service = None  # Método híbrido não suporta atas por enquanto
            print("✅ Google Sheets service criado")
            print("✅ Usando Google Sheets híbrido como armazenamento")
    else:
        storage_service = LocalStorageService()
        meeting_service = None  # Local storage não suporta atas por enquanto
        print("⚠️ Usando armazenamento local")
except Exception as e:
    print(f"❌ Erro ao configurar Google Sheets: {e}")
    storage_service = LocalStorageService()
    meeting_service = None
    print("⚠️ Fallback para armazenamento local")

# Inicializar serviço de importação - OTIMIZADO PARA MEMÓRIA
try:
    if storage_service and ImportService:
        import_service = ImportService(storage_service)
        print(f"✅ Serviço de importação inicializado ({IMPORT_SERVICE_TYPE})")
    else:
        import_service = None
        print("⚠️ Serviço de importação não disponível (storage_service não inicializado ou ImportService não encontrado)")
except Exception as e:
    print(f"❌ Erro ao inicializar serviço de importação: {e}")
    import_service = None

# Inicializar serviços adicionais apenas se necessário - OTIMIZAÇÃO MEMÓRIA
try:
    # Lazy loading: só inicializa se vai usar
    user_service = UserService(GOOGLE_SHEETS_ID)
    print("✅ Serviço de usuários inicializado")
except Exception as e:
    print(f"❌ Erro ao inicializar serviço de usuários: {e}")
    user_service = None

try:
    # Lazy loading: só inicializa se vai usar
    report_service = ReportService(GOOGLE_SHEETS_ID)
    print("✅ Serviço de relatórios inicializado")
except Exception as e:
    print(f"❌ Erro ao inicializar serviço de relatórios: {e}")
    report_service = None

# Garbage collection após inicialização para liberar memória
if os.environ.get('FLASK_ENV') == 'production':
    import gc
    gc.collect()
    print("🧠 Memory cleanup pós-inicialização completo")

# Decorator para verificar autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔐 LOGIN_REQUIRED: Verificando sessão para função {f.__name__}")
        print(f"🔐 Dados da sessão: {dict(session)}")
        if 'user_id' not in session:
            print("❌ user_id não encontrado na sessão - Redirecionando para login")
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        print(f"✅ user_id encontrado: {session['user_id']} - Executando função {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

# Função para verificar se é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        user = user_service.get_user_by_id(session['user_id'])
        if not user or user.get('perfil', '').lower() != 'administrador':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"🔐 LOGIN: Método da requisição: {request.method}")
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"🔐 LOGIN: Tentativa de login para usuário: {username}")
        print(f"🔐 LOGIN: user_service disponível: {user_service is not None}")
        
        if user_service:
            print("🔐 LOGIN: Chamando authenticate_user...")
            user = user_service.authenticate_user(username, password)
            print(f"🔐 LOGIN: Resultado da autenticação: {user}")
            
            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['nome']
                session['user_perfil'] = user['perfil']
                print(f"🔐 LOGIN: Sessão criada - user_id: {session['user_id']}")
                flash(f'Bem-vindo(a), {user["nome"]}!', 'success')
                print("🔐 LOGIN: Redirecionando para index...")
                return redirect(url_for('index'))
            else:
                print("❌ LOGIN: Falha na autenticação")
                flash('Usuário ou senha incorretos.', 'error')
        else:
            print("❌ LOGIN: user_service não disponível")
            flash('Serviço de autenticação indisponível.', 'error')
    else:
        print("🔐 LOGIN: Exibindo formulário de login (GET)")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/users')
@admin_required
def users():
    if user_service:
        users_list = user_service.list_users()
        return render_template('users.html', users=users_list)
    else:
        flash('Serviço de usuários indisponível.', 'error')
        return redirect(url_for('index'))

@app.route('/create_user', methods=['POST'])
@admin_required
def create_user():
    if user_service:
        nome = request.form['nome']
        email = request.form['email']
        usuario = request.form['usuario']
        senha = request.form['senha']
        perfil = request.form['perfil']
        
        result = user_service.create_user(nome, email, usuario, senha, perfil)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de usuários indisponível.', 'error')
    
    return redirect(url_for('users'))

@app.route('/edit_user', methods=['POST'])
@admin_required
def edit_user():
    if user_service:
        user_id = request.form['user_id']
        nome = request.form['nome']
        email = request.form['email']
        usuario = request.form['usuario']
        perfil = request.form['perfil']
        ativo = request.form['ativo']
        nova_senha = request.form.get('nova_senha', '').strip()
        
        # Se nova senha foi fornecida, usa ela, senão None
        senha_param = nova_senha if nova_senha else None
        
        result = user_service.update_user(user_id, nome, email, usuario, perfil, ativo, senha_param)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de usuários indisponível.', 'error')
    
    return redirect(url_for('users'))

@app.route('/delete_user', methods=['POST'])
@admin_required
def delete_user():
    if user_service:
        user_id = request.form['user_id']
        
        result = user_service.delete_user(user_id)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de usuários indisponível.', 'error')
    
    return redirect(url_for('users'))

@app.route('/import')
@admin_required
def import_page():
    """Página para importar clientes de planilha Excel"""
    return render_template('import.html')

@app.route('/import/upload', methods=['POST'])
@admin_required
def upload_and_import():
    """Processa upload e importa arquivo Excel"""
    print("📤 === INICIANDO UPLOAD E IMPORTAÇÃO ===")
    
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('import_page'))
        
        file = request.files['file']
        
        # Verificar se arquivo tem nome
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('import_page'))
        
        # Verificar extensão do arquivo
        if not allowed_file(file.filename):
            flash('Apenas arquivos .xlsx e .xls são permitidos', 'error')
            return redirect(url_for('import_page'))
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"💾 Salvando arquivo: {file_path}")
        file.save(file_path)
        
        # Validar estrutura do arquivo
        if import_service and import_service.is_available():
            print("🔍 Validando estrutura do arquivo...")
            is_valid, validation_message = import_service.validate_excel_structure(file_path)
            
            if not is_valid:
                # Remover arquivo
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(f'Estrutura do arquivo inválida: {validation_message}', 'error')
                return redirect(url_for('import_page'))
            
            print("✅ Estrutura válida, iniciando importação...")
            
            # Executar importação
            sucessos, erros, lista_erros = import_service.import_from_excel(file_path)
            
            # Remover arquivo temporário
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Mostrar resultados
            if sucessos > 0:
                flash(f'✅ Importação concluída: {sucessos} clientes importados com sucesso!', 'success')
            
            if erros > 0:
                flash(f'⚠️ {erros} erro(s) encontrado(s)', 'warning')
                # Limitar erros mostrados para não sobrecarregar
                erros_mostrados = lista_erros[:5]
                for erro in erros_mostrados:
                    flash(f'❌ {erro}', 'error')
                
                if len(lista_erros) > 5:
                    flash(f'... e mais {len(lista_erros) - 5} erro(s)', 'error')
            
            if sucessos == 0 and erros == 0:
                flash('Nenhum cliente foi processado', 'warning')
        
        else:
            # Remover arquivo
            if os.path.exists(file_path):
                os.remove(file_path)
            flash('Serviço de importação não disponível. Pandas não está instalado.', 'error')
    
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        flash(f'Erro durante importação: {str(e)}', 'error')
        
        # Limpar arquivo se houver erro
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    
    return redirect(url_for('index'))

@app.route('/import/template')
@admin_required  
def download_template():
    """Baixa template Excel para importação"""
    try:
        # Verificar se openpyxl está disponível
        try:
            from openpyxl import Workbook
            import io
        except ImportError as e:
            print(f"❌ OpenPyXL não encontrado: {e}")
            # Fallback: criar template CSV
            return create_simple_template()
        
        print("✅ OpenPyXL importado com sucesso")
        
        # Criar workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Clientes"
        
        # Cabeçalhos SIGEC - 8 Blocos Organizados
        headers = [
            # Bloco 1: Informações da Pessoa Jurídica (13 campos obrigatórios)
            'NOME DA EMPRESA', 'RAZÃO SOCIAL NA RECEITA', 'NOME FANTASIA NA RECEITA', 
            'CNPJ', 'PERFIL', 'INSCRIÇÃO ESTADUAL', 'INSCRIÇÃO MUNICIPAL', 
            'ESTADO', 'CIDADE', 'REGIME FEDERAL', 'REGIME ESTADUAL', 'SEGMENTO', 'ATIVIDADE',
            
            # Bloco 2: Serviços Prestados pela Control (12 campos)
            'SERVIÇO CT', 'SERVIÇO FS', 'SERVIÇO DP', 'SERVIÇO BPO FINANCEIRO', 
            'RESPONSÁVEL PELOS SERVIÇOS', 'DATA INÍCIO DOS SERVIÇOS',
            'CÓDIGO FORTES CT', 'CÓDIGO FORTES FS', 'CÓDIGO FORTES PS', 
            'CÓDIGO DOMÍNIO', 'SISTEMA UTILIZADO', 'MÓDULO SPED TRIER',
            
            # Bloco 3: Quadro Societário (6 campos)
            'SÓCIO 1 NOME', 'SÓCIO 1 CPF', 'SÓCIO 1 DATA NASCIMENTO', 
            'SÓCIO 1 ADMINISTRADOR', 'SÓCIO 1 COTAS', 'SÓCIO 1 RESPONSÁVEL LEGAL',
            
            # Bloco 4: Contatos (10 campos)
            'TELEFONE FIXO', 'TELEFONE CELULAR', 'WHATSAPP', 
            'EMAIL PRINCIPAL', 'EMAIL SECUNDÁRIO', 'RESPONSÁVEL IMEDIATO',
            'EMAILS DOS SÓCIOS', 'CONTATO CONTADOR', 'TELEFONE CONTADOR', 'EMAIL CONTADOR',
            
            # Bloco 5: Sistemas e Acessos (7 campos)
            'SISTEMA PRINCIPAL', 'VERSÃO DO SISTEMA', 'CÓDIGO ACESSO SIMPLES NACIONAL',
            'CPF/CNPJ PARA ACESSO', 'PORTAL CLIENTE ATIVO', 'INTEGRAÇÃO DOMÍNIO', 'SISTEMA ONVIO',
            
            # Bloco 6: Senhas e Credenciais (20 campos)
            'ACESSO ISS', 'SENHA ISS', 'ACESSO SEFIN', 'SENHA SEFIN', 
            'ACESSO SEUMA', 'SENHA SEUMA', 'ACESSO EMPWEB', 'SENHA EMPWEB',
            'ACESSO FAP/INSS', 'SENHA FAP/INSS', 'ACESSO CRF', 'SENHA CRF',
            'EMAIL GESTOR', 'SENHA EMAIL GESTOR', 'ANVISA GESTOR', 'ANVISA EMPRESA',
            'ACESSO IBAMA', 'SENHA IBAMA', 'ACESSO SEMACE', 'SENHA SEMACE',
            
            # Bloco 7: Procurações (12 campos)
            'PROCURAÇÃO RFB', 'DATA PROCURAÇÃO RFB', 'PROCURAÇÃO RECEITA ESTADUAL', 'DATA PROCURAÇÃO RC',
            'PROCURAÇÃO CAIXA ECONÔMICA', 'DATA PROCURAÇÃO CX', 'PROCURAÇÃO PREVIDÊNCIA SOCIAL', 'DATA PROCURAÇÃO SW',
            'PROCURAÇÃO MUNICIPAL', 'DATA PROCURAÇÃO MUNICIPAL', 'OUTRAS PROCURAÇÕES', 'OBSERVAÇÕES PROCURAÇÕES',
            
            # Bloco 8: Observações e Dados Adicionais (12 campos)
            'OBSERVAÇÕES GERAIS', 'TAREFAS VINCULADAS', 'STATUS DO CLIENTE',
            'ÚLTIMA ATUALIZAÇÃO', 'RESPONSÁVEL ATUALIZAÇÃO', 'PRIORIDADE',
            'TAGS/CATEGORIAS', 'HISTÓRICO DE ALTERAÇÕES'
        ]
        
        # Dados de exemplo SIGEC
        example_data = [
            # Bloco 1: Informações da Pessoa Jurídica
            'EMPRESA EXEMPLO LTDA', 'EMPRESA EXEMPLO LTDA', 'Exemplo Empresa', 
            '12.345.678/0001-99', 'LUCRO PRESUMIDO', '123456789', '987654321', 
            'CE', 'FORTALEZA', 'LUCRO PRESUMIDO', 'NORMAL', 'COMÉRCIO', 'VENDA DE PRODUTOS',
            
            # Bloco 2: Serviços Prestados pela Control
            'SIM', 'SIM', 'NÃO', 'SIM', 
            'João da Silva', '2024-01-01',
            '12345', '67890', '', 
            'DOM123', 'FORTES', 'COMPLETO',
            
            # Bloco 3: Quadro Societário
            'JOÃO DA SILVA', '123.456.789-00', '1980-01-01', 
            'SIM', '100%', 'SIM',
            
            # Bloco 4: Contatos
            '(85) 3333-4444', '(85) 99999-8888', '(85) 99999-8888', 
            'teste@empresa.com', 'contato@empresa.com', 'Maria Santos',
            'joao@empresa.com', 'Contador ABC', '(85) 3333-5555', 'contador@abc.com',
            
            # Bloco 5: Sistemas e Acessos
            'FORTES', '2024.1', 'SN123456',
            '12345678000190', 'SIM', 'SIM', 'NÃO',
            
            # Bloco 6: Senhas e Credenciais
            'usuario123', 'senha123', 'sefin123', 'senha456', 
            'seuma123', 'senha789', 'empweb123', 'senha999',
            'fap123', 'senha000', 'crf123', 'senha111',
            'gestor@empresa.com', 'senha222', 'anvisa123', 'empresa123',
            'ibama123', 'senha333', 'semace123', 'senha444',
            
            # Bloco 7: Procurações
            'SIM', '2024-01-15', 'SIM', '2024-01-20',
            'NÃO', '', 'SIM', '2024-02-01',
            'SIM', '2024-02-05', 'Procuração JUCEC', 'Todas válidas',
            
            # Bloco 8: Observações e Dados Adicionais
            'Cliente em dia com obrigações', '5', 'ATIVO',
            '2024-01-01', 'Sistema', 'ALTA',
            'VIP,PREMIUM', 'Cliente cadastrado via sistema'
        ]
        
        # Escrever cabeçalhos
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Escrever exemplo
        for col, value in enumerate(example_data, 1):
            ws.cell(row=2, column=col, value=value)
        
        # Salvar em buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        template_filename = f'template_importacao_clientes_{timestamp}.xlsx'
        
        from flask import send_file
        
        return send_file(
            buffer,
            as_attachment=True, 
            download_name=template_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Erro ao gerar template: {e}")
        flash(f'Erro ao gerar template: {str(e)}', 'error')
        return redirect(url_for('import_page'))

def create_simple_template():
    """Cria template simples sem pandas como fallback"""
    try:
        import csv
        import io
        from flask import Response
        
        # Dados do template em formato CSV
        csv_data = [
            ['NOME DA EMPRESA', 'CT', 'FS', 'DP', 'COD. FORTES CT', 'COD. FORTES FS', 'COD. FORTES PS', 'COD. DOMÍNIO', 'SISTEMA UTILIZADO', 'MÓDULO SPED TRIER', 'RAZÃO SOCIAL NA RECEITA', 'NOME FANTASIA NA RECEITA', 'CNPJ', 'INSC. EST.', 'INSC. MUN.', 'SEGMENTO', 'ATIVIDADE', 'TRIBUTAÇÃO', 'PERFIL', 'CIDADE', 'DONO / RESP.', 'COD. ACESSO SIMPLES', 'CPF OU CNPJ', 'ACESSO ISS', 'ACESSO SEFIN', 'ACESSO SEUMA', 'ACESSO EMP. WEB', 'SENHA EMP. WEB', 'ACESSO FAP/INSS', 'ACESSO CRF', 'EMAIL GESTOR', 'ANVISA GESTOR', 'ANVISA EMPRESA', 'ACESSO IBAMA', 'ACESSO SEMACE', 'SENHA SEMACE', 'PROC. RC', 'PROC. CX', 'PROC. SW', 'MÊS/ANO DE  INÍCIO', 'RESPONSÁVEL IMEDIATO', 'TELEFONE FIXO', 'TELEFONE CELULAR', 'E-MAILS', 'SÓCIO', 'SÓCIO.1', 'SÓCIO.2', 'SÓCIO.3'],
            ['Exemplo Empresa Ltda', 'SIM', 'NAO', 'NAO', '123', '456', '789', '999', 'Sistema XYZ', 'Módulo ABC', 'EXEMPLO EMPRESA LTDA', 'Exemplo Empresa', '12.345.678/0001-99', '123456789', '987654321', 'COMÉRCIO', 'VAREJO', 'SIMPLES', 'A', 'FORTALEZA', 'João Silva', 'ABC123', '123.456.789-00', 'usuario123', 'senha123', 'acesso123', 'web123', 'senha456', 'fap123', 'crf123', 'gestor@empresa.com', 'anvisa123', 'empresa123', 'ibama123', 'semace123', 'senha789', 'OK', 'OK', 'OK', '01/2024', 'João Silva', '(85) 3333-4444', '(85) 99999-8888', 'contato@empresa.com', 'João Silva', 'Maria Silva', '', '']
        ]
        
        # Criar CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        
        # Converter para bytes
        csv_bytes = output.getvalue().encode('utf-8-sig')  # BOM para Excel
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'template_importacao_clientes_{timestamp}.csv'
        
        return Response(
            csv_bytes,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        print(f"❌ Erro ao criar template CSV: {e}")
        flash('Erro ao gerar template. Crie manualmente um arquivo Excel com as colunas necessárias.', 'error')
        return redirect(url_for('import_page'))

# ==================== ROTAS DE RELATÓRIOS ====================

@app.route('/test-embed-auth')
def test_embed_auth():
    """Página de teste para embedding com autenticação"""
    with open('test_embed_auth.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/test-direct-embed')
def test_direct_embed():
    """Página de teste direto para iframe"""
    with open('test_direct_embed.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/debug-sistema-real')
def debug_sistema_real():
    """Página de debug que simula o sistema real"""
    with open('debug_sistema_real.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/reports')
@login_required
def reports():
    """Página de visualização de relatórios para usuários"""
    if report_service:
        # Busca apenas relatórios ativos
        reports_data = report_service.list_reports(only_active=True)
        username = session.get('user_name', '')
        
        print(f"🔍 Debug: {len(reports_data)} relatórios encontrados (apenas ativos)")
        
        # Filtrar relatórios que o usuário tem acesso
        accessible_reports = []
        for report in reports_data:
            print(f"🔍 Debug: Relatório '{report.get('nome')}' - Ativo: '{report.get('ativo')}'")
            if report_service.user_has_access(report, username):
                accessible_reports.append(report)
        
        print(f"🔍 Debug: {len(accessible_reports)} relatórios acessíveis para '{username}'")
        return render_template('reports.html', reports=accessible_reports)
    else:
        flash('Serviço de relatórios indisponível.', 'error')
        return render_template('reports.html', reports=[])

@app.route('/manage_reports')
@admin_required
def manage_reports():
    """Página de gerenciamento de relatórios (somente admin)"""
    if report_service:
        reports_data = report_service.list_reports()
        return render_template('manage_reports.html', reports=reports_data)
    else:
        flash('Serviço de relatórios indisponível.', 'error')
        return render_template('manage_reports.html', reports=[])

@app.route('/create_report', methods=['POST'])
@admin_required
def create_report():
    """Criar novo relatório"""
    if report_service:
        nome = request.form['nome']
        descricao = request.form['descricao']
        link = request.form['link']
        
        # Corrige conversão do checkbox 'ativo'
        # Se múltiplos valores com mesmo nome, getlist retorna uma lista
        ativo_values = request.form.getlist('ativo')
        print(f"🔍 Debug checkbox ativo: request.form.getlist('ativo') = {ativo_values}")
        
        # Se 'on' estiver na lista, checkbox foi marcado
        ativo = 'Sim' if 'on' in ativo_values else 'Não'
        print(f"🔍 Debug conversão final: {ativo_values} -> '{ativo}'")
        print(f"🔍 Debug form completo: {dict(request.form)}")
        
        ordem = int(request.form.get('ordem', 0))
        usuarios_autorizados = request.form.get('usuarios_autorizados', 'todos')
        
        # Obter usuário da sessão
        criado_por = session.get('user_name', 'Desconhecido')
        
        result = report_service.create_report(nome, descricao, link, ativo, ordem, criado_por, usuarios_autorizados)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de relatórios indisponível.', 'error')
    
    return redirect(url_for('manage_reports'))

@app.route('/edit_report', methods=['POST'])
@admin_required
def edit_report():
    """Editar relatório existente"""
    if report_service:
        report_id = request.form['report_id']
        nome = request.form['nome']
        descricao = request.form['descricao']
        link = request.form['link']
        
        # Corrige conversão do checkbox 'ativo' na edição
        # Se múltiplos valores com mesmo nome, getlist retorna uma lista
        ativo_values = request.form.getlist('ativo')
        print(f"🔍 Debug checkbox ativo (edição): request.form.getlist('ativo') = {ativo_values}")
        
        # Se 'on' estiver na lista, checkbox foi marcado
        ativo = 'Sim' if 'on' in ativo_values else 'Não'
        print(f"🔍 Debug conversão final (edição): {ativo_values} -> '{ativo}'")
        print(f"🔍 Debug form completo (edição): {dict(request.form)}")
        
        ordem = int(request.form.get('ordem', 0))
        usuarios_autorizados = request.form.get('usuarios_autorizados', 'todos')
        
        result = report_service.update_report(report_id, nome, descricao, link, ativo, ordem, usuarios_autorizados)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de relatórios indisponível.', 'error')
    
    return redirect(url_for('manage_reports'))

@app.route('/delete_report', methods=['POST'])
@admin_required
def delete_report():
    """Deletar relatório"""
    if report_service:
        report_id = request.form['report_id']
        
        result = report_service.delete_report(report_id)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('Serviço de relatórios indisponível.', 'error')
    
    return redirect(url_for('manage_reports'))

def calculate_dashboard_stats(clients):
    """Calcula estatísticas para o dashboard baseado nos dados SIGEC"""
    stats = {
        'total_clientes': len(clients),
        'clientes_ativos': 0,
        'empresas': 0,
        'domesticas': 0,
        'mei': 0,
        'simples_nacional': 0,
        'lucro_presumido': 0,
        'lucro_real': 0,
        'ct': 0,
        'fs': 0,
        'dp': 0,
        'bpo': 0
    }
    
    for client in clients:
        # Contadores básicos
        if client.get('ativo', True):
            stats['clientes_ativos'] += 1
        
        # Serviços
        if client.get('ct', False):
            stats['ct'] += 1
        if client.get('fs', False):
            stats['fs'] += 1
        if client.get('dp', False):
            stats['dp'] += 1
        if client.get('bpoFinanceiro', False):
            stats['bpo'] += 1
        
        # Categorização por regime federal (SIGEC)
        regime = str(client.get('regimeFederal', '')).upper().strip()
        perfil = str(client.get('perfil', '')).upper().strip()
        
        # MEI - Microempreendedor Individual
        if 'MEI' in regime or 'MICROEMPRESARIO' in perfil or 'INDIVIDUAL' in perfil:
            stats['mei'] += 1
        # Simples Nacional
        elif 'SIMPLES' in regime or 'SN' in regime:
            stats['simples_nacional'] += 1
        # Lucro Presumido
        elif 'PRESUMIDO' in regime or 'LP' in regime:
            stats['lucro_presumido'] += 1
        # Lucro Real
        elif 'REAL' in regime or 'LR' in regime:
            stats['lucro_real'] += 1
        # Domésticas - identificar por perfil ou atividade
        elif 'DOMESTICA' in perfil or 'EMPREGADA' in perfil:
            stats['domesticas'] += 1
        else:
            # Demais casos consideramos como empresas
            stats['empresas'] += 1
    
    return stats

@app.route('/api/users')
@admin_required
def get_users():
    """API para obter lista de usuários disponíveis"""
    if report_service:
        users = report_service.get_available_users()
        return jsonify({'users': users})
    else:
        return jsonify({'users': ['todos', 'admin', 'usuario']})

@app.route('/')
@login_required
def index():
    print("🔍 === ROTA INDEX CHAMADA ===")
    try:
        print("📊 Tentando carregar clientes...")
        
        # OTIMIZAÇÃO MEMÓRIA: Carregamento lazy e limite de dados
        clients = storage_service.get_clients()
        
        # Limitar quantidade de clientes carregados em produção para economizar RAM
        if os.environ.get('FLASK_ENV') == 'production' and len(clients) > 100:
            clients = clients[:100]  # Mostrar apenas primeiros 100 clientes
            print(f"🧠 Limitado para 100 clientes (otimização memória)")
            
        print(f"✅ {len(clients)} clientes carregados")
        
        # OTIMIZAÇÃO MEMÓRIA: Calcular stats apenas se necessário
        try:
            stats = calculate_dashboard_stats(clients)
            print(f"📈 Estatísticas calculadas")
        except Exception as stats_error:
            print(f"⚠️ Erro ao calcular stats: {stats_error}")
            stats = {
                'total_clientes': len(clients), 'clientes_ativos': len(clients), 
                'empresas': 0, 'domesticas': 0, 'mei': 0, 'simples_nacional': 0,
                'lucro_presumido': 0, 'lucro_real': 0,
                'ct': 0, 'fs': 0, 'dp': 0, 'bpo': 0
            }
        
        # Garbage collection após processamento de dados
        if os.environ.get('FLASK_ENV') == 'production':
            import gc
            gc.collect()
        
        # Usar template moderno com estatísticas
        return render_template('index_modern.html', clients=clients, stats=stats)
        
    except Exception as e:
        print(f"❌ ERRO na rota index: {str(e)}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        flash(f'Erro ao carregar clientes: {str(e)}', 'error')
        
        # Em caso de erro, criar stats vazias
        stats = {
            'total_clientes': 0, 'clientes_ativos': 0, 'empresas': 0,
            'domesticas': 0, 'mei': 0, 'simples_nacional': 0,
            'lucro_presumido': 0, 'lucro_real': 0,
            'ct': 0, 'fs': 0, 'dp': 0, 'bpo': 0
        }
        return render_template('index_modern.html', clients=[], stats=stats)

@app.route('/test')
@login_required
def test():
    """Rota de teste simples"""
    return """
    <html>
    <head>
        <title>Teste</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .container { background: white; padding: 20px; border-radius: 8px; }
            h1 { color: #333; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Aplicação Flask Funcionando!</h1>
            <p class="success">✅ Servidor está respondendo corretamente</p>
            <p>📊 Google Sheets configurado</p>
            <p>🔧 Sistema híbrido ativo</p>
            <a href="/">← Voltar para página principal</a>
        </div>
    </body>
    </html>
    """

@app.route('/client/<client_id>')
@login_required
def view_client(client_id):
    try:
        client = storage_service.get_client(client_id)
        if client:
            return render_template('client_view_modern.html', client=client)
        else:
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/client/new')
@login_required
def new_client():
    return render_template('client_form_modern.html')

@app.route('/client/<client_id>/edit')
@login_required
def edit_client(client_id):
    try:
        print(f"🔍 [EDIT] ===== CARREGANDO CLIENTE PARA EDIÇÃO =====")
        print(f"🔍 [EDIT] ID solicitado: '{client_id}'")
        
        client = storage_service.get_client(client_id)
        print(f"🔍 [EDIT] Cliente carregado: {client is not None}")
        
        if client:
            print(f"🔍 [EDIT] Nome do cliente: {client.get('nomeEmpresa')}")
            print(f"🔍 [EDIT] ID do cliente retornado: '{client.get('id')}'")
            print(f"🔍 [EDIT] Tipo do ID: {type(client.get('id'))}")
            print(f"🔍 [EDIT] Dados principais: {list(client.keys())[:10]}")
            
            # Garantir que o ID está correto
            if not client.get('id'):
                print(f"⚠️ [EDIT] Cliente não tem ID! Forçando ID = {client_id}")
                client['id'] = client_id
            
            return render_template('client_form_modern.html', client=client)
        else:
            print(f"❌ [EDIT] Cliente {client_id} não encontrado!")
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"❌ [EDIT] Erro ao carregar cliente: {str(e)}")
        import traceback
        print(f"❌ [EDIT] Traceback: {traceback.format_exc()}")
        flash(f'Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/client', methods=['POST'])
@login_required
def save_client():
    print("🔍 === FUNÇÃO SAVE_CLIENT CHAMADA ===")
    print(f"🔍 Método da requisição: {request.method}")
    print(f"🔍 Dados do form: {dict(request.form)}")
    
    # CORREÇÃO DUPLICAÇÃO: Verificar ID primeiro
    client_id = request.form.get('id', '').strip()
    print(f"🔍 ID do cliente (raw): '{request.form.get('id')}'")
    print(f"🔍 ID do cliente (processed): '{client_id}'")
    print(f"🔍 Operação: {'EDIÇÃO' if client_id else 'CRIAÇÃO'}")
    
    try:
        # Validar dados obrigatórios do Bloco 1
        nome_empresa = request.form.get('nomeEmpresa', '').strip()
        razao_social = request.form.get('razaoSocialReceita', '').strip()
        nome_fantasia = request.form.get('nomeFantasiaReceita', '').strip()
        cpf_cnpj = request.form.get('cpfCnpj', '').strip()
        perfil = request.form.get('perfil', '').strip()
        insc_est = request.form.get('inscEst', '').strip()
        insc_mun = request.form.get('inscMun', '').strip()
        estado = request.form.get('estado', '').strip()
        cidade = request.form.get('cidade', '').strip()
        regime_federal = request.form.get('regimeFederal', '').strip()
        regime_estadual = request.form.get('regimeEstadual', '').strip()
        segmento = request.form.get('segmento', '').strip()
        atividade = request.form.get('atividade', '').strip()
        
        # Validações obrigatórias
        if not nome_empresa:
            flash('Nome da empresa é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not razao_social:
            flash('Razão Social (Receita) é obrigatória!', 'error')
            return redirect(url_for('index'))
        if not nome_fantasia:
            flash('Nome Fantasia (Receita) é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not cpf_cnpj:
            flash('CPF/CNPJ é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not perfil:
            flash('Perfil é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not insc_est:
            flash('Inscrição Estadual é obrigatória!', 'error')
            return redirect(url_for('index'))
        if not insc_mun:
            flash('Inscrição Municipal é obrigatória!', 'error')
            return redirect(url_for('index'))
        if not estado:
            flash('Estado é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not cidade:
            flash('Cidade é obrigatória!', 'error')
            return redirect(url_for('index'))
        if not regime_federal:
            flash('Regime Federal é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not regime_estadual:
            flash('Regime Estadual é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not segmento:
            flash('Segmento é obrigatório!', 'error')
            return redirect(url_for('index'))
        if not atividade:
            flash('Atividade Principal é obrigatória!', 'error')
            return redirect(url_for('index'))
        
        print(f"🔍 Nome da empresa: {nome_empresa}")
        
        # CORREÇÃO DUPLICAÇÃO: Garantir que o ID seja passado corretamente
        # Dados básicos obrigatórios - Bloco 1
        client_data = {
            'id': client_id if client_id else None,  # FIXADO: usar variável processada
            
            # Bloco 1: Informações da Pessoa Física / Jurídica
            'nomeEmpresa': nome_empresa,
            'razaoSocialReceita': razao_social,
            'nomeFantasiaReceita': nome_fantasia,
            'cpfCnpj': cpf_cnpj,
            'cnpj': cpf_cnpj,  # Manter compatibilidade com campo antigo
            'perfil': perfil,
            'inscEst': insc_est,
            'inscMun': insc_mun,
            'estado': estado,
            'cidade': cidade,
            'regimeFederal': regime_federal,
            'tributacao': regime_federal,  # Manter compatibilidade com campo antigo
            'regimeEstadual': regime_estadual,
            'segmento': segmento,
            'atividade': atividade,
            
            # Bloco 2: Serviços Prestados pela Control
            'bpoFinanceiro': request.form.get('bpoFinanceiro') == 'on',
            'ct': request.form.get('ct') == 'on',
            'fs': request.form.get('fs') == 'on',
            'dp': request.form.get('dp') == 'on',
            'dataInicioServicos': request.form.get('dataInicioServicos', ''),
            'responsavelServicos': request.form.get('responsavelServicos', ''),
            
            # Códigos dos Sistemas (Bloco 2)
            'codFortesCt': request.form.get('codFortesCt', ''),
            'codFortesFs': request.form.get('codFortesFs', ''),
            'codFortesPs': request.form.get('codFortesPs', ''),
            'codDominio': request.form.get('codDominio', ''),
            'sistemaUtilizado': request.form.get('sistemaUtilizado', ''),
            'moduloSpedTrier': request.form.get('moduloSpedTrier', ''),
            
            # Bloco 4: Contatos
            'telefoneFixo': request.form.get('telefoneFixo', ''),
            'telefoneCelular': request.form.get('telefoneCelular', ''),
            'whatsapp': request.form.get('whatsapp', ''),
            'emailPrincipal': request.form.get('emailPrincipal', ''),
            'emailSecundario': request.form.get('emailSecundario', ''),
            'responsavelImediato': request.form.get('responsavelImediato', ''),
            'emailsSocios': request.form.get('emailsSocios', ''),
            'contatoContador': request.form.get('contatoContador', ''),
            'telefoneContador': request.form.get('telefoneContador', ''),
            'emailContador': request.form.get('emailContador', ''),
            
            # Bloco 5: Sistemas e Acessos
            'sistemaPrincipal': request.form.get('sistemaPrincipal', ''),
            'versaoSistema': request.form.get('versaoSistema', ''),
            'codAcessoSimples': request.form.get('codAcessoSimples', ''),
            'cpfCnpjAcesso': request.form.get('cpfCnpjAcesso', ''),
            'portalClienteAtivo': request.form.get('portalClienteAtivo') == 'on',
            'integracaoDominio': request.form.get('integracaoDominio') == 'on',
            'sistemaOnvio': request.form.get('sistemaOnvio') == 'on',
            
            # Bloco 6: Senhas e Credenciais
            'acessoIss': request.form.get('acessoIss', ''),
            'senhaIss': request.form.get('senhaIss', ''),
            'acessoSefin': request.form.get('acessoSefin', ''),
            'senhaSefin': request.form.get('senhaSefin', ''),
            'acessoSeuma': request.form.get('acessoSeuma', ''),
            'senhaSeuma': request.form.get('senhaSeuma', ''),
            'acessoEmpWeb': request.form.get('acessoEmpWeb', ''),
            'senhaEmpWeb': request.form.get('senhaEmpWeb', ''),
            'acessoFapInss': request.form.get('acessoFapInss', ''),
            'senhaFapInss': request.form.get('senhaFapInss', ''),
            'acessoCrf': request.form.get('acessoCrf', ''),
            'senhaCrf': request.form.get('senhaCrf', ''),
            'emailGestor': request.form.get('emailGestor', ''),
            'senhaEmailGestor': request.form.get('senhaEmailGestor', ''),
            'anvisaGestor': request.form.get('anvisaGestor', ''),
            'anvisaEmpresa': request.form.get('anvisaEmpresa', ''),
            'acessoIbama': request.form.get('acessoIbama', ''),
            'senhaIbama': request.form.get('senhaIbama', ''),
            'acessoSemace': request.form.get('acessoSemace', ''),
            'senhaSemace': request.form.get('senhaSemace', ''),
            
            # Bloco 7: Procurações
            'procRfb': request.form.get('procRfb') == 'on',
            'procRfbData': request.form.get('procRfbData', ''),
            'procRc': request.form.get('procRc') == 'on',
            'procRcData': request.form.get('procRcData', ''),
            'procCx': request.form.get('procCx') == 'on',
            'procCxData': request.form.get('procCxData', ''),
            'procSw': request.form.get('procSw') == 'on',
            'procSwData': request.form.get('procSwData', ''),
            'procMunicipal': request.form.get('procMunicipal') == 'on',
            'procMunicipalData': request.form.get('procMunicipalData', ''),
            'outrasProc': request.form.get('outrasProc', ''),
            'obsProcuracoes': request.form.get('obsProcuracoes', ''),
            
            # Bloco 8: Observações e Dados Adicionais
            'observacoesGerais': request.form.get('observacoesGerais', ''),
            'tarefasVinculadas': int(request.form.get('tarefasVinculadas', '0') or '0'),
            'dataInicioServicos': request.form.get('dataInicioServicos', ''),
            'statusCliente': request.form.get('statusCliente', 'ativo'),
            'ultimaAtualizacao': datetime.now().isoformat(),
            'responsavelAtualizacao': session.get('usuario', ''),
            'prioridadeCliente': request.form.get('prioridadeCliente', 'normal'),
            'tagsCliente': request.form.get('tagsCliente', ''),
            'historicoAlteracoes': request.form.get('historicoAlteracoes', ''),
            
            # Campos de compatibilidade (manter existentes)
            'donoResp': request.form.get('responsavelServicos', ''),
            'mesAnoInicio': request.form.get('dataInicioServicos', ''),
            
            # Status e configurações
            'ativo': request.form.get('ativo') == 'on',
        }
        
        # Processar sócios dinamicamente do Bloco 3
        for key in request.form.keys():
            if key.startswith('socio') and '_' in key:
                # Extrair número do sócio e tipo do campo (ex: socio1_nome -> 1, nome)
                parts = key.split('_', 1)
                if len(parts) == 2:
                    value = request.form.get(key, '').strip()
                    if value:  # Só incluir se tiver valor
                        client_data[key] = value
        
        # CORREÇÃO DUPLICAÇÃO: Melhor controle de criação vs edição
        if not client_data.get('id'):
            print("🔍 NOVO CLIENTE: Definindo criadoEm")
            client_data['criadoEm'] = datetime.now().isoformat()
        else:
            print(f"🔍 EDITANDO CLIENTE: ID = {client_data['id']}")
            # Para edição, sempre manter o ultimaAtualizacao
            client_data['ultimaAtualizacao'] = datetime.now().isoformat()
        
        print(f"🔍 Cliente preparado: {client_data.get('nomeEmpresa')}")
        print(f"🔍 ID final do cliente: {client_data.get('id')}")
        print(f"🔍 Tipo de operação: {'EDIÇÃO' if client_data.get('id') else 'CRIAÇÃO'}")
        print("🔍 Verificando conexão com storage_service...")
        
        if not storage_service:
            print("❌ storage_service não está disponível!")
            flash('Erro: Serviço de armazenamento não disponível', 'error')
            return redirect(url_for('index'))
        
        print("🔍 Chamando storage_service.save_client...")
        
        success = storage_service.save_client(client_data)
        
        print(f"🔍 Resultado do salvamento: {success}")
        
        if success:
            if client_data.get('id'):
                flash('Cliente atualizado com sucesso!', 'success')
                print("✅ Flash message de atualização adicionada")
            else:
                flash('Cliente criado com sucesso!', 'success')
                print("✅ Flash message de criação adicionada")
        else:
            flash('Erro ao salvar cliente', 'error')
            print("❌ Flash message de erro adicionada")
            
    except Exception as e:
        print(f"❌ EXCEÇÃO na função save_client: {str(e)}")
        print(f"❌ Tipo da exceção: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        flash(f'Erro ao salvar cliente: {str(e)}', 'error')
    
    print("🔍 Redirecionando para index...")
    return redirect(url_for('index'))

@app.route('/client/<client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    try:
        # Verificar se o usuário é administrador
        if not session.get('user_perfil') or session.get('user_perfil').lower() != 'administrador':
            flash('Acesso negado. Apenas administradores podem excluir clientes.', 'danger')
            return redirect(url_for('view_client', client_id=client_id))
        
        success = storage_service.delete_client(client_id)
        if success:
            flash('Cliente excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir cliente', 'error')
    except Exception as e:
        flash(f'Erro ao excluir cliente: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/client/<client_id>/meeting')
@login_required
def register_meeting(client_id):
    """Página para registrar ata de reunião com cliente"""
    try:
        client = storage_service.get_client(client_id)
        if client:
            return render_template('meeting_form.html', client=client)
        else:
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/client/<client_id>/meeting', methods=['POST'])
@login_required
def save_meeting(client_id):
    """Salvar ata de reunião"""
    try:
        # Busca o nome do cliente
        client = storage_service.get_client(client_id)
        client_name = client.get('nomeFantasiaReceita') or client.get('nomeEmpresa') if client else 'Cliente'
        
        meeting_data = {
            'client_id': client_id,
            'client_name': client_name,
            'date': request.form.get('meeting_date'),
            'time': request.form.get('meeting_time'),
            'participants': request.form.get('participants'),
            'topics': request.form.get('topics'),
            'decisions': request.form.get('decisions'),
            'next_steps': request.form.get('next_steps')
        }
        
        # Salva usando o serviço de atas
        if meeting_service:
            meeting_id = meeting_service.save_meeting(meeting_data)
            if meeting_id:
                flash(f'✅ Ata de reunião {meeting_id} registrada com sucesso para {client_name}!', 'success')
            else:
                flash('❌ Erro ao salvar ata de reunião', 'error')
        else:
            # Fallback - salva localmente (simulação)
            flash(f'⚠️ Ata de reunião registrada localmente para {client_name} (funcionalidade limitada)', 'warning')
        
    except Exception as e:
        flash(f'❌ Erro ao salvar ata de reunião: {str(e)}', 'error')
        print(f"❌ Erro detalhado: {e}")
    
    return redirect(url_for('index'))

@app.route('/client/<client_id>/meetings')
@login_required
def view_client_meetings(client_id):
    """Visualizar todas as atas de um cliente"""
    try:
        client = storage_service.get_client(client_id)
        if not client:
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('index'))
        
        meetings = []
        if meeting_service:
            meetings = meeting_service.get_client_meetings(client_id)
        
        return render_template('client_meetings.html', client=client, meetings=meetings)
        
    except Exception as e:
        flash(f'Erro ao carregar atas do cliente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/meetings')
@login_required
def all_meetings():
    """Visualizar todas as atas de reunião"""
    try:
        meetings = []
        if meeting_service:
            meetings = meeting_service.get_all_meetings()
        
        return render_template('all_meetings.html', meetings=meetings)
        
    except Exception as e:
        flash(f'Erro ao carregar atas: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 Iniciando aplicação Flask...")
    print(f"📊 Armazenamento: {'Google Sheets' if USE_GOOGLE_SHEETS else 'Local'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
