#!/usr/bin/env python3
"""
Verificação DIRETA dos dados na planilha Google Sheets
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import direto do serviço
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔍 VERIFICAÇÃO DIRETA - Google Sheets")
    
    try:
        # Inicializar serviço
        spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        print("✅ Serviço inicializado")
        
        # Buscar dados DIRETAMENTE da planilha
        print("\n📊 Buscando dados RAW da planilha...")
        
        # Coluna EV (152) - DATA DE CRIAÇÃO das linhas 2 e 3
        ranges_to_check = [
            "Clientes!EV2:EV3",  # DATA DE CRIAÇÃO das duas linhas problemáticas
            "Clientes!A2:A3",   # NOME DAS EMPRESAS
            "Clientes!FQ2:FQ3"  # ID (coluna 153)
        ]
        
        for range_name in ranges_to_check:
            print(f"\n🔍 Verificando range: {range_name}")
            
            try:
                result = service.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                print(f"   📝 Dados encontrados: {len(values)} linha(s)")
                
                for i, row in enumerate(values, 1):
                    if row:
                        print(f"   [{i}] {row[0] if row else 'VAZIO'}")
                    else:
                        print(f"   [{i}] LINHA VAZIA")
                        
            except Exception as e:
                print(f"   ❌ Erro ao buscar {range_name}: {e}")
        
        # Tentar uma atualização forçada DIRETA
        print(f"\n🚀 TENTATIVA DE CORREÇÃO DIRETA")
        
        # Preparar os valores corretos
        correction_data = [
            ["2025-10-02T20:28:50.267025"],  # Para linha 2
            ["2025-09-16T18:05:04.938778"]   # Para linha 3
        ]
        
        print(f"📝 Dados a serem inseridos:")
        for i, data in enumerate(correction_data, 2):
            print(f"   Linha {i}: {data[0]}")
        
        # Aplicar correção direta
        try:
            body = {'values': correction_data}
            result = service.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Clientes!EV2:EV3",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            cells_updated = result.get('updatedCells', 0)
            print(f"✅ Correção aplicada: {cells_updated} células atualizadas")
            
            # Verificar se foi aplicado
            print(f"\n🔍 VERIFICAÇÃO PÓS-CORREÇÃO")
            result_check = service.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range="Clientes!EV2:EV3"
            ).execute()
            
            values_check = result_check.get('values', [])
            print(f"📝 Dados após correção:")
            for i, row in enumerate(values_check, 2):
                if row:
                    print(f"   Linha {i}: {row[0]}")
                else:
                    print(f"   Linha {i}: VAZIO")
                    
        except Exception as e:
            print(f"❌ Erro na correção direta: {e}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()