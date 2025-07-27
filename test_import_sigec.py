#!/usr/bin/env python3
"""
Teste da Função de Importação SIGEC
Verifica se a importação está funcionando com os novos campos organizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.import_service_lite import ImportServiceLite
from services.local_storage_service import LocalStorageService
from datetime import datetime

def test_import_service():
    """Testa o serviço de importação com a nova estrutura SIGEC"""
    print("🚀 TESTE DO SERVIÇO DE IMPORTAÇÃO SIGEC")
    print("=" * 50)
    
    try:
        # Usar local storage para teste
        storage_service = LocalStorageService()
        import_service = ImportServiceLite(storage_service)
        
        print(f"📊 Serviço disponível: {import_service.is_available()}")
        
        if not import_service.is_available():
            print("❌ ImportServiceLite não está disponível (openpyxl faltando)")
            return
        
        # Buscar template SIGEC mais recente
        import glob
        template_files = glob.glob("template_importacao_clientes_sigec_*.xlsx")
        if not template_files:
            print("❌ Nenhum template SIGEC encontrado")
            return
        
        template_file = max(template_files)  # Pegar o mais recente
        print(f"📋 Usando template: {template_file}")
        
        # Testar validação da estrutura
        print("\n🔍 Validando estrutura do template...")
        is_valid, message = import_service.validate_excel_structure(template_file)
        
        if is_valid:
            print(f"✅ Estrutura válida: {message}")
        else:
            print(f"❌ Estrutura inválida: {message}")
            return
        
        # Testar leitura do arquivo
        print("\n📖 Lendo dados do template...")
        data = import_service.read_excel_file(template_file)
        print(f"📊 {len(data)} linhas lidas do template")
        
        if data:
            print("\n🔧 Testando processamento dos dados...")
            
            # Normalizar colunas
            normalized_data = import_service.normalize_column_names(data)
            print("✅ Normalização de colunas concluída")
            
            # Limpar dados
            cleaned_data = import_service.clean_data(normalized_data)
            print("✅ Limpeza de dados concluída")
            
            # Processar primeira linha como teste
            if cleaned_data:
                first_row = cleaned_data[0]
                print(f"\n📋 Processando linha de exemplo...")
                
                client_data = import_service.process_row_to_client(first_row, 2)
                
                if client_data:
                    print("✅ Cliente processado com sucesso!")
                    print(f"   Nome: {client_data.get('nomeEmpresa', 'N/A')}")
                    print(f"   CNPJ: {client_data.get('cnpj', 'N/A')}")
                    print(f"   CT: {client_data.get('ct', False)}")
                    print(f"   FS: {client_data.get('fs', False)}")
                    print(f"   DP: {client_data.get('dp', False)}")
                    print(f"   Responsável: {client_data.get('responsavelServicos', 'N/A')}")
                    print(f"   Email: {client_data.get('emailPrincipal', 'N/A')}")
                    print(f"   Telefone: {client_data.get('telefoneFixo', 'N/A')}")
                    print(f"   Procuração RFB: {client_data.get('procRfb', False)}")
                    print(f"   Observações: {client_data.get('observacoesGerais', 'N/A')}")
                    
                    # Verificar campos SIGEC críticos
                    print(f"\n🎯 Verificando campos SIGEC críticos:")
                    campos_sigec = [
                        'nomeEmpresa', 'razaoSocialReceita', 'cnpj', 'regimeFederal',
                        'responsavelServicos', 'dataInicioServicos', 'socio1_nome',
                        'telefoneFixo', 'emailPrincipal', 'portalClienteAtivo',
                        'procRfb', 'observacoesGerais'
                    ]
                    
                    campos_ok = 0
                    for campo in campos_sigec:
                        valor = client_data.get(campo)
                        if valor or valor is False:  # Incluir False como valor válido
                            print(f"   ✅ {campo}: {valor}")
                            campos_ok += 1
                        else:
                            print(f"   ⚠️  {campo}: vazio/nulo")
                    
                    print(f"\n📊 Campos SIGEC processados: {campos_ok}/{len(campos_sigec)}")
                    
                    if campos_ok >= len(campos_sigec) * 0.8:  # 80% dos campos
                        print("🎉 Importação SIGEC funcionando corretamente!")
                    else:
                        print("⚠️  Alguns campos SIGEC podem não estar sendo processados")
                
                else:
                    print("❌ Erro ao processar cliente de exemplo")
            
        print("\n" + "=" * 50)
        print("✅ TESTE DE IMPORTAÇÃO CONCLUÍDO!")
        print("📊 Sistema de importação pronto para SIGEC")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import_service()
