#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para converter IDs de timestamp para numérico
"""

import sys
sys.path.append('.')
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔄 ===== CONVERSÃO SIMPLES DE IDs =====")
    
    # Carregar service
    GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    GOOGLE_SHEETS_RANGE = "Clientes!A:FP"
    service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
    print(f"✅ Service inicializado: {service.__class__.__name__}")
    
    # Buscar todos os clientes
    print("📊 Buscando clientes...")
    clients = service.get_clients()
    print(f"📊 {len(clients)} clientes encontrados")
    
    # Filtrar clientes com IDs timestamp
    clients_timestamp = []
    for client in clients:
        client_id = client.get('id', '')
        if '.' in str(client_id) and 'T' in str(client_id):
            clients_timestamp.append(client)
    
    print(f"📊 {len(clients_timestamp)} clientes com IDs timestamp encontrados")
    
    if len(clients_timestamp) == 0:
        print("✅ Todos os clientes já têm IDs numéricos!")
        return
    
    # Confirmar operação
    print(f"\n⚠️ ATENÇÃO: Esta operação irá converter {len(clients_timestamp)} IDs de timestamp para IDs numéricos sequenciais.")
    print("   Os IDs timestamp atuais serão perdidos permanentemente.")
    confirmacao = input("Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if confirmacao != 'SIM':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print("\n🔄 Iniciando conversão...")
    
    # Converter cada cliente
    id_atual = 1
    conversoes_realizadas = 0
    
    for i, client in enumerate(clients_timestamp, 1):
        nome_empresa = client.get('nomeEmpresa', 'Sem nome')
        id_antigo = client.get('id')
        
        # Atualizar ID do cliente
        client['id'] = str(id_atual)
        
        # Salvar cliente com novo ID
        try:
            result = service.save_client(client)
            if result:
                print(f"✅ [{i:3d}/{len(clients_timestamp)}] {nome_empresa[:50]:<50} | {id_antigo} → {id_atual}")
                conversoes_realizadas += 1
                id_atual += 1
            else:
                print(f"❌ Erro ao salvar {nome_empresa}")
        except Exception as e:
            print(f"❌ Erro ao converter {nome_empresa}: {e}")
    
    print(f"\n🎉 CONVERSÃO COMPLETA!")
    print(f"✅ {conversoes_realizadas} IDs convertidos com sucesso")
    
    if conversoes_realizadas > 0:
        print("\n🔍 Verificando resultado...")
        clients_verificacao = service.get_clients()
        clients_numericos = sum(1 for c in clients_verificacao if c.get('id', '').isdigit())
        print(f"✅ {clients_numericos} clientes agora têm IDs numéricos")

if __name__ == "__main__":
    main()