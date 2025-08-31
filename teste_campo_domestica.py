#!/usr/bin/env python3
"""
Teste específico para verificar o campo Doméstica
"""

import requests
import time

def teste_campo_domestica():
    print("🏠 TESTE DO CAMPO DOMÉSTICA")
    print("=" * 50)
    
    try:
        # Fazer requisição para a página
        url = 'http://127.0.0.1:5000/client/new'
        print(f"🔄 Acessando: {url}")
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            print(f"✅ Página carregada! Status: {response.status_code}")
            
            # Verificar campo doméstica
            print("\n🔍 VERIFICANDO CAMPO DOMÉSTICA:")
            
            if 'id="domestica"' in html:
                print("  ✅ Campo domestica encontrado")
                
                # Verificar se está disabled por padrão
                if 'id="domestica" name="domestica" disabled' in html:
                    print("  ⚠️  Campo está DISABLED por padrão no HTML")
                elif 'disabled' in html.split('id="domestica"')[1].split('>')[0]:
                    print("  ⚠️  Campo tem atributo disabled")
                else:
                    print("  ✅ Campo NÃO está disabled no HTML")
                    
                # Verificar opções
                if 'value="SIM"' in html and 'value="NÃO"' in html:
                    print("  ✅ Opções SIM/NÃO encontradas")
                else:
                    print("  ❌ Opções SIM/NÃO não encontradas")
                    
            else:
                print("  ❌ Campo domestica NÃO encontrado")
                
            # Verificar função inline
            print("\n🔍 VERIFICANDO FUNÇÃO INLINE:")
            
            if 'formatarCpfCnpjInline' in html:
                print("  ✅ Função formatarCpfCnpjInline encontrada")
                
                if 'domesticaSelect.disabled = false' in html:
                    print("  ✅ Código para habilitar Doméstica encontrado")
                else:
                    print("  ❌ Código para habilitar Doméstica NÃO encontrado")
                    
                if 'domesticaSelect.disabled = true' in html:
                    print("  ✅ Código para desabilitar Doméstica encontrado")
                else:
                    print("  ❌ Código para desabilitar Doméstica NÃO encontrado")
                    
            else:
                print("  ❌ Função formatarCpfCnpjInline NÃO encontrada")
                
            # Verificar event handlers
            print("\n🔍 VERIFICANDO EVENT HANDLERS:")
            
            cpf_section = ""
            if 'id="cpfCnpj"' in html:
                # Extrair a seção do input CPF/CNPJ
                start = html.find('id="cpfCnpj"')
                end = html.find('>', start)
                cpf_section = html[start-100:end+1]  # Pegar contexto
                
                print("  ✅ Campo cpfCnpj encontrado")
                
                if 'oninput="formatarCpfCnpjInline(this)"' in cpf_section:
                    print("  ✅ Event handler oninput encontrado")
                else:
                    print("  ❌ Event handler oninput NÃO encontrado")
                    
                if 'onblur="formatarCpfCnpjInline(this)"' in cpf_section:
                    print("  ✅ Event handler onblur encontrado")
                else:
                    print("  ❌ Event handler onblur NÃO encontrado")
                    
            else:
                print("  ❌ Campo cpfCnpj NÃO encontrado")
                
            print("\n📋 INSTRUÇÕES PARA TESTE MANUAL:")
            print("1. Abra o navegador: http://127.0.0.1:5000/client/new")
            print("2. Abra o Console (F12)")
            print("3. Digite: document.getElementById('domestica').disabled")
            print("   - Se retornar true, está bloqueado")
            print("   - Se retornar false, está liberado")
            print("4. Digite um CPF: 02051962332")
            print("5. Digite novamente: document.getElementById('domestica').disabled")
            print("6. O resultado deve ser false (liberado)")
            
        else:
            print(f"❌ Erro ao carregar página. Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Servidor não está rodando")
        print("💡 Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    teste_campo_domestica()
