// CORREÇÃO DEFINITIVA PARA SÓCIOS - ARQUIVO SEPARADO
console.log('🔧 Carregando correção de sócios...');

// Função limpa para carregar sócios
function carregarSociosCorrigido(dadosCliente) {
    console.log('🚀 CORREÇÃO CARREGADA - Executando...');
    
    if (!dadosCliente) {
        console.log('❌ Dados do cliente não fornecidos');
        return;
    }
    
    console.log('📊 Dados recebidos:', {
        socio1: dadosCliente.socio_1_nome,
        socio2: dadosCliente.socio_2_nome,
        socio3: dadosCliente.socio_3_nome
    });
    
    // Aguardar DOM
    setTimeout(() => {
        try {
            // Preencher sócio 1 (sempre existe)
            const nome1 = document.querySelector('input[name="socio_1_nome"]');
            if (nome1 && dadosCliente.socio_1_nome) {
                nome1.value = dadosCliente.socio_1_nome;
                console.log('✅ Sócio 1 preenchido:', dadosCliente.socio_1_nome);
            }
            
            // Se tem sócio 2, adicionar card
            if (dadosCliente.socio_2_nome) {
                console.log('➕ Adicionando sócio 2...');
                
                // Verificar se função adicionarSocio existe
                if (typeof adicionarSocio === 'function') {
                    adicionarSocio();
                    
                    // Preencher após um tempo
                    setTimeout(() => {
                        const nome2 = document.querySelector('input[name="socio_2_nome"]');
                        if (nome2) {
                            nome2.value = dadosCliente.socio_2_nome;
                            console.log('✅ Sócio 2 preenchido:', dadosCliente.socio_2_nome);
                        }
                        
                        const cpf2 = document.querySelector('input[name="socio_2_cpf"]');
                        if (cpf2 && dadosCliente.socio_2_cpf) {
                            cpf2.value = dadosCliente.socio_2_cpf;
                        }
                    }, 300);
                } else {
                    console.error('❌ Função adicionarSocio não encontrada');
                }
            }
            
            // Se tem sócio 3, adicionar card
            if (dadosCliente.socio_3_nome) {
                setTimeout(() => {
                    console.log('➕ Adicionando sócio 3...');
                    
                    if (typeof adicionarSocio === 'function') {
                        adicionarSocio();
                        
                        // Preencher após um tempo
                        setTimeout(() => {
                            const nome3 = document.querySelector('input[name="socio_3_nome"]');
                            if (nome3) {
                                nome3.value = dadosCliente.socio_3_nome;
                                console.log('✅ Sócio 3 preenchido:', dadosCliente.socio_3_nome);
                            }
                            
                            const cpf3 = document.querySelector('input[name="socio_3_cpf"]');
                            if (cpf3 && dadosCliente.socio_3_cpf) {
                                cpf3.value = dadosCliente.socio_3_cpf;
                            }
                        }, 300);
                    }
                }, 600);
            }
            
        } catch (error) {
            console.error('❌ Erro ao carregar sócios:', error);
        }
    }, 200);
}

// Sobrescrever a função original quando este script carregar
window.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Sobrescrevendo função carregarSocios...');
    window.carregarSocios = carregarSociosCorrigido;
});

// Também sobrescrever imediatamente se já carregou
if (window.carregarSocios) {
    console.log('🔧 Sobrescrevendo carregarSocios imediatamente...');
    window.carregarSocios = carregarSociosCorrigido;
}
