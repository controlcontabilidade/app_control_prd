#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("🔧 Corrigindo campo Data de Criação em todos os cadastros...")
    
    # Inicializar serviço
    spreadsheet_id = "1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s"
    service = GoogleSheetsServiceAccountService(spreadsheet_id)
    if not service:
        print("❌ Erro ao inicializar serviço")
        return
    
    print("✅ Serviço inicializado")
    
    # Buscar todos os clientes
    clientes = service.get_clients()
    if not clientes:
        print("❌ Erro ao buscar clientes")
        return
    
    print(f"📊 Total de clientes encontrados: {len(clientes)}")
    
    # Encontrar clientes com problemas
    clientes_para_corrigir = []
    
    for i, cliente in enumerate(clientes):
        nome = cliente.get('nomeEmpresa', 'SEM NOME')
        criado_em = cliente.get('criadoEm', '')
        id_cliente = cliente.get('id', '')
        
        # Verificar se precisa correção
        precisa_correcao = False
        
        # Problema 1: criadoEm é 'ativo'
        if criado_em == 'ativo':
            precisa_correcao = True
            
        # Problema 2: criadoEm está vazio
        if not criado_em or criado_em.strip() == '':
            precisa_correcao = True
            
        # Problema 3: criadoEm não parece um timestamp válido
        if criado_em and criado_em not in ['ativo', ''] and not ('T' in criado_em and len(criado_em) > 15):
            precisa_correcao = True
        
        if precisa_correcao and id_cliente and 'T' in id_cliente:
            clientes_para_corrigir.append({
                'linha': i + 2,  # +2 porque linha 1 é cabeçalho e arrays começam em 0
                'nome': nome,
                'criadoEm_atual': criado_em,
                'id': id_cliente,
                'criadoEm_novo': id_cliente  # Usar o ID como Data de Criação
            })
    
    print(f"\n🔍 Encontrados {len(clientes_para_corrigir)} clientes para corrigir")
    
    if not clientes_para_corrigir:
        print("✅ Nenhum cliente precisa de correção!")
        return
    
    # Mostrar alguns exemplos
    print("\n📋 Primeiros 10 clientes que serão corrigidos:")
    for i, cliente in enumerate(clientes_para_corrigir[:10]):
        print(f"{i+1}. {cliente['nome']}")
        print(f"   Linha: {cliente['linha']}")
        print(f"   criadoEm atual: '{cliente['criadoEm_atual']}'")
        print(f"   criadoEm novo: '{cliente['criadoEm_novo']}'")
        print()
    
    # Confirmar antes de prosseguir
    if len(clientes_para_corrigir) > 10:
        print(f"... e mais {len(clientes_para_corrigir) - 10} clientes")
    
    print(f"\n🚀 Iniciando correção em lote...")
    
    # Preparar atualizações em lote
    # A coluna criadoEm está na posição 152 (coluna EV)
    updates = []
    
    for cliente in clientes_para_corrigir:
        linha = cliente['linha']
        novo_valor = cliente['criadoEm_novo']
        
        # Atualizar coluna EV (posição 152)
        range_name = f"Clientes!EV{linha}"
        updates.append({
            'range': range_name,
            'values': [[novo_valor]]
        })
    
    print(f"📝 Preparadas {len(updates)} atualizações")
    
    # Executar atualizações em lote
    try:
        body = {
            'valueInputOption': 'RAW',
            'data': updates
        }
        
        result = service.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        print(f"✅ Correção concluída!")
        print(f"📊 {result.get('totalUpdatedCells', 0)} células atualizadas")
        
        # Verificar alguns casos
        print(f"\n🔍 Verificando correções...")
        clientes_atualizados = service.get_clients()
        
        verificacoes_ok = 0
        verificacoes_erro = 0
        
        for cliente_original in clientes_para_corrigir[:5]:  # Verificar apenas os primeiros 5
            nome = cliente_original['nome']
            valor_esperado = cliente_original['criadoEm_novo']
            
            # Encontrar o cliente atualizado
            cliente_atualizado = None
            for c in clientes_atualizados:
                if c.get('nomeEmpresa') == nome:
                    cliente_atualizado = c
                    break
            
            if cliente_atualizado:
                criado_em_atual = cliente_atualizado.get('criadoEm', '')
                if criado_em_atual == valor_esperado:
                    print(f"✅ {nome}: criadoEm = '{criado_em_atual}'")
                    verificacoes_ok += 1
                else:
                    print(f"❌ {nome}: esperado '{valor_esperado}', atual '{criado_em_atual}'")
                    verificacoes_erro += 1
            else:
                print(f"❌ {nome}: cliente não encontrado")
                verificacoes_erro += 1
        
        print(f"\n📊 Verificação: {verificacoes_ok} OK, {verificacoes_erro} erros")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")

if __name__ == "__main__":
    main()