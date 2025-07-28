# -*- coding: utf-8 -*-
import re

def final_uppercase_conversion():
    """Conversão final para MAIÚSCULAS de todos os labels restantes"""
    
    filepath = "templates/client_form_modern.html"
    
    # Mapeamento direto de todas as conversões necessárias
    replacements = {
        'e-mail secundário': 'E-MAIL SECUNDÁRIO',
        'responsável imediato': 'RESPONSÁVEL IMEDIATO', 
        'e-mails dos sócios': 'E-MAILS DOS SÓCIOS',
        'contato contador': 'CONTATO CONTADOR',
        'telefone contador': 'TELEFONE CONTADOR',
        'e-mail contador': 'E-MAIL CONTADOR',
        'sistema principal utilizado': 'SISTEMA PRINCIPAL UTILIZADO',
        'versão do sistema': 'VERSÃO DO SISTEMA',
        'código acesso simples nacional': 'CÓDIGO ACESSO SIMPLES NACIONAL',
        'cpf/cnpj para acesso': 'CPF/CNPJ PARA ACESSO',
        'acesso iss': 'ACESSO ISS',
        'senha iss': 'SENHA ISS',
        'acesso sefin': 'ACESSO SEFIN',
        'senha sefin': 'SENHA SEFIN',
        'Acesso SEUMA': 'ACESSO SEUMA',
        'Senha SEUMA': 'SENHA SEUMA',
        'Acesso EmpWeb': 'ACESSO EMPWEB',
        'Senha EmpWeb': 'SENHA EMPWEB',
        'Acesso CRF': 'ACESSO CRF',
        'Senha CRF': 'SENHA CRF',
        'ANVISA Gestor': 'ANVISA GESTOR',
        'ANVISA Empresa': 'ANVISA EMPRESA',
        'Acesso IBAMA': 'ACESSO IBAMA',
        'Senha IBAMA': 'SENHA IBAMA',
        'Acesso SEMACE': 'ACESSO SEMACE',
        'Senha SEMACE': 'SENHA SEMACE',
        'certificado digital': 'CERTIFICADO DIGITAL',
        'certificado ecpf': 'CERTIFICADO ECPF',
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        changes = 0
        for old_text, new_text in replacements.items():
            if old_text in content:
                content = content.replace(old_text, new_text)
                changes += 1
                print(f"✅ {old_text} → {new_text}")
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"\n✅ Concluído! {changes} conversões realizadas")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    final_uppercase_conversion()
