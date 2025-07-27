#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar relatório de teste diretamente no Google Sheets
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.report_service import ReportService

def create_test_report():
    print("🚀 Criando relatório de teste...")
    
    try:
        # Usar o mesmo ID do Google Sheets da aplicação
        GOOGLE_SHEETS_ID = '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
        
        report_service = ReportService(GOOGLE_SHEETS_ID)
        print("✅ Serviço de relatórios inicializado")
        
        # Dados do relatório de teste
        nome = "Dashboard Financeiro (Teste)"
        descricao = "Relatório Power BI com autenticação para teste de embedding"
        link = "https://app.powerbi.com/reportEmbed?reportId=ef9c9663-7cec-4c9a-8b57-c1a6c895057a&autoAuth=true&ctid=0b754a09-0568-48fd-a100-8621a0bbd7ab"
        ativo = "Sim"
        ordem = 1
        criado_por = "Sistema"
        usuarios_autorizados = "todos"
        
        print(f"📊 Criando relatório: {nome}")
        print(f"🔗 Link: {link}")
        
        result = report_service.create_report(
            nome=nome,
            descricao=descricao, 
            link=link,
            ativo=ativo,
            ordem=ordem,
            criado_por=criado_por,
            usuarios_autorizados=usuarios_autorizados
        )
        
        if result['success']:
            print(f"✅ SUCESSO: {result['message']}")
            print("🎯 Relatório criado! Agora você pode testá-lo em:")
            print("   http://localhost:5000/reports")
        else:
            print(f"❌ ERRO: {result['message']}")
            
    except Exception as e:
        print(f"❌ Erro ao criar relatório: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_report()
