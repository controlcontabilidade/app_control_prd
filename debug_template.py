#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debugar problemas no template client_form_modern.html
"""

import re

def check_html_balance():
    """Verifica se as tags HTML estão balanceadas no template"""
    
    with open('templates/client_form_modern.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar divs
    div_opens = len(re.findall(r'<div[^>]*>', content))
    div_closes = len(re.findall(r'</div>', content))
    
    print(f"🔍 Análise do Template:")
    print(f"   DIVs abertas: {div_opens}")
    print(f"   DIVs fechadas: {div_closes}")
    print(f"   Diferença: {div_opens - div_closes}")
    
    # Verificar cards
    card_opens = len(re.findall(r'<div[^>]*class="card[^"]*"[^>]*>', content))
    print(f"   Cards encontrados: {card_opens}")
    
    # Verificar se há erros comuns
    unclosed_tags = []
    
    # Procurar por tags não fechadas
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if '<div' in line and not '/>' in line and not '</div>' in line:
            # Verificar se há fechamento na mesma linha ou nas próximas
            if i < len(lines) - 5:  # Verificar próximas 5 linhas
                found_close = False
                for j in range(i, min(i + 5, len(lines))):
                    if '</div>' in lines[j]:
                        found_close = True
                        break
                if not found_close:
                    unclosed_tags.append((i, line.strip()))
    
    if unclosed_tags:
        print(f"\n⚠️  Possíveis tags não fechadas:")
        for line_num, line_content in unclosed_tags[:5]:  # Mostrar apenas as primeiras 5
            print(f"   Linha {line_num}: {line_content}")
    
    return div_opens == div_closes

def check_blocks():
    """Verifica se todos os blocos estão presentes"""
    
    with open('templates/client_form_modern.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = []
    for i in range(1, 9):  # Blocos 1 a 8
        pattern = rf'Bloco {i}[:\-]'
        matches = re.findall(pattern, content, re.IGNORECASE)
        blocks.append((i, len(matches)))
        if matches:
            print(f"✅ Bloco {i}: {len(matches)} ocorrências")
        else:
            print(f"❌ Bloco {i}: Não encontrado")
    
    return all(count > 0 for _, count in blocks)

if __name__ == "__main__":
    print("🔧 Verificando template client_form_modern.html...")
    
    balance_ok = check_html_balance()
    print(f"\n📊 Tags balanceadas: {'✅ SIM' if balance_ok else '❌ NÃO'}")
    
    print(f"\n📋 Verificando blocos:")
    blocks_ok = check_blocks()
    print(f"\n🎯 Todos os blocos presentes: {'✅ SIM' if blocks_ok else '❌ NÃO'}")
