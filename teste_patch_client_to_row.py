#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patch para corrigir função client_to_row
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

def client_to_row_patch(self, client):
    """Versão corrigida da função client_to_row"""
    client_id = client.get('id', '')
    print("🔍 [SERVICE] ===== CLIENT_TO_ROW PATCH =====")
    print(f"🔍 [SERVICE] Cliente: {client.get('nomeEmpresa')}")
    print(f"🔍 [SERVICE] ID do cliente: '{client_id}'")

    headers = self.get_headers()
    row_data = [''] * len(headers)
    hidx = {name: i for i, name in enumerate(headers)}
    
    # Campos essenciais para teste
    essentials = {
        'ID': client.get('id', ''),
        'NOME DA EMPRESA': client.get('nomeEmpresa', ''),
        'CNPJ': client.get('cnpj', ''),
        'RAZÃO SOCIAL NA RECEITA': client.get('razaoSocialReceita', ''),
        'CLIENTE ATIVO': 'SIM' if client.get('ativo', True) else 'NÃO',
        # Campos de senha
        'CNPJ ACESSO SIMPLES NACIONAL': client.get('cnpjAcessoSn', ''),
        'CPF DO REPRESENTANTE LEGAL': client.get('cpfRepLegal', ''),
        'CÓDIGO ACESSO SN': client.get('codigoAcessoSn', ''),
        'SENHA ISS': client.get('senhaIss', ''),
        'SENHA SEFIN': client.get('senhaSefin', ''),
        'SENHA SEUMA': client.get('senhaSeuma', ''),
        'ACESSO EMPWEB': client.get('acessoEmpWeb', ''),
        'SENHA EMPWEB': client.get('senhaEmpWeb', ''),
        'LOGIN ANVISA EMPRESA': client.get('anvisaEmpresa', ''),
        'SENHA ANVISA EMPRESA': client.get('senhaAnvisaEmpresa', ''),
        'LOGIN ANVISA GESTOR': client.get('anvisaGestor', ''),
        'SENHA ANVISA GESTOR': client.get('senhaAnvisaGestor', ''),
        'ACESSO CRF': client.get('acessoCrf', ''),
        'SENHA FAP/INSS': client.get('senhaFapInss', ''),
        'SERVIÇO CT': 'SIM' if client.get('ct') else 'NÃO',
        'SERVIÇO FS': 'SIM' if client.get('fs') else 'NÃO',
        'SERVIÇO DP': 'SIM' if client.get('dp') else 'NÃO',
    }
    
    for field_name, value in essentials.items():
        if field_name in hidx and hidx[field_name] < len(row_data):
            row_data[hidx[field_name]] = value
            print(f"✅ {field_name}: {value}")
    
    print(f"✅ [SERVICE] Row preparada: {len(row_data)} colunas")
    return row_data

def teste_com_patch():
    """Testa salvamento com função corrigida"""
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Aplicar patch
        service.client_to_row = lambda client: client_to_row_patch(service, client)
        
        # Dados de teste
        client_data = {
            'nomeEmpresa': 'TESTE SENHAS PATCH LTDA',
            'cnpj': '12.345.678/0001-91',
            'razaoSocialReceita': 'TESTE SENHAS PATCH LTDA',
            'cnpjAcessoSn': '12345678000191',
            'cpfRepLegal': '123.456.789-01', 
            'codigoAcessoSn': 'SN123457',
            'senhaIss': 'senha_iss_patch',
            'senhaSefin': 'senha_sefin_patch',
            'senhaSeuma': 'senha_seuma_patch',
            'acessoEmpWeb': 'usuario_empweb_patch',
            'senhaEmpWeb': 'senha_empweb_patch',
            'anvisaEmpresa': 'usuario_anvisa_emp_patch',
            'senhaAnvisaEmpresa': 'senha_anvisa_emp_patch',
            'anvisaGestor': 'usuario_anvisa_gest_patch',
            'senhaAnvisaGestor': 'senha_anvisa_gest_patch',
            'acessoCrf': 'usuario_crf_patch',
            'senhaFapInss': 'senha_fap_inss_patch',
            'ativo': True,
            'ct': True,
            'fs': False,
            'dp': False
        }
        
        print("📊 Testando salvamento com patch...")
        result = service.save_client(client_data)
        
        if result:
            print(f"✅ Cliente salvo com sucesso! ID: {result}")
            return True
        else:
            print("❌ Erro ao salvar cliente")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    teste_com_patch()
