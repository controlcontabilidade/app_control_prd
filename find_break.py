#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para encontrar onde exatamente o HTML está quebrado
"""

def find_break_point():
    """Encontra onde o HTML está quebrado"""
    
    with open('templates/client_form_modern.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir em seções por bloco
    bloco_positions = []
    for i in range(1, 9):
        import re
        pattern = rf'<!-- Bloco {i}[:\-]'
        match = re.search(pattern, content)
        if match:
            bloco_positions.append((i, match.start(), match.end()))
            print(f"✅ Bloco {i}: posição {match.start()}")
        else:
            print(f"❌ Bloco {i}: não encontrado")
    
    # Verificar DIVs entre blocos
    lines = content.split('\n')
    div_count = 0
    
    print(f"\n🔍 Análise por linha:")
    for i, line in enumerate(lines, 1):
        if '<div' in line and not '/>' in line and not '</div>' in line:
            div_count += 1
        elif '</div>' in line:
            div_count -= 1
        
        # Avisar se o contador fica muito negativo
        if div_count < -5:
            print(f"⚠️  Linha {i}: {div_count} DIVs desbalanceadas: {line.strip()}")
            break
        
        # Mostrar pontos críticos
        if i in [250, 410, 516, 614, 663, 849, 959] and div_count != 0:
            print(f"📊 Linha {i} (próximo a bloco): {div_count} DIVs abertas")

if __name__ == "__main__":
    find_break_point()
