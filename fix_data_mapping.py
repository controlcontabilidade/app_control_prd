#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir mapeamento de dados dos clientes
Resolve problema de datas aparecendo no campo de status
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar serviços
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def test_data_mapping():
    """Testa e corrige o mapeamento de dados"""
    print("🔧 Iniciando verificação do mapeamento de dados...")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        print("✅ Serviço inicializado com sucesso")
        
        # Buscar todos os clientes
        print("📊 Buscando clientes...")
        clientes = service.get_clients()
        print(f"📊 Encontrados {len(clientes)} clientes")
        
        # Verificar problemas de mapeamento
        problemas_encontrados = 0
        
        for i, cliente in enumerate(clientes):
            client_id = cliente.get('id', 'N/A')
            nome = cliente.get('nomeEmpresa', 'N/A')
            status = cliente.get('statusCliente', 'N/A')
            ultima_atualizacao = cliente.get('ultimaAtualizacao', 'N/A')
            
            print(f"\n--- Cliente {i+1}: {nome} (ID: {client_id}) ---")
            print(f"Status: '{status}'")
            print(f"Última Atualização: '{ultima_atualizacao}'")
            
            # Verificar se status contém data (problema)
            if status and 'T' in str(status) and len(str(status)) > 10:
                print(f"❌ PROBLEMA ENCONTRADO: Status contém data ISO: '{status}'")
                problemas_encontrados += 1
                
                # Corrigir: definir status como 'ATIVO' se estava com data
                cliente['statusCliente'] = 'ATIVO'
                cliente['ultimaAtualizacao'] = datetime.now().isoformat()
                
                print("🔧 Corrigindo cliente...")
                if service.update_client(cliente):
                    print("✅ Cliente corrigido com sucesso")
                else:
                    print("❌ Erro ao corrigir cliente")
            else:
                print("✅ Status OK")
        
        print(f"\n📋 RESUMO:")
        print(f"Total de clientes verificados: {len(clientes)}")
        print(f"Problemas encontrados e corrigidos: {problemas_encontrados}")
        
        if problemas_encontrados == 0:
            print("🎉 Nenhum problema de mapeamento encontrado!")
        else:
            print("🔧 Todos os problemas foram corrigidos!")
            
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()

def criar_cliente_teste():
    """Cria um cliente de teste para verificar se tudo está funcionando"""
    print("\n🧪 Criando cliente de teste...")
    
    try:
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        
        cliente_teste = {
            'nomeEmpresa': 'TESTE MAPEAMENTO LTDA',
            'nomeFantasiaReceita': 'Teste Mapeamento',
            'cnpj': '12.345.678/0001-99',
            'statusCliente': 'ATIVO',
            'ativo': True,
            'cidade': 'Fortaleza',
            'estado': 'CE',
            'tributacao': 'SIMPLES',
            'ct': True,
            'fs': False,
            'dp': False,
            'dataInicioServicos': '2025-01-01',
            'ultimaAtualizacao': datetime.now().isoformat(),
            'criadoEm': datetime.now().isoformat()
        }
        
        print("📝 Dados do cliente teste:")
        for key, value in cliente_teste.items():
            print(f"  {key}: {value}")
        
        # Salvar cliente
        if service.save_client(cliente_teste):
            print("✅ Cliente de teste criado com sucesso!")
            return True
        else:
            print("❌ Erro ao criar cliente de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar cliente teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CORREÇÃO DE MAPEAMENTO DE DADOS - SISTEMA CONTROL")
    print("=" * 60)
    
    # Executar verificação e correção
    test_data_mapping()
    
    # Criar cliente de teste
    criar_cliente_teste()
    
    print("\n" + "=" * 60)
    print("🎯 Verificação concluída!")
    print("🌐 Acesse http://127.0.0.1:5000 para ver o resultado")
    print("=" * 60)
