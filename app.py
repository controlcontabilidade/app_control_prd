# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
import gc  # Para otimização de memória
from datetime import datetime
from functools import wraps

# Importar otimizador de memória
try:
    from memory_optimizer import MemoryOptimizer, MEMORY_OPTIMIZED_SETTINGS, get_optimized_batch_size
    MEMORY_OPTIMIZER_AVAILABLE = True
    print("🧠 Memory Optimizer carregado")
except ImportError:
    MEMORY_OPTIMIZER_AVAILABLE = False
    print("⚠️ Memory Optimizer não disponível")
    
    # Definir função fallback
    def get_optimized_batch_size():
        return 50

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

# Aplicar otimizações de memória se disponível
if MEMORY_OPTIMIZER_AVAILABLE:
    MemoryOptimizer.setup_production_memory_settings()
    MemoryOptimizer.optimize_flask_config(app)
    
    # Configurações específicas do Render
    if os.environ.get('FLASK_ENV') == 'production':
        from memory_optimizer import setup_render_optimizations
        setup_render_optimizations()

# Configurações de encoding UTF-8
app.config['JSON_AS_ASCII'] = False
app.jinja_env.globals['ord'] = ord  # Função para debug de encoding
import sys
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding('utf-8')

# Forçar encoding UTF-8 para templates Jinja2
app.jinja_env.charset = 'utf-8'

# Filtro customizado para remover formatação de CPF/CNPJ
@app.template_filter('only_numbers')
def only_numbers_filter(value):
    """Remove toda formatação, deixando apenas números"""
    if not value:
        return ''
    import re
    return re.sub(r'\D', '', str(value))

# Filtro customizado para formatação de datas
@app.template_filter('format_date')
def format_date_filter(value, format='%d/%m/%Y'):
    """Formata data ISO para formato brasileiro"""
    if not value:
        return '-'
    try:
        # Se já for string no formato ISO
        if isinstance(value, str):
            # Remove microsegundos se existirem
            if '.' in value:
                value = value.split('.')[0]
            # Tenta parsing ISO
            if 'T' in value:
                dt = datetime.fromisoformat(value.replace('T', ' '))
            else:
                dt = datetime.strptime(value, '%Y-%m-%d')
        elif isinstance(value, datetime):
            dt = value
        else:
            return str(value)
        
        return dt.strftime(format)
    except (ValueError, AttributeError):
        return str(value)

# Filtro customizado para formatação de data e hora
@app.template_filter('format_datetime')
def format_datetime_filter(value):
    """Formata data e hora ISO para formato brasileiro"""
    return format_date_filter(value, '%d/%m/%Y %H:%M')

# Configurações para upload de arquivos - ULTRA-OTIMIZADO PARA RENDER 512MB
# Reduzido DRASTICAMENTE para economizar RAM no Render
MAX_UPLOAD_SIZE = 1 * 1024 * 1024 if os.environ.get('FLASK_ENV') == 'production' else 4 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE  # 1MB produção, 4MB desenvolvimento
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

print(f"📁 Upload configurado: {MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB máximo")

# Configurações ULTRA-AGRESSIVAS para produção com baixíssimo consumo de memória
if os.environ.get('FLASK_ENV') == 'production':
    # Garbage collection EXTREMAMENTE agressivo
    gc.set_threshold(100, 2, 2)  # Muito mais agressivo que padrão
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60  # Cache de apenas 1 minuto
    
    # Configurações JSON ULTRA-otimizadas
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json'
    
    # Limitar DRASTICAMENTE threads e workers
    os.environ.setdefault('WEB_CONCURRENCY', '1')  # 1 worker APENAS
    os.environ.setdefault('WORKER_CONNECTIONS', '25')  # Reduzido drasticamente
    os.environ.setdefault('WORKER_TIMEOUT', '20')  # Timeout muito baixo
    os.environ.setdefault('MAX_REQUESTS', '50')  # Reiniciar worker muito frequentemente
    
    # Configurações de sessão otimizadas
    app.config['PERMANENT_SESSION_LIFETIME'] = 900  # 15 minutos apenas
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Desabilitar funcionalidades que consomem memória
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app.config['EXPLAIN_TEMPLATE_LOADING'] = False
    
    print("🧠 Configurações ULTRA-AGRESSIVAS de produção aplicadas para economia máxima de memória")

# Criar pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hook ULTRA-AGRESSIVO para limpeza de memória após cada requisição
@app.after_request
def cleanup_memory_after_request(response):
    """Limpa memória AGRESSIVAMENTE após cada requisição"""
    if MEMORY_OPTIMIZER_AVAILABLE and os.environ.get('FLASK_ENV') == 'production':
        # Múltiplas passadas de garbage collection
        MemoryOptimizer.cleanup_after_request()
        
        # Limpeza adicional para ambientes críticos de memória
        try:
            # Forçar limpeza de cache Python interno
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # Coleta de lixo adicional
            gc.collect()
        except:
            pass
    
    return response

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

# Inicializar serviços COM LAZY LOADING - OTIMIZAÇÃO MEMÓRIA RENDER
storage_service = None
meeting_service = None
user_service = None
report_service = None
import_service = None

def get_storage_service():
    """Lazy loading do storage service com fallback robusto para Render"""
    global storage_service
    if storage_service is None:
        try:
            if USE_GOOGLE_SHEETS and GOOGLE_SHEETS_ID:
                if USE_SERVICE_ACCOUNT:
                    print("🔐 Inicializando Google Sheets Service Account...")
                    from services.google_sheets_service_account import GoogleSheetsServiceAccountService
                    storage_service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
                    print("✅ Storage service inicializado (Service Account)")
                elif USE_OAUTH2:
                    print("🔐 Inicializando Google Sheets OAuth2...")
                    from services.google_sheets_oauth_service import GoogleSheetsOAuthService
                    storage_service = GoogleSheetsOAuthService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
                    print("✅ Storage service inicializado (OAuth2)")
                else:
                    print("📊 Inicializando Google Sheets híbrido...")
                    storage_service = GoogleSheetsService(GOOGLE_SHEETS_API_KEY, GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
                    print("✅ Storage service inicializado (Híbrido)")
            else:
                print("⚠️ Usando armazenamento local")
                storage_service = LocalStorageService()
                
        except Exception as e:
            print(f"❌ Erro ao inicializar storage service: {e}")
            print(f"🔍 Tipo do erro: {type(e).__name__}")
            
            # Verificar se é erro de autenticação específico do Render
            error_str = str(e).lower()
            is_auth_error = any(keyword in error_str for keyword in [
                'authentication', 'credential', 'unauthorized', 'forbidden',
                'service account', 'google', 'api', 'quota', 'permission'
            ])
            
            if is_auth_error and os.environ.get('FLASK_ENV') == 'production':
                print("🚨 Erro de autenticação detectado no Render - ativando fallback")
                try:
                    from services.render_fallback_service import RenderFallbackService
                    storage_service = RenderFallbackService()
                    print("✅ Render Fallback Service ativado")
                    
                    # Adicionar mensagem global para mostrar na interface
                    if not hasattr(get_storage_service, '_fallback_message_shown'):
                        flash('⚠️ Sistema temporariamente usando dados locais. Verifique configurações do Google Sheets.', 'warning')
                        get_storage_service._fallback_message_shown = True
                        
                except Exception as fallback_error:
                    print(f"❌ Erro ao ativar fallback: {fallback_error}")
                    storage_service = LocalStorageService()
                    print("⚠️ Fallback final para armazenamento local")
            else:
                storage_service = LocalStorageService()
                print("⚠️ Fallback para armazenamento local")
        
        # Limpeza de memória após inicialização
        if MEMORY_OPTIMIZER_AVAILABLE:
            gc.collect()
            print(f"💾 Memória após init storage: {MemoryOptimizer.get_memory_usage()}")
    
    return storage_service

def get_meeting_service():
    """Lazy loading do meeting service"""
    global meeting_service
    if meeting_service is None and GOOGLE_SHEETS_ID:
        try:
            meeting_service = MeetingService(GOOGLE_SHEETS_ID)
            print("✅ Meeting service inicializado")
        except Exception as e:
            print(f"❌ Erro ao inicializar meeting service: {e}")
            meeting_service = None
    return meeting_service

def get_user_service():
    """Lazy loading do user service com fallback"""
    global user_service
    if user_service is None:
        if GOOGLE_SHEETS_ID:
            try:
                print(f"🔄 Tentando inicializar UserService com SHEETS_ID: {GOOGLE_SHEETS_ID}")
                user_service = UserService(GOOGLE_SHEETS_ID)
                print("✅ User service inicializado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao inicializar user service: {e}")
                print(f"🔍 Tipo do erro: {type(e).__name__}")
                print("🔄 Tentando fallback de usuários...")
                
                # Usar serviço de fallback
                try:
                    from services.fallback_user_service import FallbackUserService
                    user_service = FallbackUserService()
                    print("✅ Fallback user service inicializado")
                except Exception as fallback_error:
                    print(f"❌ Erro no fallback user service: {fallback_error}")
                    user_service = None
        else:
            print("❌ GOOGLE_SHEETS_ID não disponível para UserService")
            print("🔄 Inicializando fallback user service...")
            
            # Usar serviço de fallback quando não há SHEETS_ID
            try:
                from services.fallback_user_service import FallbackUserService
                user_service = FallbackUserService()
                print("✅ Fallback user service inicializado (sem SHEETS_ID)")
            except Exception as fallback_error:
                print(f"❌ Erro no fallback user service: {fallback_error}")
                user_service = None
    else:
        print("♻️ User service já inicializado")
    return user_service

def get_report_service():
    """Lazy loading do report service"""
    global report_service
    print(f"🔍 Debug get_report_service: report_service atual = {report_service}")
    print(f"🔍 Debug get_report_service: GOOGLE_SHEETS_ID = {GOOGLE_SHEETS_ID}")
    
    if report_service is None and GOOGLE_SHEETS_ID:
        try:
            print("🔄 Inicializando ReportService...")
            report_service = ReportService(GOOGLE_SHEETS_ID)
            print("✅ Report service inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar report service: {e}")
            import traceback
            traceback.print_exc()
            report_service = None
    elif report_service is None:
        print("❌ GOOGLE_SHEETS_ID não disponível para ReportService")
    else:
        print("♻️ Report service já inicializado")
    
    print(f"🔍 Debug get_report_service: retornando = {report_service}")
    return report_service

def get_import_service():
    """Lazy loading do import service"""
    global import_service
    if import_service is None and ImportService:
        try:
            storage = get_storage_service()
            if storage:
                import_service = ImportService(storage)
                print(f"✅ Import service inicializado ({IMPORT_SERVICE_TYPE})")
        except Exception as e:
            print(f"❌ Erro ao inicializar import service: {e}")
            import_service = None
    return import_service

# Inicialização básica - só o essencial
print("🚀 Aplicação inicializada com lazy loading")
print(f"💾 Memória inicial: {MemoryOptimizer.get_memory_usage() if MEMORY_OPTIMIZER_AVAILABLE else 'N/A'}")

# Garbage collection inicial
if os.environ.get('FLASK_ENV') == 'production':
    gc.collect()
    print("🧠 Limpeza inicial de memória concluída")

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
        
        # Usar get_user_service() em vez de user_service diretamente
        current_user_service = get_user_service()
        if current_user_service:
            user = current_user_service.get_user_by_id(session['user_id'])
            if not user or user.get('perfil', '').lower() != 'administrador':
                flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
                return redirect(url_for('index'))
        else:
            # Se não há user_service, verificar se é o admin de fallback
            if session.get('user_id') != 'admin-fallback':
                flash('Acesso negado. Sistema em modo de manutenção.', 'danger')
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
        
        # Debug das variáveis de ambiente críticas
        print(f"🔍 DEBUG: GOOGLE_SHEETS_ID = {GOOGLE_SHEETS_ID}")
        print(f"🔍 DEBUG: USE_GOOGLE_SHEETS = {USE_GOOGLE_SHEETS}")
        print(f"🔍 DEBUG: USE_SERVICE_ACCOUNT = {USE_SERVICE_ACCOUNT}")
        
        # Tentar inicializar o user_service
        current_user_service = get_user_service()
        print(f"🔐 LOGIN: user_service disponível: {current_user_service is not None}")
        
        if current_user_service:
            print("🔐 LOGIN: Chamando authenticate_user...")
            user = current_user_service.authenticate_user(username, password)
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
            flash('Serviço de autenticação indisponível. Tente novamente.', 'error')
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
    current_user_service = get_user_service()
    if current_user_service:
        users_list = current_user_service.list_users()
        return render_template('users.html', users=users_list)
    else:
        flash('Serviço de usuários indisponível.', 'error')
        return redirect(url_for('index'))

@app.route('/create_user', methods=['POST'])
@admin_required
def create_user():
    current_user_service = get_user_service()
    if current_user_service:
        nome = request.form['nome']
        email = request.form['email']
        usuario = request.form['usuario']
        senha = request.form['senha']
        perfil = request.form['perfil']
        
        result = current_user_service.create_user(nome, email, usuario, senha, perfil)
        
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
    current_user_service = get_user_service()
    if current_user_service:
        user_id = request.form['user_id']
        nome = request.form['nome']
        email = request.form['email']
        usuario = request.form['usuario']
        perfil = request.form['perfil']
        ativo = request.form['ativo']
        nova_senha = request.form.get('nova_senha', '').strip()
        
        # Se nova senha foi fornecida, usa ela, senão None
        senha_param = nova_senha if nova_senha else None
        
        result = current_user_service.update_user(user_id, nome, email, usuario, perfil, ativo, senha_param)
        
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
    current_user_service = get_user_service()
    if current_user_service:
        user_id = request.form['user_id']
        
        result = current_user_service.delete_user(user_id)
        
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
    # Inicializar o serviço de relatórios se necessário
    report_svc = get_report_service()
    
    if report_svc:
        try:
            # Busca apenas relatórios ativos
            reports_data = report_svc.list_reports(only_active=True)
            username = session.get('user_name', '')
            
            print(f"🔍 Debug: {len(reports_data)} relatórios encontrados (apenas ativos)")
            
            # Filtrar relatórios que o usuário tem acesso
            accessible_reports = []
            for report in reports_data:
                print(f"🔍 Debug: Relatório '{report.get('nome')}' - Ativo: '{report.get('ativo')}'")
                if report_svc.user_has_access(report, username):
                    accessible_reports.append(report)
            
            print(f"🔍 Debug: {len(accessible_reports)} relatórios acessíveis para '{username}'")
            return render_template('reports.html', reports=accessible_reports)
        except Exception as e:
            print(f"❌ Erro ao carregar relatórios: {e}")
            flash('Erro ao carregar relatórios. Tente novamente.', 'error')
            return render_template('reports.html', reports=[])
    else:
        flash('Serviço de relatórios indisponível.', 'error')
        return render_template('reports.html', reports=[])

@app.route('/manage_reports')
@admin_required
def manage_reports():
    """Página de gerenciamento de relatórios (somente admin)"""
    # Inicializar o serviço de relatórios se necessário
    report_svc = get_report_service()
    
    if report_svc:
        try:
            reports_data = report_svc.list_reports()
            return render_template('manage_reports.html', reports=reports_data)
        except Exception as e:
            print(f"❌ Erro ao carregar relatórios para gerenciamento: {e}")
            flash('Erro ao carregar relatórios. Tente novamente.', 'error')
            return render_template('manage_reports.html', reports=[])
    else:
        flash('Serviço de relatórios indisponível.', 'error')
        return render_template('manage_reports.html', reports=[])

@app.route('/create_report', methods=['POST'])
@admin_required
def create_report():
    """Criar novo relatório"""
    # Inicializar o serviço de relatórios se necessário
    report_svc = get_report_service()
    
    if report_svc:
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
        
        result = report_svc.create_report(nome, descricao, link, ativo, ordem, criado_por, usuarios_autorizados)
        
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
    # Inicializar o serviço de relatórios se necessário
    report_svc = get_report_service()
    
    if report_svc:
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
        
        result = report_svc.update_report(report_id, nome, descricao, link, ativo, ordem, usuarios_autorizados)
        
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
    # Inicializar o serviço de relatórios se necessário
    report_svc = get_report_service()
    
    if report_svc:
        report_id = request.form['report_id']
        
        result = report_svc.delete_report(report_id)
        
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

def calculate_dashboard_stats_optimized(clients):
    """Versão otimizada para ambientes com pouca memória"""
    if not clients:
        return {
            'total_clientes': 0, 'clientes_ativos': 0, 'empresas': 0, 
            'domesticas': 0, 'mei': 0, 'simples_nacional': 0,
            'lucro_presumido': 0, 'lucro_real': 0,
            'ct': 0, 'fs': 0, 'dp': 0, 'bpo': 0
        }
    
    # Inicializar contadores
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
    
    # Processar em lotes para economizar memória
    batch_size = get_optimized_batch_size() if MEMORY_OPTIMIZER_AVAILABLE else 50
    
    for i in range(0, len(clients), batch_size):
        batch = clients[i:i+batch_size]
        
        for client in batch:
            # Contadores básicos (apenas campos essenciais)
            if client.get('ativo', True):
                stats['clientes_ativos'] += 1
            
            # Serviços básicos
            if client.get('ct'):
                stats['ct'] += 1
            if client.get('fs'):
                stats['fs'] += 1
            if client.get('dp'):
                stats['dp'] += 1
            if client.get('bpoFinanceiro'):
                stats['bpo'] += 1
            
            # Categorização simplificada (menos processamento de string)
            regime = client.get('regimeFederal', '')
            if regime:
                regime_upper = regime.upper()
                if 'MEI' in regime_upper:
                    stats['mei'] += 1
                elif 'SIMPLES' in regime_upper:
                    stats['simples_nacional'] += 1
                elif 'PRESUMIDO' in regime_upper:
                    stats['lucro_presumido'] += 1
                elif 'REAL' in regime_upper:
                    stats['lucro_real'] += 1
                else:
                    stats['empresas'] += 1
            else:
                stats['empresas'] += 1
        
        # Limpeza de memória após cada lote
        if os.environ.get('FLASK_ENV') == 'production':
            gc.collect()
    
    return stats

@app.route('/api/users')
@admin_required
def get_users():
    """API para obter lista de usuários disponíveis"""
    user_svc = get_user_service()
    if user_svc:
        users = user_svc.get_available_users()
        return jsonify({'users': users})
    else:
        return jsonify({'users': ['todos', 'admin', 'usuario']})

@app.route('/api/memory-status')
@admin_required  
def memory_status():
    """API para monitorar uso de memória em produção"""
    try:
        # Coletar informações de memória
        memory_info = {
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'python_version': sys.version.split()[0],
        }
        
        # Tentar obter info detalhada de memória
        try:
            import psutil
            process = psutil.Process()
            memory_info.update({
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 1),
                'memory_percent': round(process.memory_percent(), 1),
                'cpu_percent': round(process.cpu_percent(), 1),
                'threads': process.num_threads(),
            })
            
            # Alertas baseados nos limites do Render (512MB)
            memory_mb = memory_info['memory_mb']
            if memory_mb > 450:
                memory_info['alert'] = 'CRITICAL - Próximo do limite de 512MB'
                memory_info['alert_level'] = 'danger'
            elif memory_mb > 350:
                memory_info['alert'] = 'WARNING - Uso de memória elevado'
                memory_info['alert_level'] = 'warning'
            else:
                memory_info['alert'] = 'OK - Uso de memória normal'
                memory_info['alert_level'] = 'success'
                
        except ImportError:
            memory_info['memory_mb'] = 'N/A (psutil não disponível)'
            memory_info['alert'] = 'Monitoramento limitado'
            memory_info['alert_level'] = 'info'
        
        # Informações sobre garbage collection
        memory_info['gc_counts'] = gc.get_count()
        memory_info['gc_threshold'] = gc.get_threshold()
        
        # Informações sobre lazy loading
        services_loaded = {
            'storage_service': storage_service is not None,
            'meeting_service': meeting_service is not None,
            'user_service': user_service is not None,
            'report_service': report_service is not None,
            'import_service': import_service is not None
        }
        memory_info['services_loaded'] = services_loaded
        memory_info['services_count'] = sum(services_loaded.values())
        
        # Configurações de otimização ativas
        optimizations = {
            'memory_optimizer_available': MEMORY_OPTIMIZER_AVAILABLE,
            'max_content_length': app.config.get('MAX_CONTENT_LENGTH', 0) / 1024 / 1024,  # MB
            'json_sort_keys': app.config.get('JSON_SORT_KEYS', True),
            'web_concurrency': os.environ.get('WEB_CONCURRENCY', 'auto'),
            'worker_connections': os.environ.get('WORKER_CONNECTIONS', 'auto'),
        }
        memory_info['optimizations'] = optimizations
        
        return jsonify(memory_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'alert': 'ERROR - Falha ao obter status de memória',
            'alert_level': 'danger'
        }), 500

@app.route('/api/auth-status')
@admin_required
def auth_status():
    """API para diagnóstico de autenticação Google Sheets"""
    try:
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'google_sheets_config': {
                'use_google_sheets': USE_GOOGLE_SHEETS,
                'use_service_account': USE_SERVICE_ACCOUNT,
                'use_oauth2': USE_OAUTH2,
                'sheets_id_configured': bool(GOOGLE_SHEETS_ID),
                'api_key_configured': bool(GOOGLE_SHEETS_API_KEY),
            }
        }
        
        # Verificar variável de ambiente do Service Account
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        diagnosis['service_account'] = {
            'env_var_present': bool(service_account_json),
            'env_var_length': len(service_account_json) if service_account_json else 0,
            'is_valid_json': False,
            'project_id': None,
            'client_email': None
        }
        
        if service_account_json:
            try:
                credentials_info = json.loads(service_account_json)
                diagnosis['service_account'].update({
                    'is_valid_json': True,
                    'project_id': credentials_info.get('project_id'),
                    'client_email': credentials_info.get('client_email'),
                    'has_private_key': bool(credentials_info.get('private_key'))
                })
            except json.JSONDecodeError as e:
                diagnosis['service_account']['json_error'] = str(e)
        
        # Verificar status do storage service
        storage = get_storage_service()
        diagnosis['storage_service'] = {
            'type': type(storage).__name__,
            'is_fallback': hasattr(storage, 'is_fallback') and storage.is_fallback,
            'initialized': storage is not None
        }
        
        # Se estiver usando fallback, incluir informações adicionais
        if hasattr(storage, 'get_status_info'):
            diagnosis['fallback_info'] = storage.get_status_info()
        
        return jsonify(diagnosis)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'ERROR - Falha no diagnóstico de autenticação'
        }), 500

@app.route('/')
@login_required
def index():
    print("🔍 === ROTA INDEX CHAMADA (ULTRA-MEMORY OPTIMIZED) ===")
    try:
        print("📊 Carregando clientes com lazy loading EXTREMO...")
        
        # OTIMIZAÇÃO MEMÓRIA: Forçar limpeza antes de carregar
        if os.environ.get('FLASK_ENV') == 'production':
            gc.collect()
            gc.collect()  # Dupla passada
        
        # OTIMIZAÇÃO MEMÓRIA: Usar lazy loading e limite ULTRA-restritivo
        storage = get_storage_service()
        
        # Verificar se é possível usar serviço otimizado
        try:
            from services.memory_optimized_sheets_service import MemoryOptimizedGoogleSheetsService
            if hasattr(storage, 'spreadsheet_id'):
                print("🧠 Usando serviço ULTRA-otimizado para memória")
                optimized_service = MemoryOptimizedGoogleSheetsService(
                    storage.spreadsheet_id, 
                    storage.range_name
                )
                clients = optimized_service.get_clients()
            else:
                clients = storage.get_clients()
        except ImportError:
            clients = storage.get_clients()
        
        # Limite ULTRA-restritivo baseado na memória disponível
        max_clients = MEMORY_OPTIMIZED_SETTINGS.get('MAX_ROWS_PER_REQUEST', 25) if MEMORY_OPTIMIZER_AVAILABLE else 25
        
        # Para produção, ser ainda mais restritivo
        if os.environ.get('FLASK_ENV') == 'production':
            max_clients = min(max_clients, 15)  # Máximo 15 clientes por vez
            
        if len(clients) > max_clients:
            clients = clients[:max_clients]
            print(f"🧠 ULTRA-LIMITADO a {max_clients} clientes (economia RAM crítica)")
        
        print(f"✅ {len(clients)} clientes carregados")
        print(f"💾 Memória atual: {MemoryOptimizer.get_memory_usage() if MEMORY_OPTIMIZER_AVAILABLE else 'N/A'}")
        
        # OTIMIZAÇÃO MEMÓRIA: Stats ULTRA-simplificadas
        try:
            # Usar apenas contadores básicos para economizar memória
            stats = {
                'total_clientes': len(clients),
                'clientes_ativos': sum(1 for c in clients if c.get('ativo', True)),
                'ct': sum(1 for c in clients if c.get('ct')),
                'fs': sum(1 for c in clients if c.get('fs')),
                'dp': sum(1 for c in clients if c.get('dp')),
                # Remover cálculos complexos que consomem memória
                'empresas': len(clients),  # Simplificado
                'domesticas': 0,  # Simplificado
                'mei': 0,  # Simplificado
                'simples_nacional': 0,  # Simplificado
                'lucro_presumido': 0,  # Simplificado
                'lucro_real': 0,  # Simplificado
                'bpo': sum(1 for c in clients if c.get('bpoFinanceiro'))
            }
            print(f"📈 Estatísticas ULTRA-simplificadas calculadas")
        except Exception as stats_error:
            print(f"⚠️ Erro ao calcular stats: {stats_error}")
            stats = {
                'total_clientes': len(clients), 
                'clientes_ativos': len(clients),  # Simplificado
                'empresas': len(clients), 'domesticas': 0, 'mei': 0, 'simples_nacional': 0,
                'lucro_presumido': 0, 'lucro_real': 0,
                'ct': 0, 'fs': 0, 'dp': 0, 'bpo': 0
            }
        
        # Garbage collection AGRESSIVO após processamento
        if os.environ.get('FLASK_ENV') == 'production':
            # Múltiplas passadas para garantir limpeza máxima
            for _ in range(3):
                gc.collect()
            print(f"💾 Memória pós-GC-EXTREMO: {MemoryOptimizer.get_memory_usage() if MEMORY_OPTIMIZER_AVAILABLE else 'N/A'}")
        
        return render_template('index_modern.html', clients=clients, stats=stats)
        
    except Exception as e:
        print(f"❌ ERRO na rota index: {str(e)}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        flash(f'Erro ao carregar clientes: {str(e)}', 'error')
        
        # Em caso de erro, criar stats vazias e forçar limpeza
        stats = {
            'total_clientes': 0, 'clientes_ativos': 0, 'empresas': 0,
            'domesticas': 0, 'mei': 0, 'simples_nacional': 0,
            'lucro_presumido': 0, 'lucro_real': 0,
            'ct': 0, 'fs': 0, 'dp': 0, 'bpo': 0
        }
        
        # Limpeza de emergência
        if os.environ.get('FLASK_ENV') == 'production':
            for _ in range(5):
                gc.collect()
        
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
        print(f"🔍 [VIEW] ===== CARREGANDO CLIENTE PARA VISUALIZAÇÃO =====")
        print(f"🔍 [VIEW] ID solicitado: '{client_id}'")
        print(f"🔍 [VIEW] Tipo do ID: {type(client_id)}")
        
        # CORREÇÃO: Usar get_storage_service() para lazy loading
        storage = get_storage_service()
        client = storage.get_client(client_id)
        print(f"🔍 [VIEW] Cliente carregado: {client is not None}")
        
        if client:
            print(f"🔍 [VIEW] Nome do cliente: {client.get('nomeEmpresa')}")
            print(f"🔍 [VIEW] ID do cliente retornado: '{client.get('id')}'")
            return render_template('client_view_modern.html', client=client)
        else:
            print(f"❌ [VIEW] Cliente {client_id} não encontrado!")
            flash('Cliente não encontrado', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"❌ [VIEW] Erro ao carregar cliente: {str(e)}")
        import traceback
        print(f"❌ [VIEW] Traceback: {traceback.format_exc()}")
        flash(f'Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/client/new')
@login_required
def new_client():
    return render_template('client_form_complete.html', client=None)

@app.route('/client/<client_id>/edit')
@login_required
def edit_client(client_id):
    try:
        print(f"🔍 [EDIT] ===== CARREGANDO CLIENTE PARA EDIÇÃO =====")
        print(f"🔍 [EDIT] ID solicitado: '{client_id}'")
        
        # CORREÇÃO: Usar get_storage_service() para lazy loading
        storage = get_storage_service()
        client = storage.get_client(client_id)
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
            
            return render_template('client_form_complete.html', client=client)
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
        }
        
        # Processar dados dos sócios dinamicamente
        print("🔍 Processando dados dos sócios...")
        for i in range(1, 11):  # Suporte para até 10 sócios
            nome_socio = request.form.get(f'socio_{i}_nome', '').strip()
            if nome_socio:  # Se há nome, processar os dados do sócio
                client_data[f'socio_{i}_nome'] = nome_socio
                client_data[f'socio_{i}_cpf'] = request.form.get(f'socio_{i}_cpf', '').strip()
                client_data[f'socio_{i}_email'] = request.form.get(f'socio_{i}_email', '').strip()
                client_data[f'socio_{i}_telefone'] = request.form.get(f'socio_{i}_telefone', '').strip()
                client_data[f'socio_{i}_participacao'] = request.form.get(f'socio_{i}_participacao', '').strip()
                print(f"🔍 Sócio {i}: {nome_socio}")
        
        # Continuar com outros dados
        client_data.update({
            
            # Bloco 5: Sistemas e Acessos
            'sistemaPrincipal': request.form.get('sistemaPrincipal', ''),
            'versaoSistema': request.form.get('versaoSistema', ''),
            'codAcessoSimples': request.form.get('codAcessoSimples', ''),
            'cpfCnpjAcesso': request.form.get('cpfCnpjAcesso', ''),
            'portalClienteAtivo': request.form.get('portalClienteAtivo') == 'on',
            'integracaoDominio': request.form.get('integracaoDominio') == 'on',
            'sistemaOnvio': request.form.get('sistemaOnvio') == 'on',
            
            # Novos campos Sistema Onvio
            'sistemaOnvioContabil': request.form.get('sistemaOnvioContabil') == 'on',
            'sistemaOnvioFiscal': request.form.get('sistemaOnvioFiscal') == 'on',
            'sistemaOnvioPessoal': request.form.get('sistemaOnvioPessoal') == 'on',
            
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
            'mesAnoInicio': request.form.get('dataInicioServicos', ''),
            
            # Status e configurações
            'ativo': request.form.get('ativo') == 'on',
        })
        
        # Sincronizar statusCliente com ativo para compatibilidade
        status_cliente = client_data.get('statusCliente', 'ativo')
        client_data['ativo'] = status_cliente == 'ativo'
        
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
        
        # CORREÇÃO: Usar get_storage_service() para lazy loading
        storage = get_storage_service()
        if not storage:
            print("❌ storage_service não está disponível!")
            flash('Erro: Serviço de armazenamento não disponível', 'error')
            return redirect(url_for('index'))
        
        print("🔍 Chamando storage_service.save_client...")
        print(f"🔍 client_data['id']: '{client_data.get('id')}'")
        print(f"🔍 client_data['nomeEmpresa']: '{client_data.get('nomeEmpresa')}'")
        print(f"🔍 Dados essenciais: ID={client_data.get('id')}, Nome={client_data.get('nomeEmpresa')}")
        
        success = storage.save_client(client_data)
        
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
        
        # CORREÇÃO: Usar get_storage_service() para lazy loading
        storage = get_storage_service()
        success = storage.delete_client(client_id)
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

@app.route('/debug-render')
def debug_render():
    """Rota de debug para verificar configurações no Render"""
    try:
        import json
        import sys
        
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'environment': {}
        }
        
        # Verificar variáveis de ambiente
        env_vars = ['GOOGLE_SERVICE_ACCOUNT_JSON', 'GOOGLE_SHEETS_ID', 'FLASK_ENV']
        for var in env_vars:
            value = os.environ.get(var)
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON' and value:
                # Não expor credenciais completas
                debug_info['environment'][var] = f"Presente ({len(value)} chars)"
                try:
                    creds_info = json.loads(value)
                    debug_info['environment'][f'{var}_parsed'] = {
                        'project_id': creds_info.get('project_id', 'N/A'),
                        'client_email': creds_info.get('client_email', 'N/A'),
                        'keys_available': list(creds_info.keys())
                    }
                except:
                    debug_info['environment'][f'{var}_parsed'] = "Erro ao parsear JSON"
            else:
                debug_info['environment'][var] = value or "Não encontrada"
        
        # Testar importações
        debug_info['imports'] = {}
        try:
            from google.oauth2.service_account import Credentials
            debug_info['imports']['google_oauth2'] = "OK"
        except ImportError as e:
            debug_info['imports']['google_oauth2'] = f"ERRO: {e}"
        
        try:
            from googleapiclient.discovery import build
            debug_info['imports']['googleapiclient'] = "OK"
        except ImportError as e:
            debug_info['imports']['googleapiclient'] = f"ERRO: {e}"
        
        # Testar serviço
        debug_info['service_test'] = {}
        try:
            if USE_GOOGLE_SHEETS and storage_service:
                debug_info['service_test']['storage_type'] = "Google Sheets"
                debug_info['service_test']['service_initialized'] = bool(storage_service.service)
                debug_info['service_test']['spreadsheet_id'] = storage_service.spreadsheet_id
                
                # Testar busca de clientes
                clients = storage_service.get_clients()
                debug_info['service_test']['clients_count'] = len(clients)
                
                if clients:
                    first_client = clients[0]
                    debug_info['service_test']['first_client'] = {
                        'name': first_client.get('nomeEmpresa', 'N/A'),
                        'id': first_client.get('id', 'N/A'),
                        'keys_count': len(first_client.keys())
                    }
            else:
                debug_info['service_test']['storage_type'] = "Local"
                
        except Exception as e:
            debug_info['service_test']['error'] = str(e)
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/debug-client/<client_id>')
def debug_client_search(client_id):
    """Rota específica para debug de busca de cliente"""
    try:
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'client_id_received': client_id,
            'client_id_type': str(type(client_id)),
            'client_id_length': len(str(client_id)),
            'storage_type': 'Google Sheets' if USE_GOOGLE_SHEETS else 'Local'
        }
        
        # Teste 1: Buscar cliente específico
        print(f"🔍 [DEBUG_CLIENT] Buscando cliente: {client_id}")
        client = storage_service.get_client(client_id)
        debug_info['client_found'] = client is not None
        
        if client:
            debug_info['client_data'] = {
                'nome': client.get('nomeEmpresa', 'N/A'),
                'id': client.get('id', 'N/A'),
                'id_type': str(type(client.get('id'))),
                'fields_count': len(client.keys()),
                'has_cnpj': bool(client.get('cnpj')),
                'has_razao_social': bool(client.get('razaoSocialReceita'))
            }
        else:
            debug_info['client_data'] = None
            
            # Teste 2: Listar todos os clientes para comparar IDs
            all_clients = storage_service.get_clients()
            debug_info['total_clients'] = len(all_clients)
            debug_info['sample_client_ids'] = []
            
            for i, c in enumerate(all_clients[:10]):  # Primeiros 10
                debug_info['sample_client_ids'].append({
                    'index': i,
                    'name': c.get('nomeEmpresa', 'N/A'),
                    'id': c.get('id', 'N/A'),
                    'id_matches': str(c.get('id', '')).strip() == str(client_id).strip()
                })
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id
        })

if __name__ == '__main__':
    print("🚀 Iniciando aplicação Flask...")
    print(f"📊 Armazenamento: {'Google Sheets' if USE_GOOGLE_SHEETS else 'Local'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
