"""
TESTE DIRETO: Verificar dados que chegam ao template de edição
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

# Configurações
GOOGLE_SHEETS_ID = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
GOOGLE_SHEETS_RANGE = "Clientes!A:FG"

def testar_dados_edicao():
    print("🔍 ===== TESTE DIRETO: DADOS DE EDIÇÃO =====")
    
    try:
        # Criar serviço
        storage = GoogleSheetsServiceAccountService(GOOGLE_SHEETS_ID, GOOGLE_SHEETS_RANGE)
        
        # Buscar o cliente específico
        client_id = "1756032228826"
        client = storage.get_client(client_id)
        
        if not client:
            print(f"❌ Cliente com ID {client_id} não encontrado")
            return
        
        print(f"✅ Cliente encontrado: {client.get('nomeEmpresa')}")
        print(f"🔍 ID: {client.get('id')}")
        
        # Simular exatamente o que o Flask faz
        print(f"\n🔍 ===== SIMULAÇÃO FLASK TEMPLATE =====")
        
        # Dados que seriam passados para render_template
        template_data = {
            'client': client
        }
        
        # Simular o {{ client|tojson }} que está no template
        import json
        client_json_str = json.dumps(client, ensure_ascii=False)
        
        print(f"🔍 Dados que chegam ao JavaScript:")
        print(f"const dadosCliente = {client_json_str};")
        
        print(f"\n🔍 ===== CAMPOS DE SÓCIOS ESPECÍFICOS =====")
        for i in range(1, 4):
            nome = client.get(f'socio_{i}_nome', '')
            cpf = client.get(f'socio_{i}_cpf', '')
            participacao = client.get(f'socio_{i}_participacao', '')
            
            print(f"Sócio {i}:")
            print(f"  dadosCliente.socio_{i}_nome = '{nome}'")
            print(f"  dadosCliente.socio_{i}_cpf = '{cpf}'")
            print(f"  dadosCliente.socio_{i}_participacao = '{participacao}'")
            
            if nome and nome.strip():
                print(f"  ✅ Sócio {i} deveria ser encontrado pelo JavaScript")
            else:
                print(f"  ❌ Sócio {i} está vazio - não será processado")
        
        print(f"\n🔍 ===== VERIFICAÇÃO DO JAVASCRIPT =====")
        print("Simulação do loop JavaScript:")
        print("for (let i = 1; i <= 10; i++) {")
        print("  const nome = dadosCliente[`socio_${i}_nome`];")
        print("  if (nome && nome.trim() !== '') {")
        print("    // Sócio encontrado")
        print("  }")
        print("}")
        
        sociosEncontrados = []
        for i in range(1, 11):
            nome = client.get(f'socio_{i}_nome', '')
            if nome and nome.strip():
                sociosEncontrados.append(i)
                print(f"✅ JavaScript encontraria sócio {i}: '{nome}'")
        
        print(f"\n📊 Total de sócios que JavaScript deveria encontrar: {len(sociosEncontrados)}")
        print(f"📊 Lista: {sociosEncontrados}")
        
        # Verificar se há algum problema no JSON
        print(f"\n🔍 ===== VERIFICAÇÃO JSON =====")
        try:
            parsed_data = json.loads(client_json_str)
            print("✅ JSON válido")
            print(f"✅ socio_1_nome no JSON: '{parsed_data.get('socio_1_nome', 'UNDEFINED')}'")
            print(f"✅ socio_2_nome no JSON: '{parsed_data.get('socio_2_nome', 'UNDEFINED')}'")
            print(f"✅ socio_3_nome no JSON: '{parsed_data.get('socio_3_nome', 'UNDEFINED')}'")
        except Exception as e:
            print(f"❌ Erro no JSON: {e}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    testar_dados_edicao()
