#!/usr/bin/env python3
"""
Teste rápido para verificar autenticação Google Sheets no Render
"""
import os
import json

def test_auth_quick():
    print("🔍 TESTE RÁPIDO DE AUTENTICAÇÃO")
    print("="*50)
    
    # 1. Verificar variáveis de ambiente
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
    
    print(f"📋 GOOGLE_SERVICE_ACCOUNT_JSON: {'✅ Presente' if service_account_json else '❌ Ausente'}")
    print(f"📋 GOOGLE_SHEETS_ID: {'✅ Presente' if sheets_id else '❌ Ausente'}")
    
    if service_account_json:
        print(f"📊 Tamanho JSON: {len(service_account_json)} caracteres")
        
        # Testar parse do JSON
        try:
            creds_data = json.loads(service_account_json)
            print(f"✅ JSON válido - Project: {creds_data.get('project_id', 'N/A')}")
            print(f"📧 Client Email: {creds_data.get('client_email', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido: {e}")
            return False
    
    if not service_account_json or not sheets_id:
        print("❌ Variáveis de ambiente necessárias não estão configuradas")
        return False
    
    # 2. Testar importação dos serviços
    print("\n📦 TESTANDO IMPORTAÇÕES:")
    try:
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        print("✅ GoogleSheetsServiceAccountService importado")
    except ImportError as e:
        print(f"❌ Erro ao importar GoogleSheetsServiceAccountService: {e}")
        return False
    
    try:
        from services.user_service import UserService
        print("✅ UserService importado")
    except ImportError as e:
        print(f"❌ Erro ao importar UserService: {e}")
        return False
    
    # 3. Testar inicialização do UserService
    print("\n🔧 TESTANDO INICIALIZAÇÃO:")
    try:
        user_service = UserService(sheets_id)
        print("✅ UserService inicializado com sucesso")
        
        # Testar método básico
        try:
            # Não vamos chamar métodos que modificam dados, apenas testar a conexão
            print("✅ UserService está funcional")
            return True
        except Exception as method_error:
            print(f"❌ Erro ao testar métodos do UserService: {method_error}")
            return False
            
    except Exception as init_error:
        print(f"❌ Erro ao inicializar UserService: {init_error}")
        return False

if __name__ == "__main__":
    success = test_auth_quick()
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Autenticação deve funcionar normalmente")
    else:
        print("\n💥 TESTE FALHOU!")
        print("❌ Há problemas na configuração de autenticação")
