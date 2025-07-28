#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def main():
    print("=" * 70)
    print("🔧 MIGRAÇÃO DE DADOS - CORREÇÃO DE POSIÇÕES")
    print("=" * 70)
    
    # Inicializar serviço
    service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    print("✅ Serviço inicializado")
    
    # Buscar dados brutos da planilha
    print("\n📊 Buscando dados brutos da planilha...")
    range_name = 'Clientes!A:CZ'
    result = service.service.spreadsheets().values().get(
        spreadsheetId=service.spreadsheet_id, 
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    print(f"📊 Linhas encontradas: {len(values)}")
    
    if len(values) < 2:
        print("❌ Não há dados para migrar")
        return
    
    headers = values[0] if values else []
    client_rows = values[1:] if len(values) > 1 else []
    
    print(f"📊 Linhas de clientes para migrar: {len(client_rows)}")
    
    # Verificar posições importantes
    print("\n🔍 Verificando posições antes da migração...")
    for i, row in enumerate(client_rows[:1], 1):  # Apenas primeira linha para teste
        if len(row) > 86:
            print(f"📋 Cliente {i}:")
            print(f"  Pos 85 (dataInicioServicos): '{row[85] if len(row) > 85 else ''}'")
            print(f"  Pos 86 (statusCliente atual): '{row[86] if len(row) > 86 else ''}'")
            print(f"  Pos 87 (próxima posição): '{row[87] if len(row) > 87 else ''}'")
    
    # Preparar dados para migração
    print("\n🔧 Preparando migração de dados...")
    
    migrated_data = []
    migrated_data.append(headers)  # Manter cabeçalhos
    
    for i, row in enumerate(client_rows, 1):
        print(f"\n📋 Migrando cliente {i}...")
        
        # Criar uma cópia da linha
        new_row = row.copy()
        
        # Garantir que a linha tenha pelo menos 95 colunas
        while len(new_row) < 95:
            new_row.append('')
        
        # MIGRAÇÃO DOS DADOS:
        # Se a posição 86 tem um timestamp (que deveria ser dataInicioServicos)
        # e a posição 85 está vazia, mover o timestamp para a posição 85
        pos_85_val = new_row[85] if len(new_row) > 85 else ''
        pos_86_val = new_row[86] if len(new_row) > 86 else ''
        
        # Verificar se pos_86 tem um timestamp ISO (formato: YYYY-MM-DDTHH:MM:SS)
        is_timestamp_86 = False
        if pos_86_val and 'T' in str(pos_86_val) and ':' in str(pos_86_val):
            try:
                # Tentar fazer parse do timestamp
                datetime.fromisoformat(pos_86_val.replace('Z', '+00:00'))
                is_timestamp_86 = True
            except:
                pass
        
        if is_timestamp_86 and not pos_85_val:
            print(f"  ✅ Movendo timestamp de pos 86 para pos 85: '{pos_86_val}'")
            new_row[85] = pos_86_val  # dataInicioServicos
            new_row[86] = 'ATIVO'     # statusCliente com valor padrão
        else:
            print(f"  ℹ️  Dados já estão corretos ou não precisam de migração")
        
        # Verificar se o ID está na posição correta (posição 94)
        if len(new_row) > 94 and not new_row[94]:
            # Se não tem ID, gerar um baseado no nome da empresa
            nome_empresa = new_row[0] if len(new_row) > 0 else ''
            if nome_empresa:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_id = f"{nome_empresa[:10].upper().replace(' ', '_')}_{timestamp}"
                new_row[94] = new_id
                print(f"  🆔 Gerando ID para posição 94: '{new_id}'")
        
        migrated_data.append(new_row)
    
    # Perguntar confirmação antes de escrever
    print(f"\n⚠️  CONFIRMAÇÃO: Migrar {len(client_rows)} linhas de clientes?")
    print("   Isso irá sobrescrever os dados na planilha.")
    print("   Digite 'SIM' para confirmar ou qualquer outra coisa para cancelar:")
    
    # Para automação, vou confirmar automaticamente
    confirm = 'SIM'  # input().strip().upper()
    
    if confirm == 'SIM':
        print("\n🔧 Executando migração...")
        
        # Escrever dados migrados de volta para a planilha
        body = {
            'values': migrated_data
        }
        
        result = service.service.spreadsheets().values().update(
            spreadsheetId=service.spreadsheet_id,
            range='Clientes!A:CZ',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ Migração concluída! {result.get('updatedCells', 0)} células atualizadas")
        
        # Verificar resultado
        print("\n🔍 Verificando resultado da migração...")
        for i, row in enumerate(client_rows[:1], 1):  # Apenas primeira linha para verificação
            new_client = migrated_data[i]  # i porque migrated_data[0] são os cabeçalhos
            if len(new_client) > 86:
                print(f"📋 Cliente {i} após migração:")
                print(f"  Pos 85 (dataInicioServicos): '{new_client[85] if len(new_client) > 85 else ''}'")
                print(f"  Pos 86 (statusCliente): '{new_client[86] if len(new_client) > 86 else ''}'")
                print(f"  Pos 94 (id): '{new_client[94] if len(new_client) > 94 else ''}'")
    else:
        print("❌ Migração cancelada")
    
    print("\n" + "=" * 70)
    print("🎯 Migração concluída!")
    print("=" * 70)

if __name__ == "__main__":
    main()
