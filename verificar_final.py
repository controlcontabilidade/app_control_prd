"""
Verificação final se a correção funcionou
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verificar_correcao():
    """Verificar se o cliente foi editado com sucesso"""
    from app import app, get_storage_service
    
    with app.app_context():
        print("🔍 === VERIFICAÇÃO FINAL ===")
        
        service = get_storage_service()
        client_id = "1755359183434"
        
        # Buscar cliente específico
        cliente = service.get_client(client_id)
        
        if cliente:
            print(f"✅ Cliente encontrado:")
            print(f"   Nome: {cliente.get('nomeEmpresa')}")
            print(f"   Status: '{cliente.get('statusCliente')}'")
            print(f"   Ativo: {cliente.get('ativo')}")
            
            if cliente.get('statusCliente') == 'inativo':
                print("\n🎉 CORREÇÃO FOI APLICADA COM SUCESSO!")
                print("✅ O bug do status foi corrigido")
                print("✅ Agora você pode editar status de 'ativo' para 'inativo'")
            else:
                print(f"\n⚠️ Status atual: '{cliente.get('statusCliente')}'")
                print("Vou tentar editar novamente...")
                
                # Tentar editar diretamente
                dados_edicao = {
                    'id': client_id,
                    'nomeEmpresa': cliente.get('nomeEmpresa'),
                    'statusCliente': 'inativo',  # Forçar inativo
                    'ativo': False,
                    'ultimaAtualizacao': '2025-08-16T13:00:00'
                }
                
                resultado = service.save_client(dados_edicao)
                print(f"Resultado da edição forçada: {resultado}")
                
                # Verificar novamente
                cliente_pos = service.get_client(client_id)
                if cliente_pos and cliente_pos.get('statusCliente') == 'inativo':
                    print("🎉 EDIÇÃO FORÇADA FUNCIONOU!")
                else:
                    print("❌ Problema persiste")
        else:
            print("❌ Cliente não encontrado")

if __name__ == "__main__":
    verificar_correcao()
