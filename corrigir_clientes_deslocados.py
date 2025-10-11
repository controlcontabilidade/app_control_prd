#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Correção de Clientes Deslocados
================================
Corrige os 8 clientes (linhas 444-451) que foram salvos
com dados nas colunas erradas (a partir da coluna FB)
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.oauth2 import service_account
from googleapiclient.discovery import build

def analisar_linha_deslocada(row, linha_num):
    """Analisa uma linha deslocada e tenta recuperar os dados corretos"""
    
    print(f"\n{'='*80}")
    print(f"🔍 ANALISANDO LINHA {linha_num}")
    print(f"{'='*80}")
    
    print(f"\n📊 Total de colunas: {len(row)}")
    print(f"📊 Colunas esperadas: 172")
    print(f"📊 Colunas extras: {len(row) - 172}")
    
    # Mostrar primeiras 20 colunas
    print(f"\n📋 Primeiras 20 colunas:")
    for i, valor in enumerate(row[:20]):
        if valor:
            print(f"   Col {i}: '{valor}'")
    
    # Mostrar dados extras (após coluna 172)
    if len(row) > 172:
        print(f"\n📋 Dados extras (a partir da coluna 172):")
        for i, valor in enumerate(row[172:], start=172):
            if valor and i < 192:  # Mostrar até coluna 192
                print(f"   Col {i}: '{valor}'")
    
    return row

def corrigir_clientes_deslocados():
    """Corrige os clientes com dados deslocados"""
    
    print("\n" + "="*80)
    print("🔧 CORREÇÃO DE CLIENTES DESLOCADOS")
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
    
    # Buscar dados das linhas afetadas (444-451)
    print("\n📊 Buscando dados das linhas afetadas...")
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Clientes!A444:ZZ451'  # Linhas 444 a 451
    ).execute()
    
    values = result.get('values', [])
    
    if not values:
        print("❌ Nenhum dado encontrado!")
        return
    
    print(f"\n✅ {len(values)} linhas encontradas")
    
    # Analisar cada linha
    for idx, row in enumerate(values, start=444):
        analisar_linha_deslocada(row, idx)
    
    # Perguntar se deve prosseguir com a correção
    print("\n" + "="*80)
    print("⚠️ AVISO: A correção irá DELETAR essas linhas")
    print("="*80)
    print("\nOpções:")
    print("1. Deletar linhas (elas estão corrompidas e sem ID)")
    print("2. Exportar para análise manual")
    print("3. Cancelar")
    
    escolha = input("\nEscolha uma opção (1/2/3): ").strip()
    
    if escolha == '1':
        print("\n🗑️ Deletando linhas corrompidas...")
        
        # Deletar linhas 444-451 (8 linhas)
        requests = [{
            'deleteDimension': {
                'range': {
                    'sheetId': 0,  # ID da aba Clientes
                    'dimension': 'ROWS',
                    'startIndex': 443,  # Linha 444 (zero-based)
                    'endIndex': 451     # Linha 451 (exclusive)
                }
            }
        }]
        
        body = {'requests': requests}
        
        try:
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            print(f"\n✅ {len(values)} linhas deletadas com sucesso!")
            print("\n📋 Resultado:")
            print(f"   - Linhas removidas: 444-451")
            print(f"   - Total de linhas removidas: 8")
            print(f"   - Status: SUCESSO")
            
        except Exception as e:
            print(f"\n❌ Erro ao deletar linhas: {e}")
            import traceback
            traceback.print_exc()
    
    elif escolha == '2':
        print("\n💾 Exportando para arquivo CSV...")
        
        import csv
        filename = f'clientes_corrompidos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Linha', 'Total_Colunas'] + [f'Col_{i}' for i in range(max(len(row) for row in values))])
            
            for idx, row in enumerate(values, start=444):
                writer.writerow([idx, len(row)] + row)
        
        print(f"\n✅ Dados exportados para: {filename}")
        print("\n📋 Você pode analisar manualmente e decidir o que fazer")
    
    else:
        print("\n❌ Operação cancelada")

if __name__ == '__main__':
    corrigir_clientes_deslocados()
