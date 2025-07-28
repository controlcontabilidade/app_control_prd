#!/usr/bin/env python3
"""
Script para testar as rotas de visualização e edição de clientes
"""

import requests
import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def test_client_routes():
    """Testa as rotas de visualização e edição de clientes"""
    print("🧪 === TESTANDO ROTAS DE CLIENTES ===")
    
    try:
        # Obter lista de clientes
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        clients = service.get_clients()
        
        print(f"📊 Total de clientes: {len(clients)}")
        
        # Testar com clientes que têm IDs válidos
        base_url = "http://localhost:5000"
        
        for i, client in enumerate(clients):
            client_id = client.get('id', '')
            client_name = client.get('nomeEmpresa', 'N/A')
            
            print(f"\n🧪 Teste {i+1}: {client_name}")
            print(f"   ID: {client_id}")
            
            if not client_id or client_id == '':
                print("   ⚠️ ID vazio - pulando")
                continue
            
            # Testar rota de visualização
            try:
                view_url = f"{base_url}/client/{client_id}"
                print(f"   🔍 Testando visualização: {view_url}")
                
                response = requests.get(view_url, timeout=5)
                if response.status_code == 200:
                    print("   ✅ Visualização OK")
                else:
                    print(f"   ❌ Visualização falhou: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erro na visualização: {e}")
            
            # Testar rota de edição
            try:
                edit_url = f"{base_url}/client/{client_id}/edit"
                print(f"   ✏️ Testando edição: {edit_url}")
                
                response = requests.get(edit_url, timeout=5)
                if response.status_code == 200:
                    print("   ✅ Edição OK")
                else:
                    print(f"   ❌ Edição falhou: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erro na edição: {e}")
                
        print(f"\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_client_routes()
