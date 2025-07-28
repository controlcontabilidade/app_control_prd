# -*- coding: utf-8 -*-
"""
Script para converter todos os labels dos formulários para MAIÚSCULAS
"""
import re
import os

def convert_labels_to_uppercase(file_path):
    """Converte todos os labels de um arquivo HTML para maiúsculas"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrões para converter labels específicos
        label_patterns = [
            # Bloco 1 - Informações da Pessoa Jurídica
            (r'>nome da empresa', '>NOME DA EMPRESA'),
            (r'>razão social \(receita\)', '>RAZÃO SOCIAL (RECEITA)'),
            (r'>nome fantasia \(receita\)', '>NOME FANTASIA (RECEITA)'),
            (r'>perfil', '>PERFIL'),
            (r'>inscrição estadual', '>INSCRIÇÃO ESTADUAL'),
            (r'>inscrição municipal', '>INSCRIÇÃO MUNICIPAL'),
            (r'>estado', '>ESTADO'),
            (r'>cidade', '>CIDADE'),
            (r'>regime federal', '>REGIME FEDERAL'),
            (r'>regime estadual', '>REGIME ESTADUAL'),  
            (r'>segmento', '>SEGMENTO'),
            (r'>atividade principal', '>ATIVIDADE PRINCIPAL'),
            (r'>atividade</label>', '>ATIVIDADE</label>'),
            
            # Bloco 2 - Serviços
            (r'>data de início dos serviços', '>DATA DE INÍCIO DOS SERVIÇOS'),
            (r'>responsável pelos serviços', '>RESPONSÁVEL PELOS SERVIÇOS'),
            (r'>código fortes ct', '>CÓDIGO FORTES CT'),
            (r'>código fortes fs', '>CÓDIGO FORTES FS'),
            (r'>código fortes ps', '>CÓDIGO FORTES PS'),
            (r'>código domínio', '>CÓDIGO DOMÍNIO'),
            (r'>sistema utilizado', '>SISTEMA UTILIZADO'),
            (r'>módulo sped trier', '>MÓDULO SPED TRIER'),
            
            # Bloco 3 - Quadro Societário  
            (r'>nome completo do sócio', '>NOME COMPLETO DO SÓCIO'),
            (r'>nome do sócio', '>NOME DO SÓCIO'),
            (r'>cpf do sócio', '>CPF DO SÓCIO'),
            (r'>data de nascimento', '>DATA DE NASCIMENTO'),
            (r'>administrador', '>ADMINISTRADOR'),
            (r'>percentual de cotas', '>PERCENTUAL DE COTAS'),
            (r'>responsável legal', '>RESPONSÁVEL LEGAL'),
            
            # Bloco 4 - Contatos
            (r'>telefone fixo</label>', '>TELEFONE FIXO</label>'),
            (r'>telefone celular</label>', '>TELEFONE CELULAR</label>'),
            (r'>whatsapp</label>', '>WHATSAPP</label>'),
            (r'>e-mail principal', '>E-MAIL PRINCIPAL'),
            (r'>e-mail secundário', '>E-MAIL SECUNDÁRIO'),
            (r'>responsável imediato', '>RESPONSÁVEL IMEDIATO'),
            (r'>e-mails dos sócios', '>E-MAILS DOS SÓCIOS'),
            (r'>contato contador', '>CONTATO CONTADOR'),
            (r'>telefone contador', '>TELEFONE CONTADOR'),
            (r'>e-mail contador', '>E-MAIL CONTADOR'),
            
            # Bloco 5 - Sistemas e Acessos
            (r'>sistema principal', '>SISTEMA PRINCIPAL'),
            (r'>versão do sistema', '>VERSÃO DO SISTEMA'),
            (r'>código de acesso simples nacional', '>CÓDIGO DE ACESSO SIMPLES NACIONAL'),
            (r'>cpf/cnpj para acesso', '>CPF/CNPJ PARA ACESSO'),
            (r'>portal cliente ativo', '>PORTAL CLIENTE ATIVO'),
            (r'>integração domínio', '>INTEGRAÇÃO DOMÍNIO'),
            (r'>sistema onvio', '>SISTEMA ONVIO'),
            
            # Bloco 6 - Senhas e Credenciais
            (r'>acesso iss', '>ACESSO ISS'),
            (r'>senha iss', '>SENHA ISS'),
            (r'>acesso sefin', '>ACESSO SEFIN'),
            (r'>senha sefin', '>SENHA SEFIN'),
            (r'>acesso seuma', '>ACESSO SEUMA'),
            (r'>senha seuma', '>SENHA SEUMA'),
            (r'>acesso emp web', '>ACESSO EMP WEB'),
            (r'>senha emp web', '>SENHA EMP WEB'),
            (r'>acesso fap/inss', '>ACESSO FAP/INSS'),
            (r'>senha fap/inss', '>SENHA FAP/INSS'),
            (r'>acesso crf', '>ACESSO CRF'),
            (r'>senha crf', '>SENHA CRF'),
            (r'>e-mail gestor', '>E-MAIL GESTOR'),
            (r'>senha e-mail gestor', '>SENHA E-MAIL GESTOR'),
            (r'>anvisa gestor', '>ANVISA GESTOR'),
            (r'>anvisa empresa', '>ANVISA EMPRESA'),
            (r'>acesso ibama', '>ACESSO IBAMA'),
            (r'>senha ibama', '>SENHA IBAMA'),
            (r'>acesso semace', '>ACESSO SEMACE'),
            (r'>senha semace', '>SENHA SEMACE'),
            
            # Bloco 7 - Procurações
            (r'>procuração rfb', '>PROCURAÇÃO RFB'),
            (r'>data procuração rfb', '>DATA PROCURAÇÃO RFB'),
            (r'>procuração receita estadual', '>PROCURAÇÃO RECEITA ESTADUAL'),
            (r'>data procuração rc', '>DATA PROCURAÇÃO RC'),
            (r'>procuração caixa econômica', '>PROCURAÇÃO CAIXA ECONÔMICA'),
            (r'>data procuração cx', '>DATA PROCURAÇÃO CX'),
            (r'>procuração previdência social', '>PROCURAÇÃO PREVIDÊNCIA SOCIAL'),
            (r'>data procuração sw', '>DATA PROCURAÇÃO SW'),
            (r'>procuração municipal', '>PROCURAÇÃO MUNICIPAL'),
            (r'>data procuração municipal', '>DATA PROCURAÇÃO MUNICIPAL'),
            (r'>outras procurações', '>OUTRAS PROCURAÇÕES'),
            (r'>observações procurações', '>OBSERVAÇÕES PROCURAÇÕES'),
            
            # Bloco 8 - Observações
            (r'>observações gerais', '>OBSERVAÇÕES GERAIS'),
            (r'>tarefas vinculadas', '>TAREFAS VINCULADAS'),
            (r'>status do cliente', '>STATUS DO CLIENTE'),
            (r'>prioridade do cliente', '>PRIORIDADE DO CLIENTE'),
            (r'>tags do cliente', '>TAGS DO CLIENTE'),
            (r'>histórico de alterações', '>HISTÓRICO DE ALTERAÇÕES'),
            
            # Checkboxes e outros
            (r'>ativo</label>', '>ATIVO</label>'),
            (r'>cliente ativo', '>CLIENTE ATIVO'),
        ]
        
        # Aplicar todas as conversões
        for pattern, replacement in label_patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path} - Labels convertidos para MAIÚSCULAS")
        else:
            print(f"⚪ {file_path} - Nenhuma alteração necessária")
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")

if __name__ == "__main__":
    # Arquivos para processar
    files_to_process = [
        "templates/client_form_modern.html",
        "templates/client_form.html", 
        "templates/client_view_modern.html",
        "templates/client_view.html",
        "templates/meeting_form.html"
    ]
    
    for file_path in files_to_process:
        if os.path.exists(file_path):
            print(f"🔧 Processando {file_path}...")
            convert_labels_to_uppercase(file_path)
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print("✅ Conversão de labels concluída!")
