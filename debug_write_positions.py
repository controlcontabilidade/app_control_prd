#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def main():
    print("=" * 70)
    print("🔍 DEBUG - POSIÇÕES DE ESCRITA E LEITURA")
    print("=" * 70)
    
    # Cliente de teste
    test_client = {
        'id': 'TEST_ID_12345',
        'nomeEmpresa': 'EMPRESA TESTE',
        'dataInicioServicos': '2025-01-15',
        'statusCliente': 'ATIVO',
        'ativo': True,
        'criadoEm': datetime.now().isoformat()
    }
    
    print(f"📊 Cliente de teste: {test_client['nomeEmpresa']}")
    print(f"🗓️  dataInicioServicos: '{test_client['dataInicioServicos']}'")
    print(f"📋 statusCliente: '{test_client['statusCliente']}'")
    print(f"✅ ativo: {test_client['ativo']}")
    print(f"🆔 id: '{test_client['id']}'")
    
    # Simular client_to_row
    print("\n🔧 Simulando client_to_row...")
    row_data = [
        test_client.get('nomeEmpresa', ''),                   # 0. NOME EMPRESA
        test_client.get('cnpj', ''),                          # 1. CNPJ
        test_client.get('razaoSocial', ''),                   # 2. RAZÃO SOCIAL
        test_client.get('nomeFantasia', ''),                  # 3. NOME FANTASIA
        '', '', '', '', '', '', '', '', '', '',               # 4-13. Outros campos
        'SIM' if test_client.get('ct') else 'NÃO',           # 14. SERVIÇO CT
        'SIM' if test_client.get('fs') else 'NÃO',           # 15. SERVIÇO FS
        'SIM' if test_client.get('dp') else 'NÃO',           # 16. SERVIÇO DP
        'SIM' if test_client.get('bpoFinanceiro') else 'NÃO', # 17. SERVIÇO BPO FINANCEIRO
        '',                                                   # 18. (REMOVIDO DUPLICAÇÃO)
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', # 19-34. Outros campos
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', # 35-50. Outros campos
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', # 51-66. Outros campos
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', # 67-82. Outros campos
        test_client.get('observacoesGerais', ''),             # 83. OBSERVAÇÕES GERAIS
        test_client.get('tarefasVinculadas', 0),              # 84. TAREFAS VINCULADAS
        test_client.get('dataInicioServicos', ''),            # 85. DATA INÍCIO SERVIÇOS
        test_client.get('statusCliente', 'ATIVO'),            # 86. STATUS DO CLIENTE
        test_client.get('ultimaAtualizacao', ''),             # 87. ÚLTIMA ATUALIZAÇÃO
        test_client.get('responsavelAtualizacao', ''),        # 88. RESPONSÁVEL ATUALIZAÇÃO
        test_client.get('prioridadeCliente', 'NORMAL'),       # 89. PRIORIDADE
        test_client.get('tagsCliente', ''),                   # 90. TAGS/CATEGORIAS
        test_client.get('historicoAlteracoes', ''),           # 91. HISTÓRICO DE ALTERAÇÕES
        test_client.get('donoResp', ''),                      # 92. DONO/RESPONSÁVEL
        'SIM' if test_client.get('ativo', True) else 'NÃO',  # 93. CLIENTE ATIVO
    ]
    
    # Completar até 95 colunas
    while len(row_data) < 95:
        row_data.append('')
    
    # Colocar o ID na posição 94
    row_data[94] = test_client.get('id', '')
    
    print(f"📊 Tamanho da linha: {len(row_data)} colunas")
    print(f"🗓️  Posição 85 (dataInicioServicos): '{row_data[85]}'")
    print(f"📋 Posição 86 (statusCliente): '{row_data[86]}'")
    print(f"✅ Posição 93 (ativo): '{row_data[93]}'")
    print(f"🆔 Posição 94 (id): '{row_data[94]}'")
    
    # Simular row_to_client (lendo de volta)
    print("\n🔍 Simulando row_to_client...")
    client_from_row = {
        'nomeEmpresa': row_data[0] if len(row_data) > 0 else '',
        'dataInicioServicos': row_data[85] if len(row_data) > 85 else '',
        'statusCliente': row_data[86] if len(row_data) > 86 else 'ATIVO',
        'ativo': row_data[93] == 'SIM' if len(row_data) > 93 else True,
        'id': row_data[94] if len(row_data) > 94 else '',
    }
    
    print(f"📊 Cliente lido de volta: {client_from_row['nomeEmpresa']}")
    print(f"🗓️  dataInicioServicos: '{client_from_row['dataInicioServicos']}'")
    print(f"📋 statusCliente: '{client_from_row['statusCliente']}'")
    print(f"✅ ativo: {client_from_row['ativo']}")
    print(f"🆔 id: '{client_from_row['id']}'")
    
    print("\n✅ Teste de consistência:")
    print(f"dataInicioServicos: '{test_client['dataInicioServicos']}' == '{client_from_row['dataInicioServicos']}' : {test_client['dataInicioServicos'] == client_from_row['dataInicioServicos']}")
    print(f"statusCliente: '{test_client['statusCliente']}' == '{client_from_row['statusCliente']}' : {test_client['statusCliente'] == client_from_row['statusCliente']}")
    print(f"ativo: {test_client['ativo']} == {client_from_row['ativo']} : {test_client['ativo'] == client_from_row['ativo']}")
    print(f"id: '{test_client['id']}' == '{client_from_row['id']}' : {test_client['id'] == client_from_row['id']}")
    
    print("\n" + "=" * 70)
    print("🎯 Debug de posições concluído!")
    print("=" * 70)

if __name__ == "__main__":
    main()
