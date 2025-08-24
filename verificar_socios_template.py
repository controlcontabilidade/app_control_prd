#!/usr/bin/env python
"""
Script para verificar se a função carregarSocios está sendo executada corretamente
"""

def verificar_template():
    """Verificar se o template tem a versão correta da função"""
    try:
        with open('templates/client_form_complete.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se a função carregarSocios existe
        if 'function carregarSocios(dadosCliente) {' in content:
            print("✅ Função carregarSocios encontrada")
            
            # Verificar se tem debugging
            if '🔍 INICIANDO CARREGAR SÓCIOS...' in content:
                print("✅ Debugging encontrado na função")
                
                # Verificar se tem correções específicas
                if 'numeroSocio > 1' in content:
                    print("✅ Lógica de múltiplos sócios encontrada")
                    
                if 'adicionarSocio()' in content:
                    print("✅ Chamada adicionarSocio() encontrada")
                    
                if 'renomear o card criado' in content:
                    print("✅ Correção de renomeação de card encontrada")
                    
                # Verificar se tem timeout
                if 'setTimeout(' in content:
                    print("✅ Timeout encontrado")
                    
                print("\n🔍 Template parece estar correto com todas as correções")
            else:
                print("❌ Template NÃO tem debugging - versão antiga")
        else:
            print("❌ Função carregarSocios NÃO encontrada")
            
        # Verificar chamada da função
        if 'carregarSocios(dadosCliente);' in content:
            print("✅ Chamada carregarSocios encontrada")
        else:
            print("❌ Chamada carregarSocios NÃO encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao verificar template: {e}")

def verificar_cache_navegador():
    """Sugerir verificações de cache"""
    print("\n🔍 VERIFICAÇÕES DE CACHE:")
    print("1. O navegador pode estar usando cache do JavaScript")
    print("2. Pressione Ctrl+F5 no navegador para forçar reload completo")
    print("3. Abra as Ferramentas de Desenvolvedor (F12)")
    print("4. Vá para a aba Console")
    print("5. Procure pelas mensagens de debug começando com 🔍")
    print("6. Se não vir as mensagens, é problema de cache")

def criar_teste_javascript():
    """Criar um teste JavaScript inline para injetar"""
    js_test = """
    <script>
    console.log('🧪 TESTE DE FUNÇÃO SOCIOS');
    window.testarSocios = function() {
        console.log('🔍 Testando se carregarSocios existe...');
        if (typeof carregarSocios === 'function') {
            console.log('✅ carregarSocios encontrada!');
            
            // Simular dados de teste
            const dadosTeste = {
                socio_1_nome: 'TESTE 1',
                socio_2_nome: 'TESTE 2', 
                socio_3_nome: 'TESTE 3'
            };
            
            console.log('🧪 Executando carregarSocios...');
            carregarSocios(dadosTeste);
        } else {
            console.log('❌ carregarSocios NÃO encontrada!');
        }
    };
    
    // Executar teste após DOM carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.testarSocios);
    } else {
        window.testarSocios();
    }
    </script>
    """
    
    print("\n🧪 TESTE JAVASCRIPT:")
    print("Cole este código no console do navegador:")
    print(js_test)

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICAÇÃO DE TEMPLATE E JAVASCRIPT")
    print("=" * 60)
    
    verificar_template()
    verificar_cache_navegador()
    criar_teste_javascript()
