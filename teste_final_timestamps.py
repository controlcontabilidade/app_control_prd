import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

print("🎯 TESTE FINAL: Verificando comportamento completo dos timestamps")

# IDs de teste  
spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
client_id = "2025-10-02T20:28:50.267025"

try:
    service = GoogleSheetsServiceAccountService(spreadsheet_id=spreadsheet_id)
    print("✅ Serviço inicializado")
    
    # 1. BUSCAR CLIENTE INICIAL
    client = service.get_client(client_id)
    if client:
        print(f"✅ Cliente: {client.get('nomeEmpresa', 'NOME NÃO ENCONTRADO')}")
        print(f"📅 Data de Criação: '{client.get('criadoEm', 'VAZIO')}'")
        print(f"🕐 Última Atualização: '{client.get('ultimaAtualizacao', 'VAZIO')}'")
        
        # 2. SIMULAR CRIAÇÃO DE CLIENTE NOVO (só para testar se criadoEm é gerado)
        print(f"\n🆕 TESTE: Criando cliente novo...")
        novo_cliente = {
            'nomeEmpresa': f'TESTE TIMESTAMP {datetime.now().strftime("%H:%M:%S")}',
            'cnpj': '00.000.000/0001-99',
            'razaoSocialReceita': 'TESTE LTDA'
        }
        
        resultado_novo = service.save_client(novo_cliente)
        print(f"💾 Resultado criação: {resultado_novo}")
        
        if resultado_novo and isinstance(resultado_novo, dict) and 'client_id' in resultado_novo:
            novo_id = resultado_novo['client_id']
            print(f"🆔 Novo ID gerado: {novo_id}")
            
            # Buscar o cliente recém-criado
            novo_cliente_salvo = service.get_client(novo_id)
            if novo_cliente_salvo:
                print(f"📅 Novo cliente - Data de Criação: '{novo_cliente_salvo.get('criadoEm', 'VAZIO')}'")
                print(f"🕐 Novo cliente - Última Atualização: '{novo_cliente_salvo.get('ultimaAtualizacao', 'VAZIO')}'")
            
        # 3. TESTAR ATUALIZAÇÃO DO CLIENTE ORIGINAL
        print(f"\n✏️ TESTE: Atualizando cliente original...")
        client_atualizado = client.copy()
        client_atualizado['observacoes'] = f'Teste de atualização {datetime.now().strftime("%H:%M:%S")}'
        
        resultado_atualizacao = service.update_client(client_atualizado)
        print(f"💾 Resultado atualização: {resultado_atualizacao}")
        
        # Verificar após atualização
        client_pos_atualizacao = service.get_client(client_id)
        if client_pos_atualizacao:
            print(f"📅 Após atualização - Data de Criação: '{client_pos_atualizacao.get('criadoEm', 'VAZIO')}'")
            print(f"🕐 Após atualização - Última Atualização: '{client_pos_atualizacao.get('ultimaAtualizacao', 'VAZIO')}'")
            
            # Comparar
            criacao_mudou = client.get('criadoEm') != client_pos_atualizacao.get('criadoEm')
            atualizacao_mudou = client.get('ultimaAtualizacao') != client_pos_atualizacao.get('ultimaAtualizacao')
            
            print(f"\n📊 ANÁLISE FINAL:")
            print(f"{'❌' if criacao_mudou else '✅'} Data de Criação {'MUDOU' if criacao_mudou else 'PRESERVADA'} {'(ERRO!)' if criacao_mudou else '(correto)'}")
            print(f"{'✅' if atualizacao_mudou else '❌'} Última Atualização {'ATUALIZADA' if atualizacao_mudou else 'NÃO MUDOU'} {'(correto)' if atualizacao_mudou else '(ERRO!)'}")
    
    else:
        print("❌ Cliente não encontrado")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()