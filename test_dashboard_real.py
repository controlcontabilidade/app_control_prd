#!/usr/bin/env python3
"""
Script para testar os indicadores do dashboard com dados reais do Google Sheets
"""

import sys
sys.path.append('.')

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
import os

# Configurar variáveis
GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
GOOGLE_SHEETS_RANGE = "Clientes!A:BC"

def calculate_dashboard_stats(clients):
    """Calcula estatísticas para o dashboard baseado nos dados SIGEC"""
    stats = {
        'total_clientes': len(clients),
        'clientes_ativos': 0,
        'empresas': 0,
        'domesticas': 0,
        'mei': 0,
        'simples_nacional': 0,
        'lucro_presumido': 0,
        'lucro_real': 0,
        'ct': 0,
        'fs': 0,
        'dp': 0,
        'bpo': 0
    }
    
    print(f"🔍 Analisando {len(clients)} clientes...")
    
    for i, client in enumerate(clients):
        # Contadores básicos
        if client.get('ativo', True):
            stats['clientes_ativos'] += 1
        
        # Serviços
        if client.get('ct', False):
            stats['ct'] += 1
        if client.get('fs', False):
            stats['fs'] += 1
        if client.get('dp', False):
            stats['dp'] += 1
        if client.get('bpoFinanceiro', False):
            stats['bpo'] += 1
        
        # Categorização por regime federal (SIGEC)
        regime = str(client.get('regimeFederal', '')).upper().strip()
        perfil = str(client.get('perfil', '')).upper().strip()
        
        # Debug dos primeiros 3 clientes
        if i < 3:
            print(f"   Cliente {i+1}: {client.get('nomeEmpresa', 'N/A')}")
            print(f"      Regime: '{regime}'")
            print(f"      Perfil: '{perfil}'")
        
        # MEI - Microempreendedor Individual
        if 'MEI' in regime or 'MICROEMPRESARIO' in perfil or 'INDIVIDUAL' in perfil:
            stats['mei'] += 1
        # Simples Nacional
        elif 'SIMPLES' in regime or 'SN' in regime:
            stats['simples_nacional'] += 1
        # Lucro Presumido
        elif 'PRESUMIDO' in regime or 'LP' in regime:
            stats['lucro_presumido'] += 1
        # Lucro Real
        elif 'REAL' in regime or 'LR' in regime:
            stats['lucro_real'] += 1
        # Domésticas - identificar por perfil ou atividade
        elif 'DOMESTICA' in perfil or 'EMPREGADA' in perfil:
            stats['domesticas'] += 1
        else:
            # Demais casos consideramos como empresas
            stats['empresas'] += 1
    
    return stats

def test_real_data():
    """Testa com dados reais do Google Sheets"""
    print("🧪 === TESTE COM DADOS REAIS DO GOOGLE SHEETS ===")
    
    try:
        # Inicializar serviço
        storage_service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Carregar clientes
        print("📊 Carregando clientes do Google Sheets...")
        clients = storage_service.get_clients()
        print(f"✅ {len(clients)} clientes carregados")
        
        # Calcular estatísticas
        stats = calculate_dashboard_stats(clients)
        
        print(f"\n📊 === ESTATÍSTICAS DO DASHBOARD ===")
        print(f"   📈 Total de Clientes: {stats['total_clientes']}")
        print(f"   ✅ Clientes Ativos: {stats['clientes_ativos']}")
        print(f"   🏢 Empresas: {stats['empresas']}")
        print(f"   🏠 Domésticas: {stats['domesticas']}")
        print(f"   👤 MEI: {stats['mei']}")
        print(f"   📊 Simples Nacional: {stats['simples_nacional']}")
        print(f"   💰 Lucro Presumido: {stats['lucro_presumido']}")
        print(f"   💎 Lucro Real: {stats['lucro_real']}")
        print(f"   📋 Depto. Contábil: {stats['ct']}")
        print(f"   📄 Depto. Fiscal: {stats['fs']}")
        print(f"   👥 Depto. Pessoal: {stats['dp']}")
        print(f"   💼 BPO Financeiro: {stats['bpo']}")
        
        print(f"\n🎉 TESTE CONCLUÍDO! Dashboard funcionando com dados reais!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        return False

if __name__ == '__main__':
    test_real_data()
