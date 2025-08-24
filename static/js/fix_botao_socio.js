// CORREÇÃO DEFINITIVA - BOTÃO ADICIONAR SÓCIO
console.log('🔧 === CORREÇÃO BOTÃO ADICIONAR SÓCIO ===');

// Função para substituir o botão quebrado
function corrigirBotaoAdicionarSocio() {
    console.log('🔧 Procurando botão quebrado...');
    
    // Encontrar o botão atual
    const botaoAntigo = document.querySelector('button[onclick="adicionarSocio()"]');
    
    if (botaoAntigo) {
        console.log('✅ Botão antigo encontrado, substituindo...');
        
        // Criar novo botão funcional
        const novoBotao = document.createElement('button');
        novoBotao.type = 'button';
        novoBotao.className = 'btn btn-outline-primary btn-sm';
        novoBotao.innerHTML = '<i class="bi bi-plus-circle me-1"></i>Adicionar Sócio';
        
        // Adicionar evento funcional
        novoBotao.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🎯 NOVO BOTÃO CLICADO!');
            
            try {
                // Chamar função diretamente
                if (typeof window.adicionarSocio === 'function') {
                    console.log('✅ Chamando adicionarSocio...');
                    window.adicionarSocio();
                } else {
                    console.error('❌ Função adicionarSocio não encontrada');
                    // Tentar chamar função global
                    if (typeof adicionarSocio === 'function') {
                        console.log('✅ Chamando adicionarSocio global...');
                        adicionarSocio();
                    } else {
                        console.error('❌ Função adicionarSocio não existe em lugar nenhum');
                    }
                }
            } catch (error) {
                console.error('❌ Erro ao executar adicionarSocio:', error);
            }
        });
        
        // Substituir o botão
        botaoAntigo.parentNode.replaceChild(novoBotao, botaoAntigo);
        console.log('✅ Botão substituído com sucesso!');
    } else {
        console.error('❌ Botão antigo não encontrado');
    }
}

// Aguardar DOM carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', corrigirBotaoAdicionarSocio);
} else {
    corrigirBotaoAdicionarSocio();
}

// Também tentar após um pequeno delay
setTimeout(corrigirBotaoAdicionarSocio, 1000);
