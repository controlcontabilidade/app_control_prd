#!/usr/bin/env python3
"""
Script para testar salvamento de cliente com autenticação
"""

import requests
import sys
sys.path.append('.')

def test_authenticated_save():
    """Testa salvamento com autenticação"""
    print("🧪 === TESTANDO SALVAMENTO COM AUTENTICAÇÃO ===")
    
    try:
        session = requests.Session()
        base_url = 'http://localhost:5000'
        
        # 1. Fazer login
        print("🔐 Fazendo login...")
        login_data = {
            'username': 'admin',
            'password': '123456'
        }
        
        login_response = session.post(f'{base_url}/login', data=login_data, allow_redirects=False)
        print(f"📨 Login status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("✅ Login bem-sucedido!")
        else:
            print("❌ Falha no login")
            print(f"Response: {login_response.text[:200]}")
            return False
        
        # 2. Testar salvamento de cliente
        print("\n💾 Testando salvamento de cliente...")
        
        client_data = {
            # Campos obrigatórios
            'nomeEmpresa': 'Teste Cliente Web',
            'razaoSocialReceita': 'Teste Cliente Web LTDA',
            'nomeFantasiaReceita': 'Teste Web',
            'cpfCnpj': '11.222.333/0001-44',
            'perfil': 'EMPRESA',
            'inscEst': '123456789',
            'inscMun': '987654321',
            'estado': 'CE',
            'cidade': 'Fortaleza',
            'regimeFederal': 'SIMPLES NACIONAL',
            'regimeEstadual': 'SIMPLES NACIONAL',
            'segmento': 'SERVICOS',
            'atividade': 'Teste de Salvamento',
            
            # Campos opcionais
            'ct': 'on',
            'fs': 'on',
            'ativo': 'on',
            'telefoneFixo': '(85) 1111-2222',
            'emailPrincipal': 'teste.web@exemplo.com'
        }
        
        save_response = session.post(f'{base_url}/client', data=client_data, allow_redirects=False)
        print(f"📨 Save status: {save_response.status_code}")
        
        if save_response.status_code == 302:
            print("✅ Cliente salvo com sucesso!")
            redirect_url = save_response.headers.get('Location', '')
            print(f"🔄 Redirecionado para: {redirect_url}")
        else:
            print("❌ Falha no salvamento")
            print(f"Response: {save_response.text[:500]}")
        
        # 3. Verificar se cliente foi salvo na planilha
        print("\n🔍 Verificando se cliente foi salvo...")
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        clients = service.get_clients()
        
        print(f"📊 Total de clientes após salvamento: {len(clients)}")
        
        # Procurar pelo cliente que acabamos de criar
        found_client = None
        for client in clients:
            if client.get('nomeEmpresa') == 'Teste Cliente Web':
                found_client = client
                break
        
        if found_client:
            print("✅ Cliente encontrado na planilha!")
            print(f"   Nome: {found_client.get('nomeEmpresa')}")
            print(f"   ID: {found_client.get('id')}")
            print(f"   CNPJ: {found_client.get('cnpj')}")
        else:
            print("❌ Cliente não encontrado na planilha")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_client_edit():
    """Testa edição de cliente autenticado"""
    print("\n🧪 === TESTANDO EDIÇÃO COM AUTENTICAÇÃO ===")
    
    try:
        session = requests.Session()
        base_url = 'http://localhost:5000'
        
        # 1. Fazer login
        login_data = {
            'username': 'admin',
            'password': '123456'
        }
        session.post(f'{base_url}/login', data=login_data)
        
        # 2. Obter cliente para editar
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        clients = service.get_clients()
        
        if not clients:
            print("❌ Nenhum cliente disponível para edição")
            return False
        
        client = clients[0]
        client_id = client.get('id')
        original_name = client.get('nomeEmpresa')
        
        print(f"✏️ Editando cliente: {original_name} (ID: {client_id})")
        
        # 3. Preparar dados editados
        edited_data = client.copy()
        edited_data['nomeEmpresa'] = f"{original_name} - EDITADO"
        edited_data['emailPrincipal'] = 'editado.web@exemplo.com'
        edited_data['telefoneFixo'] = '(85) 9999-9999'
        
        # 4. Enviar edição
        edit_response = session.post(f'{base_url}/client', data=edited_data, allow_redirects=False)
        print(f"📨 Edit status: {edit_response.status_code}")
        
        if edit_response.status_code == 302:
            print("✅ Edição bem-sucedida!")
        else:
            print("❌ Falha na edição")
            print(f"Response: {edit_response.text[:500]}")
        
        # 5. Verificar se foi editado
        updated_clients = service.get_clients()
        updated_client = next((c for c in updated_clients if c.get('id') == client_id), None)
        
        if updated_client and updated_client.get('nomeEmpresa') != original_name:
            print("✅ Cliente editado com sucesso na planilha!")
            print(f"   Nome original: {original_name}")
            print(f"   Nome atual: {updated_client.get('nomeEmpresa')}")
        else:
            print("❌ Edição não refletida na planilha")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de edição: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 === INICIANDO TESTES COM AUTENTICAÇÃO ===")
    
    # Teste 1: Salvamento
    test_authenticated_save()
    
    # Teste 2: Edição
    test_client_edit()
    
    print("\n🏁 === TESTES CONCLUÍDOS ===")
