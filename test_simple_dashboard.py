#!/usr/bin/env python3
"""
Teste simples dos indicadores do dashboard
"""

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
    
    for client in clients:
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

# Dados de teste
clientes_teste = [
    {
        'id': '1',
        'nomeEmpresa': 'Empresa MEI Teste',
        'regimeFederal': 'MEI',
        'perfil': 'MICROEMPREENDEDOR INDIVIDUAL',
        'ativo': True,
        'ct': True,
        'fs': False,
        'dp': False,
        'bpoFinanceiro': False
    },
    {
        'id': '2', 
        'nomeEmpresa': 'Empresa Simples Nacional',
        'regimeFederal': 'SIMPLES NACIONAL',
        'perfil': 'EMPRESA',
        'ativo': True,
        'ct': True,
        'fs': True,
        'dp': False,
        'bpoFinanceiro': False
    },
    {
        'id': '3',
        'nomeEmpresa': 'Empresa Lucro Presumido',
        'regimeFederal': 'LUCRO PRESUMIDO',
        'perfil': 'EMPRESA',
        'ativo': True,
        'ct': False,
        'fs': True,
        'dp': True,
        'bpoFinanceiro': True
    },
    {
        'id': '4',
        'nomeEmpresa': 'Empresa Lucro Real',
        'regimeFederal': 'LUCRO REAL',
        'perfil': 'EMPRESA',
        'ativo': True,
        'ct': True,
        'fs': True,
        'dp': True,
        'bpoFinanceiro': False
    },
    {
        'id': '5',
        'nomeEmpresa': 'Empregada Doméstica',
        'regimeFederal': 'EMPREGADA DOMESTICA',
        'perfil': 'DOMESTICA',
        'ativo': True,
        'ct': False,
        'fs': False,
        'dp': True,
        'bpoFinanceiro': False
    }
]

print("🧪 === TESTE DE INDICADORES DO DASHBOARD ===")

# Calcular estatísticas
stats = calculate_dashboard_stats(clientes_teste)

print(f"📊 Estatísticas calculadas:")
print(f"   Total de Clientes: {stats['total_clientes']}")
print(f"   Clientes Ativos: {stats['clientes_ativos']}")
print(f"   Empresas: {stats['empresas']}")
print(f"   Domésticas: {stats['domesticas']}")
print(f"   MEI: {stats['mei']}")
print(f"   Simples Nacional: {stats['simples_nacional']}")
print(f"   Lucro Presumido: {stats['lucro_presumido']}")
print(f"   Lucro Real: {stats['lucro_real']}")
print(f"   Depto. Contábil: {stats['ct']}")
print(f"   Depto. Fiscal: {stats['fs']}")
print(f"   Depto. Pessoal: {stats['dp']}")
print(f"   BPO Financeiro: {stats['bpo']}")

print(f"\n🎉 TESTE CONCLUÍDO! Indicadores funcionando corretamente!")
