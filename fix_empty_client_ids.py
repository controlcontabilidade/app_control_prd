#!/usr/bin/env python3
"""
Script para corrigir IDs vazios dos clientes existentes
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def fix_empty_client_ids():
    """Corrige IDs vazios dos clientes existentes"""
    print("🧪 === CORRIGINDO IDS VAZIOS ===")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:CZ')
        
        # Obter todos os clientes
        clients = service.get_clients()
        print(f"📊 Total de clientes: {len(clients)}")
        
        # Identificar clientes com IDs problemáticos
        clients_to_fix = []
        for client in clients:
            client_id = client.get('id', '')
            client_name = client.get('nomeEmpresa', 'N/A')
            
            # Verificar se ID está vazio ou é inválido
            if not client_id or client_id.strip() == '' or client_id == 'None':
                clients_to_fix.append(client)
                print(f"⚠️ Cliente com ID vazio: {client_name}")
        
        print(f"\n🔧 {len(clients_to_fix)} clientes precisam de correção")
        
        if not clients_to_fix:
            print("✅ Todos os clientes já têm IDs válidos!")
            return True
        
        # Corrigir cada cliente
        base_timestamp = int(datetime.now().timestamp())
        fixed_count = 0
        
        for i, client in enumerate(clients_to_fix):
            client_name = client.get('nomeEmpresa', 'N/A')
            new_id = str(base_timestamp + i + 100)  # Garantir IDs únicos
            
            print(f"\n🔧 Corrigindo: {client_name}")
            print(f"   Novo ID: {new_id}")
            
            # Atualizar o ID
            client['id'] = new_id
            
            # Salvar cliente atualizado
            if service.save_client(client):
                fixed_count += 1
                print(f"   ✅ ID corrigido com sucesso!")
            else:
                print(f"   ❌ Erro ao corrigir ID")
        
        print(f"\n🎉 {fixed_count}/{len(clients_to_fix)} IDs corrigidos!")
        
        # Verificar resultado final
        print(f"\n🔍 Verificação final...")
        updated_clients = service.get_clients()
        
        print(f"📋 Lista final de clientes:")
        for client in updated_clients:
            client_id = client.get('id', 'SEM ID')
            client_name = client.get('nomeEmpresa', 'N/A')
            status = "✅" if client_id and client_id != '' and client_id != 'None' else "❌"
            print(f"   {status} {client_name} (ID: {client_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir IDs: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    fix_empty_client_ids()
