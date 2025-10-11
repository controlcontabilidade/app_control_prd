#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análise de Duplicação em client_to_row
======================================
Verifica se há duplicação de dados ao criar o array
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analisar_client_to_row():
    """Analisa a estrutura do método client_to_row"""
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE DO MÉTODO client_to_row")
    print("="*80)
    
    from services.google_sheets_service_account import GoogleSheetsServiceAccountService
    
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID', '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    service = GoogleSheetsServiceAccountService(spreadsheet_id)
    
    # Criar cliente de teste
    test_client = {
        'id': 'TEST_ARRAY_999',
        'nomeEmpresa': 'TESTE EMPRESA XYZ',
        'razaoSocialReceita': 'TESTE EMPRESA XYZ LTDA',
        'cnpj': '12.345.678/0001-99',
        'perfil': 'LUCRO PRESUMIDO',
        'estado': 'CE',
        'cidade': 'Fortaleza',
        'ct': True,
        'fs': True,
        'dp': False,
        'telefoneFixo': '(85) 3333-4444',
        'telefoneCelular': '(85) 99999-8888',
        'emailPrincipal': 'teste@control.com.br',
        'observacoes': 'Cliente de teste para análise',
        'statusCliente': 'ATIVO',
        'ativo': 'true'
    }
    
    print("\n📝 Cliente de teste criado:")
    print(f"   ID: {test_client['id']}")
    print(f"   Nome: {test_client['nomeEmpresa']}")
    
    # Converter para row
    print("\n🔄 Convertendo para array (row_data)...")
    row_data = service.client_to_row(test_client)
    
    print(f"\n📊 Resultado:")
    print(f"   Total de elementos no array: {len(row_data)}")
    print(f"   Esperado: 172")
    print(f"   Diferença: {len(row_data) - 172}")
    
    # Analisar os primeiros 20 elementos
    print(f"\n📋 Primeiros 20 elementos do array:")
    for i, valor in enumerate(row_data[:20]):
        print(f"   [{i:3d}] = '{valor}'")
    
    # Contar elementos vazios
    vazios = sum(1 for v in row_data if not v)
    print(f"\n📊 Estatísticas:")
    print(f"   Elementos vazios: {vazios}")
    print(f"   Elementos com dados: {len(row_data) - vazios}")
    
    # Procurar onde está o ID
    print(f"\n🔍 Procurando posição do ID '{test_client['id']}'...")
    for i, valor in enumerate(row_data):
        if valor == test_client['id']:
            print(f"   ✅ ID encontrado na posição: {i}")
            break
    else:
        print(f"   ❌ ID NÃO ENCONTRADO no array!")
    
    # Procurar onde está o nome
    print(f"\n🔍 Procurando posição do nome '{test_client['nomeEmpresa']}'...")
    for i, valor in enumerate(row_data):
        if valor == test_client['nomeEmpresa']:
            print(f"   ✅ Nome encontrado na posição: {i}")
            break
    else:
        print(f"   ❌ Nome NÃO ENCONTRADO no array!")
    
    # Verificar se há duplicação (array dentro de array)
    print(f"\n🔍 Verificando tipo dos elementos...")
    for i, valor in enumerate(row_data[:10]):
        print(f"   [{i}] tipo: {type(valor).__name__}, valor: '{valor}'")
    
    # Verificar se algum elemento é uma lista
    print(f"\n🔍 Procurando listas dentro do array...")
    for i, valor in enumerate(row_data):
        if isinstance(valor, (list, tuple)):
            print(f"   ⚠️ ENCONTRADA LISTA na posição {i}!")
            print(f"      Conteúdo: {valor[:5] if len(valor) > 5 else valor}")
    
    return row_data

if __name__ == '__main__':
    analisar_client_to_row()
