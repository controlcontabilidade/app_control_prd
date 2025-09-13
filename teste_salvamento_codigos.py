#!/usr/bin/env python3
"""
Teste específico para verificar se os campos de códigos estão sendo salvos corretamente
"""

import requests
import json

# URL do servidor local
BASE_URL = "http://127.0.0.1:5000"

def teste_salvamento_codigos():
    """Testa se os campos de códigos estão sendo processados corretamente"""
    
    print("🔍 Testando salvamento dos campos de códigos...")
    
    # Dados de teste para um cliente existente (simulando edição)
    form_data = {
        'id': '1',  # ID de um cliente existente
        'nomeEmpresa': 'Empresa Teste',
        'cpfCnpj': '12.345.678/0001-90',
        'codDominio': '12345',
        'codFortesCt': '67890',
        'codFortesFs': '11111',
        'codFortesPs': '22222'
    }
    
    print(f"📋 Dados que serão enviados:")
    for key, value in form_data.items():
        if 'cod' in key.lower():
            print(f"   {key}: '{value}'")
    
    try:
        # Fazer POST para /save_client
        response = requests.post(f"{BASE_URL}/save_client", data=form_data)
        
        print(f"📡 Status da resposta: {response.status_code}")
        print(f"📄 Conteúdo da resposta: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Requisição enviada com sucesso")
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor Flask está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    teste_salvamento_codigos()