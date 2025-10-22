#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a EDIÇÃO do campo Doméstica em cliente existente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("\n" + "="*70)
    print("TESTE DE EDIÇÃO DO CAMPO DOMÉSTICA")
    print("="*70 + "\n")
    
    # Conectar ao serviço
    spreadsheet_id = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
    service = GoogleSheetsServiceAccountService(spreadsheet_id)
    
    # 1. Criar cliente de teste
    print("1️⃣ Criando cliente de teste...")
    cliente_teste = {
        'nomeEmpresa': 'TESTE EDICAO DOMESTICA',
        'razaoSocialReceita': 'TESTE EDICAO DOMESTICA LTDA',
        'cnpj': '12.345.678/0001-90',
        'cpfCnpj': '123.456.789-00',  # CPF para permitir doméstica
        'perfil': 'TESTE',
        'ct': True,
        'fs': False,
        'dp': False,
        'ativo': True,
        'domestica': ''  # INICIALMENTE VAZIO
    }
    
    client_id = service.save_client(cliente_teste)
    if not client_id:
        print("   ❌ Falha ao criar cliente!")
        return
    
    print(f"   ✅ Cliente criado com ID: {client_id}")
    
    # 2. Verificar que foi salvo sem doméstica
    print("\n2️⃣ Verificando estado inicial...")
    cliente = service.get_client(client_id)
    if not cliente:
        print("   ❌ Cliente não encontrado!")
        return
    
    print(f"   📊 Doméstica inicial: '{cliente.get('domestica', '')}'")
    
    # 3. EDITAR o cliente para adicionar Doméstica = SIM
    print("\n3️⃣ Editando cliente para adicionar Doméstica=SIM...")
    cliente['domestica'] = 'SIM'
    
    # Mostrar o que está sendo enviado
    print(f"   📤 Enviando: domestica='{cliente['domestica']}'")
    
    result = service.save_client(cliente)
    if not result:
        print("   ❌ Falha ao salvar edição!")
        return
    
    print(f"   ✅ Edição salva! Retorno: {result}")
    
    # 4. Recarregar o cliente e verificar
    print("\n4️⃣ Recarregando cliente para verificar...")
    cliente_reload = service.get_client(client_id)
    if not cliente_reload:
        print("   ❌ Cliente não encontrado após edição!")
        return
    
    domestica_final = cliente_reload.get('domestica', '')
    print(f"   📊 Doméstica após edição: '{domestica_final}'")
    
    if domestica_final == 'SIM':
        print("   ✅ SUCESSO! Campo Doméstica foi salvo corretamente!")
    else:
        print(f"   ❌ FALHA! Esperado 'SIM', recebido '{domestica_final}'")
    
    # 5. Verificar RAW na planilha
    print("\n5️⃣ Verificando valor RAW na planilha...")
    row_num = service.find_client_row(client_id)
    if row_num:
        all_data = service.get_all_data()
        if row_num <= len(all_data):
            row_data = all_data[row_num - 1]
            headers = service.get_headers()
            
            if 'DOMÉSTICA' in headers:
                idx = headers.index('DOMÉSTICA')
                valor_raw = row_data[idx] if idx < len(row_data) else ''
                print(f"   📊 Valor RAW na coluna {idx}: '{valor_raw}'")
                
                if valor_raw == 'SIM':
                    print("   ✅ Valor correto na planilha!")
                else:
                    print(f"   ❌ Valor incorreto na planilha! Esperado 'SIM', encontrado '{valor_raw}'")
            else:
                print("   ❌ Cabeçalho 'DOMÉSTICA' não encontrado!")
    
    # 6. Limpar - deletar cliente de teste
    print("\n6️⃣ Removendo cliente de teste...")
    service.delete_client(client_id)
    print("   ✅ Cliente de teste removido!")
    
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
