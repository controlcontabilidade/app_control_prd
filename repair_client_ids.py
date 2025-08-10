#!/usr/bin/env python3
"""
Script para reparar IDs dos clientes na planilha
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_storage_service
import uuid
from datetime import datetime

def repair_client_ids():
    """Repara IDs dos clientes na planilha"""
    print("🔧 Reparando IDs dos Clientes na Planilha")
    print("=" * 60)
    
    try:
        # Obter serviço de armazenamento
        storage = get_storage_service()
        
        if not storage:
            print("❌ Erro: Não foi possível obter o serviço de armazenamento")
            return False
            
        # Buscar todos os clientes
        print("🔍 Buscando todos os clientes...")
        clients = storage.get_clients()
        
        if not clients:
            print("⚠️ Nenhum cliente encontrado")
            return True
            
        print(f"✅ {len(clients)} clientes encontrados")
        
        # Verificar quais clientes precisam de ID permanente
        clients_to_fix = []
        for client in clients:
            client_id = client.get('id', '')
            nome = client.get('nomeEmpresa', 'SEM_NOME')
            
            # Verificar se é ID temporário (começa com iniciais + timestamp)
            if not client_id or client_id.startswith(nome[:2].upper()) and len(client_id) > 10:
                print(f"⚠️ Cliente '{nome}' precisa de ID permanente (atual: '{client_id}')")
                clients_to_fix.append(client)
        
        if not clients_to_fix:
            print("✅ Todos os clientes já têm IDs permanentes!")
            return True
        
        print(f"\n🔧 Reparando {len(clients_to_fix)} cliente(s)...")
        
        for client in clients_to_fix:
            nome = client.get('nomeEmpresa', 'SEM_NOME')
            old_id = client.get('id', '')
            
            # Gerar ID permanente baseado no nome e timestamp
            # Formato: INICIAIS + TIMESTAMP_SIMPLIFICADO
            initials = ''.join([word[0].upper() for word in nome.split()[:3] if word])
            if len(initials) < 2:
                initials = nome[:3].upper().replace(' ', '')
            
            # Usar timestamp do momento da criação se disponível, senão atual
            timestamp = int(datetime.now().timestamp())
            permanent_id = f"{initials}{timestamp}"
            
            print(f"🔧 {nome[:30]:<30} | {old_id} → {permanent_id}")
            
            # Atualizar ID no cliente
            client['id'] = permanent_id
            
            # Salvar cliente com novo ID
            result = storage.save_client(client)
            if result:
                print(f"   ✅ ID atualizado com sucesso!")
            else:
                print(f"   ❌ Erro ao atualizar ID!")
        
        print(f"\n✅ Reparo concluído! {len(clients_to_fix)} cliente(s) atualizados.")
        
        # Verificar resultado
        print("\n🔍 Verificando resultado...")
        updated_clients = storage.get_clients()
        permanent_ids = 0
        temporary_ids = 0
        
        for client in updated_clients:
            client_id = client.get('id', '')
            nome = client.get('nomeEmpresa', 'SEM_NOME')
            
            # Verificar se ainda é temporário
            if client_id.startswith(nome[:2].upper()) and len(client_id) > 10:
                temporary_ids += 1
            else:
                permanent_ids += 1
        
        print(f"📊 Resultado final:")
        print(f"   ✅ IDs permanentes: {permanent_ids}")
        print(f"   ⚠️ IDs temporários:  {temporary_ids}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o reparo: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = repair_client_ids()
    print("\n" + "=" * 60)
    if success:
        print("✅ Reparo concluído!")
    else:
        print("❌ Reparo falhou!")
    print("=" * 60)
