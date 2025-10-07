#!/usr/bin/env python3
"""
Correção FORÇADA para os cadastros específicos que ainda têm 'SIM' na Data de Criação
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import direto do serviço
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def column_letter(col_num):
    """Converte número da coluna para letra (152 -> EU)"""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord('A')) + result
        col_num //= 26
    return result

def main():
    print("🚀 CORREÇÃO FORÇADA - Clientes específicos com 'SIM'")
    
    try:
        # Inicializar serviço
        spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        print("✅ Serviço inicializado")
        
        # Lista dos clientes problemáticos identificados
        problematic_clients = [
            {
                'nome': 'A P DO AMARAL LEITE DE SENA MANIPULACAO',
                'id': '2025-10-02T20:28:50.267025',
                'linha': 2  # Linha 2 na planilha
            },
            {
                'nome': 'ALBERTO COMERCIO DE MEDICAMENTOS E CORRELATOS LTDA',
                'id': '2025-09-16T18:05:04.938778',
                'linha': 3  # Linha 3 na planilha
            }
        ]
        
        print(f"🎯 Corrigindo {len(problematic_clients)} clientes específicos...")
        
        # Coluna DATA DE CRIAÇÃO é a 152 (EU)
        criado_em_col = 152
        col_letter = column_letter(criado_em_col)
        print(f"📍 Coluna DATA DE CRIAÇÃO: {criado_em_col} ({col_letter})")
        
        corrections_made = 0
        
        for i, client in enumerate(problematic_clients, 1):
            print(f"\n🔧 [{i}/{len(problematic_clients)}] Corrigindo: {client['nome'][:40]}...")
            
            # Usar o ID como Data de Criação (já está no formato timestamp)
            new_created_date = client['id']
            
            # Calcular célula específica
            cell_range = f"{col_letter}{client['linha']}"
            
            print(f"   📍 Célula: {cell_range}")
            print(f"   📅 Nova data: {new_created_date}")
            
            try:
                # Atualizar célula específica diretamente
                values = [[new_created_date]]
                body = {'values': values}
                
                result = service.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Clientes!{cell_range}",
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                cells_updated = result.get('updatedCells', 0)
                if cells_updated > 0:
                    print(f"   ✅ Correção aplicada! ({cells_updated} célula atualizada)")
                    corrections_made += 1
                else:
                    print(f"   ❌ Nenhuma célula foi atualizada")
                    
            except Exception as e:
                print(f"   ❌ Erro ao corrigir: {e}")
                
        print(f"\n🎯 RESUMO DA CORREÇÃO FORÇADA:")
        print(f"   ✅ Clientes corrigidos: {corrections_made}")
        print(f"   📊 Total processados: {len(problematic_clients)}")
        
        if corrections_made > 0:
            print(f"\n🎉 Correção concluída! {corrections_made} clientes foram corrigidos.")
            print("📝 Aguarde alguns segundos e verifique novamente a tela de visualização.")
        else:
            print("\n⚠️  Nenhuma correção foi aplicada. Pode haver outro problema.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()