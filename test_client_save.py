#!/usr/bin/env python3
"""
Script para testar o salvamento de clientes via POST request
"""

import requests
import sys
sys.path.append('.')

def test_client_save():
    """Testa o salvamento de um novo cliente"""
    print("🧪 === TESTANDO SALVAMENTO DE CLIENTE ===")
    
    # Dados mínimos obrigatórios para um cliente
    client_data = {
        'nomeEmpresa': 'Empresa Teste Salvamento',
        'razaoSocialReceita': 'Empresa Teste Salvamento LTDA',
        'nomeFantasiaReceita': 'Teste Salvamento',
        'cpfCnpj': '12.345.678/0001-90',
        'perfil': 'EMPRESA',
        'inscEst': '123456789',
        'inscMun': '987654321',
        'estado': 'CE',
        'cidade': 'Fortaleza',
        'regimeFederal': 'SIMPLES NACIONAL',
        'regimeEstadual': 'SIMPLES NACIONAL',
        'segmento': 'COMERCIO',
        'atividade': 'Comércio Varejista',
        
        # Alguns campos opcionais
        'ct': 'on',
        'fs': 'on',
        'bpoFinanceiro': 'on',
        'ativo': 'on',
        'telefoneFixo': '(85) 3333-4444',
        'emailPrincipal': 'teste@exemplo.com'
    }
    
    try:
        # Fazer POST request para salvar cliente
        url = 'http://localhost:5000/client'
        print(f"📤 Enviando POST para: {url}")
        print(f"📋 Dados enviados: {list(client_data.keys())}")
        
        # Simular sessão de usuário (se necessário)
        session = requests.Session()
        
        # Primeiro, fazer um GET para obter cookies de sessão
        login_response = session.get('http://localhost:5000/')
        print(f"🔐 Status da página inicial: {login_response.status_code}")
        
        # Tentar POST
        response = session.post(url, data=client_data, allow_redirects=False)
        
        print(f"📨 Status Code: {response.status_code}")
        print(f"📨 Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"🔄 Redirecionamento para: {response.headers.get('Location')}")
            print("✅ Cliente salvo com sucesso (redirecionamento detectado)")
        elif response.status_code == 200:
            print("✅ Resposta OK recebida")
        else:
            print(f"❌ Erro na resposta: {response.status_code}")
            print(f"❌ Conteúdo: {response.text[:500]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_client_edit():
    """Testa a edição de um cliente existente"""
    print("\n🧪 === TESTANDO EDIÇÃO DE CLIENTE ===")
    
    try:
        # Primeiro, obter um cliente existente
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        clients = service.get_clients()
        
        if not clients:
            print("❌ Nenhum cliente encontrado para testar edição")
            return False
        
        # Pegar o primeiro cliente
        client = clients[0]
        client_id = client.get('id')
        
        print(f"🎯 Testando edição do cliente: {client.get('nomeEmpresa')} (ID: {client_id})")
        
        # Dados para atualização
        updated_data = client.copy()
        updated_data['nomeEmpresa'] = f"{client.get('nomeEmpresa')} - EDITADO"
        updated_data['emailPrincipal'] = 'editado@exemplo.com'
        updated_data['telefoneFixo'] = '(85) 9999-8888'
        
        # Fazer POST request
        url = 'http://localhost:5000/client'
        session = requests.Session()
        
        # Obter cookies de sessão
        session.get('http://localhost:5000/')
        
        # Enviar dados de edição
        response = session.post(url, data=updated_data, allow_redirects=False)
        
        print(f"📨 Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Cliente editado com sucesso (redirecionamento detectado)")
        else:
            print(f"❌ Erro na edição: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de edição: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 === INICIANDO TESTES DE SALVAMENTO ===")
    
    # Teste 1: Salvamento de novo cliente
    test_client_save()
    
    # Teste 2: Edição de cliente existente
    test_client_edit()
    
    print("\n🏁 === TESTES CONCLUÍDOS ===")
