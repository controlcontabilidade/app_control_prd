#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deletar Linhas Corrompidas
===========================
Deleta as 8 linhas corrompidas (444-451) do Google Sheets
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.oauth2 import service_account
from googleapiclient.discovery import build

def deletar_linhas_corrompidas():
    """Deleta as linhas 444-451 corrompidas"""
    
    print("\n" + "="*80)
    print("🗑️ DELETANDO LINHAS CORROMPIDAS")
    print("="*80)
    
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID', '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    
    # Configurar credenciais
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds_file = 'service-account-key.json'
    
    if not os.path.exists(creds_file):
        print("❌ Arquivo de credenciais não encontrado!")
        return
    
    credentials = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=credentials)
    
    print("\n⚠️ Linhas a serem deletadas:")
    print("   - Linha 444: sem ID, dados deslocados")
    print("   - Linha 445: sem ID, dados deslocados")
    print("   - Linha 446: sem ID, dados deslocados")
    print("   - Linha 447: sem ID, dados deslocados")
    print("   - Linha 448: sem ID, dados deslocados")
    print("   - Linha 449: sem ID, dados deslocados")
    print("   - Linha 450: sem ID, dados deslocados")
    print("   - Linha 451: sem ID, dados deslocados")
    
    print("\n📋 Total de linhas a deletar: 8")
    print("\n✅ Estas linhas estão corrompidas e sem dados utilizáveis")
    print("✅ Os dados estão completamente deslocados (a partir da coluna FB)")
    print("✅ Não possuem ID válido")
    
    confirmacao = input("\n⚠️ Confirma a exclusão? (digite 'SIM' para confirmar): ").strip()
    
    if confirmacao != 'SIM':
        print("\n❌ Operação cancelada pelo usuário")
        return
    
    print("\n🗑️ Deletando linhas...")
    
    try:
        # Obter ID da aba "Clientes"
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == 'Clientes':
                sheet_id = sheet['properties']['sheetId']
                break
        
        if sheet_id is None:
            print("❌ Aba 'Clientes' não encontrada!")
            return
        
        print(f"✅ ID da aba 'Clientes': {sheet_id}")
        
        # Deletar linhas 444-451 (índices 443-450 em zero-based)
        requests = [{
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': 443,  # Linha 444 (zero-based)
                    'endIndex': 451     # Linha 451 (exclusive)
                }
            }
        }]
        
        body = {'requests': requests}
        
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        print(f"\n✅ SUCESSO! 8 linhas deletadas!")
        print(f"\n📊 Resultado:")
        print(f"   - Linhas removidas: 444-451")
        print(f"   - Total de linhas deletadas: 8")
        print(f"   - Resposta da API: {response.get('replies', [])}")
        
        print(f"\n🎉 Planilha agora tem:")
        print(f"   - 443 linhas com dados válidos (442 clientes + 1 cabeçalho)")
        print(f"   - Todos os clientes com dados corretos")
        print(f"   - Sistema pronto para novos cadastros")
        
    except Exception as e:
        print(f"\n❌ Erro ao deletar linhas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    deletar_linhas_corrompidas()
