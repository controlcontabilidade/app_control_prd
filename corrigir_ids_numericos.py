#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir IDs numéricos na coluna ID dos clientes
Converte IDs numéricos (formato antigo) para timestamps válidos
"""

import sys
import os
from datetime import datetime
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def corrigir_ids_numericos():
    print("🔧 Corrigindo IDs numéricos na coluna ID dos clientes...")
    
    # Inicializar serviço
    SPREADSHEET_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    service = GoogleSheetsServiceAccountService(SPREADSHEET_ID)
    print(f"🔧 Service Account Service inicializado para planilha: {service.spreadsheet_id}")
    
    try:
        # Buscar todos os clientes
        print("📊 Buscando todos os clientes...")
        clients = service.get_clients()
        
        if not clients:
            print("❌ Nenhum cliente encontrado!")
            return False
            
        print(f"📊 Total de clientes encontrados: {len(clients)}")
        
        # Identificar clientes com IDs numéricos
        clientes_com_problema = []
        
        for i, client in enumerate(clients, 1):
            client_id = client.get('id', '')
            nome = client.get('nomeEmpresa', 'SEM NOME')
            
            # Verificar se é ID numérico (formato antigo)
            if client_id and client_id.isdigit():
                clientes_com_problema.append({
                    'cliente': client,
                    'linha': i + 1,  # +1 porque linha 1 é cabeçalho
                    'nome': nome,
                    'id_antigo': client_id,
                    'indice': i - 1  # índice na lista de clientes
                })
        
        if not clientes_com_problema:
            print("✅ Nenhum cliente com ID numérico encontrado!")
            return True
            
        print(f"🔧 Encontrados {len(clientes_com_problema)} clientes com IDs numéricos para corrigir")
        
        # Corrigir cada cliente
        correções_realizadas = 0
        
        for i, problema in enumerate(clientes_com_problema, 1):
            cliente = problema['cliente']
            nome = problema['nome']
            id_antigo = problema['id_antigo']
            
            print(f"🔧 Cliente {i}/{len(clientes_com_problema)}: '{nome}' - ID antigo: {id_antigo}")
            
            try:
                # Gerar novo timestamp ISO
                novo_timestamp = datetime.now().isoformat()
                
                # Atualizar o ID do cliente
                cliente['id'] = novo_timestamp
                
                # Salvar cliente com novo ID
                print(f"   🔄 Atualizando ID para: {novo_timestamp}")
                resultado = service.save_client(cliente)
                
                if resultado:
                    print(f"   ✅ Cliente atualizado com sucesso!")
                    correções_realizadas += 1
                else:
                    print(f"   ❌ Erro ao atualizar cliente: {resultado}")
                    
            except Exception as e:
                print(f"   ❌ Exceção ao corrigir cliente '{nome}': {e}")
                continue
        
        print(f"\n📊 ===== RESUMO FINAL =====")
        print(f"📊 Clientes com problema encontrados: {len(clientes_com_problema)}")
        print(f"📊 Correções realizadas: {correções_realizadas}")
        print(f"📊 Taxa de sucesso: {(correções_realizadas/len(clientes_com_problema)*100):.1f}%")
        
        return correções_realizadas == len(clientes_com_problema)
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        import traceback
        print(f"❌ Tipo do erro: {type(e).__name__}")
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        return False

def verificar_correcoes():
    """Verificar se as correções foram aplicadas com sucesso"""
    print("\n🔍 ===== VERIFICAÇÃO FINAL =====")
    print("🔍 Recarregando dados para verificar correções...")
    
    try:
        SPREADSHEET_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
        service = GoogleSheetsServiceAccountService(SPREADSHEET_ID)
        clients = service.get_clients()
        
        if not clients:
            print("❌ Erro ao recarregar dados para verificação!")
            return False
        
        # Contar IDs numéricos restantes
        ids_numericos_restantes = 0
        
        for client in clients:
            client_id = client.get('id', '')
            if client_id and client_id.isdigit():
                ids_numericos_restantes += 1
        
        print(f"📊 IDs numéricos restantes: {ids_numericos_restantes}")
        
        if ids_numericos_restantes == 0:
            print("🎉 Todos os IDs foram corrigidos com sucesso!")
            return True
        else:
            print(f"⚠️ Ainda restam {ids_numericos_restantes} IDs numéricos para corrigir")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao recarregar dados para verificação: {e}")
        return False

if __name__ == "__main__":
    try:
        sucesso = corrigir_ids_numericos()
        
        if sucesso:
            print("\n✅ Todas as correções foram aplicadas com sucesso!")
        else:
            print("\n⚠️ Algumas correções falharam. Execute novamente se necessário.")
            
        # Verificar resultado final
        verificar_correcoes()
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")