#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se os contatos de teste foram adicionados corretamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def verificar_contatos():
    # Inicializar service
    service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    
    print("🔍 [VERIFICAR] ===== VERIFICANDO CONTATOS DO CLIENTE TESTE =====")
    
    # ID do cliente de teste
    client_id = '1756032228826'
    
    # Buscar o cliente
    client = service.get_client(client_id)
    
    if client:
        print(f"✅ [VERIFICAR] Cliente encontrado: {client.get('nomeEmpresa', 'N/A')}")
        print(f"🔍 [VERIFICAR] ID do cliente: {client.get('id', 'N/A')}")
        
        print("\n🔍 [VERIFICAR] ===== DEBUG CONTATOS =====")
        for i in range(1, 6):
            nome = client.get(f'contato_{i}_nome', '')
            cargo = client.get(f'contato_{i}_cargo', '')
            telefone = client.get(f'contato_{i}_telefone', '')
            email = client.get(f'contato_{i}_email', '')
            
            print(f"🔍 [VERIFICAR] Contato {i}:")
            print(f"  Nome: '{nome}'")
            print(f"  Cargo: '{cargo}'")
            print(f"  Telefone: '{telefone}'")
            print(f"  Email: '{email}'")
            print()
            
        # Contar contatos válidos
        contatos_validos = 0
        for i in range(1, 6):
            nome = client.get(f'contato_{i}_nome', '').strip()
            if nome:
                contatos_validos += 1
                
        print(f"📊 [VERIFICAR] Total de contatos com nome preenchido: {contatos_validos}")
        
        if contatos_validos >= 3:
            print("✅ [VERIFICAR] SUCESSO: Cliente tem múltiplos contatos para teste!")
            return True
        else:
            print("❌ [VERIFICAR] ERRO: Cliente não tem contatos suficientes para teste!")
            return False
            
    else:
        print("❌ [VERIFICAR] Cliente não encontrado!")
        return False

if __name__ == "__main__":
    verificar_contatos()
