"""
Script para criar um cliente teste com múltiplos sócios
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

# Configurações
GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
GOOGLE_SHEETS_RANGE = "Clientes!A:FG"

def criar_cliente_teste():
    print("🔍 ===== CRIANDO CLIENTE TESTE COM 3 SÓCIOS =====")
    
    try:
        # Criar serviço
        storage = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Dados do cliente teste
        temp_data = {
            'nomeEmpresa': 'TESTE DEBUG SOCIOS MULTIPLOS LTDA',
            'razaoSocialReceita': 'TESTE DEBUG SOCIOS MULTIPLOS LTDA',
            'nomeFantasiaReceita': 'TESTE DEBUG',
            'cpfCnpj': '99.888.777/0001-66',
            'perfil': 'PESSOA JURÍDICA',
            'inscEst': '99999999',
            'inscMun': '88888888',
            'estado': 'SP',
            'cidade': 'SÃO PAULO',
            'regimeFederal': 'LUCRO PRESUMIDO',
            'regimeEstadual': 'SIMPLES NACIONAL',
            'segmento': 'COMÉRCIO',
            'atividade': 'VENDAS',
            'sistemaUtilizado': 'TESTE',
            'ativo': True,
            
            # Três sócios para teste
            'socio_1_nome': 'PRIMEIRO SOCIO COMPLETO',
            'socio_1_cpf': '111.111.111-11',
            'socio_1_participacao': '50.00',
            'socio_1_data_nascimento': '1980-01-01',
            'socio_1_administrador': True,
            'socio_1_resp_legal': True,
            
            'socio_2_nome': 'SEGUNDO SOCIO COMPLETO',
            'socio_2_cpf': '222.222.222-22', 
            'socio_2_participacao': '30.00',
            'socio_2_data_nascimento': '1985-05-15',
            'socio_2_administrador': False,
            'socio_2_resp_legal': False,
            
            'socio_3_nome': 'TERCEIRO SOCIO COMPLETO',
            'socio_3_cpf': '333.333.333-33',
            'socio_3_participacao': '20.00',
            'socio_3_data_nascimento': '1990-12-31',
            'socio_3_administrador': False,
            'socio_3_resp_legal': False,
        }
        
        print("📊 Salvando cliente teste...")
        success = storage.save_client(temp_data)
        
        if success:
            print("✅ Cliente teste criado com sucesso!")
            
            # Buscar o cliente recém criado para confirmar
            clients = storage.get_clients()
            for client in clients:
                if client.get('nomeEmpresa') == 'TESTE DEBUG SOCIOS MULTIPLOS LTDA':
                    print(f"\n🔍 ===== CLIENTE TESTE CRIADO =====")
                    print(f"Nome: {client.get('nomeEmpresa')}")
                    print(f"ID: {client.get('id')}")
                    
                    print(f"\n📊 Sócios cadastrados:")
                    for i in range(1, 4):
                        nome = client.get(f'socio_{i}_nome', '')
                        cpf = client.get(f'socio_{i}_cpf', '')
                        participacao = client.get(f'socio_{i}_participacao', '')
                        
                        if nome:
                            print(f"   Sócio {i}: {nome} - CPF: {cpf} - Part.: {participacao}%")
                    
                    print(f"\n✅ Cliente está disponível para edição na URL:")
                    print(f"   http://localhost:5000/editar/{client.get('id')}")
                    
                    break
        else:
            print("❌ Falhou ao criar cliente teste")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    criar_cliente_teste()
