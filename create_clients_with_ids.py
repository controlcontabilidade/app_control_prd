#!/usr/bin/env python3
"""
Script para criar novos clientes com IDs válidos
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def create_clients_with_ids():
    """Cria novos clientes de exemplo com IDs válidos"""
    print("🧪 === CRIANDO CLIENTES COM IDS VÁLIDOS ===")
    
    try:
        # Inicializar serviço com range expandido
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        
        # Limpar dados existentes primeiro (opcional)
        print("🗑️ Limpando dados existentes...")
        
        # Dados de exemplo com IDs válidos
        sample_clients = [
            {
                'id': f"CL_{datetime.now().strftime('%Y%m%d')}_001",
                'nomeEmpresa': 'Empresa MEI Teste',
                'regimeFederal': 'MEI',
                'perfil': 'MICROEMPREENDEDOR INDIVIDUAL',
                'cnpj': '12.345.678/0001-90',
                'ativo': True,
                'ct': True,
                'fs': False,
                'dp': False,
                'bpoFinanceiro': False,
                'criadoEm': datetime.now().isoformat()
            },
            {
                'id': f"CL_{datetime.now().strftime('%Y%m%d')}_002",
                'nomeEmpresa': 'Empresa Simples Nacional Teste',
                'regimeFederal': 'SIMPLES NACIONAL',
                'perfil': 'EMPRESA',
                'cnpj': '98.765.432/0001-10',
                'ativo': True,
                'ct': True,
                'fs': True,
                'dp': False,
                'bpoFinanceiro': False,
                'criadoEm': datetime.now().isoformat()
            },
            {
                'id': f"CL_{datetime.now().strftime('%Y%m%d')}_003",
                'nomeEmpresa': 'Empresa Lucro Presumido Teste',
                'regimeFederal': 'LUCRO PRESUMIDO',
                'perfil': 'EMPRESA',
                'cnpj': '11.222.333/0001-44',
                'ativo': True,
                'ct': False,
                'fs': True,
                'dp': True,
                'bpoFinanceiro': True,
                'criadoEm': datetime.now().isoformat()
            }
        ]
        
        # Criar cada cliente
        sucessos = 0
        for i, client in enumerate(sample_clients, 1):
            print(f"💾 Criando cliente {i}: {client['nomeEmpresa']}")
            print(f"   ID: {client['id']}")
            
            if service.save_client(client):
                sucessos += 1
                print(f"   ✅ Cliente criado com sucesso!")
            else:
                print(f"   ❌ Erro ao criar cliente")
            
            print()
        
        print(f"🎉 {sucessos}/{len(sample_clients)} clientes criados!")
        
        # Verificar resultado
        print(f"\n🔍 Verificando clientes criados...")
        clients = service.get_clients()
        print(f"📊 Total de clientes: {len(clients)}")
        
        for client in clients:
            print(f"   - {client.get('nomeEmpresa', 'N/A')} (ID: {client.get('id', 'SEM ID')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar clientes: {e}")
        return False

if __name__ == '__main__':
    create_clients_with_ids()
