#!/usr/bin/env python3
"""
Análise de Campos do Formulário vs função save_client
Este script compara os campos do formulário HTML com os campos processados na função save_client
"""

import re

def extrair_campos_html():
    """Extrai todos os campos name do HTML"""
    try:
        with open('templates/client_form_complete.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair todos os campos name
        pattern = r'name="([^"]+)"'
        matches = re.findall(pattern, content)
        
        # Remover duplicatas e ordenar
        campos_html = sorted(set(matches))
        
        print("=== CAMPOS DO FORMULÁRIO HTML ===")
        for i, campo in enumerate(campos_html, 1):
            print(f"{i:2d}. {campo}")
        
        return campos_html
    except Exception as e:
        print(f"Erro ao ler HTML: {e}")
        return []

def extrair_campos_python():
    """Extrai campos processados no Python"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procurar pela função save_client
        match = re.search(r'def save_client.*?(?=def|\Z)', content, re.DOTALL)
        if not match:
            print("Função save_client não encontrada")
            return []
        
        func_content = match.group(0)
        
        # Extrair request.form.get calls
        pattern = r"request\.form\.get\(['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, func_content)
        
        # Remover duplicatas e ordenar
        campos_python = sorted(set(matches))
        
        print("\n=== CAMPOS PROCESSADOS NO PYTHON ===")
        for i, campo in enumerate(campos_python, 1):
            print(f"{i:2d}. {campo}")
        
        return campos_python
    except Exception as e:
        print(f"Erro ao ler Python: {e}")
        return []

def comparar_campos(html_fields, python_fields):
    """Compara os campos HTML com Python"""
    html_set = set(html_fields)
    python_set = set(python_fields)
    
    # Campos no HTML mas não no Python (PERDIDOS)
    perdidos = html_set - python_set
    
    # Campos no Python mas não no HTML (EXTRAS/ALIASES)
    extras = python_set - html_set
    
    # Campos em ambos (OK)
    ok = html_set & python_set
    
    print("\n" + "="*60)
    print("ANÁLISE COMPARATIVA")
    print("="*60)
    
    print(f"\n✅ CAMPOS OK (presentes em ambos): {len(ok)}")
    for campo in sorted(ok):
        print(f"   ✓ {campo}")
    
    print(f"\n🚨 CAMPOS PERDIDOS (HTML → Python): {len(perdidos)}")
    if perdidos:
        for campo in sorted(perdidos):
            print(f"   ❌ {campo}")
    else:
        print("   Nenhum campo perdido!")
    
    print(f"\n📋 CAMPOS EXTRAS no Python: {len(extras)}")
    if extras:
        for campo in sorted(extras):
            print(f"   ➕ {campo}")
    else:
        print("   Nenhum campo extra!")
    
    # Análise por categorias
    print("\n" + "="*60)
    print("ANÁLISE POR CATEGORIAS")
    print("="*60)
    
    categorias = {
        'Sócios': [f for f in html_fields if f.startswith('socio_')],
        'Contatos': [f for f in html_fields if f.startswith('contato_')],
        'Procurações': [f for f in html_fields if f.startswith('proc') or 'Proc' in f],
        'Códigos': [f for f in html_fields if f.startswith('cod')],
        'Senhas': [f for f in html_fields if 'senha' in f.lower() or 'acesso' in f.lower()],
        'Básicos': [f for f in html_fields if not any(f.startswith(prefix) for prefix in ['socio_', 'contato_', 'proc', 'cod']) and 'senha' not in f.lower() and 'acesso' not in f.lower()]
    }
    
    for categoria, campos in categorias.items():
        perdidos_cat = [c for c in campos if c in perdidos]
        ok_cat = [c for c in campos if c in ok]
        
        print(f"\n📂 {categoria.upper()}:")
        print(f"   Total: {len(campos)} | OK: {len(ok_cat)} | Perdidos: {len(perdidos_cat)}")
        
        if perdidos_cat:
            print("   🚨 Perdidos:")
            for p in sorted(perdidos_cat):
                print(f"      ❌ {p}")

def main():
    print("ANALISANDO CAMPOS DO FORMULÁRIO DE CADASTRO")
    print("="*60)
    
    campos_html = extrair_campos_html()
    campos_python = extrair_campos_python()
    
    if campos_html and campos_python:
        comparar_campos(campos_html, campos_python)
    else:
        print("❌ Erro ao extrair campos")

if __name__ == "__main__":
    main()