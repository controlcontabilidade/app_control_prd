"""
Verificar campo DOMÉSTICA do cliente criado
"""

import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_SHEETS_ID'] = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def verificar_cliente_525():
    """Verifica o cliente ID 525 criado pelo teste"""
    
    print("\n" + "="*70)
    print("🔍 VERIFICANDO CLIENTE ID 525 (TESTE DOMÉSTICA)")
    print("="*70)
    
    try:
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        
        # Buscar cliente 525
        print("\n1️⃣ Buscando cliente ID 525...")
        client = service.get_client('525')
        
        if client:
            print(f"   ✅ Cliente encontrado!")
            print(f"\n   📋 Dados do cliente:")
            print(f"   - ID: {client.get('id', 'N/A')}")
            print(f"   - Nome: {client.get('nomeEmpresa', 'N/A')}")
            print(f"   - CPF/CNPJ: {client.get('cnpj', 'N/A')}")
            print(f"   - Doméstica: {client.get('domestica', 'N/A')}")
            print(f"   - CT: {client.get('ct', 'N/A')}")
            print(f"   - FS: {client.get('fs', 'N/A')}")
            print(f"   - DP: {client.get('dp', 'N/A')}")
            
            if client.get('domestica') == 'SIM':
                print(f"\n   ✅ SUCESSO! Campo 'doméstica' está correto!")
            else:
                print(f"\n   ❌ ERRO! Campo 'doméstica' está incorreto!")
                print(f"   📊 Esperado: 'SIM'")
                print(f"   📊 Recebido: '{client.get('domestica', 'N/A')}'")
            
            # Deletar cliente de teste
            print(f"\n2️⃣ Removendo cliente de teste...")
            delete_result = service.delete_client('525')
            if delete_result:
                print(f"   ✅ Cliente removido com sucesso!")
            else:
                print(f"   ⚠️ Não foi possível remover o cliente")
        else:
            print(f"   ❌ Cliente 525 não encontrado!")
            
            # Tentar encontrar na planilha RAW
            print(f"\n2️⃣ Buscando na planilha RAW...")
            result = service.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Clientes!A:FP'
            ).execute()
            
            rows = result.get('values', [])
            
            for i, row in enumerate(rows):
                if len(row) > 153 and row[153] == '525':
                    print(f"   ✅ Encontrado na linha {i+1}!")
                    print(f"   - Nome (col 0): {row[0] if len(row) > 0 else 'N/A'}")
                    print(f"   - CNPJ (col 2): {row[2] if len(row) > 2 else 'N/A'}")
                    print(f"   - Doméstica (col 104): {row[104] if len(row) > 104 else 'N/A'}")
                    print(f"   - ID (col 153): {row[153] if len(row) > 153 else 'N/A'}")
                    break
        
        print("\n" + "="*70)
        print("✅ VERIFICAÇÃO CONCLUÍDA!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_cliente_525()
