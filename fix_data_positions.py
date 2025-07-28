#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("=" * 70)
    print("🔧 CORREÇÃO MANUAL DOS DADOS")
    print("=" * 70)
    
    # Inicializar serviço
    service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    print("✅ Serviço inicializado")
    
    # Buscar dados brutos
    range_name = 'Clientes!A:CZ'
    result = service.service.spreadsheets().values().get(
        spreadsheetId=service.spreadsheet_id, 
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    
    if len(values) < 2:
        print("❌ Não há dados para corrigir")
        return
    
    headers = values[0]
    client_rows = values[1:]
    
    print(f"\n📊 Dados antes da correção:")
    for i, row in enumerate(client_rows, 1):
        if len(row) > 86:
            print(f"Cliente {i}:")
            print(f"  Índice 84 (DATA INÍCIO): '{row[84] if len(row) > 84 else ''}'")
            print(f"  Índice 85 (STATUS): '{row[85] if len(row) > 85 else ''}'")
            print(f"  Índice 86 (ÚLTIMA ATUALIZAÇÃO): '{row[86] if len(row) > 86 else ''}'")
    
    # Corrigir os dados
    print(f"\n🔧 Corrigindo dados...")
    corrected_data = [headers]  # Manter cabeçalhos
    
    for i, row in enumerate(client_rows, 1):
        print(f"\n📋 Corrigindo cliente {i}...")
        
        # Criar cópia da linha
        new_row = row.copy()
        
        # Garantir tamanho mínimo
        while len(new_row) < 95:
            new_row.append('')
        
        # CORREÇÃO MANUAL baseada na análise:
        # Atualmente:
        # - Índice 84: '' (vazio)
        # - Índice 85: '2025-07-28T13:37:28.036387' (deveria ser status)
        # - Índice 86: '2025-07-28T13:38:09.043601' (última atualização)
        
        # Deveria ser:
        # - Índice 84: '2025-07-28T13:37:28.036387' (data início)
        # - Índice 85: 'ATIVO' (status)
        # - Índice 86: '2025-07-28T13:38:09.043601' (última atualização)
        
        data_inicio_timestamp = new_row[85] if len(new_row) > 85 else ''
        ultima_atualizacao_timestamp = new_row[86] if len(new_row) > 86 else ''
        
        if data_inicio_timestamp and 'T' in data_inicio_timestamp:
            # Mover o timestamp para a posição correta
            new_row[84] = data_inicio_timestamp  # DATA INÍCIO SERVIÇOS
            new_row[85] = 'ATIVO'               # STATUS DO CLIENTE
            new_row[86] = ultima_atualizacao_timestamp  # ÚLTIMA ATUALIZAÇÃO (mantém onde está)
            
            print(f"  ✅ Dados corrigidos:")
            print(f"    Índice 84 (DATA INÍCIO): '{new_row[84]}'")
            print(f"    Índice 85 (STATUS): '{new_row[85]}'")
            print(f"    Índice 86 (ÚLTIMA ATUALIZAÇÃO): '{new_row[86]}'")
        else:
            print(f"  ℹ️  Dados não precisam de correção")
        
        # Garantir que tenha um ID válido
        if len(new_row) > 94 and (not new_row[94] or new_row[94] == 'SIM'):
            # Gerar ID baseado no nome da empresa
            nome_empresa = new_row[0] if len(new_row) > 0 else 'CLIENTE'
            timestamp = '20250128140000'  # Timestamp fixo para consistência
            new_id = f"{nome_empresa[:10].upper().replace(' ', '_')}_{timestamp}"
            new_row[94] = new_id
            print(f"    🆔 ID corrigido: '{new_id}'")
        
        corrected_data.append(new_row)
    
    # Aplicar correções
    print(f"\n🔧 Aplicando correções à planilha...")
    
    body = {
        'values': corrected_data
    }
    
    result = service.service.spreadsheets().values().update(
        spreadsheetId=service.spreadsheet_id,
        range='Clientes!A:CZ',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"✅ Correção aplicada! {result.get('updatedCells', 0)} células atualizadas")
    
    # Verificar resultado
    print(f"\n🔍 Verificando resultado...")
    result = service.service.spreadsheets().values().get(
        spreadsheetId=service.spreadsheet_id, 
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    client_rows = values[1:] if len(values) > 1 else []
    
    for i, row in enumerate(client_rows, 1):
        if len(row) > 86:
            print(f"Cliente {i} após correção:")
            print(f"  Índice 84 (DATA INÍCIO): '{row[84] if len(row) > 84 else ''}'")
            print(f"  Índice 85 (STATUS): '{row[85] if len(row) > 85 else ''}'")
            print(f"  Índice 86 (ÚLTIMA ATUALIZAÇÃO): '{row[86] if len(row) > 86 else ''}'")
            print(f"  Índice 94 (ID): '{row[94] if len(row) > 94 else ''}'")
    
    print("\n" + "=" * 70)
    print("🎯 Correção concluída!")
    print("=" * 70)

if __name__ == "__main__":
    main()
