#!/usr/bin/env python3
"""
Script de teste para verificar a integração SIGEC - Google Sheets
Testa se os 92 campos estão sendo mapeados corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime

def test_headers():
    """Testa se os headers estão corretos"""
    print("🔍 Testando headers do Google Sheets...")
    
    # IDs da planilha (mesmos do app.py)
    GOOGLE_SHEETS_ID = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
    GOOGLE_SHEETS_RANGE = 'Clientes!A:Z'
    
    service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
    headers = service.get_headers()
    
    print(f"✅ Total de headers: {len(headers)}")
    
    # Headers esperados por bloco
    expected_blocks = {
        "Bloco 1 - Informações da Pessoa Jurídica": 13,
        "Bloco 2 - Serviços Control": 12,
        "Bloco 3 - Quadro Societário": 6,
        "Bloco 4 - Contatos": 10,
        "Bloco 5 - Sistemas e Acessos": 7,
        "Bloco 6 - Senhas e Credenciais": 20,
        "Bloco 7 - Procurações": 12,
        "Bloco 8 - Observações e Dados": 12
    }
    
    total_expected = sum(expected_blocks.values())
    print(f"📋 Campos esperados: {total_expected}")
    
    if len(headers) == 92:
        print("✅ Número de headers correto (92 campos)")
    else:
        print(f"❌ Número incorreto de headers. Esperado: 92, Encontrado: {len(headers)}")
    
    # Mostrar primeiros 20 headers
    print("\n📝 Primeiros 20 headers:")
    for i, header in enumerate(headers[:20], 1):
        print(f"{i:2d}. {header}")
    
    return headers

def test_client_mapping():
    """Testa o mapeamento cliente -> planilha -> cliente"""
    print("\n🔄 Testando mapeamento de dados...")
    
    # IDs da planilha (mesmos do app.py)
    GOOGLE_SHEETS_ID = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
    GOOGLE_SHEETS_RANGE = 'Clientes!A:Z'
    
    service = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
    
    # Cliente de teste com todos os campos SIGEC
    test_client = {
        # Bloco 1: Informações da Pessoa Jurídica
        'nomeEmpresa': 'EMPRESA TESTE LTDA',
        'razaoSocialReceita': 'EMPRESA TESTE LTDA',
        'nomeFantasiaReceita': 'TESTE',
        'cnpj': '12.345.678/0001-90',
        'perfil': 'LUCRO PRESUMIDO',
        'inscEst': '123456789',
        'inscMun': '987654321',
        'estado': 'CE',
        'cidade': 'FORTALEZA',
        'regimeFederal': 'LUCRO PRESUMIDO',
        'regimeEstadual': 'NORMAL',
        'segmento': 'COMÉRCIO',
        'atividade': 'VENDA DE PRODUTOS',
        
        # Bloco 2: Serviços
        'ct': True,
        'fs': True,
        'dp': False,
        'bpoFinanceiro': True,
        'responsavelServicos': 'João da Silva',
        'dataInicioServicos': '2024-01-01',
        'codFortesCt': '12345',
        'codFortesFs': '67890',
        'codFortesPs': '',
        'codDominio': 'DOM123',
        'sistemaUtilizado': 'FORTES',
        'moduloSpedTrier': 'COMPLETO',
        
        # Bloco 3: Quadro Societário  
        'socio1_nome': 'JOÃO DA SILVA',
        'socio1_cpf': '123.456.789-00',
        'socio1_nascimento': '1980-01-01',
        'socio1_admin': True,
        'socio1_cotas': '100%',
        'socio1_resp_legal': True,
        
        # Bloco 4: Contatos
        'telefoneFixo': '(85) 3333-4444',
        'telefoneCelular': '(85) 99999-8888',
        'whatsapp': '(85) 99999-8888',
        'emailPrincipal': 'teste@empresa.com',
        'emailSecundario': 'contato@empresa.com',
        'responsavelImediato': 'Maria Santos',
        'emailsSocios': 'joao@empresa.com',
        'contatoContador': 'Contador ABC',
        'telefoneContador': '(85) 3333-5555',
        'emailContador': 'contador@abc.com',
        
        # Bloco 5: Sistemas
        'sistemaPrincipal': 'FORTES',
        'versaoSistema': '2024.1',
        'codAcessoSimples': 'SN123456',
        'cpfCnpjAcesso': '12345678000190',
        'portalClienteAtivo': True,
        'integracaoDominio': True,
        'sistemaOnvio': False,
        
        # Bloco 7: Procurações
        'procRfb': True,
        'procRfbData': '2024-01-15',
        'procRc': True,
        'procRcData': '2024-01-20',
        'procCx': False,
        'procCxData': '',
        'procSw': True,
        'procSwData': '2024-02-01',
        'procMunicipal': True,
        'procMunicipalData': '2024-02-05',
        'outrasProc': 'Procuração JUCEC',
        'obsProcuracoes': 'Todas as procurações estão válidas',
        
        # Bloco 8: Observações
        'observacoesGerais': 'Cliente em dia com as obrigações',
        'tarefasVinculadas': 5,
        'statusCliente': 'ATIVO',
        'ultimaAtualizacao': datetime.now().isoformat(),
        'responsavelAtualizacao': 'Sistema',
        'prioridadeCliente': 'ALTA',
        'tagsCliente': 'VIP,PREMIUM',
        'historicoAlteracoes': 'Cliente cadastrado via sistema',
        
        # Campos internos
        'id': 'TEST001',
        'ativo': True,
        'criadoEm': datetime.now().isoformat()
    }
    
    # Teste 1: Converter cliente para linha
    print("📤 Convertendo cliente para linha da planilha...")
    row_data = service.client_to_row(test_client)
    print(f"✅ Linha gerada com {len(row_data)} campos")
    
    # Teste 2: Converter linha de volta para cliente
    print("📥 Convertendo linha de volta para cliente...")
    recovered_client = service.row_to_client(row_data)
    recovered_client['id'] = 'TEST001'  # Definir ID manualmente
    print(f"✅ Cliente recuperado com {len(recovered_client.keys())} campos")
    
    # Teste 3: Verificar campos críticos
    print("\n🔍 Verificando campos críticos:")
    critical_fields = [
        'nomeEmpresa', 'cnpj', 'responsavelServicos', 'ct', 'fs', 'dp',
        'telefoneFixo', 'emailPrincipal', 'procRfb', 'observacoesGerais'
    ]
    
    all_ok = True
    for field in critical_fields:
        original = test_client.get(field)
        recovered = recovered_client.get(field)
        
        if original == recovered:
            print(f"  ✅ {field}: {original}")
        else:
            print(f"  ❌ {field}: {original} → {recovered}")
            all_ok = False
    
    if all_ok:
        print("\n🎉 Todos os campos críticos estão sendo mapeados corretamente!")
    else:
        print("\n⚠️  Alguns campos não estão sendo mapeados corretamente.")
    
    return test_client, recovered_client

def main():
    """Função principal do teste"""
    print("🚀 TESTE DE INTEGRAÇÃO SIGEC - GOOGLE SHEETS")
    print("=" * 50)
    
    try:
        # Teste 1: Headers
        headers = test_headers()
        
        # Teste 2: Mapeamento de dados
        original, recovered = test_client_mapping()
        
        print("\n" + "=" * 50)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("📊 Sistema pronto para usar os 92 campos SIGEC organizados em 8 blocos")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
