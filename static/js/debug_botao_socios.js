// TESTE DIRETO PARA BOTÃO ADICIONAR SÓCIO
console.log('🧪 === TESTE BOTÃO ADICIONAR SÓCIO ===');

// Aguardar o DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM carregado, procurando botão...');
    
    // Encontrar o botão
    const botaoAdicionar = document.querySelector('button[onclick="adicionarSocio()"]');
    console.log('🔍 Botão encontrado?', !!botaoAdicionar);
    
    if (botaoAdicionar) {
        console.log('✅ Botão "Adicionar Sócio" encontrado');
        console.log('🔍 Texto do botão:', botaoAdicionar.textContent.trim());
        console.log('🔍 onclick:', botaoAdicionar.getAttribute('onclick'));
        
        // Adicionar um listener adicional para debug
        botaoAdicionar.addEventListener('click', function(e) {
            console.log('🎯 BOTÃO CLICADO! Event:', e);
            console.log('🎯 Tipo de adicionarSocio:', typeof window.adicionarSocio);
            
            // Tentar chamar a função manualmente
            try {
                console.log('🧪 Tentando chamar adicionarSocio() manualmente...');
                if (typeof window.adicionarSocio === 'function') {
                    window.adicionarSocio();
                } else {
                    console.error('❌ adicionarSocio não é uma função!');
                }
            } catch (error) {
                console.error('❌ Erro ao chamar adicionarSocio:', error);
            }
        });
    } else {
        console.error('❌ Botão "Adicionar Sócio" NÃO encontrado!');
    }
});
