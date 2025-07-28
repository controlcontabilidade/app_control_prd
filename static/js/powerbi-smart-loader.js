/**
 * Sistema inteligente de carregamento do Power BI
 * Tenta iframe primeiro, com fallback rápido para interface alternativa
 */

function loadReportSmart(link) {
    console.log('🚀 SMART LOADER: Analisando link do Power BI');
    console.log('📊 Link:', link);
    
    // Validação básica
    if (!link || !link.includes('powerbi.com')) {
        console.error('❌ Link inválido do Power BI');
        showSmartError('Link inválido', 'Este não é um link válido do Power BI.');
        return;
    }
    
    // Detecta tipo de link e estratégia
    if (link.includes('/view?r=')) {
        console.log('🔍 Link público detectado - Power BI bloqueia embedding');
        showDirectAlternative(link, 'público');
    } else if (link.includes('/reportEmbed') && link.includes('autoAuth=true')) {
        console.log('🔍 Link de embed com autenticação detectado - TENTANDO IFRAME!');
        console.log('✨ Este tipo de link TEM CHANCE de funcionar embedado!');
        attemptAuthenticatedEmbed(link);
    } else if (link.includes('/reportEmbed')) {
        console.log('🔍 Link de embed detectado - tentando iframe');
        attemptIframeWithQuickFallback(link);
    } else {
        console.log('🔍 Tipo de link desconhecido - tentando iframe');
        attemptIframeWithQuickFallback(link);
    }
}

function attemptAuthenticatedEmbed(link) {
    console.log('🔐 TENTATIVA ESPECIAL: Embed com autenticação do Power BI');
    console.log('🎯 Este link pode funcionar porque inclui autoAuth=true');
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    // Mostra loading específico para autenticação
    showAuthLoadingState();
    removeExistingAlternative();
    
    // Configura iframe otimizado para autenticação
    configureIframeForAuthentication(reportFrame);
    
    let hasLoaded = false;
    let authCheckStartTime = Date.now();
    
    // Timeout mais longo para links com autenticação (20 segundos)
    const authTimeout = setTimeout(() => {
        if (!hasLoaded) {
            const elapsed = Date.now() - authCheckStartTime;
            console.log(`⏰ Timeout de autenticação após ${elapsed}ms`);
            showAuthFailureAlternative(link);
        }
    }, 20000);
    
    reportFrame.onload = function() {
        const loadTime = Date.now() - authCheckStartTime;
        console.log(`📡 OnLoad após ${loadTime}ms - verificando autenticação...`);
        
        // Aguarda menos tempo já que sabemos que funciona
        setTimeout(() => {
            if (verifyAuthenticatedContent(reportFrame)) {
                console.log('✅ SUCESSO! Embed com autenticação funcionou!');
                hasLoaded = true;
                clearTimeout(authTimeout);
                showSuccessfulEmbed();
            } else {
                console.log('⚠️ Aguardando mais um pouco para carregar...');
                // Segunda tentativa após mais tempo
                setTimeout(() => {
                    if (verifyAuthenticatedContent(reportFrame)) {
                        console.log('✅ SUCESSO na segunda verificação!');
                        hasLoaded = true;
                        clearTimeout(authTimeout);
                        showSuccessfulEmbed();
                    } else {
                        console.log('❌ Autenticação falhou após segunda tentativa');
                        clearTimeout(authTimeout);
                        showAuthFailureAlternative(link);
                    }
                }, 3000);
            }
        }, 2000); // Reduzido de 3000 para 2000ms
    };
    
    reportFrame.onerror = function() {
        console.error('❌ Erro no iframe com autenticação');
        clearTimeout(authTimeout);
        showAuthFailureAlternative(link);
    };
    
    // Monitora mudanças no iframe durante autenticação
    let checkCount = 0;
    const authMonitor = setInterval(() => {
        checkCount++;
        console.log(`🔍 Verificação ${checkCount}: Monitorando autenticação...`);
        
        if (hasLoaded || checkCount > 20) {
            clearInterval(authMonitor);
            return;
        }
        
        // Verifica se algo mudou no iframe
        try {
            const rect = reportFrame.getBoundingClientRect();
            if (rect.height > 200 && rect.width > 400) {
                console.log(`📊 Iframe cresceu para ${rect.width}x${rect.height} - possível sucesso!`);
                // Se as dimensões são boas, considera sucesso
                if (rect.height > 250 && !hasLoaded) {
                    console.log('✅ Dimensões indicam sucesso - finalizando positivamente');
                    hasLoaded = true;
                    clearTimeout(authTimeout);
                    clearInterval(authMonitor);
                    showSuccessfulEmbed();
                }
            }
        } catch (error) {
            console.log('🔒 Iframe protegido por CORS (normal)');
        }
    }, 1000);
    
    try {
        console.log('🌐 Carregando iframe com autenticação...');
        reportFrame.src = link;
    } catch (error) {
        console.error('❌ Erro ao definir src com autenticação:', error);
        clearTimeout(authTimeout);
        clearInterval(authMonitor);
        showAuthFailureAlternative(link);
    }
}

function configureIframeForAuthentication(iframe) {
    console.log('🔧 Configurando iframe para autenticação Power BI');
    
    // Remove todas as restrições
    iframe.removeAttribute('sandbox');
    
    // Máximas permissões para autenticação
    iframe.setAttribute('allow', 'microphone; camera; fullscreen; display-capture; autoplay; encrypted-media; clipboard-read; clipboard-write; geolocation; cross-origin-isolated');
    iframe.setAttribute('referrerpolicy', 'unsafe-url');
    iframe.setAttribute('allowfullscreen', 'true');
    iframe.setAttribute('allowtransparency', 'true');
    iframe.setAttribute('crossorigin', 'use-credentials');
    
    // Adiciona headers específicos para Power BI
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    
    console.log('✅ Iframe configurado para máxima compatibilidade com autenticação');
}

function verifyAuthenticatedContent(iframe) {
    try {
        const rect = iframe.getBoundingClientRect();
        console.log(`📏 Verificando conteúdo autenticado: ${rect.width}x${rect.height}`);
        
        // Com base no teste, sabemos que 1075x284 é um tamanho válido
        // Ajustamos os critérios para serem mais realistas
        if (rect.height > 200 && rect.width > 400) {
            console.log('✅ Dimensões indicam carregamento bem-sucedido');
            return true;
        }
        
        // Tenta detectar se há conteúdo Power BI
        try {
            const doc = iframe.contentDocument;
            if (doc) {
                console.log('📄 Documento acessível - possível sucesso');
                return true;
            }
        } catch (corsError) {
            console.log('🔒 CORS bloqueado - ISSO É BOM! Indica que o Power BI carregou');
            // CORS error com iframe de tamanho razoável = sucesso!
            if (rect.height > 150 && rect.width > 300) {
                return true;
            }
        }
        
        console.log('❓ Conteúdo ainda não verificável');
        return false;
        
    } catch (error) {
        console.log('❓ Erro ao verificar conteúdo autenticado:', error);
        return false;
    }
}

function showAuthLoadingState() {
    const reportLoading = document.getElementById('reportLoading');
    const reportFrame = document.getElementById('reportFrame');
    
    reportFrame.style.display = 'none';
    reportLoading.style.display = 'flex';
    
    // Atualiza mensagem de loading para autenticação
    const loadingContent = reportLoading.querySelector('.text-center');
    if (loadingContent) {
        loadingContent.innerHTML = `
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
            <h5 class="text-primary">🔐 Processando Autenticação</h5>
            <p class="text-muted">Conectando com Power BI...</p>
            <div class="mt-3">
                <div class="progress" style="width: 300px; margin: 0 auto;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         style="width: 70%"></div>
                </div>
                <small class="text-muted mt-2 d-block">
                    Links com autenticação podem demorar mais para carregar
                </small>
            </div>
        `;
    }
}

function showSuccessfulEmbed() {
    const reportLoading = document.getElementById('reportLoading');
    const reportFrame = document.getElementById('reportFrame');
    
    console.log('🎉 Mostrando embed bem-sucedido');
    
    reportLoading.style.display = 'none';
    reportFrame.style.display = 'block';
    
    // Mostra mensagem de sucesso temporária
    const successMsg = document.createElement('div');
    successMsg.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
    successMsg.style.zIndex = '9999';
    successMsg.innerHTML = `
        <i class="bi bi-check-circle-fill me-2"></i>
        <strong>✅ Sucesso!</strong> Relatório Power BI carregado com autenticação
    `;
    
    document.body.appendChild(successMsg);
    
    setTimeout(() => {
        successMsg.remove();
    }, 4000);
}

function showAuthFailureAlternative(link) {
    console.log('🔐 Falha na autenticação - mostrando alternativas específicas');
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    reportLoading.style.display = 'none';
    reportFrame.style.display = 'none';
    
    const modalBody = reportFrame.parentElement;
    removeExistingAlternative();
    
    const alternativeDiv = document.createElement('div');
    alternativeDiv.className = 'powerbi-alternative text-center py-4';
    
    alternativeDiv.innerHTML = `
        <div class="mb-4">
            <i class="bi bi-shield-lock text-warning" style="font-size: 4rem;"></i>
        </div>
        <h4 class="mb-3 text-warning">🔐 Autenticação Necessária</h4>
        
        <div class="alert alert-warning py-3 mb-4">
            <div class="mb-2">
                <i class="bi bi-info-circle-fill me-1"></i>
                <strong>Este relatório requer autenticação no Power BI</strong>
            </div>
            <small class="text-muted">
                Você precisa estar logado na sua conta Microsoft/Power BI para visualizar este conteúdo.
            </small>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary mb-3">🚀 Como acessar o relatório:</h6>
        </div>
        
        <div class="d-grid gap-3 col-10 col-md-8 mx-auto">
            <button onclick="openOptimizedPopup('${link}')" class="btn btn-success btn-lg">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="bi bi-window-stack me-3" style="font-size: 1.5rem;"></i>
                    <div class="text-start">
                        <div><strong>🪟 Popup com Login</strong></div>
                        <small class="opacity-75">Abre popup onde você pode fazer login no Power BI</small>
                    </div>
                </div>
            </button>
            
            <a href="${link}" target="_blank" class="btn btn-primary btn-lg">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="bi bi-box-arrow-up-right me-3" style="font-size: 1.5rem;"></i>
                    <div class="text-start">
                        <div><strong>🔗 Nova Aba</strong></div>
                        <small class="opacity-75">Abre em nova aba para fazer login</small>
                    </div>
                </div>
            </a>
            
            <button onclick="retryAuthenticatedEmbed('${link}')" class="btn btn-outline-success btn-lg">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="bi bi-arrow-clockwise me-3" style="font-size: 1.5rem;"></i>
                    <div class="text-start">
                        <div><strong>🔄 Tentar Novamente</strong></div>
                        <small class="opacity-75">Se você já fez login, tente embedar novamente</small>
                    </div>
                </div>
            </button>
        </div>
        
        <div class="mt-4 p-3 bg-info bg-opacity-10 border border-info rounded">
            <small class="text-info">
                <i class="bi bi-lightbulb-fill me-1"></i>
                <strong>Dica:</strong> Após fazer login no Power BI em outra aba, clique em "Tentar Novamente"
            </small>
        </div>
        
        <div class="mt-4">
            <details class="text-start">
                <summary class="btn btn-link btn-sm text-muted">
                    <i class="bi bi-question-circle me-1"></i>Por que preciso fazer login?
                </summary>
                <div class="mt-2 p-3 bg-light rounded small text-muted">
                    <p class="mb-2">
                        <strong>Segurança:</strong> Este relatório contém dados protegidos que requerem 
                        autenticação com sua conta Microsoft ou Power BI Pro/Premium.
                    </p>
                    <p class="mb-0">
                        <strong>Processo:</strong> Use o popup ou nova aba para fazer login, depois tente novamente.
                    </p>
                </div>
            </details>
        </div>
        
        <div class="mt-3">
            <button class="btn btn-outline-secondary btn-sm" onclick="copyLinkToClipboard('${link}')">
                <i class="bi bi-clipboard me-1"></i>Copiar Link do Relatório
            </button>
        </div>
    `;
    
    modalBody.appendChild(alternativeDiv);
}

function retryAuthenticatedEmbed(link) {
    console.log('🔄 RETRY: Tentando embed autenticado novamente');
    removeExistingAlternative();
    attemptAuthenticatedEmbed(link);
}

function showDirectAlternative(link, linkType) {
    console.log(`� Mostrando explicação direta para link ${linkType}`);
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    reportLoading.style.display = 'none';
    reportFrame.style.display = 'none';
    
    const modalBody = reportFrame.parentElement;
    removeExistingAlternative();
    
    const alternativeDiv = document.createElement('div');
    alternativeDiv.className = 'powerbi-alternative text-center py-4';
    
    const explanationText = linkType === 'público' 
        ? 'Links públicos do Power BI não podem ser embedados por política de segurança da Microsoft.'
        : 'Este link do Power BI não pode ser embedado diretamente.';
    
    alternativeDiv.innerHTML = `
        <div class="mb-4">
            <i class="bi bi-shield-exclamation text-warning" style="font-size: 4rem;"></i>
        </div>
        <h4 class="mb-3 text-warning">🚫 Embedding Bloqueado</h4>
        
        <div class="alert alert-warning py-3 mb-4">
            <div class="mb-2">
                <i class="bi bi-info-circle-fill me-1"></i>
                <strong>${explanationText}</strong>
            </div>
            <small class="text-muted">
                Esta é uma limitação técnica do Power BI, não do nosso sistema.
            </small>
        </div>
        
        <div class="mb-4">
            <h6 class="text-primary mb-3">✨ Escolha a melhor opção para você:</h6>
        </div>
        
        <div class="d-grid gap-3 col-10 col-md-8 mx-auto">
            <button onclick="openOptimizedPopup('${link}')" class="btn btn-success btn-lg">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="bi bi-window-stack me-3" style="font-size: 1.5rem;"></i>
                    <div class="text-start">
                        <div><strong>🪟 Popup Integrado</strong></div>
                        <small class="opacity-75">Melhor experiência - mantém você no sistema</small>
                    </div>
                </div>
            </button>
            
            <a href="${link}" target="_blank" class="btn btn-primary btn-lg">
                <div class="d-flex align-items-center justify-content-center">
                    <i class="bi bi-box-arrow-up-right me-3" style="font-size: 1.5rem;"></i>
                    <div class="text-start">
                        <div><strong>🔗 Nova Aba</strong></div>
                        <small class="opacity-75">Abre em aba separada do navegador</small>
                    </div>
                </div>
            </a>
        </div>
        
        <div class="mt-4 p-3 bg-success bg-opacity-10 border border-success rounded">
            <small class="text-success">
                <i class="bi bi-lightbulb-fill me-1"></i>
                <strong>Recomendamos o Popup:</strong> Oferece experiência integrada sem sair do sistema
            </small>
        </div>
        
        <div class="mt-4">
            <details class="text-start">
                <summary class="btn btn-link btn-sm text-muted">
                    <i class="bi bi-question-circle me-1"></i>Por que não funciona embedado?
                </summary>
                <div class="mt-2 p-3 bg-light rounded small text-muted">
                    <p class="mb-2">
                        <strong>Motivo técnico:</strong> A Microsoft bloqueia links públicos do Power BI 
                        (que terminam com /view?r=) de serem exibidos em iframes por questões de segurança.
                    </p>
                    <p class="mb-0">
                        <strong>Solução:</strong> Use os botões acima para acessar o relatório de forma segura e eficiente.
                    </p>
                </div>
            </details>
        </div>
        
        <div class="mt-3">
            <button class="btn btn-outline-secondary btn-sm" onclick="copyLinkToClipboard('${link}')">
                <i class="bi bi-clipboard me-1"></i>Copiar Link do Relatório
            </button>
        </div>
    `;
    
    modalBody.appendChild(alternativeDiv);
}

function attemptIframeWithQuickFallback(link) {
    console.log('🎯 Tentativa rápida de iframe (3 segundos)');
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    // Mostra loading
    reportLoading.style.display = 'flex';
    reportFrame.style.display = 'none';
    removeExistingAlternative();
    
    // Configura iframe
    configureIframeForPowerBI(reportFrame);
    
    let hasLoaded = false;
    
    // Timeout muito rápido - se não carregar em 3 segundos, assume que não vai carregar
    const quickTimeout = setTimeout(() => {
        if (!hasLoaded) {
            console.log('⚡ Timeout rápido - mostrando alternativas');
            showDirectAlternative(link, 'embed');
        }
    }, 3000);
    
    reportFrame.onload = function() {
        console.log('📡 OnLoad - verificando conteúdo...');
        
        setTimeout(() => {
            if (verifyIframeContent(reportFrame)) {
                console.log('✅ Iframe funcionou!');
                hasLoaded = true;
                clearTimeout(quickTimeout);
                reportLoading.style.display = 'none';
                reportFrame.style.display = 'block';
            } else {
                console.log('❌ Iframe vazio');
                clearTimeout(quickTimeout);
                showDirectAlternative(link, 'embed');
            }
        }, 1000);
    };
    
    reportFrame.onerror = function() {
        console.error('❌ Erro no iframe');
        clearTimeout(quickTimeout);
        showDirectAlternative(link, 'embed');
    };
    
    try {
        reportFrame.src = link;
    } catch (error) {
        console.error('❌ Erro ao definir src:', error);
        clearTimeout(quickTimeout);
        showDirectAlternative(link, 'embed');
    }
}

function configureIframeForPowerBI(iframe) {
    // Remove restrições
    iframe.removeAttribute('sandbox');
    
    // Adiciona permissões máximas
    iframe.setAttribute('allow', 'microphone; camera; fullscreen; display-capture; autoplay; encrypted-media; clipboard-read; clipboard-write; geolocation');
    iframe.setAttribute('referrerpolicy', 'unsafe-url');
    iframe.setAttribute('allowfullscreen', 'true');
    iframe.setAttribute('allowtransparency', 'true');
    
    console.log('⚙️ Iframe configurado para máxima compatibilidade');
}

function verifyIframeContent(iframe) {
    try {
        const rect = iframe.getBoundingClientRect();
        console.log(`📏 Dimensões: ${rect.width}x${rect.height}`);
        
        // Se tem dimensões razoáveis, provavelmente carregou
        if (rect.height > 100 && rect.width > 100) {
            return true;
        }
        
        // Tenta acessar documento (CORS error é esperado para Power BI)
        try {
            const doc = iframe.contentDocument;
            if (doc) {
                console.log('📄 Documento acessível');
                return true;
            }
        } catch (corsError) {
            console.log('🔒 CORS bloqueado (normal para Power BI)');
            // CORS error indica que algo carregou
            return true;
        }
        
    } catch (error) {
        console.log('❓ Erro ao verificar conteúdo:', error);
    }
    
    return false;
}

function removeExistingAlternative() {
    const existing = document.querySelector('.powerbi-alternative');
    if (existing) {
        existing.remove();
        console.log('🧹 Interface alternativa anterior removida');
    }
}

function showPowerBIAlternativeInterface(link) {
    console.log('🎨 Mostrando interface alternativa melhorada');
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    reportLoading.style.display = 'none';
    reportFrame.style.display = 'none';
    
    const modalBody = reportFrame.parentElement;
    removeExistingAlternative();
    
    const alternativeDiv = document.createElement('div');
    alternativeDiv.className = 'powerbi-alternative text-center py-4';
    alternativeDiv.innerHTML = `
        <div class="mb-4">
            <i class="bi bi-bar-chart-fill text-primary" style="font-size: 4rem;"></i>
        </div>
        <h4 class="mb-3 text-primary">📊 Relatório Power BI</h4>
        
        <div class="alert alert-info py-2 mb-4">
            <small>
                <i class="bi bi-shield-exclamation me-1"></i>
                Por questões de segurança, o Power BI bloqueia embedding direto.
            </small>
        </div>
        
        <div class="d-grid gap-3 col-10 col-md-8 mx-auto">
            <button onclick="openOptimizedPopup('${link}')" class="btn btn-primary btn-lg">
                <i class="bi bi-window-stack me-2"></i>
                <strong>Abrir em Popup</strong>
                <br><small class="opacity-75">Experiência integrada (Recomendado)</small>
            </button>
            
            <a href="${link}" target="_blank" class="btn btn-outline-primary btn-lg">
                <i class="bi bi-box-arrow-up-right me-2"></i>
                <strong>Abrir em Nova Aba</strong>
                <br><small class="opacity-75">Abre em aba separada</small>
            </a>
            
            <button class="btn btn-outline-secondary" onclick="forceIframeLoad('${link}')">
                <i class="bi bi-arrow-repeat me-1"></i>
                Forçar Iframe (Última tentativa)
            </button>
        </div>
        
        <div class="mt-4 p-3 bg-light rounded">
            <small class="text-success">
                <i class="bi bi-patch-check-fill me-1"></i>
                <strong>Popup Integrado</strong> mantém você no sistema e oferece melhor experiência
            </small>
        </div>
        
        <div class="mt-3">
            <button class="btn btn-link btn-sm" onclick="copyLinkToClipboard('${link}')">
                <i class="bi bi-clipboard me-1"></i>Copiar Link
            </button>
        </div>
    `;
    
    modalBody.appendChild(alternativeDiv);
}

function openOptimizedPopup(link) {
    console.log('🪟 Abrindo popup otimizado do Power BI');
    
    // Calcula dimensões ótimas baseadas na tela
    const screenWidth = window.screen.availWidth;
    const screenHeight = window.screen.availHeight;
    const width = Math.min(1600, screenWidth * 0.85);
    const height = Math.min(1000, screenHeight * 0.85);
    const left = (screenWidth - width) / 2;
    const top = (screenHeight - height) / 2;
    
    const features = [
        `width=${width}`,
        `height=${height}`,
        `left=${left}`,
        `top=${top}`,
        'scrollbars=yes',
        'resizable=yes',
        'status=no',
        'menubar=no',
        'toolbar=no',
        'location=no',
        'directories=no'
    ].join(',');
    
    // Tenta abrir popup
    const popup = window.open('', 'PowerBIReport', features);
    
    if (popup) {
        // Personaliza o popup enquanto carrega
        popup.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Relatório Power BI</title>
                <meta charset="utf-8">
                <style>
                    body { 
                        margin: 0; 
                        padding: 20px; 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        text-align: center;
                    }
                    .loading {
                        background: rgba(255,255,255,0.1);
                        padding: 40px;
                        border-radius: 15px;
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255,255,255,0.2);
                    }
                    .spinner {
                        border: 3px solid rgba(255,255,255,0.3);
                        border-radius: 50%;
                        border-top: 3px solid white;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 20px;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    h2 { margin: 0 0 10px 0; font-size: 24px; }
                    p { margin: 0; opacity: 0.8; font-size: 16px; }
                </style>
            </head>
            <body>
                <div class="loading">
                    <div class="spinner"></div>
                    <h2>📊 Carregando Power BI</h2>
                    <p>Redirecionando para o relatório...</p>
                </div>
                <script>
                    setTimeout(() => {
                        window.location.href = '${link}';
                    }, 1500);
                </script>
            </body>
            </html>
        `);
        
        popup.focus();
        console.log('✅ Popup personalizado criado');
        
        // Fecha modal após pequeno delay
        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            if (modal) {
                modal.hide();
                console.log('🔽 Modal fechado após abrir popup');
            }
        }, 800);
        
        // Monitora se popup foi fechado para reabrir modal se necessário
        const checkClosed = setInterval(() => {
            if (popup.closed) {
                clearInterval(checkClosed);
                console.log('🔄 Popup foi fechado pelo usuário');
            }
        }, 1000);
        
    } else {
        console.error('❌ Popup foi bloqueado pelo navegador');
        
        // Fallback: tenta abrir em nova aba
        const newTab = window.open(link, '_blank');
        if (newTab) {
            console.log('✅ Fallback: Aberto em nova aba');
        } else {
            console.error('❌ Nova aba também foi bloqueada');
            // Mostra instrução para o usuário
            alert('Popup foi bloqueado pelo navegador. Por favor, clique no link "Nova Aba" ou permita popups para este site.');
        }
    }
}

function forceIframeLoad(link) {
    console.log('🆘 FORÇANDO carregamento do iframe');
    
    removeExistingAlternative();
    
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    // Remove TODAS as restrições possíveis
    reportFrame.removeAttribute('sandbox');
    reportFrame.removeAttribute('allow');
    reportFrame.removeAttribute('referrerpolicy');
    reportFrame.removeAttribute('crossorigin');
    reportFrame.setAttribute('frameborder', '0');
    
    reportLoading.style.display = 'flex';
    reportFrame.style.display = 'none';
    
    reportFrame.src = link;
    
    // Timeout mais longo para tentativa forçada
    setTimeout(() => {
        reportLoading.style.display = 'none';
        reportFrame.style.display = 'block';
        
        // Verifica após alguns segundos se funcionou
        setTimeout(() => {
            if (!verifyIframeContent(reportFrame)) {
                console.log('❌ Tentativa forçada falhou');
                reportFrame.style.display = 'none';
                showPowerBIAlternativeInterface(link);
            }
        }, 3000);
    }, 10000);
}

function copyLinkToClipboard(link) {
    navigator.clipboard.writeText(link).then(() => {
        const btn = event.target.closest('button');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Copiado!';
        btn.classList.add('text-success');
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.classList.remove('text-success');
        }, 2000);
    }).catch(err => {
        console.error('Erro ao copiar link:', err);
    });
}

function showSmartError(title, message) {
    const reportFrame = document.getElementById('reportFrame');
    const reportLoading = document.getElementById('reportLoading');
    
    reportLoading.style.display = 'none';
    reportFrame.style.display = 'none';
    
    const modalBody = reportFrame.parentElement;
    removeExistingAlternative();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'powerbi-alternative text-center py-5';
    errorDiv.innerHTML = `
        <div class="mb-4">
            <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
        </div>
        <h5 class="text-warning mb-3">${title}</h5>
        <p class="text-muted">${message}</p>
    `;
    
    modalBody.appendChild(errorDiv);
}

// Exporta função principal para uso global
window.loadReportSmart = loadReportSmart;
