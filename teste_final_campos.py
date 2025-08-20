#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo dos 10 campos problemáticos do Bloco 5
Verifica: HTML template + Backend + Service
"""

def teste_completo_campos():
    """Testa todos os componentes dos 10 campos problemáticos"""
    
    campos_problematicos = [
        'cpfCnpjSn',
        'codigoAcessoSn', 
        'acessoSeuma',
        'acessoSemace',
        'acessoIbama',
        'acessoFapInss',
        'acessoCrf',
        'senhaSemace',
        'anvisaGestor',
        'anvisaEmpresa'
    ]
    
    print("🔍 === TESTE COMPLETO DOS 10 CAMPOS PROBLEMÁTICOS ===")
    
    # Teste 1: HTML Template
    print("\n1. 📄 VERIFICANDO HTML TEMPLATE...")
    html_ok = 0
    try:
        with open('templates/client_form_complete.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        for campo in campos_problematicos:
            if f'name="{campo}"' in html_content:
                print(f"   ✅ {campo} - Template OK")
                html_ok += 1
            else:
                print(f"   ❌ {campo} - AUSENTE no template")
    except Exception as e:
        print(f"   ❌ Erro ao ler template: {e}")
    
    # Teste 2: Backend (app.py)
    print("\n2. 🔧 VERIFICANDO BACKEND (app.py)...")
    backend_ok = 0
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        for campo in campos_problematicos:
            if f"request.form.get('{campo}'" in app_content:
                print(f"   ✅ {campo} - Backend OK")
                backend_ok += 1
            else:
                print(f"   ❌ {campo} - AUSENTE no backend")
    except Exception as e:
        print(f"   ❌ Erro ao ler app.py: {e}")
    
    # Teste 3: Service (Google Sheets)
    print("\n3. 📊 VERIFICANDO SERVICE (Google Sheets)...")
    service_ok = 0
    try:
        with open('services/google_sheets_service_account.py', 'r', encoding='utf-8') as f:
            service_content = f.read()
        
        for campo in campos_problematicos:
            if f"'{campo}'" in service_content:
                print(f"   ✅ {campo} - Service OK")  
                service_ok += 1
            else:
                print(f"   ❌ {campo} - AUSENTE no service")
    except Exception as e:
        print(f"   ❌ Erro ao ler service: {e}")
    
    # Resultado Final
    print(f"\n📊 === RESULTADO FINAL ===")
    print(f"📄 HTML Template: {html_ok}/{len(campos_problematicos)} campos")
    print(f"🔧 Backend: {backend_ok}/{len(campos_problematicos)} campos")
    print(f"📊 Service: {service_ok}/{len(campos_problematicos)} campos")
    
    total_ok = html_ok + backend_ok + service_ok
    total_esperado = len(campos_problematicos) * 3
    
    if total_ok == total_esperado:
        print(f"\n🎉 SUCESSO TOTAL! Todos os componentes estão corretos!")
        print(f"Taxa de sucesso: 100% ({total_ok}/{total_esperado})")
        return True
    else:
        print(f"\n⚠️ PROBLEMAS ENCONTRADOS!")
        print(f"Taxa de sucesso: {(total_ok/total_esperado)*100:.1f}% ({total_ok}/{total_esperado})")
        return False

if __name__ == "__main__":
    teste_completo_campos()
