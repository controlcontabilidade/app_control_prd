#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar especificamente o cliente mais novo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Testa o cliente mais recente"""
    print("🔍 Testando o cliente mais novo...")
    
    try:
        # Importar e usar as configurações do app
        import app
        spreadsheet_id = app.GOOGLE_SHEETS_ID
        
        from services.google_sheets_service_account import GoogleSheetsServiceAccountService
        service = GoogleSheetsServiceAccountService(spreadsheet_id)
        
        # Buscar todos os clientes
        clientes = service.get_clients()
        print(f"📊 Total de clientes encontrados: {len(clientes)}")
        
        # Encontrar o cliente mais novo por timestamp ID
        cliente_mais_novo = max(clientes, key=lambda c: int(c.get('id', 0)))
        
        print(f"\n🆕 Cliente mais novo:")
        print(f"   Nome: {cliente_mais_novo.get('nomeEmpresa', 'N/A')}")
        print(f"   ID: {cliente_mais_novo.get('id', 'N/A')}")
        
        print(f"\n🔐 Verificação dos campos de senha:")
        campos_senha = [
            'cnpjAcessoSn', 'cpfRepLegal', 'codigoAcessoSn', 'senhaIss',
            'senhaSefin', 'senhaSeuma', 'anvisaEmpresa', 'senhaAnvisaEmpresa',
            'anvisaGestor', 'senhaAnvisaGestor', 'senhaFapInss',
            'acessoEmpWeb', 'senhaEmpWeb', 'acessoCrf'
        ]
        
        for campo in campos_senha:
            valor = cliente_mais_novo.get(campo, '')
            status = "✅" if valor and valor != 'NÃO' else "❌"
            print(f"   {status} {campo}: '{valor}'")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
