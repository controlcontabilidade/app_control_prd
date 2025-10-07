#!/usr/bin/env python3
"""
Script final para corrigir o campo criadoEm de todos os clientes que têm 'ativo' ao invés de timestamp.
Este script vai fazer a correção individual de cada cliente, usando o valor do campo 'id' como timestamp.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔧 Iniciando correção final do campo criadoEm...")
    
    # Inicializar serviço
    SPREADSHEET_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    service = GoogleSheetsServiceAccountService(SPREADSHEET_ID)
    
    print("✅ Serviço inicializado")
    
    # Buscar todos os clientes
    print("\n📊 ===== BUSCANDO CLIENTES =====")
    clients = service.get_clients()
    
    if not clients:
        print("❌ Nenhum cliente encontrado!")
        return
    
    print(f"📊 Total de clientes: {len(clients)}")
    
    # Encontrar clientes com problema
    problematic_clients = []
    for client in clients:
        if client.get('criadoEm') == 'ativo':
            problematic_clients.append(client)
    
    print(f"🔍 Clientes com criadoEm='ativo': {len(problematic_clients)}")
    
    if not problematic_clients:
        print("✅ Nenhum cliente com problema encontrado!")
        return
    
    # Corrigir cada cliente individualmente
    print("\n🔧 ===== INICIANDO CORREÇÕES =====")
    corrections_made = 0
    
    for i, client in enumerate(problematic_clients, 1):
        client_id = client.get('id')
        client_name = client.get('nomeEmpresa', 'NOME_NAO_ENCONTRADO')
        
        if not client_id:
            print(f"⚠️  Cliente {i}: '{client_name}' - ID não encontrado, pulando...")
            continue
        
        print(f"🔧 Cliente {i}/{len(problematic_clients)}: '{client_name}' - ID: {client_id}")
        
        # Atualizar o campo criadoEm com o valor do ID
        client['criadoEm'] = client_id
        
        # Salvar cliente individual
        try:
            result = service.save_client(client)
            if result and result.get('success'):
                corrections_made += 1
                print(f"   ✅ Corrigido com sucesso!")
            else:
                error_msg = result.get('message', 'Erro desconhecido') if result else 'Falha na operação'
                print(f"   ❌ Erro: {error_msg}")
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")
    
    print(f"\n📊 ===== RESUMO FINAL =====")
    print(f"📊 Clientes com problema encontrados: {len(problematic_clients)}")
    print(f"📊 Correções aplicadas: {corrections_made}")
    print(f"📊 Taxa de sucesso: {(corrections_made/len(problematic_clients)*100):.1f}%")
    
    # Verificação final
    print(f"\n🔍 ===== VERIFICAÇÃO FINAL =====")
    print("🔍 Recarregando dados para verificar correções...")
    
    # Recarregar dados
    clients_after = service.get_clients()
    if not clients_after:
        print("❌ Erro ao recarregar dados para verificação!")
        return
    
    # Verificar se ainda há problemas
    still_problematic = []
    for client in clients_after:
        if client.get('criadoEm') == 'ativo':
            still_problematic.append(client)
    
    print(f"📊 Clientes que ainda têm problemas: {len(still_problematic)}")
    
    if still_problematic:
        print("\n❌ Ainda há clientes com problemas:")
        for i, client in enumerate(still_problematic[:5], 1):  # Mostrar apenas os primeiros 5
            client_name = client.get('nomeEmpresa', 'NOME_NAO_ENCONTRADO')
            client_id = client.get('id', 'ID_NAO_ENCONTRADO')
            print(f"   {i}. {client_name} - ID: {client_id}")
        
        if len(still_problematic) > 5:
            print(f"   ... e mais {len(still_problematic) - 5} clientes")
    else:
        print("✅ Todos os problemas foram corrigidos!")
    
    print("\n🎉 Processo finalizado!")

if __name__ == "__main__":
    main()