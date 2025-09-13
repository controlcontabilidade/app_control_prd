// Teste do botão Adicionar Contato
// Execute no console do navegador: testBotaoContato()

function testBotaoContato() {
    console.log('🧪 === TESTE DO BOTÃO ADICIONAR CONTATO ===');
    
    // 1. Verificar se a função existe
    if (typeof adicionarContato !== 'function') {
        console.error('❌ ERRO: Função adicionarContato não está definida!');
        return false;
    }
    console.log('✅ Função adicionarContato encontrada');
    
    // 2. Verificar se o container existe
    const container = document.getElementById('contatosContainer');
    if (!container) {
        console.error('❌ ERRO: Container contatosContainer não encontrado!');
        return false;
    }
    console.log('✅ Container contatosContainer encontrado');
    
    // 3. Verificar se o botão existe
    const botao = document.querySelector('button[onclick="adicionarContato()"]');
    if (!botao) {
        console.error('❌ ERRO: Botão "Adicionar Contato" não encontrado!');
        return false;
    }
    console.log('✅ Botão "Adicionar Contato" encontrado');
    
    // 4. Verificar contatos existentes
    console.log('🔍 Contatos atualmente visíveis:');
    for (let i = 1; i <= 10; i++) {
        const contato = document.getElementById(`contato_${i}`);
        if (contato) {
            const visivel = contato.style.display !== 'none';
            console.log(`   contato_${i}: ${visivel ? 'VISÍVEL' : 'OCULTO'}`);
        }
    }
    
    // 5. Testar a função manualmente
    console.log('🧪 Executando adicionarContato()...');
    try {
        const resultado = adicionarContato();
        console.log('✅ Função executada com sucesso. Resultado:', resultado);
        
        // Verificar novamente os contatos após execução
        setTimeout(() => {
            console.log('🔍 Contatos após execução da função:');
            for (let i = 1; i <= 10; i++) {
                const contato = document.getElementById(`contato_${i}`);
                if (contato) {
                    const visivel = contato.style.display !== 'none';
                    console.log(`   contato_${i}: ${visivel ? 'VISÍVEL' : 'OCULTO'}`);
                }
            }
        }, 500);
        
    } catch (error) {
        console.error('❌ ERRO ao executar adicionarContato():', error);
        return false;
    }
    
    return true;
}

// Auto-executar quando o script for carregado
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(() => {
        console.log('🔧 Script de teste de contatos carregado. Execute testBotaoContato() no console.');
    }, 1000);
} else {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            console.log('🔧 Script de teste de contatos carregado. Execute testBotaoContato() no console.');
        }, 1000);
    });
}
