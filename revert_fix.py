#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("=" * 70)
    print("🔧 REVERTER CORREÇÃO INCORRETA")
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
    
    print(f"\n📊 Estado atual dos dados:")
    for i, row in enumerate(client_rows, 1):
        if len(row) > 86:
            print(f"Cliente {i}:")
            print(f"  Índice 84 (DATA INÍCIO): '{row[84] if len(row) > 84 else ''}'")
            print(f"  Índice 85 (STATUS): '{row[85] if len(row) > 85 else ''}'")
            print(f"  Índice 86 (ÚLTIMA ATUALIZAÇÃO): '{row[86] if len(row) > 86 else ''}'")
    
    # Reverter correção
    print(f"\n🔧 Revertendo correção incorreta...")
    corrected_data = [headers]  # Manter cabeçalhos
    
    for i, row in enumerate(client_rows, 1):
        print(f"\n📋 Revertendo cliente {i}...")
        
        # Criar cópia da linha
        new_row = row.copy()
        
        # Garantir tamanho mínimo
        while len(new_row) < 95:
            new_row.append('')
        
        # REVERSÃO: O timestamp correto de data de início era '2025-07-28T13:37:28.036387'
        # que estava na posição correta antes da "correção" incorreta
        
        # Restaurar o valor correto
        new_row[84] = '2025-07-28T13:37:28.036387'  # DATA INÍCIO SERVIÇOS (timestamp correto)
        new_row[85] = 'ATIVO'                       # STATUS DO CLIENTE (mantém correto)
        new_row[86] = '2025-07-28T13:38:09.043601'  # ÚLTIMA ATUALIZAÇÃO (mantém correto)
        
        print(f"  ✅ Dados revertidos:")
        print(f"    Índice 84 (DATA INÍCIO): '{new_row[84]}'")
        print(f"    Índice 85 (STATUS): '{new_row[85]}'")
        print(f"    Índice 86 (ÚLTIMA ATUALIZAÇÃO): '{new_row[86]}'")
        
        # Manter o ID correto
        if len(new_row) > 94:
            print(f"    🆔 ID mantido: '{new_row[94]}'")
        
        corrected_data.append(new_row)
    
    # Aplicar reversão
    print(f"\n🔧 Aplicando reversão à planilha...")
    
    body = {
        'values': corrected_data
    }
    
    result = service.service.spreadsheets().values().update(
        spreadsheetId=service.spreadsheet_id,
        range='Clientes!A:CZ',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"✅ Reversão aplicada! {result.get('updatedCells', 0)} células atualizadas")
    
    print("\n" + "=" * 70)
    print("🎯 Reversão concluída!")
    print("=" * 70)

if __name__ == "__main__":
    main()
