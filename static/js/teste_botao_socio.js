// Versão simplificada e corrigida da função adicionarSocio()
let numeroSocios = 1;

function adicionarSocio() {
    console.log('🔧 TESTE: Iniciando adicionarSocio...');
    
    // Verificar limite
    if (numeroSocios >= 10) {
        alert('Limite máximo de 10 sócios atingido!');
        return false;
    }
    
    // Verificar container
    const container = document.getElementById('sociosContainer');
    if (!container) {
        console.error('❌ ERRO: sociosContainer não encontrado!');
        alert('Erro: Container de sócios não encontrado!');
        return false;
    }
    
    console.log('✅ Container encontrado:', container);
    
    // Contar sócios existentes
    const sociosExistentes = container.querySelectorAll('[id^="socio_"]').length;
    numeroSocios = sociosExistentes + 1;
    
    console.log(`📊 Sócios existentes: ${sociosExistentes}, próximo número: ${numeroSocios}`);
    
    // Criar novo sócio
    const novoSocio = document.createElement('div');
    novoSocio.className = 'card border-light mb-2 socio-card';
    novoSocio.id = `socio_${numeroSocios}`;
    
    console.log(`🆕 Criando card: ${novoSocio.id}`);
    
    // HTML simplificado para teste
    novoSocio.innerHTML = `
        <div class="card-body py-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-primary">Sócio ${numeroSocios}</span>
                <button type="button" class="btn btn-sm btn-outline-danger" 
                        onclick="removerSocio(${numeroSocios})">
                    ❌
                </button>
            </div>
            <div class="row">
                <div class="col-md-6 mb-2">
                    <label class="form-label">Nome do Sócio</label>
                    <input type="text" class="form-control" 
                           name="socio_${numeroSocios}_nome" 
                           id="socio_${numeroSocios}_nome"
                           placeholder="Nome completo do sócio">
                </div>
                <div class="col-md-3 mb-2">
                    <label class="form-label">CPF</label>
                    <input type="text" class="form-control" 
                           name="socio_${numeroSocios}_cpf" 
                           id="socio_${numeroSocios}_cpf"
                           placeholder="000.000.000-00">
                </div>
                <div class="col-md-3 mb-2">
                    <label class="form-label">% Quotas</label>
                    <input type="number" class="form-control" 
                           name="socio_${numeroSocios}_participacao" 
                           id="socio_${numeroSocios}_participacao"
                           placeholder="50.00" step="0.01">
                </div>
            </div>
        </div>
    `;
    
    // Adicionar ao container
    container.appendChild(novoSocio);
    
    console.log('✅ Sócio adicionado ao container');
    
    // Verificar se foi adicionado
    setTimeout(() => {
        const verificar = document.getElementById(`socio_${numeroSocios}`);
        console.log('🔍 Verificação - elemento existe?', !!verificar);
        
        if (verificar) {
            console.log('✅ SUCESSO: Sócio adicionado com sucesso!');
            
            // Focar no campo nome
            const nomeInput = document.getElementById(`socio_${numeroSocios}_nome`);
            if (nomeInput) {
                nomeInput.focus();
                console.log('🎯 Foco definido no campo nome');
            }
        } else {
            console.error('❌ ERRO: Sócio não foi adicionado corretamente');
        }
    }, 100);
    
    return true;
}

function removerSocio(numero) {
    console.log(`🗑️ Removendo sócio ${numero}`);
    
    if (numero === 1) {
        alert('O primeiro sócio não pode ser removido!');
        return;
    }
    
    const socio = document.getElementById(`socio_${numero}`);
    if (socio) {
        if (confirm('Deseja realmente remover este sócio?')) {
            socio.remove();
            console.log(`✅ Sócio ${numero} removido`);
        }
    } else {
        console.error(`❌ Sócio ${numero} não encontrado`);
    }
}

// Teste da função quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página carregada, testando funções...');
    
    const container = document.getElementById('sociosContainer');
    console.log('📦 Container existe?', !!container);
    
    const botao = document.querySelector('button[onclick="adicionarSocio()"]');
    console.log('🔘 Botão existe?', !!botao);
    
    if (botao) {
        console.log('✅ Botão Adicionar Sócio está configurado corretamente');
    }
});
