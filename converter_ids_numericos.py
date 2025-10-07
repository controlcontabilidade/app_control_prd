#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuração
os.environ['FLASK_ENV'] = 'development'  
os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'] = ''  # Usar arquivo local

# Importar dependências
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def converter_ids_para_numericos():
    """Converte todos os IDs de timestamp para IDs numéricos sequenciais"""
    print("🔄 ===== CONVERSÃO DE IDs PARA FORMATO NUMÉRICO =====")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        print("✅ Service inicializado")
        
        # Buscar todos os clientes
        clients = service.get_clients()
        print(f"📊 {len(clients)} clientes encontrados")
        
        if not clients:
            print("❌ Nenhum cliente encontrado para converter")
            return
            
        # Separar clientes com IDs de timestamp vs IDs já numéricos
        clients_timestamp = []
        clients_numericos = []
        
        for client in clients:
            client_id = client.get('id', '')
            
            # Verificar se é timestamp (contém "-" ou "T" ou ":" indicando formato ISO)
            if any(char in str(client_id) for char in ['-', 'T', ':']):
                clients_timestamp.append(client)
            else:
                # Verificar se é numérico
                try:
                    int(client_id)
                    clients_numericos.append(client)
                except (ValueError, TypeError):
                    print(f"⚠️ Cliente com ID não reconhecido: {client_id} - {client.get('nomeEmpresa', 'N/A')}")
                    clients_timestamp.append(client)  # Tratar como timestamp para conversão
        
        print(f"📊 Clientes com IDs timestamp: {len(clients_timestamp)}")
        print(f"📊 Clientes com IDs numéricos: {len(clients_numericos)}")
        
        if len(clients_timestamp) == 0:
            print("✅ Todos os clientes já possuem IDs numéricos!")
            return
            
        # Determinar próximo ID numérico disponível
        proximo_id = 1
        if clients_numericos:
            ids_existentes = []
            for client in clients_numericos:
                try:
                    id_num = int(client['id'])
                    ids_existentes.append(id_num)
                except (ValueError, TypeError):
                    pass
            
            if ids_existentes:
                proximo_id = max(ids_existentes) + 1
                
        print(f"🔢 Próximo ID numérico disponível: {proximo_id}")
        
        # Confirmar operação
        print(f"\n⚠️ ATENÇÃO: Esta operação irá converter {len(clients_timestamp)} IDs de timestamp para IDs numéricos.")
        print("   Os IDs timestamp atuais serão perdidos permanentemente.")
        confirmacao = input("Deseja continuar? (digite 'SIM' para confirmar): ")
        
        if confirmacao.strip().upper() != 'SIM':
            print("❌ Operação cancelada pelo usuário")
            return
            
        # Preparar dados para atualização em lote
        range_name = "Clientes!A:FP"
        
        try:
            # Buscar dados brutos da planilha
            print("📊 Buscando dados da planilha...")
            values = service._get_all_values()
            print(f"📊 {len(values)} linhas encontradas na planilha")
            
            if len(values) < 2:
                print("❌ Planilha não contém dados suficientes")
                return
                
            headers = values[0]
            
            # Encontrar coluna do ID
            try:
                id_col_index = headers.index('ID')
                print(f"📍 Coluna ID encontrada no índice: {id_col_index}")
            except ValueError:
                print("❌ Coluna ID não encontrada nos cabeçalhos")
                return
                
            # Processar conversões
            conversoes_realizadas = 0
            id_atual = proximo_id
            
            print(f"\n🔄 Iniciando conversão de {len(clients_timestamp)} clientes...")
            
            for i, client in enumerate(clients_timestamp, 1):
                nome_empresa = client.get('nomeEmpresa', 'N/A')
                id_antigo = client.get('id', 'N/A')
                
                # Encontrar linha do cliente na planilha
                linha_encontrada = None
                for row_idx, row in enumerate(values[1:], start=2):  # Pular cabeçalho
                    if len(row) > id_col_index and row[id_col_index] == id_antigo:
                        linha_encontrada = row_idx
                        break
                        
                if linha_encontrada is None:
                    print(f"⚠️ Linha não encontrada para cliente: {nome_empresa} (ID: {id_antigo})")
                    continue
                    
                # Atualizar ID na planilha
                novo_id = str(id_atual)
                cell_range = f"Clientes!{chr(65 + id_col_index)}{linha_encontrada}"
                
                try:
                    # Usar método interno do service para atualizar
                    service._update_cell_direct(cell_range, novo_id)
                    
                    print(f"✅ [{i:3d}/{len(clients_timestamp)}] {nome_empresa[:50]:<50} | {id_antigo} → {novo_id}")
                    conversoes_realizadas += 1
                    id_atual += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao atualizar {nome_empresa}: {e}")
                    
            print(f"\n🎉 CONVERSÃO COMPLETA!")
            print(f"✅ {conversoes_realizadas} IDs convertidos com sucesso")
            print(f"📊 Próximo ID disponível: {id_atual}")
            
            if conversoes_realizadas < len(clients_timestamp):
                falhas = len(clients_timestamp) - conversoes_realizadas
                print(f"⚠️ {falhas} conversões falharam")
                
        except Exception as e:
            print(f"❌ Erro durante conversão em lote: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    converter_ids_para_numericos()