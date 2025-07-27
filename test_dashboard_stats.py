#!/usr/bin/env python3
"""
Script de teste para validar os indicadores do dashboard SIGEC
"""

import sys
sys.path.append('.')

from app import calculate_dashboard_stats

# Dados de teste simulando diferentes tipos de clientes SIGEC
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
    },
    {
        'id': '6',
        'nomeEmpresa': 'Cliente Inativo',
        'regimeFederal': 'SIMPLES NACIONAL',
        'perfil': 'EMPRESA',
        'ativo': False,
        'ct': True,
        'fs': False,
        'dp': False,
        'bpoFinanceiro': False
    }
]

def test_dashboard_stats():
    """Testa o cálculo de estatísticas do dashboard"""
    print("🧪 === TESTE DE INDICADORES DO DASHBOARD ===")
    
    try:
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
        
        # Validações esperadas
        validacoes = {
            'total_clientes': 6,
            'clientes_ativos': 5,  # 5 ativos, 1 inativo
            'mei': 1,
            'simples_nacional': 1,  # Apenas o ativo
            'lucro_presumido': 1,
            'lucro_real': 1,
            'domesticas': 1,
            'empresas': 2,  # Casos não categorizados como MEI, SN, LP, LR ou domésticas
            'ct': 3,  # MEI, SN, LR
            'fs': 3,  # SN, LP, LR
            'dp': 3,  # LP, LR, Doméstica
            'bpo': 1   # Apenas LP
        }
        
        print(f"\n✅ Validações:")
        todos_corretos = True
        for campo, esperado in validacoes.items():
            obtido = stats[campo]
            status = "✅" if obtido == esperado else "❌"
            print(f"   {status} {campo}: {obtido} (esperado: {esperado})")
            if obtido != esperado:
                todos_corretos = False
        
        if todos_corretos:
            print(f"\n🎉 TESTE PASSOU! Todos os indicadores estão corretos!")
        else:
            print(f"\n⚠️ TESTE FALHOU! Alguns indicadores estão incorretos.")
            
        return todos_corretos
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        return False

if __name__ == '__main__':
    test_dashboard_stats()
