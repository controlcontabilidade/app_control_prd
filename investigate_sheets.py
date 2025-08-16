#!/usr/bin/env python3
"""
Investigação DIRETA na Google Sheets para verificar os valores salvos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar dependências
import json
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def investigate_sheets_directly():
    """Investigar diretamente o que está na planilha"""
    print("🔍 INVESTIGAÇÃO DIRETA - GOOGLE SHEETS")
    print("="*60)
    
    try:
        # Inicializar serviço Google Sheets
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        
        # ID da planilha
        spreadsheet_id = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
        
        # Buscar dados da linha 3 (GRUPO SOLONOPOLE)
        print("📋 Buscando linha 3 (GRUPO SOLONOPOLE)...")
        
        # Buscar cabeçalhos primeiro
        headers_result = service.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Clientes!A1:DD1'
        ).execute()
        
        headers = headers_result.get('values', [])
        if headers:
            headers = headers[0]
            print(f"📊 Total de cabeçalhos: {len(headers)}")
            
            # Encontrar colunas importantes
            status_col = None
            ativo_col = None
            id_col = None
            
            for i, header in enumerate(headers):
                if 'STATUS' in header.upper() and 'CLIENTE' in header.upper():
                    status_col = i
                    print(f"📍 Coluna STATUS CLIENTE: {i+1} (header: '{header}')")
                elif 'ATIVO' in header.upper() and 'CLIENTE' in header.upper():
                    ativo_col = i
                    print(f"📍 Coluna CLIENTE ATIVO: {i+1} (header: '{header}')")
                elif header.upper() == 'ID':
                    id_col = i
                    print(f"📍 Coluna ID: {i+1} (header: '{header}')")
        
        # Buscar dados da linha 3
        data_result = service.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Clientes!A3:DD3'
        ).execute()
        
        data = data_result.get('values', [])
        if data and data[0]:
            row_data = data[0]
            print(f"\n📊 Dados da linha 3: {len(row_data)} colunas")
            
            # Verificar valores específicos
            if status_col is not None and status_col < len(row_data):
                status_value = row_data[status_col]
                print(f"🎯 STATUS CLIENTE (col {status_col+1}): '{status_value}'")
            else:
                print("❌ Coluna STATUS CLIENTE não encontrada ou sem dados")
                
            if ativo_col is not None and ativo_col < len(row_data):
                ativo_value = row_data[ativo_col]
                print(f"🎯 CLIENTE ATIVO (col {ativo_col+1}): '{ativo_value}'")
            else:
                print("❌ Coluna CLIENTE ATIVO não encontrada ou sem dados")
                
            if id_col is not None and id_col < len(row_data):
                id_value = row_data[id_col]
                print(f"🎯 ID (col {id_col+1}): '{id_value}'")
            else:
                print("❌ Coluna ID não encontrada ou sem dados")
            
            # Mostrar as primeiras 10 colunas
            print(f"\n📋 Primeiras 10 colunas:")
            for i in range(min(10, len(row_data))):
                header_name = headers[i] if i < len(headers) else f"Col{i+1}"
                value = row_data[i] if row_data[i] else "(vazio)"
                print(f"   {i+1:2d}. {header_name:<30}: '{value}'")
                
            print(f"\n📋 Últimas 10 colunas:")
            start_idx = max(0, len(row_data) - 10)
            for i in range(start_idx, len(row_data)):
                header_name = headers[i] if i < len(headers) else f"Col{i+1}"
                value = row_data[i] if row_data[i] else "(vazio)"
                print(f"   {i+1:2d}. {header_name:<30}: '{value}'")
        
        else:
            print("❌ Nenhum dado encontrado na linha 3")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_sheets_directly()
