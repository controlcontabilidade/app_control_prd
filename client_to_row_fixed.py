#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Função client_to_row corrigida para evitar erro de índice
"""

def client_to_row_fixed(client: dict, headers: list) -> list:
    """Converte cliente para linha da planilha usando mapeamento de headers"""
    
    # Inicializar row_data com tamanho correto
    row_data = [''] * len(headers)
    
    # Mapear índices de cabeçalho
    hidx = {name: i for i, name in enumerate(headers)}
    
    # Preencher apenas os campos que existem nos headers
    field_mappings = {
        'NOME DA EMPRESA': client.get('nomeEmpresa', ''),
        'RAZÃO SOCIAL NA RECEITA': client.get('razaoSocialReceita', ''),
        'NOME FANTASIA NA RECEITA': client.get('nomeFantasiaReceita', ''),
        'CNPJ': client.get('cnpj', ''),
        'PERFIL': client.get('perfil', ''),
        'INSCRIÇÃO ESTADUAL': client.get('inscEst', ''),
        'INSCRIÇÃO MUNICIPAL': client.get('inscMun', ''),
        'ESTADO': client.get('estado', ''),
        'CIDADE': client.get('cidade', ''),
        'REGIME FEDERAL': client.get('regimeFederal', ''),
        'REGIME ESTADUAL': client.get('regimeEstadual', ''),
        'SEGMENTO': client.get('segmento', ''),
        'ATIVIDADE': client.get('atividade', ''),
        'SERVIÇO CT': 'SIM' if client.get('ct') else 'NÃO',
        'SERVIÇO FS': 'SIM' if client.get('fs') else 'NÃO',
        'SERVIÇO DP': 'SIM' if client.get('dp') else 'NÃO',
        'SERVIÇO BPO FINANCEIRO': 'SIM' if client.get('bpoFinanceiro') else 'NÃO',
        'DATA INÍCIO DOS SERVIÇOS': client.get('dataInicioServicos', ''),
        'CÓDIGO FORTES CT': f"'{str(client.get('codFortesCt', ''))}" if client.get('codFortesCt') else '',
        'CÓDIGO FORTES FS': f"'{str(client.get('codFortesFs', ''))}" if client.get('codFortesFs') else '',
        'CÓDIGO FORTES PS': f"'{str(client.get('codFortesPs', ''))}" if client.get('codFortesPs') else '',
        'CÓDIGO DOMÍNIO': f"'{str(client.get('codDominio', ''))}" if client.get('codDominio') else '',
        'SISTEMA UTILIZADO': client.get('sistemaUtilizado', ''),
        # Campos de senha (organizados em 4 linhas)
        'CNPJ ACESSO SIMPLES NACIONAL': client.get('cnpjAcessoSn', ''),
        'CPF DO REPRESENTANTE LEGAL': client.get('cpfRepLegal', ''),
        'CÓDIGO ACESSO SN': client.get('codigoAcessoSn', ''),
        'SENHA ISS': client.get('senhaIss', ''),
        'SENHA SEFIN': client.get('senhaSefin', ''),
        'SENHA SEUMA': client.get('senhaSeuma', ''),
        'ACESSO EMPWEB': client.get('acessoEmpWeb', ''),
        'SENHA EMPWEB': client.get('senhaEmpWeb', ''),
        'LOGIN ANVISA EMPRESA': client.get('anvisaEmpresa', ''),
        'SENHA ANVISA EMPRESA': client.get('senhaAnvisaEmpresa', ''),
        'LOGIN ANVISA GESTOR': client.get('anvisaGestor', ''),
        'SENHA ANVISA GESTOR': client.get('senhaAnvisaGestor', ''),
        'ACESSO CRF': client.get('acessoCrf', ''),
        'SENHA FAP/INSS': client.get('senhaFapInss', ''),
        # Campos internos
        'DONO/RESPONSÁVEL': client.get('donoResp', ''),
        'CLIENTE ATIVO': 'SIM' if client.get('ativo', True) else 'NÃO',
        'DATA DE CRIAÇÃO': client.get('criadoEm', ''),
        'ID': client.get('id', ''),
    }
    
    # Preencher apenas campos que existem nos headers
    for field_name, value in field_mappings.items():
        if field_name in hidx:
            row_data[hidx[field_name]] = value
    
    # Processar campos especiais
    try:
        import re
        doc = client.get('cnpj') or client.get('cpfCnpj') or ''
        digits = re.sub(r'\D', '', str(doc))
    except Exception:
        digits = ''

    domestica_val = (client.get('domestica') or '').strip().upper()
    if len(digits) == 11:
        domestica_final = domestica_val if domestica_val in ['SIM', 'NÃO'] else 'NÃO'
    else:
        domestica_final = 'NÃO'
    if 'DOMÉSTICA' in hidx:
        row_data[hidx['DOMÉSTICA']] = domestica_final

    gera_sped_val = (client.get('geraArquivoSped') or '').strip().upper()
    if 'GERA ARQUIVO DO SPED' in hidx:
        row_data[hidx['GERA ARQUIVO DO SPED']] = gera_sped_val if gera_sped_val in ['SIM', 'NÃO'] else ''

    print(f"✅ [SERVICE] Total de colunas na linha: {len(row_data)} (esperado {len(headers)})")
    print("✅ [SERVICE] Linha preparada com cabeçalhos alinhados")
    
    return row_data

if __name__ == "__main__":
    # Teste da função
    client_test = {
        'nomeEmpresa': 'TESTE LTDA',
        'cnpj': '12.345.678/0001-90',
        'razaoSocialReceita': 'TESTE LTDA',
        'cnpjAcessoSn': '12345678000190',
        'cpfRepLegal': '123.456.789-00',
        'codigoAcessoSn': 'SN123456',
        'senhaIss': 'senha_iss_123',
        'senhaSefin': 'senha_sefin_123',
        'senhaSeuma': 'senha_seuma_123',
        'acessoEmpWeb': 'usuario_empweb',
        'senhaEmpWeb': 'senha_empweb_123',
        'anvisaEmpresa': 'usuario_anvisa_emp',
        'senhaAnvisaEmpresa': 'senha_anvisa_emp_123',
        'anvisaGestor': 'usuario_anvisa_gest',
        'senhaAnvisaGestor': 'senha_anvisa_gest_123',
        'acessoCrf': 'usuario_crf',
        'senhaFapInss': 'senha_fap_inss_123',
        'id': '123456789',
        'ativo': True
    }
    
    headers_test = [
        'NOME DA EMPRESA', 'RAZÃO SOCIAL NA RECEITA', 'CNPJ', 
        'CNPJ ACESSO SIMPLES NACIONAL', 'CPF DO REPRESENTANTE LEGAL', 
        'CÓDIGO ACESSO SN', 'SENHA ISS', 'SENHA SEFIN', 'SENHA SEUMA',
        'ACESSO EMPWEB', 'SENHA EMPWEB', 'LOGIN ANVISA EMPRESA', 
        'SENHA ANVISA EMPRESA', 'LOGIN ANVISA GESTOR', 'SENHA ANVISA GESTOR',
        'ACESSO CRF', 'SENHA FAP/INSS', 'ID', 'CLIENTE ATIVO'
    ]
    
    result = client_to_row_fixed(client_test, headers_test)
    print(f"Resultado: {len(result)} colunas")
    for i, val in enumerate(result):
        if val:
            print(f"{i}: {headers_test[i] if i < len(headers_test) else 'N/A'} = {val}")
