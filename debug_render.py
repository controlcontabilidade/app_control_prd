#!/usr/bin/env python3
"""
Script de debug para verificar configuração no Render
"""
import os
import json
import sys

def debug_render_environment():
    """Debug das configurações do Render"""
    print("🔍 ===== DEBUG RENDER ENVIRONMENT =====")
    
    # 1. Verificar variáveis de ambiente críticas
    print("\n📋 VARIÁVEIS DE AMBIENTE:")
    
    # Google Service Account
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_json:
        print(f"✅ GOOGLE_SERVICE_ACCOUNT_JSON: Presente ({len(service_account_json)} chars)")
        try:
            creds_info = json.loads(service_account_json)
            print(f"   📊 Project ID: {creds_info.get('project_id', 'N/A')}")
            print(f"   📊 Client Email: {creds_info.get('client_email', 'N/A')}")
            print(f"   📊 Chaves disponíveis: {list(creds_info.keys())}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Erro ao parsear JSON: {e}")
            print(f"   🔍 Primeiros 100 chars: {service_account_json[:100]}")
    else:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON: Não encontrada")
    
    # Google Sheets ID
    sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
    if sheets_id:
        print(f"✅ GOOGLE_SHEETS_ID: {sheets_id}")
    else:
        print("❌ GOOGLE_SHEETS_ID: Não encontrada")
    
    # Flask Environment
    flask_env = os.environ.get('FLASK_ENV', 'production')
    print(f"📊 FLASK_ENV: {flask_env}")
    
    # Python Path
    print(f"📊 Python Path: {sys.executable}")
    print(f"📊 Python Version: {sys.version}")
    
    # 2. Testar importações
    print("\n📦 TESTANDO IMPORTAÇÕES:")
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google.oauth2.service_account: OK")
    except ImportError as e:
        print(f"❌ google.oauth2.service_account: {e}")
    
    try:
        from googleapiclient.discovery import build
        print("✅ googleapiclient.discovery: OK")
    except ImportError as e:
        print(f"❌ googleapiclient.discovery: {e}")
    
    # 3. Testar conexão com Google Sheets (se credenciais estão OK)
    if service_account_json and sheets_id:
        print("\n🔍 TESTANDO CONEXÃO COM GOOGLE SHEETS:")
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            creds_info = json.loads(service_account_json)
            credentials = Credentials.from_service_account_info(
                creds_info, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            service = build('sheets', 'v4', credentials=credentials)
            print("✅ Serviço Google Sheets criado")
            
            # Testar acesso à planilha
            try:
                spreadsheet = service.spreadsheets().get(
                    spreadsheetId=sheets_id
                ).execute()
                
                sheet_title = spreadsheet.get('properties', {}).get('title', 'N/A')
                sheet_count = len(spreadsheet.get('sheets', []))
                print(f"✅ Planilha acessível: '{sheet_title}' ({sheet_count} abas)")
                
                # Testar leitura de dados
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheets_id,
                    range='Clientes!A1:A10'
                ).execute()
                
                values = result.get('values', [])
                print(f"✅ Dados lidos: {len(values)} linhas")
                
                if values:
                    print(f"   📊 Primeira linha: {values[0] if values[0] else 'vazia'}")
                
            except Exception as sheets_error:
                print(f"❌ Erro ao acessar planilha: {sheets_error}")
                
        except Exception as conn_error:
            print(f"❌ Erro na conexão: {conn_error}")
    
    print("\n🏁 ===== FIM DO DEBUG =====")

if __name__ == "__main__":
    debug_render_environment()
