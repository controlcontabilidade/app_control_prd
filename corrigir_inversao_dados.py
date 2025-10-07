#!/usr/bin/env python3
"""
Correção da INVERSÃO de dados entre criadoEm (pos 152) e id (pos 153)
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import direto do serviço
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🚀 CORREÇÃO DA INVERSÃO DE DADOS")
    
    try:
        # Inicializar serviço
        spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        print("✅ Serviço inicializado")
        
        # Definir os dados CORRETOS para cada posição
        corrections = [
            {
                'linha': 2,
                'nome': 'A P DO AMARAL LEITE DE SENA MANIPULACAO',
                'id_correto': '2025-10-02T20:28:50.267025',  # Deve ir para posição 153
                'criado_em_correto': '2025-10-02T20:28:50.267025'  # Deve ir para posição 152
            },
            {
                'linha': 3,
                'nome': 'ALBERTO COMERCIO DE MEDICAMENTOS E CORRELATOS LTDA',
                'id_correto': '2025-09-16T18:05:04.938778',  # Deve ir para posição 153
                'criado_em_correto': '2025-09-16T18:05:04.938778'  # Deve ir para posição 152
            }
        ]
        
        print(f"🎯 Corrigindo {len(corrections)} registros...")
        
        for correction in corrections:
            linha = correction['linha']
            nome = correction['nome']
            id_correto = correction['id_correto']
            criado_em_correto = correction['criado_em_correto']
            
            print(f"\n🔧 Corrigindo linha {linha}: {nome[:40]}...")
            
            # Corrigir posição 152 (criadoEm) - EV
            try:
                body_criado_em = {'values': [[criado_em_correto]]}
                result1 = service.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Clientes!EV{linha}",  # Posição 152
                    valueInputOption='RAW',
                    body=body_criado_em
                ).execute()
                print(f"   ✅ criadoEm (pos 152): {result1.get('updatedCells', 0)} célula")
            except Exception as e:
                print(f"   ❌ Erro ao corrigir criadoEm: {e}")
            
            # Corrigir posição 153 (id) - EW
            try:
                body_id = {'values': [[id_correto]]}
                result2 = service.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Clientes!EW{linha}",  # Posição 153
                    valueInputOption='RAW',
                    body=body_id
                ).execute()
                print(f"   ✅ id (pos 153): {result2.get('updatedCells', 0)} célula")
            except Exception as e:
                print(f"   ❌ Erro ao corrigir id: {e}")
        
        # Verificar se as correções funcionaram
        print(f"\n🔍 VERIFICAÇÃO FINAL...")
        
        # Buscar dados atualizados
        result = service.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Clientes!EV2:EW3"  # Posições 152 e 153 das linhas 2 e 3
        ).execute()
        
        values = result.get('values', [])
        for i, row in enumerate(values, 2):
            if len(row) >= 2:
                criado_em = row[0]  # Posição 152
                id_val = row[1]     # Posição 153
                print(f"   Linha {i}: criadoEm='{criado_em}' | id='{id_val}'")
            else:
                print(f"   Linha {i}: DADOS INCOMPLETOS")
                
        print(f"\n🎉 Correção concluída! Aguarde alguns segundos e teste a visualização.")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()