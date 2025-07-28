#!/usr/bin/env python3
"""
Script de diagnóstico especificamente para o Render
Execute este script no console do Render para diagnosticar problemas
"""
import os
import json
import sys

def render_diagnostic():
    print("🚀 DIAGNÓSTICO RENDER - Control Contabilidade")
    print("="*60)
    
    # 1. Informações básicas do ambiente
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Diretório atual: {os.getcwd()}")
    print(f"🌍 Variáveis de ambiente relacionadas:")
    
    env_vars_to_check = [
        'FLASK_ENV', 'GOOGLE_SERVICE_ACCOUNT_JSON', 'GOOGLE_SHEETS_ID', 
        'SECRET_KEY', 'PYTHONOPTIMIZE', 'WEB_CONCURRENCY'
    ]
    
    for var in env_vars_to_check:
        value = os.environ.get(var)
        if value:
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                print(f"   {var}: ✅ Presente ({len(value)} chars)")
            elif var == 'SECRET_KEY':
                print(f"   {var}: ✅ Presente ({len(value)} chars)")
            else:
                print(f"   {var}: ✅ {value}")
        else:
            print(f"   {var}: ❌ Ausente")
    
    # 2. Testar parse do JSON do Service Account
    service_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_json:
        print(f"\n🔍 ANALISANDO GOOGLE_SERVICE_ACCOUNT_JSON:")
        
        # Verificar caracteres suspeitos
        print(f"   📊 Tamanho: {len(service_json)} caracteres")
        print(f"   📊 Primeiros 50 chars: {service_json[:50]}")
        print(f"   📊 Últimos 50 chars: {service_json[-50:]}")
        
        # Testar parse JSON
        try:
            creds_data = json.loads(service_json)
            print("   ✅ JSON válido!")
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            for field in required_fields:
                if field in creds_data:
                    if field == 'private_key':
                        print(f"   ✅ {field}: Presente ({len(creds_data[field])} chars)")
                    else:
                        print(f"   ✅ {field}: {creds_data[field]}")
                else:
                    print(f"   ❌ {field}: AUSENTE!")
                    
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON INVÁLIDO: {e}")
            print(f"   🔍 Possível problema de escape ou formato")
            
            # Tentar diagnósticos extras
            if '"' not in service_json[:10]:
                print("   🚨 ERRO: JSON não começa com aspas duplas")
            if '\\n' in service_json:
                print("   ⚠️  AVISO: Contém \\n (quebras de linha escapadas)")
            if "'" in service_json:
                print("   🚨 ERRO: Contém aspas simples (deve usar apenas duplas)")
    
    # 3. Testar importações necessárias
    print(f"\n📦 TESTANDO IMPORTAÇÕES:")
    
    imports_to_test = [
        ('google.oauth2.service_account', 'Credentials'),
        ('googleapiclient.discovery', 'build'),
        ('services.user_service', 'UserService'),
        ('services.fallback_user_service', 'FallbackUserService'),
    ]
    
    for module, item in imports_to_test:
        try:
            mod = __import__(module, fromlist=[item])
            getattr(mod, item)
            print(f"   ✅ {module}.{item}")
        except ImportError as e:
            print(f"   ❌ {module}.{item}: {e}")
        except AttributeError as e:
            print(f"   ❌ {module}.{item}: {e}")
    
    # 4. Testar conexão Google Sheets (se possível)
    if service_json and os.environ.get('GOOGLE_SHEETS_ID'):
        print(f"\n🔗 TESTANDO CONEXÃO GOOGLE SHEETS:")
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            creds_data = json.loads(service_json)
            credentials = Credentials.from_service_account_info(
                creds_data, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            print("   ✅ Serviço Google Sheets criado")
            
            # Teste básico de acesso
            sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
            try:
                spreadsheet = service.spreadsheets().get(spreadsheetId=sheets_id).execute()
                title = spreadsheet.get('properties', {}).get('title', 'N/A')
                print(f"   ✅ Planilha acessível: '{title}'")
            except Exception as sheets_error:
                print(f"   ❌ Erro ao acessar planilha: {sheets_error}")
                
        except Exception as conn_error:
            print(f"   ❌ Erro na conexão: {conn_error}")
    
    # 5. Teste do UserService
    print(f"\n👤 TESTANDO USER SERVICE:")
    try:
        from services.user_service import UserService
        sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
        
        if sheets_id:
            user_service = UserService(sheets_id)
            print("   ✅ UserService inicializado")
            
            # Teste básico (sem modificar dados)
            print("   ✅ UserService funcionando")
        else:
            print("   ❌ GOOGLE_SHEETS_ID não disponível")
            
    except Exception as user_error:
        print(f"   ❌ Erro no UserService: {user_error}")
        
        # Tentar fallback
        print("   🔄 Tentando FallbackUserService...")
        try:
            from services.fallback_user_service import FallbackUserService
            fallback_service = FallbackUserService()
            print("   ✅ FallbackUserService funcionando")
        except Exception as fallback_error:
            print(f"   ❌ FallbackUserService também falhou: {fallback_error}")
    
    print(f"\n🏁 DIAGNÓSTICO CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    render_diagnostic()
