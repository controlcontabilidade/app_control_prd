#!/usr/bin/env python3
"""
Teste do campo Doméstica com login
"""

import requests
import re

def teste_domestica_com_login():
    print("🔐 TESTE CAMPO DOMÉSTICA (COM LOGIN)")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # 1. Fazer login
        print("🔐 Fazendo login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            return
            
        # 2. Acessar página de novo cliente
        print("🔄 Acessando página de novo cliente...")
        response = session.get('http://127.0.0.1:5000/client/new')
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            return
            
        html = response.text
        print(f"✅ Página carregada! Tamanho: {len(html)} caracteres")
        
        # 3. Verificar campo doméstica
        print("\n🔍 VERIFICANDO CAMPO DOMÉSTICA:")
        
        if 'id="domestica"' in html:
            print("  ✅ Campo domestica encontrado")
            
            # Extrair o elemento completo
            pattern = r'<select[^>]*id="domestica"[^>]*>(.*?)</select>'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                select_element = match.group(0)
                print(f"  📋 Elemento: {select_element[:100]}...")
                
                if 'disabled' in select_element:
                    print("  ⚠️  Campo tem atributo 'disabled'")
                else:
                    print("  ✅ Campo NÃO tem atributo 'disabled'")
                    
                if 'value="SIM"' in select_element and 'value="NÃO"' in select_element:
                    print("  ✅ Opções SIM/NÃO encontradas")
                    
        else:
            print("  ❌ Campo domestica NÃO encontrado")
            
        # 4. Verificar campo CPF/CNPJ
        print("\n🔍 VERIFICANDO CAMPO CPF/CNPJ:")
        
        if 'id="cpfCnpj"' in html:
            print("  ✅ Campo cpfCnpj encontrado")
            
            # Extrair o elemento completo
            pattern = r'<input[^>]*id="cpfCnpj"[^>]*>'
            match = re.search(pattern, html)
            
            if match:
                input_element = match.group(0)
                print(f"  📋 Elemento: {input_element}")
                
                if 'oninput="formatarCpfCnpjInline(this)"' in input_element:
                    print("  ✅ Event handler oninput encontrado")
                else:
                    print("  ❌ Event handler oninput NÃO encontrado")
                    
        else:
            print("  ❌ Campo cpfCnpj NÃO encontrado")
            
        # 5. Verificar função inline
        print("\n🔍 VERIFICANDO FUNÇÃO INLINE:")
        
        if 'function formatarCpfCnpjInline(' in html:
            print("  ✅ Função formatarCpfCnpjInline encontrada")
            
            if 'domesticaSelect.disabled = false' in html:
                print("  ✅ Código para habilitar Doméstica encontrado")
            else:
                print("  ❌ Código para habilitar Doméstica NÃO encontrado")
                
            if 'configurarCampoDomesticaInicial' in html:
                print("  ✅ Função de inicialização encontrada")
            else:
                print("  ❌ Função de inicialização NÃO encontrada")
                
        else:
            print("  ❌ Função formatarCpfCnpjInline NÃO encontrada")
            
        print("\n🎯 RESULTADO:")
        print("Se todos os itens foram encontrados, a implementação está correta!")
        print("Teste manual: acesse http://127.0.0.1:5000/client/new no navegador")
        print("Digite um CPF e verifique se o campo Doméstica é habilitado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    teste_domestica_com_login()
