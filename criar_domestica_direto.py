#!/usr/bin/env python3
"""
Script para criar cliente doméstica teste DIRETO
"""

import sys
sys.path.append('.')

# Importar usando o método correto do arquivo app.py
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

print("� ===== CRIANDO CLIENTE EMPRESA TESTE DIRETO =====")

# Inicializar serviço diretamente 
service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')

# Dados do cliente empresa (NÃO doméstica)
cliente_empresa = {
    'nomeEmpresa': 'EMPRESA TESTE CONTAGEM',
    'razaoSocialReceita': 'EMPRESA LTDA',
    'nomeFantasiaReceita': 'EMPRESA TESTE',
    'cpfCnpj': '12.345.678/0001-99',
    'perfil': 'A',
    'domestica': 'NÃO',  # CAMPO CRUCIAL - EMPRESA
    'regimeFederal': 'SIMPLES_NACIONAL',
    'estado': 'MA',
    'cidade': 'SAO LUIS',
    'ativo': 'SIM'
}

print("📊 Salvando cliente empresa...")
resultado = service.save_client(cliente_empresa)

if resultado:
    print("✅ Cliente empresa criado com sucesso!")
    
    print("\n🔍 ===== VERIFICANDO CONTAGEM DO DASHBOARD =====")
    
    # Buscar todos os clientes
    clientes = service.get_clients()
    total = len(clientes)
    
    # Contar por categoria usando a nova lógica
    empresas = 0
    domesticas = 0
    
    for client in clientes:
        domestica_val = (client.get('domestica') or '').strip().upper()
        print(f"Cliente: {client.get('nomeEmpresa', 'SEM_NOME')} - domestica: '{domestica_val}'")
        
        if domestica_val == 'SIM':
            domesticas += 1
            print(f"  → Contado como DOMÉSTICA")
        else:
            empresas += 1
            print(f"  → Contado como EMPRESA")
    
    print(f"\n📈 ===== RESULTADO DA CONTAGEM =====")
    print(f"Total de clientes: {total}")
    print(f"Empresas: {empresas}")
    print(f"Domésticas: {domesticas}")
    
else:
    print(f"❌ Erro ao criar cliente")