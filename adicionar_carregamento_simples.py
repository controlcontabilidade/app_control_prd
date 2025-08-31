#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛠️ SCRIPT PARA INSERIR CARREGAMENTO SIMPLES DE SÓCIOS
====================================================

Este script vai adicionar um código JavaScript muito simples
para carregar o sócio 2 no final do template, após o {% endif %}
"""

import os

def adicionar_carregamento_simples():
    template_path = "templates/client_form_complete.html"
    
    print(f"🔍 Verificando arquivo: {template_path}")
    
    if not os.path.exists(template_path):
        print("❌ Template não encontrado!")
        return
    
    print("✅ Template encontrado!")
    
    # Ler o arquivo
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Arquivo lido: {len(content)} caracteres")
    
    # Código JavaScript simples para adicionar
    js_code = '''
<!-- CARREGAMENTO SUPER SIMPLES DE SÓCIOS -->
<script>
{% if client %}
console.log('🚀 CARREGAMENTO SIMPLES DE SÓCIOS');
var dadosCliente = {{ client|tojson }};
console.log('📊 Dados recebidos:', dadosCliente);
console.log('🔍 Sócio 2:', dadosCliente.socio_2_nome);

// Carregar após 1 segundo
setTimeout(function() {
    console.log('⚡ Executando carregamento...');
    
    if (dadosCliente.socio_2_nome && dadosCliente.socio_2_nome.trim()) {
        console.log('✅ Sócio 2 encontrado:', dadosCliente.socio_2_nome);
        
        var container = document.getElementById('sociosContainer');
        if (container) {
            console.log('✅ Container encontrado');
            
            var html = '';
            html += '<div class="card border-light mb-2 socio-card" id="socio_2">';
            html += '  <div class="card-body py-3">';
            html += '    <div class="d-flex justify-content-between align-items-center mb-2">';
            html += '      <span class="badge bg-primary">Sócio 2</span>';
            html += '      <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest(\\'.socio-card\\').remove()">❌</button>';
            html += '    </div>';
            html += '    <div class="row align-items-center">';
            html += '      <div class="col-md-4 mb-2">';
            html += '        <label class="form-label small mb-1">Nome do Sócio</label>';
            html += '        <input type="text" class="form-control form-control-sm" name="socio_2_nome" value="' + dadosCliente.socio_2_nome + '">';
            html += '      </div>';
            html += '      <div class="col-md-2 mb-2">';
            html += '        <label class="form-label small mb-1">CPF</label>';
            html += '        <input type="text" class="form-control form-control-sm" name="socio_2_cpf" value="' + (dadosCliente.socio_2_cpf || '') + '">';
            html += '      </div>';
            html += '      <div class="col-md-2 mb-2">';
            html += '        <label class="form-label small mb-1">Data Nascimento</label>';
            html += '        <input type="date" class="form-control form-control-sm" name="socio_2_data_nascimento" value="' + (dadosCliente.socio_2_data_nascimento || '') + '">';
            html += '      </div>';
            html += '      <div class="col-md-2 mb-2">';
            html += '        <label class="form-label small mb-1">% Quotas</label>';
            html += '        <input type="number" class="form-control form-control-sm" name="socio_2_participacao" value="' + (dadosCliente.socio_2_participacao || '') + '">';
            html += '      </div>';
            html += '      <div class="col-md-2 mb-2">';
            html += '        <small class="text-muted">Flags: Em desenvolvimento</small>';
            html += '      </div>';
            html += '    </div>';
            html += '  </div>';
            html += '</div>';
            
            container.innerHTML += html;
            console.log('🎉 SÓCIO 2 CARREGADO COM SUCESSO!');
        } else {
            console.error('❌ Container sociosContainer não encontrado');
        }
    } else {
        console.log('ℹ️ Sócio 2 não tem nome ou está vazio');
    }
}, 1000);
{% endif %}
</script>
'''
    
    # Procurar por </body> e inserir antes
    if '</body>' in content:
        print("✅ Tag </body> encontrada!")
        content = content.replace('</body>', js_code + '\n</body>')
        
        # Salvar o arquivo
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Código de carregamento simples adicionado!")
        print("📍 Inserido antes da tag </body>")
        print("🔍 Teste agora e verifique o console!")
    else:
        print("❌ Tag </body> não encontrada!")
        print("🔍 Procurando por outras tags...")
        if '</html>' in content:
            print("✅ Tag </html> encontrada - usando ela")
            content = content.replace('</html>', js_code + '\n</html>')
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Código adicionado antes de </html>!")
        else:
            print("❌ Nenhuma tag de fechamento encontrada!")

if __name__ == "__main__":
    adicionar_carregamento_simples()
