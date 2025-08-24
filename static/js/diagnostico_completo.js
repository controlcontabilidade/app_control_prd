// Script para detectar erros JavaScript no template

console.log('🔍 DIAGNÓSTICO DETALHADO DO BOTÃO ADICIONAR SÓCIO');
console.log('========================================');

// 1. Verificar se a função existe
try {
    if (typeof adicionarSocio === 'function') {
        console.log('✅ Função adicionarSocio definida');
        console.log('   Código da função:', adicionarSocio.toString().substring(0, 100) + '...');
    } else {
        console.error('❌ Função adicionarSocio NÃO definida');
        console.log('   Tipo encontrado:', typeof adicionarSocio);
    }
} catch (e) {
    console.error('❌ Erro ao verificar função adicionarSocio:', e);
}

// 2. Verificar container
try {
    const container = document.getElementById('sociosContainer');
    if (container) {
        console.log('✅ Container sociosContainer encontrado');
        console.log('   Classes:', container.className);
        console.log('   Filhos:', container.children.length);
    } else {
        console.error('❌ Container sociosContainer NÃO encontrado');
    }
} catch (e) {
    console.error('❌ Erro ao verificar container:', e);
}

// 3. Verificar botão
try {
    const botao = document.querySelector('button[onclick="adicionarSocio()"]');
    if (botao) {
        console.log('✅ Botão encontrado');
        console.log('   Texto:', botao.textContent.trim());
        console.log('   Classes:', botao.className);
        console.log('   onclick:', botao.onclick);
        console.log('   getAttribute onclick:', botao.getAttribute('onclick'));
    } else {
        console.error('❌ Botão NÃO encontrado');
        
        // Procurar botões similares
        const botoesComTexto = document.querySelectorAll('button');
        console.log('🔍 Outros botões encontrados:');
        botoesComTexto.forEach((btn, i) => {
            if (btn.textContent.includes('Adicionar') || btn.textContent.includes('Sócio')) {
                console.log(`   ${i}: "${btn.textContent.trim()}" - onclick: ${btn.getAttribute('onclick')}`);
            }
        });
    }
} catch (e) {
    console.error('❌ Erro ao verificar botão:', e);
}

// 4. Verificar variável numeroSocios
try {
    console.log('📊 Variável numeroSocios:', typeof numeroSocios !== 'undefined' ? numeroSocios : 'NÃO DEFINIDA');
} catch (e) {
    console.error('❌ Erro ao verificar numeroSocios:', e);
}

// 5. Verificar erros JavaScript na página
window.addEventListener('error', function(e) {
    console.error('🚨 ERRO JAVASCRIPT DETECTADO:', e.error);
    console.error('   Arquivo:', e.filename);
    console.error('   Linha:', e.lineno);
    console.error('   Mensagem:', e.message);
});

// 6. Teste direto da função
console.log('🧪 TESTE DIRETO DA FUNÇÃO:');
try {
    if (typeof adicionarSocio === 'function') {
        console.log('   Executando adicionarSocio()...');
        const resultado = adicionarSocio();
        console.log('   Resultado:', resultado);
    } else {
        console.log('   Função não disponível para teste');
    }
} catch (e) {
    console.error('   ❌ ERRO ao executar função:', e);
    console.error('   Stack:', e.stack);
}

console.log('========================================');
console.log('🔚 Diagnóstico concluído.');
