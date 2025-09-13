#!/usr/bin/env python3
"""
Script para diagnosticar problemas específicos na edição de clientes.
Este script simula exatamente o que acontece quando um usuário edita um cliente via formulário.
"""

import os
import sys
import json
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variáveis de ambiente necessárias
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_GOOGLE_SHEETS'] = 'true'
os.environ['USE_SERVICE_ACCOUNT'] = 'true'

def listar_clientes_disponiveis():
    """Lista clientes disponíveis para teste"""
    print("🔍 ===== LISTANDO CLIENTES DISPONÍVEIS =====")
    
    try:
        from app import get_storage_service
        storage = get_storage_service()
        
        clients = storage.get_clients()
        
        if not clients:
            print("❌ Nenhum cliente encontrado")
            return None
        
        print(f"✅ {len(clients)} clientes encontrados:")
        for i, client in enumerate(clients[-5:], 1):  # Mostrar últimos 5
            print(f"  {i}. {client.get('nomeEmpresa')} (ID: {client.get('id')})")
        
        return clients
        
    except Exception as e:
        print(f"❌ Erro ao listar clientes: {e}")
        return None

def buscar_cliente_por_id(client_id):
    """Busca um cliente específico por ID"""
    print(f"🔍 ===== BUSCANDO CLIENTE {client_id} =====")
    
    try:
        from app import get_storage_service
        storage = get_storage_service()
        
        client = storage.get_client(client_id)
        
        if client:
            print(f"✅ Cliente encontrado: {client.get('nomeEmpresa')}")
            print(f"🔍 ID: {client.get('id')}")
            print(f"🔍 Campos disponíveis: {len(client)} campos")
            print(f"🔍 Telefone atual: {client.get('telefoneFixo', 'NÃO DEFINIDO')}")
            print(f"🔍 Email atual: {client.get('emailPrincipal', 'NÃO DEFINIDO')}")
            print(f"🔍 Criado em: {client.get('criadoEm', 'NÃO DEFINIDO')}")
            print(f"🔍 Última atualização: {client.get('ultimaAtualizacao', 'NÃO DEFINIDO')}")
            return client
        else:
            print(f"❌ Cliente {client_id} não encontrado")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar cliente: {e}")
        return None

def simular_edicao_cliente(client_id, alteracoes):
    """Simula a edição de um cliente com alterações específicas"""
    print(f"🔍 ===== SIMULANDO EDIÇÃO DO CLIENTE {client_id} =====")
    
    try:
        # 1. Buscar cliente atual
        client_original = buscar_cliente_por_id(client_id)
        if not client_original:
            return False
        
        # 2. Preparar dados de edição (simulando formulário)
        print("🔍 Preparando dados de edição...")
        
        # Começar com dados originais
        client_data = dict(client_original)
        
        # Aplicar alterações específicas
        for campo, novo_valor in alteracoes.items():
            valor_antigo = client_data.get(campo, 'NÃO DEFINIDO')
            client_data[campo] = novo_valor
            print(f"   {campo}: '{valor_antigo}' → '{novo_valor}'")
        
        # Garantir que temos o ID
        client_data['id'] = client_id
        client_data['ultimaAtualizacao'] = datetime.now().isoformat()
        
        print(f"✅ Dados de edição preparados com {len(client_data)} campos")
        
        # 3. Simular salvamento
        print("🔍 Simulando salvamento...")
        
        from app import get_storage_service
        storage = get_storage_service()
        
        resultado = storage.save_client(client_data)
        
        print(f"🔍 Resultado do salvamento: {resultado}")
        
        if not resultado:
            print("❌ Falha no salvamento")
            return False
        
        # 4. Verificar se as alterações foram persistidas
        print("🔍 Verificando se alterações foram persistidas...")
        
        client_atualizado = storage.get_client(client_id)
        
        if not client_atualizado:
            print("❌ Cliente não encontrado após atualização")
            return False
        
        # Verificar cada alteração
        alteracoes_aplicadas = True
        for campo, valor_esperado in alteracoes.items():
            valor_atual = client_atualizado.get(campo)
            if valor_atual != valor_esperado:
                print(f"❌ {campo}: esperado '{valor_esperado}', encontrado '{valor_atual}'")
                alteracoes_aplicadas = False
            else:
                print(f"✅ {campo}: atualizado corretamente para '{valor_atual}'")
        
        if alteracoes_aplicadas:
            print("✅ SUCESSO: Todas as alterações foram persistidas!")
            return True
        else:
            print("❌ FALHA: Algumas alterações não foram persistidas")
            return False
            
    except Exception as e:
        print(f"❌ Erro na simulação de edição: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def testar_varios_cenarios():
    """Testa vários cenários de edição"""
    print("🔍 ===== TESTANDO VÁRIOS CENÁRIOS DE EDIÇÃO =====")
    
    # Primeiro, listar clientes disponíveis
    clients = listar_clientes_disponiveis()
    if not clients:
        print("❌ Não há clientes para testar")
        return
    
    # Pegar o último cliente para teste
    client_teste = clients[-1]
    client_id = client_teste.get('id')
    
    print(f"🎯 Cliente selecionado para teste: {client_teste.get('nomeEmpresa')} (ID: {client_id})")
    
    # Cenário 1: Alterar dados básicos
    print("\n🔍 CENÁRIO 1: Alterando dados básicos")
    alteracoes_basicas = {
        'telefoneFixo': f'(98) 9999-{datetime.now().strftime("%H%M")}',
        'emailPrincipal': f'teste-{datetime.now().strftime("%H%M%S")}@exemplo.com',
        'observacoes': f'Teste de edição realizado em {datetime.now().isoformat()}'
    }
    
    sucesso_basico = simular_edicao_cliente(client_id, alteracoes_basicas)
    
    # Cenário 2: Alterar nome da empresa
    print("\n🔍 CENÁRIO 2: Alterando nome da empresa")
    nome_original = client_teste.get('nomeEmpresa', '')
    alteracoes_nome = {
        'nomeEmpresa': f"{nome_original} - EDITADO {datetime.now().strftime('%H%M%S')}"
    }
    
    sucesso_nome = simular_edicao_cliente(client_id, alteracoes_nome)
    
    # Resumo
    print("\n🎉 ===== RESUMO DOS TESTES =====")
    print(f"Alterações básicas: {'✅ SUCESSO' if sucesso_basico else '❌ FALHA'}")
    print(f"Alteração de nome: {'✅ SUCESSO' if sucesso_nome else '❌ FALHA'}")
    
    if sucesso_basico and sucesso_nome:
        print("✅ CONCLUSÃO: Sistema de edição funcionando corretamente")
        print("⚠️ Se o usuário relata problemas, pode ser questão de interface ou cache")
    else:
        print("❌ CONCLUSÃO: Há problemas no sistema de edição que precisam ser investigados")

def main():
    """Função principal"""
    print("🚀 ===== DIAGNÓSTICO DE EDIÇÃO DE CLIENTES =====")
    print("ℹ️ Este script testa a funcionalidade de edição de clientes")
    
    try:
        testar_varios_cenarios()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()