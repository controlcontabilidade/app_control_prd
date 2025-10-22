#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar a posição correta do campo DOMÉSTICA nos cabeçalhos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("\n" + "="*70)
    print("VERIFICAÇÃO DA POSIÇÃO DO CAMPO DOMÉSTICA")
    print("="*70 + "\n")
    
    service = GoogleSheetsServiceAccountService()
    
    # Pegar headers
    headers = service.get_headers()
    
    print(f"📊 Total de cabeçalhos: {len(headers)}")
    print()
    
    # Encontrar DOMÉSTICA
    try:
        pos_domestica = headers.index('DOMÉSTICA')
        print(f"✅ Campo 'DOMÉSTICA' encontrado!")
        print(f"   📍 Posição nos headers: {pos_domestica}")
        print(f"   📍 Índice para row[]: {pos_domestica}")
        print(f"   📍 Número da coluna: {pos_domestica + 1}")
        print()
        
        # Mostrar vizinhos
        print(f"🔍 Campos vizinhos:")
        if pos_domestica > 0:
            print(f"   [{pos_domestica - 1}] {headers[pos_domestica - 1]}")
        print(f"   [{pos_domestica}] *** {headers[pos_domestica]} ***")
        if pos_domestica < len(headers) - 1:
            print(f"   [{pos_domestica + 1}] {headers[pos_domestica + 1]}")
        print()
        
        # Verificar a posição 104 que está no código
        print(f"❌ Posição ERRADA no código (104):")
        print(f"   Campo na posição 104: '{headers[104] if 104 < len(headers) else 'FORA DO RANGE'}'")
        print()
        
    except ValueError:
        print(f"❌ Campo 'DOMÉSTICA' NÃO encontrado nos headers!")
        print()
        
        # Procurar variações
        for i, h in enumerate(headers):
            if 'DOMÉST' in h.upper() or 'DOMESTIC' in h.upper():
                print(f"   🔍 Possível match na posição {i}: '{h}'")
        print()
    
    print("="*70)

if __name__ == '__main__':
    main()
