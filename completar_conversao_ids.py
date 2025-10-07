#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para completar a conversão dos IDs restantes (127 clientes pendentes)
"""

import time
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔄 ===== COMPLETANDO CONVERSÃO DE IDs PENDENTES =====")
    
    # Carregar service
    GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    GOOGLE_SHEETS_RANGE = "Clientes!A:FP"
    service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
    print(f"✅ Service inicializado")
    
    # Buscar todos os clientes
    print("📊 Buscando clientes...")
    clients = service.get_clients()
    print(f"📊 {len(clients)} clientes encontrados")
    
    # Filtrar clientes com IDs timestamp
    clients_timestamp = []
    ids_numericos = []
    
    for client in clients:
        client_id = client.get('id', '')
        if str(client_id).isdigit():
            ids_numericos.append(int(client_id))
        elif '.' in str(client_id) and 'T' in str(client_id):
            clients_timestamp.append(client)
    
    print(f"📊 {len(clients_timestamp)} clientes com IDs timestamp encontrados")
    print(f"📊 {len(ids_numericos)} clientes já têm IDs numéricos")
    
    if len(clients_timestamp) == 0:
        print("✅ Todos os IDs já estão convertidos!")
        return
    
    # Determinar próximo ID disponível
    proximo_id = max(ids_numericos) + 1 if ids_numericos else 1
    print(f"🔢 Próximo ID disponível: {proximo_id}")
    
    # Confirmar operação
    print(f"\n⚠️ ATENÇÃO: Esta operação irá converter os {len(clients_timestamp)} IDs restantes")
    print(f"   Começando do ID {proximo_id}")
    confirmacao = input("Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if confirmacao != 'SIM':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print("\n🔄 Iniciando conversão dos IDs restantes...")
    
    # Converter cada cliente pendente
    id_atual = proximo_id
    conversoes_realizadas = 0
    total_pendentes = len(clients_timestamp)
    
    for i, client in enumerate(clients_timestamp, 1):
        nome_empresa = client.get('nomeEmpresa', 'Sem nome')
        id_antigo = client.get('id')
        
        # Atualizar ID do cliente
        client['id'] = str(id_atual)
        
        # Salvar cliente com novo ID
        try:
            print(f"🔄 [{i:3d}/{total_pendentes}] Convertendo {nome_empresa[:45]:<45} | {id_antigo} → {id_atual}")
            result = service.save_client(client)
            if result:
                print(f"✅ [{i:3d}/{total_pendentes}] {nome_empresa[:45]:<45} | Convertido para ID {id_atual}")
                conversoes_realizadas += 1
                id_atual += 1
            else:
                print(f"❌ Erro ao salvar {nome_empresa}")
                
            # Pequena pausa para evitar rate limiting
            if i % 5 == 0:
                print(f"⏸️  Pausando 2 segundos para evitar limite de API...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Erro ao converter {nome_empresa}: {e}")
            # Pausa maior em caso de erro
            time.sleep(3)
    
    print(f"\n🎉 CONVERSÃO RESTANTE COMPLETA!")
    print(f"✅ {conversoes_realizadas} IDs restantes convertidos com sucesso")
    print(f"🔢 Último ID usado: {id_atual - 1}")
    
    if conversoes_realizadas > 0:
        print("\n🔍 Verificando resultado final...")
        clients_verificacao = service.get_clients()
        clients_numericos = sum(1 for c in clients_verificacao if c.get('id', '').isdigit())
        clients_timestamp_restantes = sum(1 for c in clients_verificacao 
                                        if '.' in str(c.get('id', '')) and 'T' in str(c.get('id', '')))
        
        print(f"✅ {clients_numericos} clientes agora têm IDs numéricos")
        print(f"🔄 {clients_timestamp_restantes} clientes ainda têm IDs timestamp")
        
        if clients_timestamp_restantes == 0:
            print("🎉 TODOS OS IDs FORAM CONVERTIDOS COM SUCESSO! 🎉")

if __name__ == "__main__":
    main()