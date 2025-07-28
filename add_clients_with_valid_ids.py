#!/usr/bin/env python3
"""
Script para adicionar novos clientes com IDs válidos
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def add_clients_with_valid_ids():
    """Adiciona novos clientes com IDs válidos"""
    print("🧪 === ADICIONANDO CLIENTES COM IDS VÁLIDOS ===")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        
        # Gerar timestamp único para IDs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Dados de exemplo com IDs únicos - SEM campo 'id' para forçar criação
        sample_clients = [
            {
                'nomeEmpresa': 'Nova Empresa MEI Test',
                'regimeFederal': 'MEI',
                'perfil': 'MICROEMPREENDEDOR INDIVIDUAL',
                'cnpj': '12.345.678/0001-90',
                'ativo': True,
                'ct': True,
                'fs': False,
                'dp': False,
                'bpoFinanceiro': False
            },
            {
                'nomeEmpresa': 'Nova Empresa Simples Test',
                'regimeFederal': 'SIMPLES NACIONAL',
                'perfil': 'EMPRESA',
                'cnpj': '98.765.432/0001-10',
                'ativo': True,
                'ct': True,
                'fs': True,
                'dp': False,
                'bpoFinanceiro': False
            },
            {
                'nomeEmpresa': 'Nova Empresa Presumido Test',
                'regimeFederal': 'LUCRO PRESUMIDO',
                'perfil': 'EMPRESA',
                'cnpj': '11.222.333/0001-44',
                'ativo': True,
                'ct': False,
                'fs': True,
                'dp': True,
                'bpoFinanceiro': True
            }
        ]
        
        # Adicionar cada cliente
        sucessos = 0
        for i, client in enumerate(sample_clients, 1):
            print(f"\n💾 Criando cliente {i}: {client['nomeEmpresa']}")
            
            # Usar save_client que deve detectar novo cliente e gerar ID
            if service.save_client(client):
                sucessos += 1
                print(f"   ✅ Cliente criado com sucesso!")
            else:
                print(f"   ❌ Erro ao criar cliente")
        
        print(f"\n🎉 {sucessos}/{len(sample_clients)} clientes criados!")
        
        # Verificar resultado
        print(f"\n🔍 Verificando resultado...")
        clients = service.get_clients()
        print(f"📊 Total de clientes: {len(clients)}")
        
        print("\n📋 Lista atual de clientes:")
        for client in clients:
            client_id = client.get('id', 'SEM ID')
            client_name = client.get('nomeEmpresa', 'N/A')
            print(f"   - {client_name} (ID: {client_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar clientes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    add_clients_with_valid_ids()
