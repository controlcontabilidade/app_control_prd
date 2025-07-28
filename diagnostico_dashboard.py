#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_sheets_service_account import GoogleSheetsServiceAccountService

def main():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO - STATUS E ONVIO NA DASHBOARD")
    print("=" * 70)
    
    # Inicializar serviço
    service = GoogleSheetsServiceAccountService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
    print("✅ Serviço inicializado")
    
    # Buscar clientes
    print("\n📊 Buscando clientes...")
    clients = service.get_clients()
    
    if not clients:
        print("❌ Nenhum cliente encontrado")
        return
    
    print(f"📊 Encontrados {len(clients)} clientes")
    
    # Analisar cada cliente
    for i, client in enumerate(clients, 1):
        print(f"\n--- Cliente {i}: {client.get('nomeEmpresa', 'N/A')} ---")
        
        # STATUS
        status_cliente = client.get('statusCliente', '')
        ativo = client.get('ativo', True)
        print(f"📊 STATUS:")
        print(f"  statusCliente: '{status_cliente}' (tipo: {type(status_cliente)})")
        print(f"  ativo: {ativo} (tipo: {type(ativo)})")
        
        # Verificar se statusCliente tem formato de data/timestamp
        if status_cliente and ('T' in str(status_cliente) or '/' in str(status_cliente) or '-' in str(status_cliente)):
            print(f"  ⚠️  PROBLEMA: statusCliente parece ser data/timestamp!")
        
        # ONVIO
        sistema_onvio = client.get('sistemaOnvio', False)
        sistema_onvio_contabil = client.get('sistemaOnvioContabil', False)
        sistema_onvio_fiscal = client.get('sistemaOnvioFiscal', False)
        sistema_onvio_pessoal = client.get('sistemaOnvioPessoal', False)
        
        print(f"📊 ONVIO:")
        print(f"  sistemaOnvio: {sistema_onvio} (tipo: {type(sistema_onvio)})")
        print(f"  sistemaOnvioContabil: {sistema_onvio_contabil} (tipo: {type(sistema_onvio_contabil)})")
        print(f"  sistemaOnvioFiscal: {sistema_onvio_fiscal} (tipo: {type(sistema_onvio_fiscal)})")
        print(f"  sistemaOnvioPessoal: {sistema_onvio_pessoal} (tipo: {type(sistema_onvio_pessoal)})")
        
        has_any_onvio = sistema_onvio or sistema_onvio_contabil or sistema_onvio_fiscal or sistema_onvio_pessoal
        print(f"  Resultado final: {'SIM' if has_any_onvio else 'NÃO'}")
        
        # Status final que seria exibido
        display_status = status_cliente or ('ativo' if ativo else 'inativo')
        print(f"📋 Status que será exibido: '{display_status}'")
    
    print("\n" + "=" * 70)
    print("🎯 Diagnóstico concluído!")
    print("=" * 70)

if __name__ == "__main__":
    main()
