#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste para verificar as posições corretas dos campos de senha nos cabeçalhos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

# Configurações
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
GOOGLE_SHEETS_RANGE = 'Clientes!A:DD'

def verificar_posicoes_senha():
    """Verifica as posições dos campos de senha nos cabeçalhos"""
    
    try:
        service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        headers = service.get_headers()
        
        # Campos que estamos procurando
        campos_senha = [
            'CNPJ ACESSO SIMPLES NACIONAL',
            'CPF DO REPRESENTANTE LEGAL', 
            'CÓDIGO ACESSO SN',
            'SENHA ISS',
            'SENHA SEFIN',
            'SENHA SEUMA',
            'ACESSO EMPWEB',
            'SENHA EMPWEB',
            'LOGIN ANVISA EMPRESA',
            'SENHA ANVISA EMPRESA',
            'LOGIN ANVISA GESTOR',
            'SENHA ANVISA GESTOR',
            'ACESSO CRF',
            'SENHA FAP/INSS'
        ]
        
        print("📊 Posições dos campos de senha nos cabeçalhos:")
        print(f"📊 Total de headers: {len(headers)}")
        print()
        
        for campo in campos_senha:
            try:
                posicao = headers.index(campo)
                print(f"✅ {campo}: posição {posicao}")
            except ValueError:
                print(f"❌ {campo}: NÃO ENCONTRADO")
        
        print()
        print("📋 Headers próximos às posições 59-73:")
        for i in range(59, min(74, len(headers))):
            print(f"   {i}: {headers[i]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_posicoes_senha()
