// CORREÇÃO ESPECÍFICA - BOTÃO XPATH
console.log('🎯 === CORREÇÃO BOTÃO POR XPATH ===');

function corrigirBotaoXPath() {
    console.log('🔍 Procurando botão pelo XPath...');
    
    // Função para buscar elemento por XPath
    function getElementByXPath(xpath) {
        return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }
    
    // Buscar o botão exato pelo XPath fornecido
    const botaoXPath = '/html/body/div/div/div/div/div/form/div[2]/div[2]/div/div/div[1]/button';
    const botaoAntigo = getElementByXPath(botaoXPath);
    
    if (botaoAntigo) {
        console.log('✅ Botão encontrado pelo XPath!');
        console.log('🔍 Texto atual:', botaoAntigo.textContent.trim());
        console.log('🔍 Classes:', botaoAntigo.className);
        console.log('🔍 onclick:', botaoAntigo.getAttribute('onclick'));
        
        // Remover onclick antigo
        botaoAntigo.removeAttribute('onclick');
        
        // Criar novo evento funcional
        botaoAntigo.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 BOTÃO XPATH CLICADO!');
            
            try {
                // Verificar se função existe
                if (typeof window.adicionarSocio === 'function') {
                    console.log('✅ Chamando window.adicionarSocio...');
                    window.adicionarSocio();
                } else if (typeof adicionarSocio === 'function') {
                    console.log('✅ Chamando adicionarSocio global...');
                    adicionarSocio();
                } else {
                    console.error('❌ Função adicionarSocio não encontrada!');
                    alert('Erro: Função adicionarSocio não está disponível');
                }
            } catch (error) {
                console.error('❌ Erro ao executar:', error);
                alert('Erro ao adicionar sócio: ' + error.message);
            }
        });
        
        // Adicionar indicador visual de que foi corrigido
        botaoAntigo.style.borderColor = '#28a745';
        botaoAntigo.title = 'Botão corrigido - funcional';
        
        console.log('✅ Botão XPath corrigido com sucesso!');
        
        return true;
    } else {
        console.error('❌ Botão não encontrado pelo XPath');
        console.log('🔍 Tentando busca alternativa...');
        
        // Busca alternativa
        const botaoAlternativo = document.querySelector('button[onclick*="adicionarSocio"]');
        if (botaoAlternativo) {
            console.log('✅ Encontrado por seletor alternativo!');
            return corrigirBotaoAlternativo(botaoAlternativo);
        }
        
        return false;
    }
}

function corrigirBotaoAlternativo(botao) {
    console.log('🔧 Corrigindo botão alternativo...');
    
    // Remover onclick antigo
    botao.removeAttribute('onclick');
    
    // Criar novo evento
    botao.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🎯 BOTÃO ALTERNATIVO CLICADO!');
        
        try {
            if (typeof adicionarSocio === 'function') {
                console.log('✅ Executando adicionarSocio...');
                adicionarSocio();
            } else {
                console.error('❌ adicionarSocio não é função');
            }
        } catch (error) {
            console.error('❌ Erro:', error);
        }
    });
    
    botao.style.borderColor = '#28a745';
    console.log('✅ Botão alternativo corrigido!');
    return true;
}

// Executar correção quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(corrigirBotaoXPath, 100);
    });
} else {
    setTimeout(corrigirBotaoXPath, 100);
}

// Tentar novamente após delay maior
setTimeout(function() {
    console.log('🔄 Tentativa adicional de correção...');
    corrigirBotaoXPath();
}, 2000);
