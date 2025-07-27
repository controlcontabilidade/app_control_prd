#!/usr/bin/env python3
"""
Script para corrigir IDs vazios dos clientes
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def fix_client_ids():
    """Corrige os IDs vazios dos clientes"""
    print("🔧 === CORRIGINDO IDS DOS CLIENTES ===")
    
    try:
        # Carregar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:BC')
        
        # Carregar clientes
        clients = service.get_clients()
        print(f"📊 Total de clientes: {len(clients)}")
        
        if not clients:
            print("⚠️ Nenhum cliente encontrado!")
            return
        
        # Identificar clientes com IDs vazios
        clients_sem_id = [c for c in clients if not c.get('id') or not str(c.get('id')).strip()]
        print(f"🔍 Clientes sem ID: {len(clients_sem_id)}")
        
        if not clients_sem_id:
            print("✅ Todos os clientes já têm IDs válidos!")
            return
        
        # Corrigir IDs
        sucesso = 0
        for i, client in enumerate(clients_sem_id):
            nome = client.get('nomeEmpresa', 'N/A')
            
            # Gerar ID único baseado em timestamp
            novo_id = str(int(datetime.now().timestamp() * 1000) + i)  # Adicionar offset para evitar duplicatas
            
            print(f"🔧 Corrigindo cliente '{nome}':")
            print(f"   ID antigo: '{client.get('id')}'")
            print(f"   ID novo: '{novo_id}'")
            
            # Atualizar cliente
            client['id'] = novo_id
            
            # Salvar no Google Sheets
            if service.save_client(client):
                sucesso += 1
                print(f"   ✅ ID corrigido com sucesso!")
            else:
                print(f"   ❌ Erro ao corrigir ID")
            
            print()
        
        print(f"🎉 Correção concluída: {sucesso}/{len(clients_sem_id)} IDs corrigidos!")
        
        # Verificar resultado
        print(f"\n🔍 Verificando resultado...")
        clients_atualizados = service.get_clients()
        ids_vazios = [c for c in clients_atualizados if not c.get('id') or not str(c.get('id')).strip()]
        
        if not ids_vazios:
            print("✅ Todos os clientes agora têm IDs válidos!")
        else:
            print(f"⚠️ Ainda existem {len(ids_vazios)} clientes sem ID válido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir IDs: {e}")
        return False

if __name__ == '__main__':
    fix_client_ids()
