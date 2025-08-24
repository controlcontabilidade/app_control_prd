// SOLUÇÃO DEFINITIVA - SUBSTITUIR BOTÃO COMPLETAMENTE
console.log('🚀 === SOLUÇÃO DEFINITIVA BOTÃO ===');

function criarBotaoFuncional() {
    console.log('🔧 Criando botão funcional...');
    
    // Função para buscar por XPath
    function getElementByXPath(xpath) {
        return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    }
    
    // Buscar o botão pelo XPath exato
    const xpathBotao = '/html/body/div/div/div/div/div/form/div[2]/div[2]/div/div/div[1]/button';
    let botaoAntigo = getElementByXPath(xpathBotao);
    
    // Se não encontrar pelo XPath, tentar outras formas
    if (!botaoAntigo) {
        console.log('⚠️ XPath não encontrou, tentando seletores...');
        botaoAntigo = document.querySelector('button[onclick*="adicionarSocio"]');
    }
    
    if (!botaoAntigo) {
        console.log('⚠️ Seletor onclick não encontrou, tentando por texto...');
        const botoes = document.querySelectorAll('button');
        for (let botao of botoes) {
            if (botao.textContent.includes('Adicionar Sócio')) {
                botaoAntigo = botao;
                break;
            }
        }
    }
    
    if (botaoAntigo) {
        console.log('✅ Botão encontrado! Substituindo...');
        console.log('📍 Localização:', botaoAntigo.outerHTML.substring(0, 100) + '...');
        
        // Criar o novo botão
        const novoBotao = document.createElement('button');
        novoBotao.type = 'button';
        novoBotao.className = botaoAntigo.className;
        novoBotao.innerHTML = '<i class="bi bi-plus-circle me-1"></i>Adicionar Sócio (CORRIGIDO)';
        novoBotao.style.backgroundColor = '#d4edda';
        novoBotao.style.borderColor = '#28a745';
        novoBotao.title = 'Botão funcional criado pelo script';
        
        // Adicionar o evento funcional
        novoBotao.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 NOVO BOTÃO CLICADO!!!');
            
            try {
                // Tentar executar a função de várias formas
                let sucesso = false;
                
                // Forma 1: window.adicionarSocio
                if (typeof window.adicionarSocio === 'function') {
                    console.log('✅ Executando window.adicionarSocio...');
                    window.adicionarSocio();
                    sucesso = true;
                }
                // Forma 2: adicionarSocio global
                else if (typeof adicionarSocio === 'function') {
                    console.log('✅ Executando adicionarSocio global...');
                    adicionarSocio();
                    sucesso = true;
                }
                // Forma 3: Procurar na window
                else if (window['adicionarSocio']) {
                    console.log('✅ Executando window["adicionarSocio"]...');
                    window['adicionarSocio']();
                    sucesso = true;
                }
                // Forma 4: Executar manualmente o código da função
                else {
                    console.log('⚠️ Função não encontrada, executando código manual...');
                    executarAdicionarSocioManual();
                    sucesso = true;
                }
                
                if (sucesso) {
                    console.log('🎉 SUCESSO! Sócio adicionado!');
                } else {
                    console.error('❌ Falha em todas as tentativas');
                }
                
            } catch (error) {
                console.error('❌ Erro ao executar:', error);
                alert('Erro: ' + error.message);
            }
        });
        
        // Substituir o botão antigo pelo novo
        botaoAntigo.parentNode.replaceChild(novoBotao, botaoAntigo);
        console.log('✅ BOTÃO SUBSTITUÍDO COM SUCESSO!');
        
    } else {
        console.error('❌ Botão não encontrado de forma alguma!');
        console.log('🔍 Listando todos os botões da página...');
        const todosBotoes = document.querySelectorAll('button');
        todosBotoes.forEach((btn, i) => {
            console.log(`Botão ${i}: ${btn.textContent.trim().substring(0, 30)}`);
        });
    }
}

// Função manual para adicionar sócio (fallback)
function executarAdicionarSocioManual() {
    console.log('🔧 Executando adicionarSocio manualmente...');
    
    // Verificar se variáveis globais existem
    let numeroSociosAtual = window.numeroSocios || 1;
    
    const container = document.getElementById('sociosContainer');
    if (!container) {
        console.error('❌ sociosContainer não encontrado');
        alert('Erro: Container de sócios não encontrado');
        return;
    }
    
    numeroSociosAtual++;
    console.log('📊 Novo número de sócios:', numeroSociosAtual);
    
    // Atualizar variável global se existir
    if (window.numeroSocios !== undefined) {
        window.numeroSocios = numeroSociosAtual;
    }
    
    // Criar o card do novo sócio
    const novoSocio = document.createElement('div');
    novoSocio.className = 'card border-light mb-2 socio-card';
    novoSocio.id = `socio_${numeroSociosAtual}`;
    
    novoSocio.innerHTML = `
        <div class="card-body py-3">
            <div class="row align-items-center">
                <div class="col-md-3 mb-2">
                    <label class="form-label small mb-1">Nome do Sócio</label>
                    <input type="text" class="form-control form-control-sm" 
                           name="socio_${numeroSociosAtual}_nome" 
                           placeholder="Nome completo do sócio">
                </div>
                <div class="col-md-2 mb-2">
                    <label class="form-label small mb-1">CPF</label>
                    <input type="text" class="form-control form-control-sm cpf-mask" 
                           name="socio_${numeroSociosAtual}_cpf" 
                           placeholder="000.000.000-00">
                </div>
                <div class="col-md-2 mb-2">
                    <label class="form-label small mb-1">% de Quotas</label>
                    <input type="number" class="form-control form-control-sm" 
                           name="socio_${numeroSociosAtual}_participacao" 
                           placeholder="50.00" step="0.01" min="0" max="100">
                </div>
                <div class="col-md-1 mb-2">
                    <button type="button" class="btn btn-outline-danger btn-sm w-100" 
                            onclick="this.parentElement.parentElement.parentElement.parentElement.remove()" 
                            title="Remover sócio">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(novoSocio);
    console.log('✅ Card de sócio adicionado manualmente!');
    
    // Animação
    novoSocio.style.opacity = '0';
    setTimeout(() => {
        novoSocio.style.transition = 'all 0.3s ease';
        novoSocio.style.opacity = '1';
    }, 10);
}

// Executar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', criarBotaoFuncional);
} else {
    setTimeout(criarBotaoFuncional, 100);
}

// Tentar novamente com delay
setTimeout(criarBotaoFuncional, 1000);
setTimeout(criarBotaoFuncional, 3000);
