#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste direto do funcionamento do botão Adicionar Sócio
"""

print("🔧 TESTANDO BOTÃO ADICIONAR SÓCIO")
print("=" * 50)

# Instruções para o usuário
print("📋 INSTRUÇÕES PARA TESTE:")
print("1. Acesse: http://localhost:5000/add")
print("2. Abra o DevTools do navegador (F12)")
print("3. Vá na aba 'Console'")
print("4. Procure pela seção 'SÓCIOS DA EMPRESA'")
print("5. Clique no botão 'Adicionar Sócio'")
print()

print("✅ O QUE DEVE ACONTECER:")
print("- Deve aparecer logs no console começando com '🔧 INICIANDO adicionarSocio()...'")
print("- Deve aparecer um novo card de sócio")
print("- O campo nome deve ficar em foco")
print("- Deve ser possível adicionar até 10 sócios")
print()

print("❌ SE NÃO FUNCIONAR:")
print("- Verifique se há erros no console")
print("- Verifique se o botão tem onclick='adicionarSocio()'")
print("- Verifique se existe o elemento com id='sociosContainer'")
print()

print("🔍 COMANDOS PARA TESTAR NO CONSOLE DO NAVEGADOR:")
print("// Verificar se a função existe:")
print("typeof adicionarSocio")
print()
print("// Verificar se o container existe:")
print("document.getElementById('sociosContainer')")
print()
print("// Testar a função manualmente:")
print("adicionarSocio()")
print()

print("🚀 TESTE AUTOMATIZADO:")
print("Execute este comando no console do navegador:")
print("""
console.log('=== TESTE AUTOMÁTICO DO BOTÃO ADICIONAR SÓCIO ===');

// 1. Verificar função
if (typeof adicionarSocio === 'function') {
    console.log('✅ Função adicionarSocio existe');
} else {
    console.error('❌ Função adicionarSocio NÃO existe');
}

// 2. Verificar container
const container = document.getElementById('sociosContainer');
if (container) {
    console.log('✅ Container sociosContainer existe');
} else {
    console.error('❌ Container sociosContainer NÃO existe');
}

// 3. Verificar botão
const botao = document.querySelector('button[onclick="adicionarSocio()"]');
if (botao) {
    console.log('✅ Botão onclick="adicionarSocio()" existe');
} else {
    console.error('❌ Botão onclick="adicionarSocio()" NÃO existe');
}

// 4. Contar sócios atuais
const sociosAtuais = container ? container.querySelectorAll('.socio-card').length : 0;
console.log(`📊 Sócios atuais: ${sociosAtuais}`);

// 5. Testar função (descomente para executar)
// console.log('Testando função...');
// adicionarSocio();
""")

print("\n" + "="*50)
print("🌐 PÁGINA DE TESTE ABERTA: http://localhost:5000/add")
print("Teste o botão 'Adicionar Sócio' agora!")
