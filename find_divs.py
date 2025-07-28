#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script específico para encontrar DIVs não fechadas
"""

def find_unmatched_divs():
    """Encontra DIVs não fechadas no template"""
    
    with open('templates/client_form_modern.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    div_stack = []
    problems = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Procurar por DIVs de abertura
        if '<div' in line and not '/>' in line and not '</div>' in line:
            div_stack.append((i, line_content))
        
        # Procurar por DIVs de fechamento
        elif '</div>' in line:
            if div_stack:
                div_stack.pop()
            else:
                problems.append(f"Linha {i}: Fechamento de DIV sem abertura: {line_content}")
    
    # DIVs que não foram fechadas
    if div_stack:
        print("🚨 DIVs não fechadas:")
        for line_num, line_content in div_stack[-10:]:  # Últimas 10
            print(f"   Linha {line_num}: {line_content}")
    
    # Outros problemas
    if problems:
        print("\n⚠️  Outros problemas:")
        for problem in problems[:5]:
            print(f"   {problem}")
    
    print(f"\n📊 Resumo:")
    print(f"   DIVs não fechadas: {len(div_stack)}")
    print(f"   Fechamentos sem abertura: {len(problems)}")
    
    return len(div_stack) == 0 and len(problems) == 0

if __name__ == "__main__":
    print("🔍 Procurando DIVs não fechadas...")
    result = find_unmatched_divs()
    print(f"\n✅ Template válido: {'SIM' if result else 'NÃO'}")
