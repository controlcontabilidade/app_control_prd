#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para contar exatamente as posições dos contatos nos headers
"""

def contar_posicoes_headers():
    """Conta exatamente onde estão os contatos nos headers"""
    
    print("🔍 === CONTANDO POSIÇÕES DOS CONTATOS ===")
    
    # Vou ler o arquivo diretamente para pegar o get_headers completo
    with open('services/google_sheets_service_account.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a função get_headers
    lines = content.split('\n')
    in_get_headers = False
    header_lines = []
    bracket_count = 0
    
    for line in lines:
        if 'def get_headers(self)' in line:
            in_get_headers = True
            continue
            
        if in_get_headers:
            # Contar brackets para saber quando terminar
            bracket_count += line.count('[') - line.count(']')
            
            if "'" in line and '#' in line:  # Linha com header
                # Extrair o header
                start = line.find("'") + 1
                end = line.find("'", start)
                if start < end:
                    header = line[start:end]
                    header_lines.append(header)
            
            if bracket_count == 0 and ']' in line:
                break
    
    print(f"🔍 Total de headers encontrados: {len(header_lines)}")
    
    # Procurar posições dos contatos
    contato_positions = {}
    contador_positions = {}
    
    for i, header in enumerate(header_lines):
        position = i + 1  # +1 porque as posições começam em 1
        
        if 'CONTATO_' in header and ('NOME' in header or 'CARGO' in header or 'TELEFONE' in header or 'EMAIL' in header):
            contato_positions[header] = position
        elif 'CONTADOR' in header:
            contador_positions[header] = position
            
    print("\n🔍 === POSIÇÕES DOS CONTATOS DETALHADOS ===")
    for header, pos in sorted(contato_positions.items()):
        print(f"🔍 {header}: Posição {pos}")
        
    print("\n🔍 === POSIÇÕES DOS CONTATOS CONTADOR ===")
    for header, pos in sorted(contador_positions.items()):
        print(f"🔍 {header}: Posição {pos}")
        
    # Análise das posições
    contato_1_nome_pos = contato_positions.get('CONTATO_1_NOME', 0)
    contato_2_nome_pos = contato_positions.get('CONTATO_2_NOME', 0)
    contato_3_nome_pos = contato_positions.get('CONTATO_3_NOME', 0)
    
    print(f"\n🔍 === ANÁLISE ===")
    print(f"🔍 CONTATO_1_NOME está na posição: {contato_1_nome_pos}")
    print(f"🔍 CONTATO_2_NOME está na posição: {contato_2_nome_pos}")
    print(f"🔍 CONTATO_3_NOME está na posição: {contato_3_nome_pos}")
    
    if contato_2_nome_pos > 0:
        print(f"🔍 Para acessar CONTATO_2_NOME no array: posição {contato_2_nome_pos - 1} (0-indexed)")
        print(f"🔍 Para acessar CONTATO_3_NOME no array: posição {contato_3_nome_pos - 1} (0-indexed)")
        
        diferenca = contato_3_nome_pos - contato_2_nome_pos
        print(f"🔍 Diferença entre contato_2 e contato_3: {diferenca} posições")

if __name__ == "__main__":
    contar_posicoes_headers()