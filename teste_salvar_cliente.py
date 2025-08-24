#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste para identificar erro ao salvar cliente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import do serviço
try:
    from services.google_sheets_service_account import GoogleSheetsServiceAccountService
    print("✅ Importação do serviço realizada com sucesso")
except ImportError as e:
    print(f"❌ Erro na importação do serviço: {e}")
    sys.exit(1)

# Configurações
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
GOOGLE_SHEETS_RANGE = 'Clientes!A:DD'

def teste_salvar_cliente():
    """Testa o salvamento de um cliente com dados de senha"""
    
    try:
        # Inicializar serviço
        print("🔄 Inicializando serviço...")
        service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Dados de teste com campos de senha
        client_data = {
            'nomeEmpresa': 'TESTE SENHAS LTDA',
            'cnpj': '12.345.678/0001-90',
            'razaoSocialReceita': 'TESTE SENHAS LTDA',
            
            # Campos de senha - Linha 1
            'cnpjAcessoSn': '12345678000190',
            'cpfRepLegal': '123.456.789-00', 
            'codigoAcessoSn': 'SN123456',
            'senhaIss': 'senha_iss_123',
            
            # Campos de senha - Linha 2
            'senhaSefin': 'senha_sefin_123',
            'senhaSeuma': 'senha_seuma_123',
            'acessoEmpWeb': 'usuario_empweb',
            'senhaEmpWeb': 'senha_empweb_123',
            
            # Campos de senha - Linha 3
            'anvisaEmpresa': 'usuario_anvisa_emp',
            'senhaAnvisaEmpresa': 'senha_anvisa_emp_123',
            'anvisaGestor': 'usuario_anvisa_gest',
            'senhaAnvisaGestor': 'senha_anvisa_gest_123',
            
            # Campos de senha - Linha 4
            'acessoCrf': 'usuario_crf',
            'senhaFapInss': 'senha_fap_inss_123',
            
            # Outros campos obrigatórios
            'ativo': True,
            'ct': False,
            'fs': False,
            'dp': False
        }
        
        print("📊 Testando salvamento do cliente...")
        result = service.save_client(client_data)
        
        if result:
            print("✅ Cliente salvo com sucesso!")
            
            # Buscar o cliente pelo nome para pegar o ID real
            print("🔍 Buscando cliente por nome para pegar ID...")
            all_clients = service.get_clients()
            saved_client = None
            
            for client in all_clients:
                if client.get('nomeEmpresa') == 'TESTE SENHAS LTDA':
                    saved_client = client
                    break
            
            if saved_client:
                actual_id = saved_client.get('id')
                print(f"   ID real do cliente encontrado: {actual_id}")
                
                print("\n🔐 Verificação dos campos de senha:")
                senha_fields = [
                    'cnpjAcessoSn', 'cpfRepLegal', 'codigoAcessoSn', 'senhaIss',
                    'senhaSefin', 'senhaSeuma', 'acessoEmpWeb', 'senhaEmpWeb',
                    'anvisaEmpresa', 'senhaAnvisaEmpresa', 'anvisaGestor', 'senhaAnvisaGestor',
                    'acessoCrf', 'senhaFapInss'
                ]
                
                for field in senha_fields:
                    original = client_data.get(field, '')
                    saved = saved_client.get(field, '')
                    status = "✅" if saved == original else "❌"
                    print(f"   {status} {field}: '{original}' -> '{saved}'")
                    
            else:
                print("❌ Erro ao encontrar o cliente salvo")
        else:
            print("❌ Erro ao salvar cliente")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    teste_salvar_cliente()
