#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para atualizar os cabeçalhos da planilha com os novos campos de senha
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Atualiza cabeçalhos da planilha"""
    print("🔄 Atualizando cabeçalhos da planilha...")
    
    try:
        # Obter ID da planilha das configurações do app
        try:
            # Importar configurações do app
            import app
            spreadsheet_id = app.GOOGLE_SHEETS_ID
        except:
            # Fallback: usar variável de ambiente
            spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID')
            
        if not spreadsheet_id:
            print("❌ GOOGLE_SHEETS_ID não definido. Verificando storage_service do app...")
            # Tentar obter do storage_service inicializado
            try:
                import app
                if hasattr(app, 'storage_service') and app.storage_service:
                    spreadsheet_id = app.storage_service.spreadsheet_id
                    print(f"✅ Obtido do storage_service: {spreadsheet_id[:20]}...")
            except:
                pass
                
        if not spreadsheet_id:
            print("❌ Não foi possível obter o GOOGLE_SHEETS_ID")
            return
            
        print(f"📊 Usando planilha: {spreadsheet_id[:20]}...")
        
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        
        # Forçar atualização dos cabeçalhos
        result = service.ensure_correct_headers()
        
        # Obter os cabeçalhos atuais
        headers = service.get_headers()
        
        if isinstance(result, bool) and result:
            print(f"✅ Cabeçalhos já estavam corretos! Total: {len(headers)} colunas")
        else:
            print(f"✅ Cabeçalhos atualizados! Total: {len(headers)} colunas")
        
        # Verificar campos de senha
        password_fields = [
            'CNPJ ACESSO SIMPLES NACIONAL',
            'CPF DO REPRESENTANTE LEGAL', 
            'CÓDIGO ACESSO SN',
            'SENHA ISS',
            'SENHA SEFIN',
            'SENHA SEUMA',
            'LOGIN ANVISA EMPRESA',
            'SENHA ANVISA EMPRESA',
            'LOGIN ANVISA GESTOR',
            'SENHA ANVISA GESTOR',
            'SENHA FAP/INSS'
        ]
        
        print("\n🔍 Verificação de campos de senha:")
        for field in password_fields:
            if field in headers:
                pos = headers.index(field) + 1  # +1 porque planilha começa em 1
                print(f"✅ {field}: posição {pos}")
            else:
                print(f"❌ {field}: NÃO ENCONTRADO")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
