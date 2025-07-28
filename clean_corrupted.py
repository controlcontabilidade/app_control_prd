# -*- coding: utf-8 -*-
import re

def clean_corrupted_text():
    """Remove texto corrompido do arquivo HTML"""
    
    filepath = "templates/client_form_modern.html"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Padrões problemáticos para remover
        problematic_patterns = [
            r'\.Groups\[1\]\.Value\.ToUpper\(\).*?required>',
            r'\.Groups\[1\]\.Value\.ToUpper\(\).*?>',
            r'Groups\[1\]',
            r'Value\.ToUpper\(\)',
            r'`""',
            # Padrões regex que podem ter sido inseridos incorretamente
            r'class="form-label">.*?SISTEMA PRINCIPAL utilizado<',
        ]
        
        for pattern in problematic_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Limpar possíveis duplicações de linhas
        lines = content.split('\n')
        cleaned_lines = []
        prev_line = ""
        
        for line in lines:
            # Remove linhas completamente duplicadas consecutivas
            if line.strip() != prev_line.strip() or line.strip() == "":
                cleaned_lines.append(line)
            prev_line = line
        
        content = '\n'.join(cleaned_lines)
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print("✅ Arquivo limpo com sucesso!")
            print(f"Tamanho original: {len(original_content)} caracteres")
            print(f"Tamanho novo: {len(content)} caracteres")
        else:
            print("⚪ Nenhuma limpeza necessária")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    clean_corrupted_text()
