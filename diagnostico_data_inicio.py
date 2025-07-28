#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problema específico do campo dataInicioServicos
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar serviços
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def diagnosticar_campo_data():
    """Diagnostica especificamente o campo dataInicioServicos"""
    print("🔍 Diagnosticando campo 'Data de Início dos Serviços'...")
    
    try:
        # Inicializar serviço
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        print("✅ Serviço inicializado")
        
        # Buscar todos os clientes
        clientes = service.get_clients()
        print(f"📊 Encontrados {len(clientes)} clientes")
        
        for i, cliente in enumerate(clientes):
            nome = cliente.get('nomeEmpresa', 'N/A')
            client_id = cliente.get('id', 'N/A')
            data_inicio = cliente.get('dataInicioServicos', 'N/A')
            status_cliente = cliente.get('statusCliente', 'N/A')
            ativo = cliente.get('ativo', 'N/A')
            
            print(f"\n--- Cliente {i+1}: {nome} (ID: {client_id}) ---")
            print(f"🗓️  dataInicioServicos: '{data_inicio}'")
            print(f"📋 statusCliente: '{status_cliente}'")
            print(f"✅ ativo: '{ativo}'")
            
            # Verificar se o campo data está com valor inválido
            if str(data_inicio).lower() in ['ativo', 'inativo', 'sim', 'não', 'true', 'false']:
                print(f"❌ PROBLEMA: Campo dataInicioServicos contém valor boolean/status: '{data_inicio}'")
                
                # Corrigir o problema
                cliente['dataInicioServicos'] = ''  # Limpar campo problemático
                cliente['ultimaAtualizacao'] = datetime.now().isoformat()
                
                print("🔧 Corrigindo cliente...")
                if service.update_client(cliente):
                    print("✅ Cliente corrigido")
                else:
                    print("❌ Erro ao corrigir cliente")
            
            elif data_inicio and data_inicio != 'N/A':
                print(f"✅ Campo OK - Data válida: '{data_inicio}'")
            else:
                print("ℹ️  Campo vazio - OK")
                
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

def buscar_dados_brutos():
    """Busca dados brutos da planilha para análise"""
    print("\n🔍 Buscando dados brutos da planilha...")
    
    try:
        service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        
        # Buscar dados brutos
        result = service.service.spreadsheets().values().get(
            spreadsheetId=service.spreadsheet_id,
            range='Clientes!A:CZ'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("❌ Nenhum dado encontrado")
            return
            
        print(f"📊 Total de linhas: {len(values)}")
        
        # Mostrar cabeçalhos relevantes
        if len(values) > 0:
            headers = values[0]
            print(f"📝 Total de colunas: {len(headers)}")
            
            # Encontrar índices dos campos relevantes
            indices_importantes = {}
            for i, header in enumerate(headers):
                if 'DATA INÍCIO' in header.upper() or 'INICIO' in header.upper():
                    indices_importantes[f'dataInicioServicos (col {i+1})'] = i
                elif 'STATUS' in header.upper():
                    indices_importantes[f'statusCliente (col {i+1})'] = i
                elif header.upper() == 'ATIVO' or 'CLIENTE ATIVO' in header.upper():
                    indices_importantes[f'ativo (col {i+1})'] = i
                elif header.upper() == 'ID':
                    indices_importantes[f'id (col {i+1})'] = i
            
            print("\n📋 Campos importantes encontrados:")
            for nome, indice in indices_importantes.items():
                print(f"  {nome}: '{headers[indice]}'")
            
            # Mostrar dados da primeira linha de cliente (linha 2)
            if len(values) > 1:
                linha_cliente = values[1]
                print(f"\n📊 Dados da primeira linha de cliente (linha 2):")
                print(f"  Total de colunas na linha: {len(linha_cliente)}")
                
                for nome, indice in indices_importantes.items():
                    valor = linha_cliente[indice] if indice < len(linha_cliente) else 'VAZIO'
                    print(f"  {nome}: '{valor}'")
                    
    except Exception as e:
        print(f"❌ Erro ao buscar dados brutos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DO CAMPO 'DATA DE INÍCIO DOS SERVIÇOS'")
    print("=" * 70)
    
    # Buscar dados brutos primeiro
    buscar_dados_brutos()
    
    # Depois diagnosticar os campos processados
    diagnosticar_campo_data()
    
    print("\n" + "=" * 70)
    print("🎯 Diagnóstico concluído!")
    print("=" * 70)
