#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("=" * 70)
    print("🔍 ANÁLISE DETALHADA DOS CAMPOS ONVIO")
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
        print("❌ Não há dados para analisar")
        return
    
    headers = values[0]
    client_row = values[1] if len(values) > 1 else []
    
    print(f"\n📊 Cabeçalhos dos campos Onvio:")
    onvio_cols = [47, 48, 49, 50]
    for col in onvio_cols:
        if col < len(headers):
            print(f"  Col {col+1} (índice {col}): '{headers[col]}'")
    
    print(f"\n📊 Dados da linha do cliente:")
    print(f"  Total de colunas: {len(client_row)}")
    
    for col in onvio_cols:
        if col < len(client_row):
            value = client_row[col] if client_row[col] else ''
            print(f"  Col {col+1} (índice {col}): '{value}'")
    
    # Verificar também algumas outras colunas importantes
    print(f"\n📊 Outros campos importantes:")
    other_cols = [44, 45, 46]  
    for col in other_cols:
        if col < len(headers) and col < len(client_row):
            header = headers[col] if col < len(headers) else 'N/A'
            value = client_row[col] if col < len(client_row) and client_row[col] else ''
            print(f"  Col {col+1} (índice {col}): '{header}' = '{value}'")
    
    print("\n" + "=" * 70)
    print("🎯 Análise concluída!")
    print("=" * 70)

if __name__ == "__main__":
    main()
