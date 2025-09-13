console.log('🔧 TESTE DE DEBUG - verificando se JavaScript está funcionando');

// Aguardar o carregamento da página
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Página carregada');
    
    // Verificar se o formulário existe
    const form = document.querySelector('form.needs-validation');
    console.log('📝 Formulário encontrado:', !!form);
    
    if (form) {
        console.log('📝 Action do formulário:', form.action);
        console.log('📝 Method do formulário:', form.method);
        
        // Verificar campos de códigos
        const codDominio = document.getElementById('codDominio');
        const codFortesCt = document.getElementById('codFortesCt');
        const codFortesFs = document.getElementById('codFortesFs');
        const codFortesPs = document.getElementById('codFortesPs');
        
        console.log('🔍 Campo codDominio:', !!codDominio);
        console.log('🔍 Campo codFortesCt:', !!codFortesCt);
        console.log('🔍 Campo codFortesFs:', !!codFortesFs);
        console.log('🔍 Campo codFortesPs:', !!codFortesPs);
        
        // Verificar se há ID (cliente existente)
        const idField = document.querySelector('input[name="id"]');
        console.log('🔍 Campo ID encontrado:', !!idField);
        if (idField) {
            console.log('🔍 Valor do ID:', idField.value);
        }
        
        // Adicionar listener direto no botão de salvar
        const saveButton = document.querySelector('button[type="submit"]');
        if (saveButton) {
            console.log('🔘 Botão de salvar encontrado');
            saveButton.addEventListener('click', function(e) {
                console.log('🔘 BOTÃO SALVAR CLICADO!');
                
                // Mostrar valores dos campos de códigos
                if (codDominio) console.log('📝 codDominio value:', codDominio.value);
                if (codFortesCt) console.log('📝 codFortesCt value:', codFortesCt.value);
                if (codFortesFs) console.log('📝 codFortesFs value:', codFortesFs.value);
                if (codFortesPs) console.log('📝 codFortesPs value:', codFortesPs.value);
            });
        }
    }
});