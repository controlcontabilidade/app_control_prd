#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DIAGNÓSTICO CRÍTICO CORREÇÃO 14: Por que o botão não funciona
Verifica problemas fundamentais de JavaScript
"""

def diagnose_button_problem():
    """Diagnóstica problemas específicos do botão"""
    print("🚨 === DIAGNÓSTICO CRÍTICO DO BOTÃO ===")
    
    template_path = r"c:\Users\user\Documents\GitHub\app_control_prd\templates\client_form_complete.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Template carregado")
        
        # 1. Verificar se há erros JavaScript óbvios
        print("\n🔍 === VERIFICANDO PROBLEMAS CRÍTICOS ===")
        
        # Verificar se existe undefined que pode quebrar o JS
        if 'undefined' in content.lower():
            undefined_count = content.lower().count('undefined')
            print(f"⚠️ AVISO: {undefined_count} ocorrências de 'undefined' encontradas")
        
        # Verificar se há console.error que indica problemas
        errors = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'console.error' in line and 'adicionarContato' in line:
                errors.append((i, line.strip()))
        
        if errors:
            print(f"❌ PROBLEMAS ENCONTRADOS: {len(errors)} erros relacionados a adicionarContato")
            for line_num, error_line in errors:
                print(f"   Linha {line_num}: {error_line}")
        
        # 2. Verificar se a função está dentro de uma estrutura condicional
        print("\n🔍 === VERIFICANDO ESTRUTURA DA FUNÇÃO ===")
        
        func_start = content.find("function adicionarContato()")
        if func_start != -1:
            # Verificar 500 caracteres antes da função
            context_before = content[max(0, func_start-500):func_start]
            
            # Procurar por estruturas que podem impedir execução
            problematic_structures = [
                'if (',
                'if(',
                'try {',
                'try{',
                '} catch',
                '}catch',
                'function(',
                'function ('
            ]
            
            for structure in problematic_structures:
                if structure in context_before[-100:]:  # Últimos 100 chars antes da função
                    print(f"⚠️ AVISO: Estrutura '{structure}' encontrada antes da função")
        
        # 3. Verificar se há múltiplas definições da função
        print("\n🔍 === VERIFICANDO MÚLTIPLAS DEFINIÇÕES ===")
        
        func_definitions = []
        start = 0
        while True:
            pos = content.find("function adicionarContato()", start)
            if pos == -1:
                break
            
            # Encontrar número da linha
            line_num = content[:pos].count('\n') + 1
            func_definitions.append(line_num)
            start = pos + 1
        
        if len(func_definitions) > 1:
            print(f"❌ PROBLEMA CRÍTICO: {len(func_definitions)} definições da função encontradas!")
            print(f"   Linhas: {func_definitions}")
            print("   A última definição sobrescreve as anteriores!")
        else:
            print(f"✅ Apenas 1 definição da função (linha {func_definitions[0]})")
        
        # 4. Verificar se há window.adicionarContato = null ou similar
        print("\n🔍 === VERIFICANDO SOBRESCRITAS ===")
        
        nullifying_patterns = [
            "adicionarContato = null",
            "adicionarContato = undefined",
            "delete adicionarContato",
            "window.adicionarContato = null",
            "adicionarContato = function",
            "adicionarContato="
        ]
        
        for pattern in nullifying_patterns:
            if pattern in content:
                print(f"❌ PROBLEMA CRÍTICO: Padrão '{pattern}' encontrado!")
                # Encontrar linha
                pattern_pos = content.find(pattern)
                line_num = content[:pattern_pos].count('\n') + 1
                print(f"   Linha {line_num}")
        
        # 5. Verificar se há erros de sintaxe antes da função
        print("\n🔍 === VERIFICANDO SINTAXE ANTES DA FUNÇÃO ===")
        
        if func_start != -1:
            js_before_func = content[:func_start]
            
            # Contar chaves apenas na parte antes da função
            open_braces = js_before_func.count('{')
            close_braces = js_before_func.count('}')
            
            if open_braces != close_braces:
                print(f"❌ PROBLEMA CRÍTICO: Sintaxe desbalanceada ANTES da função!")
                print(f"   {open_braces} chaves abertas vs {close_braces} fechadas")
                print("   Isso pode impedir que a função seja definida!")
        
        # 6. Verificar se há comentários que quebram a função
        print("\n🔍 === VERIFICANDO COMENTÁRIOS PROBLEMÁTICOS ===")
        
        if func_start != -1:
            func_content = content[func_start:func_start+2000]  # Primeiros 2000 chars da função
            
            # Procurar por comentários mal formados
            if '/*' in func_content and '*/' not in func_content:
                print("❌ PROBLEMA CRÍTICO: Comentário /* sem fechamento */ na função!")
            
            if func_content.count('/*') != func_content.count('*/'):
                print("❌ PROBLEMA CRÍTICO: Comentários /* */ desbalanceados!")
        
        print("\n📊 === RESUMO DO DIAGNÓSTICO ===")
        print("Execute este diagnóstico para identificar o problema raiz.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return False

if __name__ == "__main__":
    diagnose_button_problem()
