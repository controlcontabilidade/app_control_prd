# -*- coding: utf-8 -*-
import re
import os

def convert_remaining_labels():
    """Converte TODOS os labels restantes em client_form_modern.html"""
    
    filepath = "templates/client_form_modern.html"
    
    # Lista completa de conversões para client_form_modern.html
    conversions = [
        ('telefone fixo', 'TELEFONE FIXO'),
        ('telefone celular', 'TELEFONE CELULAR'),
        ('whatsapp', 'WHATSAPP'),
        ('e-mail principal', 'E-MAIL PRINCIPAL'),
        ('e-mail secundário', 'E-MAIL SECUNDÁRIO'),
        ('responsável imediato', 'RESPONSÁVEL IMEDIATO'),
        ('e-mails dos sócios', 'E-MAILS DOS SÓCIOS'),
        ('contato contador', 'CONTATO CONTADOR'),
        ('telefone contador', 'TELEFONE CONTADOR'),
        ('e-mail contador', 'E-MAIL CONTADOR'),
        ('sistema principal utilizado', 'SISTEMA PRINCIPAL UTILIZADO'),
        ('versão do sistema', 'VERSÃO DO SISTEMA'),
        ('código acesso simples nacional', 'CÓDIGO ACESSO SIMPLES NACIONAL'),
        ('cpf/cnpj para acesso', 'CPF/CNPJ PARA ACESSO'),
        ('acesso iss', 'ACESSO ISS'),
        ('senha iss', 'SENHA ISS'),
        ('acesso sefin', 'ACESSO SEFIN'),
        ('senha sefin', 'SENHA SEFIN'),
        ('Acesso SEUMA', 'ACESSO SEUMA'),
        ('Senha SEUMA', 'SENHA SEUMA'),
        ('Acesso EmpWeb', 'ACESSO EMPWEB'),
        ('Senha EmpWeb', 'SENHA EMPWEB'),
        ('Acesso CRF', 'ACESSO CRF'),
        ('Senha CRF', 'SENHA CRF'),
        ('ANVISA Gestor', 'ANVISA GESTOR'),
        ('ANVISA Empresa', 'ANVISA EMPRESA'),
        ('Acesso IBAMA', 'ACESSO IBAMA'),
        ('Senha IBAMA', 'SENHA IBAMA'),
        ('Acesso SEMACE', 'ACESSO SEMACE'),
        ('Senha SEMACE', 'SENHA SEMACE'),
        ('certificado digital', 'CERTIFICADO DIGITAL'),
        ('certificado ecpf', 'CERTIFICADO ECPF'),
        ('observações', 'OBSERVAÇÕES'),
    ]
    
    if not os.path.exists(filepath):
        print(f"❌ Arquivo não encontrado: {filepath}")
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        changes_made = 0
        
        # Aplicar conversões específicas
        for old_text, new_text in conversions:
            # Buscar padrão label com o texto
            pattern = f'"form-label">{old_text}'
            replacement = f'"form-label">{new_text}'
            
            if pattern in content:
                content = content.replace(pattern, replacement)
                changes_made += 1
                print(f"  ✅ {old_text} → {new_text}")
        
        # Buscar outros padrões mais complexos
        complex_patterns = [
            (r'label.*">([a-z][^<]*)<', lambda m: m.group(0).replace(m.group(1), m.group(1).upper())),
        ]
        
        for pattern, replacement_func in complex_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                old_match = match.group(0)
                new_match = replacement_func(match)
                if old_match != new_match:
                    content = content.replace(old_match, new_match)
                    changes_made += 1
                    print(f"  ✅ Conversão complexa: {old_match} → {new_match}")
        
        # Salvar se houve mudanças
        if changes_made > 0:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ {filepath} - {changes_made} labels convertidos")
        else:
            print(f"⚪ {filepath} - Nenhuma alteração necessária")
            
    except Exception as e:
        print(f"❌ Erro ao processar {filepath}: {e}")

if __name__ == "__main__":
    convert_remaining_labels()
