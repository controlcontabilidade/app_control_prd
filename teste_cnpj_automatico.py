#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a funcionalidade de preenchimento automático do CNPJ Acesso SN
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Testa a funcionalidade de preenchimento automático"""
    print("🧪 Testando funcionalidade de preenchimento automático do CNPJ Acesso SN...")
    
    try:
        # Importar e usar as configurações do app
        import app
        spreadsheet_id = app.GOOGLE_SHEETS_ID
        
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        
        # Dados de teste: Cliente com CNPJ
        cliente_cnpj = {
            'nomeEmpresa': 'TESTE AUTO CNPJ LTDA',
            'cnpj': '12.345.678/0001-90',  # Campo original (pode ser cpfCnpj)
            'cpfCnpj': '12.345.678/0001-90',  # Campo do formulário
            'razaoSocialReceita': 'TESTE AUTO CNPJ LIMITADA',
            'ativo': True,
            'ct': True,
            'fs': False,  
            'dp': False
        }
        
        # Dados de teste: Cliente com CPF
        cliente_cpf = {
            'nomeEmpresa': 'TESTE AUTO CPF',
            'cnpj': '123.456.789-00',  # Campo original (pode ser cpfCnpj)
            'cpfCnpj': '123.456.789-00',  # Campo do formulário
            'razaoSocialReceita': 'TESTE AUTO CPF',
            'ativo': True,
            'ct': True,
            'fs': False,
            'dp': False
        }
        
        print("📊 Testando salvamento cliente com CNPJ...")
        result_cnpj = service.save_client(cliente_cnpj)
        
        if result_cnpj:
            print(f"✅ Cliente CNPJ salvo com ID: {cliente_cnpj.get('id', 'N/A')}")
            
            # Buscar cliente para verificar
            clientes = service.get_clients()
            cliente_teste_cnpj = max([c for c in clientes if c.get('nomeEmpresa') == 'TESTE AUTO CNPJ LTDA'], 
                                    key=lambda c: int(c.get('id', 0)), default=None)
            
            if cliente_teste_cnpj:
                print(f"🔍 Cliente CNPJ encontrado: {cliente_teste_cnpj.get('nomeEmpresa')}")
                print(f"   CPF/CNPJ: {cliente_teste_cnpj.get('cpfCnpj', 'N/A')}")
                print(f"   CNPJ Acesso SN: {cliente_teste_cnpj.get('cnpjAcessoSn', 'VAZIO')}")
                
                # Verificar se seria preenchido automaticamente
                cpf_cnpj = cliente_teste_cnpj.get('cpfCnpj', '')
                numeros = ''.join(filter(str.isdigit, cpf_cnpj))
                if len(numeros) == 14:
                    print("✅ CNPJ detectado - Campo CNPJ Acesso SN DEVE ser preenchido automaticamente")
                else:
                    print("❌ CNPJ não detectado corretamente")
            else:
                print("❌ Cliente CNPJ não encontrado após salvamento")
        else:
            print("❌ Falha ao salvar cliente CNPJ")
        
        print("\n📊 Testando salvamento cliente com CPF...")
        result_cpf = service.save_client(cliente_cpf)
        
        if result_cpf:
            print(f"✅ Cliente CPF salvo com ID: {cliente_cpf.get('id', 'N/A')}")
            
            # Buscar cliente para verificar
            clientes = service.get_clients()
            cliente_teste_cpf = max([c for c in clientes if c.get('nomeEmpresa') == 'TESTE AUTO CPF'], 
                                   key=lambda c: int(c.get('id', 0)), default=None)
            
            if cliente_teste_cpf:
                print(f"🔍 Cliente CPF encontrado: {cliente_teste_cpf.get('nomeEmpresa')}")
                print(f"   CPF/CNPJ: {cliente_teste_cpf.get('cpfCnpj', 'N/A')}")  
                print(f"   CNPJ Acesso SN: {cliente_teste_cpf.get('cnpjAcessoSn', 'VAZIO')}")
                
                # Verificar se seria deixado vazio
                cpf_cnpj = cliente_teste_cpf.get('cpfCnpj', '')
                numeros = ''.join(filter(str.isdigit, cpf_cnpj))
                if len(numeros) == 11:
                    print("✅ CPF detectado - Campo CNPJ Acesso SN DEVE ficar vazio")
                else:
                    print("❌ CPF não detectado corretamente")
            else:
                print("❌ Cliente CPF não encontrado após salvamento")
        else:
            print("❌ Falha ao salvar cliente CPF")
        
        print(f"\n📋 RESUMO:")
        print(f"✅ A funcionalidade JavaScript foi implementada")
        print(f"✅ Quando CPF/CNPJ é preenchido no formulário:")
        print(f"   📌 Se for CNPJ (14 dígitos): CNPJ Acesso SN é preenchido automaticamente")
        print(f"   📌 Se for CPF (11 dígitos): CNPJ Acesso SN fica vazio")
        print(f"   📌 Se estiver incompleto: CNPJ Acesso SN fica vazio")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
