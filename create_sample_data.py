#!/usr/bin/env python3
"""
Script para criar dados de exemplo no Google Sheets para testar o dashboard
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime
import uuid

# Configurar variáveis
GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
GOOGLE_SHEETS_RANGE = "Clientes!A:BC"

def create_sample_clients():
    """Cria clientes de exemplo para teste do dashboard"""
    print("🧪 === CRIANDO DADOS DE EXEMPLO ===")
    
    try:
        # Inicializar serviço
        storage_service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Dados de exemplo com diferentes regimes
        sample_clients = [
            {
                'nomeEmpresa': 'Empresa MEI Exemplo',
                'regimeFederal': 'MEI',
                'perfil': 'MICROEMPREENDEDOR INDIVIDUAL',
                'cnpj': '12.345.678/0001-90',
                'ativo': True,
                'ct': True,
                'fs': False,
                'dp': False,
                'bpoFinanceiro': False
            },
            {
                'nomeEmpresa': 'Empresa Simples Nacional',
                'regimeFederal': 'SIMPLES NACIONAL',
                'perfil': 'EMPRESA',
                'cnpj': '98.765.432/0001-10',
                'ativo': True,
                'ct': True,
                'fs': True,
                'dp': False,
                'bpoFinanceiro': False
            },
            {
                'nomeEmpresa': 'Empresa Lucro Presumido',
                'regimeFederal': 'LUCRO PRESUMIDO',
                'perfil': 'EMPRESA',
                'cnpj': '11.222.333/0001-44',
                'ativo': True,
                'ct': False,
                'fs': True,
                'dp': True,
                'bpoFinanceiro': True
            },
            {
                'nomeEmpresa': 'Empresa Lucro Real',
                'regimeFederal': 'LUCRO REAL',
                'perfil': 'EMPRESA',
                'cnpj': '55.666.777/0001-88',
                'ativo': True,
                'ct': True,
                'fs': True,
                'dp': True,
                'bpoFinanceiro': False
            },
            {
                'nomeEmpresa': 'Empregada Doméstica Exemplo',
                'regimeFederal': 'EMPREGADA DOMESTICA',
                'perfil': 'DOMESTICA',
                'cnpj': '',
                'ativo': True,
                'ct': False,
                'fs': False,
                'dp': True,
                'bpoFinanceiro': False
            }
        ]
        
        # Salvar cada cliente
        sucessos = 0
        for i, client in enumerate(sample_clients, 1):
            print(f"💾 Salvando cliente {i}: {client['nomeEmpresa']}")
            
            if storage_service.save_client(client):
                sucessos += 1
                print(f"   ✅ Cliente salvo com sucesso!")
            else:
                print(f"   ❌ Erro ao salvar cliente")
        
        print(f"\n🎉 {sucessos}/{len(sample_clients)} clientes de exemplo criados!")
        
        # Verificar os dados
        print(f"\n📊 Verificando dados...")
        clients = storage_service.get_clients()
        print(f"✅ {len(clients)} clientes encontrados no total")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao criar dados de exemplo: {e}")
        return False

if __name__ == '__main__':
    create_sample_clients()
