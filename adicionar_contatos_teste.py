"""
Script para adicionar contatos ao cliente teste
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

# Configurações
GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
GOOGLE_SHEETS_RANGE = "Clientes!A:FG"

def adicionar_contatos_cliente_teste():
    print("🔍 ===== ADICIONANDO CONTATOS AO CLIENTE TESTE =====")
    
    try:
        storage = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        client_id = "1756032228826"
        
        # Buscar cliente
        client = storage.get_client(client_id)
        if not client:
            print("❌ Cliente teste não encontrado!")
            return
            
        print(f"✅ Cliente encontrado: {client['nomeEmpresa']}")
        
        # Adicionar múltiplos contatos
        client.update({
            'contato_1_nome': 'CONTATO PRINCIPAL TESTE',
            'contato_1_cargo': 'GERENTE GERAL',
            'contato_1_telefone': '(85) 99999-1111',
            'contato_1_email': 'principal@testecliente.com',
            
            'contato_2_nome': 'SEGUNDO CONTATO TESTE',
            'contato_2_cargo': 'DIRETOR COMERCIAL',
            'contato_2_telefone': '(85) 99999-2222',
            'contato_2_email': 'comercial@testecliente.com',
            
            'contato_3_nome': 'TERCEIRO CONTATO TESTE',
            'contato_3_cargo': 'COORDENADOR FINANCEIRO',
            'contato_3_telefone': '(85) 99999-3333',
            'contato_3_email': 'financeiro@testecliente.com',
        })
        
        # Salvar cliente
        success = storage.save_client(client)
        
        if success:
            print("✅ Contatos adicionados com sucesso!")
            print("\nContatos cadastrados:")
            for i in range(1, 4):
                nome = client.get(f'contato_{i}_nome', '')
                cargo = client.get(f'contato_{i}_cargo', '')
                telefone = client.get(f'contato_{i}_telefone', '')
                email = client.get(f'contato_{i}_email', '')
                
                if nome:
                    print(f"   Contato {i}: {nome} - {cargo}")
                    print(f"      Tel: {telefone} | Email: {email}")
            
            print(f"\n✅ Cliente disponível para teste em:")
            print(f"   http://localhost:5000/client/{client_id}/edit")
        else:
            print("❌ Erro ao salvar contatos")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    adicionar_contatos_cliente_teste()
