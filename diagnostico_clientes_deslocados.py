#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de Clientes com Dados Deslocados
===========================================
Identifica clientes salvos fora do mapeamento correto (coluna FB+)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def diagnosticar_clientes_deslocados():
    """Identifica clientes com dados na coluna FB ou posterior"""
    
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DE CLIENTES DESLOCADOS")
    print("="*80)
    
    spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID', '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    service = GoogleSheetsServiceAccountService(spreadsheet_id)
    
    # Buscar dados brutos da planilha
    print("\n📊 Buscando dados da planilha...")
    
    try:
        # Usar o serviço do Google Sheets diretamente
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Obter credenciais
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds_file = 'service-account-key.json'
        
        if os.path.exists(creds_file):
            credentials = service_account.Credentials.from_service_account_file(
                creds_file, scopes=SCOPES)
        else:
            print("❌ Arquivo de credenciais não encontrado!")
            return
        
        # Criar serviço
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Clientes!A1:ZZ500'  # Expandir para pegar colunas além do esperado
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ Nenhum dado encontrado!")
            return
        
        headers = values[0] if values else []
        total_colunas = len(headers)
        
        print(f"\n📊 Total de colunas com cabeçalho: {total_colunas}")
        print(f"📊 Total de linhas: {len(values)}")
        
        # Índice da coluna FB (FB = coluna 158 no formato A=1, B=2... AA=27, AB=28... FB=158)
        # F = 6, B = 2 -> FB = (6-1)*26 + 2 = 132
        coluna_fb_index = 158  # FB em zero-based
        
        print(f"\n🔍 Procurando dados a partir da coluna {coluna_fb_index} (FB)...")
        
        clientes_afetados = []
        
        # Analisar cada linha a partir da linha 444 (índice 443 em zero-based, mas 444 em 1-based)
        print(f"\n📋 Analisando linhas a partir da linha 444...")
        
        for idx, row in enumerate(values[1:], start=2):  # Pula cabeçalho, linha 2 = idx 2
            if idx < 444:
                continue
            
            # Verificar se há dados além da coluna esperada (172)
            if len(row) > 172:
                # Pegar nome da empresa (coluna 0)
                nome_empresa = row[0] if len(row) > 0 else 'DESCONHECIDO'
                client_id = row[153] if len(row) > 153 else 'SEM ID'
                
                # Contar quantas colunas extras
                colunas_extras = len(row) - 172
                
                # Verificar se há dados nas colunas extras
                dados_extras = row[172:]
                tem_dados_extras = any(cell.strip() for cell in dados_extras if cell)
                
                if tem_dados_extras:
                    clientes_afetados.append({
                        'linha': idx,
                        'nome': nome_empresa,
                        'id': client_id,
                        'total_colunas': len(row),
                        'colunas_extras': colunas_extras,
                        'dados_extras': [cell for cell in dados_extras if cell.strip()][:5]  # Primeiros 5 dados
                    })
        
        # Resultados
        print("\n" + "="*80)
        print("📊 RESULTADOS DO DIAGNÓSTICO")
        print("="*80)
        
        if not clientes_afetados:
            print("\n✅ Nenhum cliente com dados deslocados encontrado!")
        else:
            print(f"\n⚠️ ENCONTRADOS {len(clientes_afetados)} CLIENTES COM DADOS DESLOCADOS:")
            print("-" * 80)
            
            for cliente in clientes_afetados:
                print(f"\n📍 Linha {cliente['linha']}: {cliente['nome']}")
                print(f"   ID: {cliente['id']}")
                print(f"   Total de colunas: {cliente['total_colunas']} (esperado: 172)")
                print(f"   Colunas extras: {cliente['colunas_extras']}")
                print(f"   Primeiros dados extras: {cliente['dados_extras']}")
        
        # Analisar padrão
        if clientes_afetados:
            print("\n" + "="*80)
            print("📊 ANÁLISE DE PADRÃO")
            print("="*80)
            
            # Verificar se todos têm o mesmo número de colunas extras
            colunas_extras_set = set(c['colunas_extras'] for c in clientes_afetados)
            
            if len(colunas_extras_set) == 1:
                print(f"\n✅ Padrão consistente: Todos têm {list(colunas_extras_set)[0]} colunas extras")
            else:
                print(f"\n⚠️ Padrão inconsistente: Diferentes números de colunas extras")
                print(f"   Variações: {sorted(colunas_extras_set)}")
            
            # Verificar primeira linha afetada
            primeira_linha = min(c['linha'] for c in clientes_afetados)
            print(f"\n📍 Primeira linha afetada: {primeira_linha}")
            
            # Listar todos os IDs afetados
            print(f"\n📋 IDs dos clientes afetados:")
            for cliente in clientes_afetados:
                print(f"   - ID {cliente['id']}: {cliente['nome']} (linha {cliente['linha']})")
        
        return clientes_afetados
        
    except Exception as e:
        print(f"\n❌ Erro ao buscar dados: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    diagnosticar_clientes_deslocados()
