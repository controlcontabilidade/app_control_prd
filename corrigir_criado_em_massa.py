import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

print("🔧 CORREÇÃO EM MASSA: Fixando todos os clientes com criadoEm = 'SIM'")

# IDs de teste  
spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"

try:
    service = GoogleSheetsServiceAccountService(spreadsheet_id=spreadsheet_id)
    print("✅ Serviço inicializado")
    
    # Buscar todos os clientes
    print("🔍 Buscando todos os clientes...")
    all_clients = service.get_clients()
    print(f"📊 Total de clientes encontrados: {len(all_clients)}")
    
    # Filtrar clientes com problema
    clientes_com_problema = []
    for client in all_clients:
        criado_em = client.get('criadoEm', '')
        if criado_em == 'SIM':
            clientes_com_problema.append(client)
    
    print(f"❌ Clientes com problema (criadoEm = 'SIM'): {len(clientes_com_problema)}")
    
    if len(clientes_com_problema) == 0:
        print("✅ Nenhum cliente com problema encontrado!")
        exit(0)
    
    # Mostrar alguns exemplos
    print(f"\n📋 Primeiros 5 clientes com problema:")
    for i, client in enumerate(clientes_com_problema[:5]):
        nome = client.get('nomeEmpresa', 'SEM NOME')[:50]
        client_id = client.get('id', 'SEM ID')
        print(f"   {i+1}. {nome} (ID: {client_id})")
    
    if len(clientes_com_problema) > 5:
        print(f"   ... e mais {len(clientes_com_problema) - 5} clientes")
    
    # Perguntar confirmação
    print(f"\n⚠️  ATENÇÃO: Será feita correção em {len(clientes_com_problema)} clientes!")
    print("📝 Estratégia de correção:")
    print("   1. Se o cliente tem ID no formato timestamp (YYYY-MM-DD...), usar o ID como criadoEm")
    print("   2. Se o ID é numérico, tentar extrair timestamp de outros campos")
    print("   3. Como último recurso, usar data padrão baseada no contexto")
    
    resposta = input(f"\n🤔 Deseja continuar com a correção? (sim/não): ").strip().lower()
    
    if resposta not in ['sim', 's', 'yes', 'y']:
        print("❌ Operação cancelada pelo usuário")
        exit(0)
    
    print(f"\n🚀 Iniciando correção de {len(clientes_com_problema)} clientes...")
    
    corrigidos = 0
    erros = 0
    
    for i, client in enumerate(clientes_com_problema, 1):
        try:
            nome = client.get('nomeEmpresa', 'SEM NOME')[:30]
            client_id = client.get('id', 'SEM ID')
            
            print(f"\n🔧 [{i}/{len(clientes_com_problema)}] Corrigindo: {nome}")
            print(f"   ID: {client_id}")
            
            # Estratégia 1: ID é timestamp
            novo_criado_em = None
            if client_id and len(str(client_id)) > 10:
                # Verificar se ID parece ser timestamp ISO
                if '-' in str(client_id) and 'T' in str(client_id):
                    novo_criado_em = str(client_id)
                    print(f"   ✅ Usando ID como criadoEm: {novo_criado_em}")
                elif str(client_id).isdigit() and len(str(client_id)) >= 10:
                    # ID é timestamp Unix?
                    try:
                        timestamp_unix = int(str(client_id)[:10])  # Primeiros 10 dígitos
                        dt = datetime.fromtimestamp(timestamp_unix)
                        novo_criado_em = dt.isoformat()
                        print(f"   ✅ ID convertido de Unix timestamp: {novo_criado_em}")
                    except:
                        pass
            
            # Estratégia 2: Verificar ultimaAtualizacao
            if not novo_criado_em:
                ultima_atualizacao = client.get('ultimaAtualizacao', '')
                if ultima_atualizacao and ultima_atualizacao != 'SIM':
                    novo_criado_em = ultima_atualizacao
                    print(f"   ✅ Usando ultimaAtualizacao como base: {novo_criado_em}")
            
            # Estratégia 3: Data padrão (2025-09-01 - início da operação atual)
            if not novo_criado_em:
                novo_criado_em = "2025-09-01T00:00:00.000000"
                print(f"   ⚠️  Usando data padrão: {novo_criado_em}")
            
            # Fazer a correção diretamente na planilha
            row_number = client.get('_row_number')
            if not row_number:
                # Buscar linha do cliente
                row_number = service.find_client_row(client_id)
            
            if row_number:
                print(f"   📍 Atualizando linha {row_number}, coluna 152 (DATA DE CRIAÇÃO)")
                
                # Calcular letra da coluna 152
                def number_to_column(n):
                    result = ""
                    while n > 0:
                        n -= 1
                        result = chr(n % 26 + ord('A')) + result
                        n //= 26
                    return result
                
                column_letter = number_to_column(152)
                cell_range = f"{column_letter}{row_number}"
                
                # Atualizar célula específica
                update_body = {
                    'values': [[novo_criado_em]]
                }
                
                result = service.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Clientes!{cell_range}",
                    valueInputOption='USER_ENTERED',
                    body=update_body
                ).execute()
                
                cells_updated = result.get('updatedCells', 0)
                if cells_updated > 0:
                    print(f"   ✅ Correção aplicada! ({cells_updated} célula atualizada)")
                    corrigidos += 1
                else:
                    print(f"   ❌ Erro: Nenhuma célula foi atualizada")
                    erros += 1
            else:
                print(f"   ❌ Erro: Não foi possível encontrar linha do cliente")
                erros += 1
                
        except Exception as e:
            print(f"   ❌ Erro ao corrigir cliente: {e}")
            erros += 1
    
    print(f"\n🎯 RESUMO DA CORREÇÃO:")
    print(f"   ✅ Clientes corrigidos: {corrigidos}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📊 Total processados: {len(clientes_com_problema)}")
    
    if corrigidos > 0:
        print(f"\n🎉 Correção concluída! {corrigidos} clientes foram corrigidos.")
        print("📝 Os clientes agora devem mostrar datas válidas no campo 'Data de Criação'")
    
    if erros > 0:
        print(f"\n⚠️  Atenção: {erros} clientes tiveram erro na correção")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()