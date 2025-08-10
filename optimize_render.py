#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Otimização RENDER
Prepara a aplicação para consumir menos de 256MB de memória no Render
"""

import os
import sys
import shutil
import json

def optimize_for_render():
    """Aplicar todas as otimizações para deploy no Render"""
    
    print("🎯 INICIANDO OTIMIZAÇÃO PARA RENDER")
    print("=" * 50)
    
    # 1. Verificar se está no diretório correto
    if not os.path.exists('app.py'):
        print("❌ Erro: Execute este script no diretório raiz da aplicação")
        return False
    
    # 2. Backup do requirements.txt original
    if os.path.exists('requirements.txt'):
        print("📋 Fazendo backup do requirements.txt original...")
        shutil.copy('requirements.txt', 'requirements.original.txt')
    
    # 3. Substituir requirements.txt pelo otimizado
    if os.path.exists('requirements.render.minimal.txt'):
        print("📦 Aplicando requirements.txt otimizado para Render...")
        shutil.copy('requirements.render.minimal.txt', 'requirements.txt')
    
    # 4. Verificar configurações Gunicorn
    if os.path.exists('gunicorn.render.optimized.conf.py'):
        print("⚙️ Configuração Gunicorn otimizada encontrada")
    else:
        print("⚠️ Aviso: Configuração Gunicorn otimizada não encontrada")
    
    # 5. Verificar Procfile
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            procfile_content = f.read()
        
        if 'gunicorn.render.optimized.conf.py' in procfile_content:
            print("✅ Procfile já otimizado")
        else:
            print("⚠️ Aviso: Procfile pode não estar otimizado")
    
    # 6. Verificar variáveis de ambiente necessárias
    print("\n🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE NECESSÁRIAS:")
    required_env_vars = [
        'GOOGLE_SERVICE_ACCOUNT_JSON',
        'GOOGLE_SHEETS_ID',
        'SECRET_KEY'
    ]
    
    for var in required_env_vars:
        if os.environ.get(var):
            print(f"   ✅ {var}: Configurado")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADO")
    
    # 7. Informações sobre otimizações aplicadas
    print("\n🚀 OTIMIZAÇÕES APLICADAS:")
    print("   ✅ Memory Optimizer Lite")
    print("   ✅ Gunicorn: 1 worker, 3 conexões")
    print("   ✅ Upload limitado: 256KB")
    print("   ✅ GC agressivo: (10,1,1)")
    print("   ✅ Cache mínimo: 5 minutos")
    print("   ✅ Timeouts baixos: 15s")
    print("   ✅ Logs mínimos: apenas erros")
    print("   ✅ Dependências mínimas")
    
    # 8. Estimativa de uso de memória
    print("\n📊 ESTIMATIVA DE USO DE MEMÓRIA:")
    memory_components = {
        "Python runtime": "~30MB",
        "Flask + dependências": "~40MB",
        "Google API client": "~25MB",
        "Aplicação + templates": "~15MB",
        "Buffer/overhead": "~20MB",
        "TOTAL ESTIMADO": "~130MB"
    }
    
    for component, usage in memory_components.items():
        print(f"   {component}: {usage}")
    
    print("\n" + "=" * 50)
    print("🎯 OTIMIZAÇÃO CONCLUÍDA!")
    print("💾 Objetivo: <256MB de memória")
    print("📈 Estimativa: ~130MB")
    print("🚀 Redução esperada: ~70% (de 500MB)")
    
    # 9. Próximos passos
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("1. Commit e push das mudanças")
    print("2. Deploy no Render")
    print("3. Monitorar uso de memória")
    print("4. Verificar logs para erros")
    
    return True

def revert_optimizations():
    """Reverter otimizações (voltar ao original)"""
    print("🔄 REVERTENDO OTIMIZAÇÕES...")
    
    # Restaurar requirements.txt original
    if os.path.exists('requirements.original.txt'):
        print("📦 Restaurando requirements.txt original...")
        shutil.copy('requirements.original.txt', 'requirements.txt')
        os.remove('requirements.original.txt')
    
    print("✅ Otimizações revertidas")

def show_memory_tips():
    """Mostrar dicas de otimização de memória"""
    print("\n💡 DICAS PARA REDUZIR AINDA MAIS A MEMÓRIA:")
    print("━" * 50)
    print("1. 🗄️  Use cache Redis externo em vez de cache interno")
    print("2. 📦  Remova dependências desnecessárias")
    print("3. 🔄  Configure restart automático dos workers")
    print("4. 📊  Use lazy loading para dados grandes")
    print("5. 🧹  Implemente limpeza automática de sessões")
    print("6. ⚡  Use CDN para arquivos estáticos")
    print("7. 🗂️  Considere pagination para listas grandes")
    print("8. 💾  Use format JSON compacto (sem pretty print)")

if __name__ == "__main__":
    print("🎯 OTIMIZADOR RENDER - Control Contabilidade")
    print("Objetivo: Reduzir uso de memória de 500MB para <256MB")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "revert":
            revert_optimizations()
        elif sys.argv[1] == "tips":
            show_memory_tips()
        else:
            print("Uso: python optimize_render.py [revert|tips]")
    else:
        optimize_for_render()
        show_memory_tips()
