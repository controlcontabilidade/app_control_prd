#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar quantos IDs ainda estão pendentes de conversão
"""

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔍 ===== VERIFICANDO IDs PENDENTES =====")
    
    # Carregar service
    GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    GOOGLE_SHEETS_RANGE = "Clientes!A:FP"
    service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
    print(f"✅ Service inicializado")
    
    # Buscar todos os clientes
    print("📊 Buscando clientes...")
    clients = service.get_clients()
    print(f"📊 {len(clients)} clientes encontrados")
    
    # Categorizar IDs
    ids_numericos = []
    ids_timestamp = []
    
    for client in clients:
        client_id = client.get('id', '')
        nome = client.get('nomeEmpresa', 'Sem nome')
        
        if str(client_id).isdigit():
            ids_numericos.append((client_id, nome))
        elif '.' in str(client_id) and 'T' in str(client_id):
            ids_timestamp.append((client_id, nome))
        else:
            print(f"⚠️ ID inválido encontrado: '{client_id}' - {nome}")
    
    print(f"\n📊 ===== RESUMO =====")
    print(f"✅ IDs numéricos: {len(ids_numericos)}")
    print(f"🔄 IDs timestamp (pendentes): {len(ids_timestamp)}")
    print(f"📊 Total: {len(clients)}")
    
    if len(ids_timestamp) > 0:
        print(f"\n🔄 ===== IDs TIMESTAMP PENDENTES =====")
        for i, (id_timestamp, nome) in enumerate(ids_timestamp[:20], 1):  # Mostrar primeiros 20
            print(f"{i:2d}. {nome[:50]:<50} | ID: {id_timestamp}")
        
        if len(ids_timestamp) > 20:
            print(f"... e mais {len(ids_timestamp) - 20} clientes pendentes")
    
    # Verificar qual seria o próximo ID numérico
    if ids_numericos:
        maior_id = max(int(id_num) for id_num, _ in ids_numericos)
        print(f"\n🔢 Maior ID numérico atual: {maior_id}")
        print(f"🔢 Próximo ID disponível: {maior_id + 1}")
    
    return len(ids_timestamp)

if __name__ == "__main__":
    pendentes = main()
    print(f"\n{'🎉 Todos os IDs estão convertidos!' if pendentes == 0 else f'⚠️ {pendentes} IDs ainda precisam ser convertidos'}")