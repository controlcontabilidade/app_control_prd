# -*- coding: utf-8 -*-
import re
import os

def convert_labels_final():
    """Converte TODOS os labels restantes para maiúsculas"""
    
    template_dir = "templates"
    files_to_process = [
        "client_form_modern.html",
        "users.html", 
        "login.html",
        "client_view_modern_new.html"
    ]
    
    # Mapeamento específico de conversões
    conversions = {
        # client_form_modern.html
        '>telefone fixo<': '>TELEFONE FIXO<',
        '>telefone celular<': '>TELEFONE CELULAR<',
        '>whatsapp<': '>WHATSAPP<',
        '>contato contador<': '>CONTATO CONTADOR<',
        '>telefone contador<': '>TELEFONE CONTADOR<',
        '>sistema principal utilizado<': '>SISTEMA PRINCIPAL UTILIZADO<',
        '>acesso iss<': '>ACESSO ISS<',
        '>senha iss<': '>SENHA ISS<',
        '>acesso sefin<': '>ACESSO SEFIN<',
        '>senha sefin<': '>SENHA SEFIN<',
        
        # users.html
        '>nome completo<': '>NOME COMPLETO<',
        '>Email<': '>EMAIL<',
        '>perfil<': '>PERFIL<',
        '>senha<': '>SENHA<',
        '>status<': '>STATUS<',
        '>nova senha<': '>NOVA SENHA<',
        
        # login.html
        '>usuário<': '>USUÁRIO<',
        
        # client_view_modern_new.html
        '>Nome da Empresa<': '>NOME DA EMPRESA<',
        '>Perfil do Cliente<': '>PERFIL DO CLIENTE<',
        '>Estado<': '>ESTADO<',
        '>Cidade<': '>CIDADE<',
        '>Regime Federal<': '>REGIME FEDERAL<',
        '>Regime Estadual<': '>REGIME ESTADUAL<',
        '>Segmento<': '>SEGMENTO<',
        '>Atividade Principal<': '>ATIVIDADE PRINCIPAL<',
        '>Nome<': '>NOME<',
        '>CPF<': '>CPF<',
    }
    
    for filename in files_to_process:
        filepath = os.path.join(template_dir, filename)
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            original_content = content
            changes_made = 0
            
            # Aplicar conversões específicas
            for old_text, new_text in conversions.items():
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    changes_made += 1
                    print(f"  ✅ {old_text} → {new_text}")
            
            # Salvar apenas se houve mudanças
            if changes_made > 0:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"✅ {filename} - {changes_made} labels convertidos")
            else:
                print(f"⚪ {filename} - Nenhuma alteração necessária")
                
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    convert_labels_final()
