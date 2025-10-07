import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

print("🧪 TESTE FINAL: Criação de novo cliente com timestamps corretos")

spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"

try:
    service = GoogleSheetsServiceAccountService(spreadsheet_id=spreadsheet_id)
    print("✅ Serviço inicializado")
    
    # Criar um cliente completamente novo
    timestamp_now = datetime.now().isoformat()
    client_teste = {
        'nomeEmpresa': f'TESTE FINAL TIMESTAMPS {datetime.now().strftime("%H:%M:%S")}',
        'razaoSocialReceita': 'TESTE FINAL RAZAO SOCIAL',
        'cnpj': '98.765.432/0001-10',
        'perfil': 'TESTE FINAL',
        'criadoEm': timestamp_now,
        'ultimaAtualizacao': timestamp_now,
        'ct': True,
        'fs': False,
        'dp': False,
        'ativo': True
    }
    
    print(f"🧪 Criando cliente de teste:")
    print(f"   - Nome: {client_teste['nomeEmpresa']}")
    print(f"   - criadoEm: '{client_teste['criadoEm']}'")
    print(f"   - ultimaAtualizacao: '{client_teste['ultimaAtualizacao']}'")
    
    # Salvar o cliente
    print(f"\n💾 Salvando cliente...")
    result = service.save_client(client_teste)
    
    if result:
        print("✅ Cliente salvo com sucesso!")
        
        # Buscar o cliente recém-criado
        client_id = client_teste.get('id')
        if client_id:
            print(f"\n🔍 Buscando cliente recém-criado (ID: {client_id})...")
            client_recuperado = service.get_client(client_id)
            
            if client_recuperado:
                print(f"✅ Cliente recuperado:")
                print(f"   - Nome: {client_recuperado.get('nomeEmpresa')}")
                print(f"   - criadoEm: '{client_recuperado.get('criadoEm')}'")
                print(f"   - ultimaAtualizacao: '{client_recuperado.get('ultimaAtualizacao')}'")
                print(f"   - ativo: {client_recuperado.get('ativo')}")
                
                # Verificar se os timestamps estão corretos
                criado_em_correto = client_recuperado.get('criadoEm') == timestamp_now
                tem_ultima_atualizacao = bool(client_recuperado.get('ultimaAtualizacao'))
                
                print(f"\n✅ RESULTADOS DO TESTE:")
                print(f"   - criadoEm correto: {'✅ SIM' if criado_em_correto else '❌ NÃO'}")
                print(f"   - ultimaAtualizacao presente: {'✅ SIM' if tem_ultima_atualizacao else '❌ NÃO'}")
                
                if criado_em_correto and tem_ultima_atualizacao:
                    print(f"\n🎉 TESTE APROVADO! Os timestamps estão funcionando corretamente!")
                else:
                    print(f"\n❌ TESTE REPROVADO! Ainda há problemas com os timestamps.")
                    
            else:
                print("❌ Não foi possível recuperar o cliente")
        else:
            print("❌ Cliente não tem ID")
    else:
        print("❌ Falha ao salvar cliente")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()