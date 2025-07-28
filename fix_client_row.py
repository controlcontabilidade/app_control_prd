#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir a linha do cliente na planilha Google Sheets
Problema: A linha de dados tem apenas 92 colunas, mas o ID deve estar no índice 92 (coluna 93)
"""

import os
import sys
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def fix_client_row():
    """Corrige a linha do cliente expandindo-a para 93 colunas e colocando o ID na posição correta"""
    
    print("🔧 === SCRIPT DE CORREÇÃO DA LINHA DO CLIENTE ===")
    
    # Configurar service
    spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    service_obj = GoogleSheetsServiceAccountService(spreadsheet_id)
    service = service_obj
    
    try:
        print("📊 Buscando dados da planilha...")
        
        # Buscar dados atuais da planilha
        result = service.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Clientes!A:CZ'
        ).execute()
        
        values = result.get('values', [])
        print(f"📊 Planilha tem {len(values)} linhas")
        
        if len(values) < 2:
            print("❌ Não há dados para corrigir")
            return False
        
        # Cabeçalhos (linha 1)
        headers = values[0]
        # Dados do cliente (linha 2)
        client_row = values[1] if len(values) > 1 else []
        
        print(f"📊 Cabeçalhos: {len(headers)} colunas")  
        print(f"📊 Linha do cliente: {len(client_row)} colunas")
        
        # Verificar se precisa de correção
        if len(client_row) >= 93:
            print("✅ Linha do cliente já tem 93+ colunas. Verificando ID...")
            
            # Verificar se ID está na posição correta
            if len(client_row) > 92 and client_row[92]:
                print(f"✅ ID já está na posição 92: '{client_row[92]}'")
                return True
        
        print("🔧 Corrigindo linha do cliente...")
        
        # Fazer uma cópia da linha atual
        fixed_row = client_row[:]
        
        # Encontrar o ID atual (pode estar em posições antigas)
        current_id = "1753699151"  # ID conhecido do logs
        
        # Verificar se o ID está em alguma posição antiga (89, 90, 91)
        for i in [89, 90, 91]:
            if i < len(fixed_row) and fixed_row[i] and str(fixed_row[i]).strip():
                potential_id = str(fixed_row[i]).strip()
                if potential_id.isdigit() and len(potential_id) == 10:
                    current_id = potential_id
                    print(f"🔍 ID encontrado na posição {i}: '{current_id}'")
                    break
        
        print(f"🔍 Usando ID: '{current_id}'")
        
        # Expandir a linha até 93 colunas
        while len(fixed_row) < 93:
            fixed_row.append('')
        
        # Colocar o ID na posição correta (índice 92)
        fixed_row[92] = current_id
        fixed_row[91] = 'SIM'  # CLIENTE ATIVO
        
        print(f"✅ Linha expandida para {len(fixed_row)} colunas")
        print(f"✅ ID colocado na posição 92: '{fixed_row[92]}'")
        
        # Atualizar a planilha
        range_name = 'Clientes!A2:CZ2'
        body = {'values': [fixed_row]}
        
        print(f"📝 Atualizando planilha no range: {range_name}")
        
        update_result = service.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        updated_cells = update_result.get('updatedCells', 0)
        print(f"✅ SUCESSO! Linha corrigida com {updated_cells} células atualizadas")
        
        # Verificar se a correção funcionou
        print("🔍 Verificando correção...")
        verification_result = service.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Clientes!A2:CZ2'
        ).execute()
        
        verification_row = verification_result.get('values', [[]])[0] if verification_result.get('values') else []
        print(f"📊 Linha verificada: {len(verification_row)} colunas")
        
        if len(verification_row) > 92:
            print(f"✅ ID na posição 92: '{verification_row[92]}'")
        else:
            print("❌ Linha ainda não tem colunas suficientes")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = fix_client_row()
    if success:
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("🔄 Reinicie o servidor Flask para testar a edição do cliente")
    else:
        print("\n❌ FALHA NA CORREÇÃO")
        print("🔍 Verifique os logs acima para detalhes")
    
    sys.exit(0 if success else 1)
