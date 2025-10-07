import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

print("🆕 TESTE: Criando cliente novo para verificar se criadoEm é salvo corretamente")

# IDs de teste  
spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"

try:
    service = GoogleSheetsServiceAccountService(spreadsheet_id=spreadsheet_id)
    print("✅ Serviço inicializado")
    
    # Criar cliente novo
    timestamp_teste = datetime.now().strftime("%H:%M:%S")
    novo_cliente = {
        'nomeEmpresa': f'TESTE DATA CRIAÇÃO {timestamp_teste}',
        'cnpj': '00.000.000/0001-88',
        'razaoSocialReceita': 'TESTE DATA LTDA'
    }
    
    print(f"🆕 Criando cliente: {novo_cliente['nomeEmpresa']}")
    resultado = service.save_client(novo_cliente)
    print(f"💾 Resultado: {resultado}")
    
    if resultado and isinstance(resultado, dict) and 'client_id' in resultado:
        novo_id = resultado['client_id']
        print(f"🆔 ID gerado: {novo_id}")
        
        # Buscar o cliente recém-criado
        cliente_criado = service.get_client(novo_id)
        if cliente_criado:
            print(f"✅ Cliente criado: {cliente_criado.get('nomeEmpresa')}")
            print(f"📅 criadoEm: '{cliente_criado.get('criadoEm', 'VAZIO')}'")
            print(f"🕐 ultimaAtualizacao: '{cliente_criado.get('ultimaAtualizacao', 'VAZIO')}'")
            
            # Verificar se são timestamps válidos
            criado = cliente_criado.get('criadoEm', '')
            if criado:
                try:
                    if criado.count('T') == 1 and criado.count(':') >= 2:
                        parsed = datetime.fromisoformat(criado.replace('Z', '+00:00'))
                        print(f"✅ criadoEm é timestamp válido: {parsed}")
                    else:
                        print(f"❌ criadoEm NÃO é timestamp válido: '{criado}'")
                except Exception as e:
                    print(f"❌ Erro ao parsear criadoEm: {e}")
                    
            # Verificar também diretamente na planilha
            print(f"\n🔍 Verificando na planilha...")
            # Encontrar linha do cliente
            clients = service.get_clients()
            for i, client in enumerate(clients):
                if client.get('id') == novo_id:
                    row_num = i + 2  # Linha na planilha (header + índice)
                    print(f"📊 Cliente encontrado na linha {row_num}")
                    
                    # Buscar dados diretos da planilha
                    result = service.service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=f"Clientes!A{row_num}:FP{row_num}"
                    ).execute()
                    
                    if 'values' in result and result['values']:
                        row = result['values'][0]
                        if len(row) > 151:
                            valor_criado = row[151]  # posição 152
                            print(f"📅 Valor direto na planilha (pos 152): '{valor_criado}'")
                        if len(row) > 148:
                            valor_atualizado = row[148]  # posição 149
                            print(f"🕐 Valor direto na planilha (pos 149): '{valor_atualizado}'")
                    break
        else:
            print("❌ Não foi possível buscar o cliente criado")
    else:
        print("❌ Falha na criação do cliente")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()