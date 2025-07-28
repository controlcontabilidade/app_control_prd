#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("=" * 70)
    print("🔍 ANÁLISE DETALHADA DOS DADOS BRUTOS")
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
    
    print(f"\n📊 Cabeçalhos importantes:")
    important_cols = [17, 18, 84, 85, 86, 87, 88, 92, 93, 94]
    for col in important_cols:
        if col < len(headers):
            print(f"  Col {col+1} (índice {col}): '{headers[col]}'")
    
    print(f"\n📊 Dados da linha do cliente:")
    print(f"  Total de colunas: {len(client_row)}")
    
    for col in important_cols:
        if col < len(client_row):
            value = client_row[col] if client_row[col] else ''
            print(f"  Col {col+1} (índice {col}): '{value}'")
    
    print(f"\n🔍 Analisando padrão de timestamps:")
    timestamps_found = []
    for i, value in enumerate(client_row):
        if value and 'T' in str(value) and ':' in str(value):
            timestamps_found.append((i, value))
    
    print(f"📊 Timestamps encontrados: {len(timestamps_found)}")
    for col, value in timestamps_found:
        print(f"  Col {col+1} (índice {col}): '{value}'")
    
    print("\n" + "=" * 70)
    print("🎯 Análise concluída!")
    print("=" * 70)

if __name__ == "__main__":
    main()
