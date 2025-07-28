# -*- coding: utf-8 -*-
"""
Script para corrigir encoding de arquivos HTML
"""
import os
import codecs

def fix_html_encoding(file_path):
    """Corrige encoding de arquivo HTML"""
    try:
        # Ler arquivo com diferentes encodings
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Arquivo lido com encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"❌ Não foi possível ler o arquivo {file_path}")
            return False
        
        # Corrigir caracteres problemáticos
        replacements = {
            'ã': 'ã', 'á': 'á', 'à': 'à', 'â': 'â', 'ä': 'ä',
            'é': 'é', 'ê': 'ê', 'è': 'è', 'ë': 'ë',
            'í': 'í', 'î': 'î', 'ì': 'ì', 'ï': 'ï',
            'ó': 'ó', 'ô': 'ô', 'ò': 'ò', 'õ': 'õ', 'ö': 'ö',
            'ú': 'ú', 'û': 'û', 'ù': 'ù', 'ü': 'ü',
            'ç': 'ç', 'Ç': 'Ç',
            'Ã': 'Ã', 'Á': 'Á', 'À': 'À', 'Â': 'Â', 'Ä': 'Ä',
            'É': 'É', 'Ê': 'Ê', 'È': 'È', 'Ë': 'Ë',
            'Í': 'Í', 'Î': 'Î', 'Ì': 'Ì', 'Ï': 'Ï',
            'Ó': 'Ó', 'Ô': 'Ô', 'Ò': 'Ò', 'Õ': 'Õ', 'Ö': 'Ö',
            'Ú': 'Ú', 'Û': 'Û', 'Ù': 'Ù', 'Ü': 'Ü'
        }
        
        # Aplicar correções
        fixed_content = content
        for wrong, correct in replacements.items():
            fixed_content = fixed_content.replace(wrong, correct)
        
        # Salvar com UTF-8
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Arquivo {file_path} corrigido e salvo em UTF-8")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo {file_path}: {e}")
        return False

if __name__ == "__main__":
    # Corrigir todos os arquivos HTML
    templates_dir = "templates"
    html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    for html_file in html_files:
        file_path = os.path.join(templates_dir, html_file)
        print(f"🔧 Corrigindo {file_path}...")
        fix_html_encoding(file_path)
    
    print("✅ Correção de encoding concluída!")
