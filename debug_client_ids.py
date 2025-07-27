#!/usr/bin/env python3
"""
Script para verificar os IDs dos clientes e debug das rotas
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def debug_client_ids():
    """Verifica os IDs dos clientes carregados"""
    print("🔍 === DEBUG DOS IDS DOS CLIENTES ===")
    
    try:
        # Carregar clientes
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s', 'Clientes!A:BC')
        clients = service.get_clients()
        
        print(f"📊 Total de clientes carregados: {len(clients)}")
        
        if not clients:
            print("⚠️ Nenhum cliente encontrado!")
            return
        
        print(f"\n🔍 Verificando IDs dos primeiros clientes:")
        for i, client in enumerate(clients[:5]):
            client_id = client.get('id')
            nome = client.get('nomeEmpresa', 'N/A')
            
            print(f"   Cliente {i+1}:")
            print(f"      ID: '{client_id}' (tipo: {type(client_id).__name__})")
            print(f"      Nome: {nome}")
            print(f"      ID válido: {'✅' if client_id and str(client_id).strip() else '❌'}")
            print()
        
        # Verificar se tem IDs vazios ou None
        ids_invalidos = [c for c in clients if not c.get('id') or not str(c.get('id')).strip()]
        if ids_invalidos:
            print(f"⚠️ {len(ids_invalidos)} clientes com IDs inválidos encontrados!")
        else:
            print(f"✅ Todos os clientes têm IDs válidos")
            
        return clients
        
    except Exception as e:
        print(f"❌ Erro ao carregar clientes: {e}")
        return []

if __name__ == '__main__':
    debug_client_ids()
