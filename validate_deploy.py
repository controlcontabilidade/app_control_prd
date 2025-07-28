#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 VERIFICAÇÃO PRÉ-DEPLOY - Control Contabilidade
Valida todas as configurações antes do deploy no Render
"""

import os
import sys
import json
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}🔍 {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

class PreDeployValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path(__file__).parent
        
    def validate_environment(self):
        """Valida variáveis de ambiente essenciais"""
        print_header("VALIDAÇÃO DE VARIÁVEIS DE AMBIENTE")
        
        required_vars = {
            'GOOGLE_SERVICE_ACCOUNT_JSON': 'Credenciais do Google Service Account',
            'GOOGLE_SHEETS_ID': 'ID da planilha Google Sheets',
            'SECRET_KEY': 'Chave secreta do Flask'
        }
        
        for var, description in required_vars.items():
            value = os.environ.get(var)
            if value:
                print_success(f"{var}: Configurada")
                
                # Validações específicas
                if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                    self._validate_service_account_json(value)
                elif var == 'GOOGLE_SHEETS_ID':
                    self._validate_sheets_id(value)
                elif var == 'SECRET_KEY':
                    if len(value) < 16:
                        self.warnings.append(f"SECRET_KEY muito curta (recomendado: 32+ caracteres)")
            else:
                self.errors.append(f"Variável {var} não definida ({description})")
                print_error(f"{var}: NÃO CONFIGURADA")
    
    def _validate_service_account_json(self, json_str):
        """Valida o JSON do Service Account"""
        try:
            data = json.loads(json_str)
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.errors.append(f"Campos obrigatórios ausentes no JSON: {missing_fields}")
                print_error(f"JSON inválido - campos ausentes: {missing_fields}")
            else:
                print_success(f"JSON válido - Project: {data.get('project_id')}")
                print_success(f"Service Account: {data.get('client_email')}")
                
                # Verificar se a chave privada está bem formatada
                private_key = data.get('private_key', '')
                if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                    self.warnings.append("Formato da chave privada pode estar incorreto")
                    
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON do Service Account inválido: {e}")
            print_error(f"JSON inválido: {e}")
    
    def _validate_sheets_id(self, sheets_id):
        """Valida o ID da planilha"""
        if len(sheets_id) < 40:
            self.warnings.append("ID da planilha parece muito curto")
        
        # Tentar acessar a planilha (se credenciais estiverem OK)
        try:
            from services.google_sheets_service_account import GoogleSheetsServiceAccountService
            service = GoogleSheetsServiceAccountService(sheets_id)
            # Teste básico - tentar ler algumas células
            result = service.get_clients()
            if result:
                print_success("Conexão com Google Sheets OK")
            else:
                self.warnings.append("Planilha acessível mas sem dados")
        except Exception as e:
            self.warnings.append(f"Não foi possível testar conexão com Google Sheets: {e}")
    
    def validate_files(self):
        """Valida arquivos essenciais"""
        print_header("VALIDAÇÃO DE ARQUIVOS")
        
        required_files = [
            ('app.py', 'Aplicação principal'),
            ('wsgi.py', 'WSGI entry point'),
            ('requirements.txt', 'Dependências Python'),
            ('gunicorn.conf.py', 'Configuração Gunicorn'),
            ('memory_optimizer.py', 'Otimizador de memória'),
            ('Procfile', 'Arquivo de processo para deploy'),
        ]
        
        for filename, description in required_files:
            filepath = self.project_root / filename
            if filepath.exists():
                print_success(f"{filename}: Encontrado")
                
                # Validações específicas
                if filename == 'requirements.txt':
                    self._validate_requirements_file(filepath)
                elif filename == 'wsgi.py':
                    self._validate_wsgi_file(filepath)
            else:
                self.errors.append(f"Arquivo {filename} não encontrado ({description})")
                print_error(f"{filename}: NÃO ENCONTRADO")
    
    def _validate_requirements_file(self, filepath):
        """Valida o arquivo requirements.txt"""
        try:
            content = filepath.read_text(encoding='utf-8')
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            essential_packages = ['flask', 'gunicorn', 'google-auth', 'google-auth-oauthlib']
            missing_packages = []
            
            for package in essential_packages:
                if not any(package.lower() in line.lower() for line in lines):
                    missing_packages.append(package)
            
            if missing_packages:
                self.warnings.append(f"Pacotes possivelmente ausentes: {missing_packages}")
            
            print_info(f"Requirements.txt tem {len(lines)} dependências")
            
        except Exception as e:
            self.warnings.append(f"Erro ao validar requirements.txt: {e}")
    
    def _validate_wsgi_file(self, filepath):
        """Valida o arquivo wsgi.py"""
        try:
            content = filepath.read_text(encoding='utf-8')
            if 'from app import app as application' in content or 'application = ' in content:
                print_success("WSGI entry point configurado corretamente")
            else:
                self.warnings.append("WSGI entry point pode estar mal configurado")
        except Exception as e:
            self.warnings.append(f"Erro ao validar wsgi.py: {e}")
    
    def validate_services(self):
        """Valida serviços essenciais"""
        print_header("VALIDAÇÃO DE SERVIÇOS")
        
        services_dir = self.project_root / 'services'
        if not services_dir.exists():
            self.errors.append("Diretório 'services' não encontrado")
            print_error("Diretório 'services': NÃO ENCONTRADO")
            return
        
        required_services = [
            'google_sheets_service_account.py',
            'local_storage_service.py',
            'render_fallback_service.py',
            'user_service.py'
        ]
        
        for service_file in required_services:
            service_path = services_dir / service_file
            if service_path.exists():
                print_success(f"Serviço {service_file}: Encontrado")
            else:
                self.errors.append(f"Serviço {service_file} não encontrado")
                print_error(f"Serviço {service_file}: NÃO ENCONTRADO")
    
    def validate_memory_optimization(self):
        """Valida configurações de otimização de memória"""
        print_header("VALIDAÇÃO DE OTIMIZAÇÃO DE MEMÓRIA")
        
        # Verificar gunicorn.conf.py
        gunicorn_conf = self.project_root / 'gunicorn.conf.py'
        if gunicorn_conf.exists():
            try:
                content = gunicorn_conf.read_text(encoding='utf-8')
                
                # Verificar configurações essenciais para Render 512MB
                checks = {
                    'workers = 1': 'Um único worker para economizar memória',
                    'max_requests = 100': 'Limite de requests por worker',
                    'worker_connections = 25': 'Conexões limitadas por worker',
                    'worker_memory_limit': 'Limite de memória por worker'
                }
                
                for config, description in checks.items():
                    if config.split('=')[0].strip() in content:
                        print_success(f"Config {config.split('=')[0].strip()}: OK")
                    else:
                        self.warnings.append(f"Configuração {config} não encontrada ({description})")
                        
            except Exception as e:
                self.warnings.append(f"Erro ao validar gunicorn.conf.py: {e}")
        
        # Verificar memory_optimizer.py
        memory_opt = self.project_root / 'memory_optimizer.py'
        if memory_opt.exists():
            print_success("Memory Optimizer: Configurado")
        else:
            self.warnings.append("Memory Optimizer não encontrado")
    
    def validate_render_config(self):
        """Valida configurações específicas do Render"""
        print_header("VALIDAÇÃO DE CONFIGURAÇÃO RENDER")
        
        # Verificar se tem Procfile (opcional no Render)
        procfile = self.project_root / 'Procfile'
        if procfile.exists():
            try:
                content = procfile.read_text(encoding='utf-8').strip()
                if 'gunicorn' in content and 'wsgi:application' in content:
                    print_success("Procfile: Configurado corretamente")
                else:
                    self.warnings.append("Procfile pode estar mal configurado")
            except Exception as e:
                self.warnings.append(f"Erro ao validar Procfile: {e}")
        
        # Verificar runtime.txt (opcional)
        runtime = self.project_root / 'runtime.txt'
        if runtime.exists():
            try:
                content = runtime.read_text(encoding='utf-8').strip()
                if content.startswith('python-'):
                    print_success(f"Runtime Python: {content}")
                else:
                    self.warnings.append("Runtime.txt pode estar mal formatado")
            except Exception as e:
                self.warnings.append(f"Erro ao validar runtime.txt: {e}")
        
        # Verificar se variáveis de produção estão configuradas
        prod_vars = {
            'FLASK_ENV': 'production',
            'PYTHONOPTIMIZE': '2',
            'WEB_CONCURRENCY': '1'
        }
        
        for var, expected in prod_vars.items():
            value = os.environ.get(var)
            if value == expected:
                print_success(f"{var}: {value}")
            else:
                self.warnings.append(f"Variável {var} deveria ser '{expected}' (atual: {value})")
    
    def test_app_startup(self):
        """Testa se a aplicação consegue inicializar"""
        print_header("TESTE DE INICIALIZAÇÃO")
        
        try:
            # Importar app sem executar
            sys.path.insert(0, str(self.project_root))
            from app import app
            
            # Configurar para teste
            app.config['TESTING'] = True
            
            # Criar context e testar rotas básicas
            with app.test_client() as client:
                # Testar rota principal
                response = client.get('/')
                if response.status_code in [200, 302]:  # 302 = redirect para login
                    print_success("Rota principal: OK")
                else:
                    self.warnings.append(f"Rota principal retornou status {response.status_code}")
                
                # Testar API de status
                response = client.get('/api/auth-status')
                if response.status_code == 200:
                    print_success("API de status: OK")
                else:
                    self.warnings.append(f"API de status retornou status {response.status_code}")
                    
        except Exception as e:
            self.errors.append(f"Erro ao testar inicialização: {e}")
            print_error(f"Teste de inicialização falhou: {e}")
    
    def generate_report(self):
        """Gera relatório final"""
        print_header("RELATÓRIO FINAL")
        
        if not self.errors and not self.warnings:
            print_success("🎉 TUDO OK! Aplicação pronta para deploy!")
            print_info("Execute: git push origin main (se usando auto-deploy)")
            return True
        
        if self.errors:
            print_error(f"ERROS CRÍTICOS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
            print()
        
        if self.warnings:
            print_warning(f"AVISOS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
            print()
        
        if self.errors:
            print_error("❌ CORRIJA OS ERROS ANTES DO DEPLOY!")
            return False
        else:
            print_warning("⚠️  DEPLOY POSSÍVEL, MAS VERIFIQUE OS AVISOS")
            return True

def main():
    print_header("🚀 VERIFICAÇÃO PRÉ-DEPLOY - CONTROL CONTABILIDADE")
    
    validator = PreDeployValidator()
    
    # Executar todas as validações
    validator.validate_environment()
    validator.validate_files()
    validator.validate_services()
    validator.validate_memory_optimization()
    validator.validate_render_config()
    validator.test_app_startup()
    
    # Gerar relatório final
    success = validator.generate_report()
    
    if success:
        print_info("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Commit e push das alterações")
        print("   2. Configurar variáveis de ambiente no Render")
        print("   3. Verificar logs após deploy")
        print("   4. Testar aplicação em produção")
        print("   5. Monitorar uso de memória")
        
        print_info("\n🔗 LINKS ÚTEIS:")
        print("   • Dashboard: https://sua-app.render.com")
        print("   • Status Auth: https://sua-app.render.com/api/auth-status")
        print("   • Status Memory: https://sua-app.render.com/api/memory-status")
        print("   • Troubleshooting: TROUBLESHOOTING_RENDER.md")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
