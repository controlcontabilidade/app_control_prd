#!/usr/bin/env python3
"""
Script para adicionar novos clientes diretamente no Google Sheets
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def add_new_clients():
    """Adiciona novos clientes diretamente"""
    print("🧪 === ADICIONANDO NOVOS CLIENTES ===")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        
        # Gerar timestamp único para IDs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Dados de exemplo com IDs únicos
        sample_clients = [
            {
                'id': f"CL_{timestamp}_001",
                'nomeEmpresa': 'Nova Empresa MEI',
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
                'id': f"CL_{timestamp}_002",
                'nomeEmpresa': 'Nova Empresa Simples',
                'regimeFederal': 'SIMPLES NACIONAL',
                'perfil': 'EMPRESA',
                'cnpj': '98.765.432/0001-10',
                'ativo': True,
                'ct': True,
                'fs': True,
                'dp': False,
                'bpoFinanceiro': False,
                'criadoEm': datetime.now().isoformat()
            }
        ]
        
        # Obter planilha diretamente
        sheet = service.sheet
        
        # Obter dados atuais para determinar próxima linha
        all_values = sheet.get(service.range).get('values', [])
        next_row = len(all_values) + 1
        
        print(f"📍 Próxima linha disponível: {next_row}")
        
        # Adicionar cada cliente
        for i, client in enumerate(sample_clients):
            print(f"💾 Adicionando cliente {i+1}: {client['nomeEmpresa']}")
            print(f"   ID: {client['id']}")
            
            # Converter cliente para row
            row = service.client_to_row(client)
            
            # Inserir na próxima linha
            range_name = f"Clientes!A{next_row + i}:CZ{next_row + i}"
            
            try:
                result = sheet.update(
                    range_name,
                    {'values': [row]},
                    value_input_option='USER_ENTERED'
                )
                print(f"   ✅ Cliente adicionado na linha {next_row + i}")
                
            except Exception as e:
                print(f"   ❌ Erro ao adicionar cliente: {e}")
        
        # Verificar resultado
        print(f"\n🔍 Verificando resultado...")
        clients = service.get_clients()
        print(f"📊 Total de clientes: {len(clients)}")
        
        print("\n📋 Lista atual de clientes:")
        for client in clients:
            print(f"   - {client.get('nomeEmpresa', 'N/A')} (ID: {client.get('id', 'SEM ID')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar clientes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    add_new_clients()
