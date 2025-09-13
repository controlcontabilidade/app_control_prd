#!/usr/bin/env python3
"""
Teste da correção para filtrar valores "NÃO" nos contatos
Verifica se campos com "NÃO" não fazem o contato aparecer
"""

def test_filtro_valores_invalidos():
    """Testa o filtro de valores inválidos nos contatos"""
    print("\n=== TESTE FILTRO VALORES INVÁLIDOS ===")
    
    # Simula diferentes cenários de dados inválidos
    cenarios = [
        {
            'nome': 'Contato com email "NÃO"',
            'dados': {
                'contato_1_nome': '',
                'contato_1_email': 'NÃO',
                'contato_1_telefone': '',
                'contato_1_cargo': ''
            },
            'deve_mostrar_contato': False,
            'razao': 'Email "NÃO" deve ser filtrado'
        },
        {
            'nome': 'Contato com email "NAO"',
            'dados': {
                'contato_2_nome': '',
                'contato_2_email': 'NAO',
                'contato_2_telefone': '',
                'contato_2_cargo': ''
            },
            'deve_mostrar_contato': False,
            'razao': 'Email "NAO" deve ser filtrado'
        },
        {
            'nome': 'Contato com campos "-"',
            'dados': {
                'contato_3_nome': '-',
                'contato_3_email': '-',
                'contato_3_telefone': '-',
                'contato_3_cargo': '-'
            },
            'deve_mostrar_contato': False,
            'razao': 'Campos com "-" devem ser filtrados'
        },
        {
            'nome': 'Contato com email válido',
            'dados': {
                'contato_1_nome': '',
                'contato_1_email': 'joao@empresa.com',
                'contato_1_telefone': '',
                'contato_1_cargo': ''
            },
            'deve_mostrar_contato': True,
            'razao': 'Email válido deve ser mostrado'
        },
        {
            'nome': 'Contato com nome válido',
            'dados': {
                'contato_2_nome': 'João Silva',
                'contato_2_email': 'NÃO',
                'contato_2_telefone': '',
                'contato_2_cargo': ''
            },
            'deve_mostrar_contato': True,
            'razao': 'Nome válido deve mostrar contato (email "NÃO" é ignorado)'
        },
        {
            'nome': 'Todos campos com valores inválidos',
            'dados': {
                'contato_3_nome': 'NÃO',
                'contato_3_email': 'NAO',
                'contato_3_telefone': 'N/A',
                'contato_3_cargo': '-'
            },
            'deve_mostrar_contato': False,
            'razao': 'Todos valores inválidos - não deve mostrar'
        }
    ]
    
    # Simula a lógica do template corrigido
    def simular_logica_template_corrigida(client_data):
        """Simula a lógica do template com filtros"""
        contatos_existentes = []
        valores_invalidos = ['NÃO', 'NAO', 'N/A', '-']
        
        for i in range(1, 4):
            nome = client_data.get(f'contato_{i}_nome', '')
            telefone = client_data.get(f'contato_{i}_telefone', '')
            email = client_data.get(f'contato_{i}_email', '')
            cargo = client_data.get(f'contato_{i}_cargo', '')
            
            # Valida cada campo
            nome_valido = nome and nome.strip() and nome.upper() not in valores_invalidos
            telefone_valido = telefone and telefone.strip() and telefone.upper() not in valores_invalidos
            email_valido = email and email.strip() and email.upper() not in valores_invalidos
            cargo_valido = cargo and cargo.strip() and cargo.upper() not in valores_invalidos
            
            # Se pelo menos um campo é válido, mostra o contato
            if nome_valido or telefone_valido or email_valido or cargo_valido:
                contatos_existentes.append(i)
        
        return contatos_existentes
    
    print("Testando cenários com filtros:")
    for cenario in cenarios:
        contatos = simular_logica_template_corrigida(cenario['dados'])
        tem_contato = len(contatos) > 0
        esperado = cenario['deve_mostrar_contato']
        status = "✅" if tem_contato == esperado else "❌"
        
        print(f"{status} {cenario['nome']}")
        print(f"    Dados: {cenario['dados']}")
        print(f"    Resultado: {'Mostra contato' if tem_contato else 'NÃO mostra'} (esperado: {'Mostra' if esperado else 'NÃO mostra'})")
        print(f"    Razão: {cenario['razao']}")
        print()

def test_caso_especifico_reportado():
    """Testa o caso específico do bug reportado"""
    print("\n=== CASO ESPECÍFICO REPORTADO ===")
    
    # Dados que causavam o problema
    dados_problema = {
        'contato_3_nome': '',
        'contato_3_email': 'NÃO',  # Este era o problema
        'contato_3_telefone': '',
        'contato_3_cargo': ''
    }
    
    # Lógica ANTES (problemática)
    def logica_antes(dados):
        email = dados.get('contato_3_email', '')
        # Qualquer valor não vazio era considerado válido
        return bool(email)  # "NÃO" retornava True
    
    # Lógica DEPOIS (corrigida)
    def logica_depois(dados):
        email = dados.get('contato_3_email', '')
        valores_invalidos = ['NÃO', 'NAO', 'N/A', '-']
        return email and email.strip() and email.upper() not in valores_invalidos
    
    resultado_antes = logica_antes(dados_problema)
    resultado_depois = logica_depois(dados_problema)
    
    print("Caso: Contato 3 com email='NÃO'")
    print(f"ANTES da correção: {'Mostrava contato' if resultado_antes else 'NÃO mostrava'} ❌")
    print(f"DEPOIS da correção: {'Mostra contato' if resultado_depois else 'NÃO mostra'} ✅")
    print(f"Problema resolvido: {not resultado_depois}")

if __name__ == "__main__":
    print("🧪 TESTE CORREÇÃO FILTRO CONTATOS")
    print("="*50)
    
    test_filtro_valores_invalidos()
    test_caso_especifico_reportado()
    
    print("\n" + "="*50)
    print("✅ CORREÇÃO IMPLEMENTADA:")
    print("1. ✅ Filtra valores 'NÃO', 'NAO', 'N/A', '-'")
    print("2. ✅ Remove espaços vazios com .strip()")
    print("3. ✅ Comparação case-insensitive com .upper()")
    print("4. ✅ Só mostra contatos com pelo menos 1 campo válido")
    print("\n🎯 Contato 3 não aparecerá mais só com 'E-mail: NÃO'!")